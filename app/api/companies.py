from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Company, Filing, Metric, Quarter, Summary
from app.db.session import SessionLocal
from app.ingestion.edgar import EdgarClient, FixtureEdgarClient, facts_sha256
from app.llm import LLMRouter
from app.summarize.metrics import extract_metrics, period_end_from_metrics

SUMMARIZE_PROMPT_NAME = "summarize_quarter"
SUMMARIZE_PROMPT_VERSION = 1

# Slice-scope ticker registry. A real implementation looks up CIKs from SEC's
# company-tickers index or a seed table.
TICKER_TO_CIK: dict[str, tuple[str, str]] = {
    "AAPL": ("0000320193", "Apple Inc."),
}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_edgar_client() -> EdgarClient:
    return FixtureEdgarClient()


def get_llm_router(request: Request) -> LLMRouter:
    return request.app.state.llm_router


router = APIRouter(prefix="/companies", tags=["companies"])

DbDep = Annotated[Session, Depends(get_db)]
EdgarDep = Annotated[EdgarClient, Depends(get_edgar_client)]
LLMDep = Annotated[LLMRouter, Depends(get_llm_router)]


@router.get("/{ticker}/quarters/{fy}/{fq}")
def get_quarter(
    ticker: str,
    fy: int,
    fq: str,
    db: DbDep,
    edgar: EdgarDep,
) -> dict:
    ticker = ticker.upper()
    fq = fq.upper()
    if not fq.startswith("Q") or fq[1:] not in {"1", "2", "3", "4"}:
        raise HTTPException(400, "fq must be Q1, Q2, Q3, or Q4")
    if ticker not in TICKER_TO_CIK:
        raise HTTPException(404, f"Unknown ticker: {ticker}")
    cik, name = TICKER_TO_CIK[ticker]
    quarter_num = int(fq[1:])

    company = db.scalar(select(Company).where(Company.ticker == ticker))
    if company is None:
        company = Company(ticker=ticker, cik=cik, name=name)
        db.add(company)
        db.flush()

    quarter = db.scalar(
        select(Quarter).where(
            Quarter.company_id == company.id,
            Quarter.fiscal_year == fy,
            Quarter.fiscal_quarter == quarter_num,
        )
    )

    if quarter is None or not quarter.filings:
        facts = edgar.company_facts(cik)
        metrics_payload = extract_metrics(facts, fy=fy, fp=fq)
        if not metrics_payload:
            raise HTTPException(404, f"No XBRL facts for {ticker} {fy} {fq}")
        period_end = period_end_from_metrics(metrics_payload) or ""

        if quarter is None:
            quarter = Quarter(
                company_id=company.id,
                fiscal_year=fy,
                fiscal_quarter=quarter_num,
                period_end=period_end,
            )
            db.add(quarter)
            db.flush()

        filing = Filing(
            quarter_id=quarter.id,
            kind="FACTS",
            source="fixture",
            sha256=facts_sha256(facts),
        )
        db.add(filing)
        db.flush()

        for metric_name, payload in metrics_payload.items():
            db.add(
                Metric(
                    quarter_id=quarter.id,
                    name=metric_name,
                    value=payload["value"],
                    unit=payload["unit"],
                    source_filing_id=filing.id,
                )
            )
        db.commit()
        db.refresh(quarter)

    return {
        "ticker": company.ticker,
        "name": company.name,
        "cik": company.cik,
        "fiscal_year": quarter.fiscal_year,
        "fiscal_quarter": f"Q{quarter.fiscal_quarter}",
        "period_end": quarter.period_end,
        "metrics": [
            {
                "name": m.name,
                "value": str(m.value),
                "unit": m.unit,
                "source_filing_id": m.source_filing_id,
            }
            for m in quarter.metrics
        ],
        "disclaimer": "Informational only, not investment advice.",
    }


@router.get("/{ticker}/quarters/{fy}/{fq}/summary")
def get_quarter_summary(
    ticker: str,
    fy: int,
    fq: str,
    db: DbDep,
    edgar: EdgarDep,
    llm: LLMDep,
) -> dict:
    quarter_data = get_quarter(ticker=ticker, fy=fy, fq=fq, db=db, edgar=edgar)

    quarter = db.scalar(
        select(Quarter)
        .join(Company, Quarter.company_id == Company.id)
        .where(
            Company.ticker == quarter_data["ticker"],
            Quarter.fiscal_year == quarter_data["fiscal_year"],
            Quarter.fiscal_quarter == int(quarter_data["fiscal_quarter"][1:]),
        )
    )

    prompt_id = f"{SUMMARIZE_PROMPT_NAME}:v{SUMMARIZE_PROMPT_VERSION}"
    summary = db.scalar(
        select(Summary).where(
            Summary.quarter_id == quarter.id,
            Summary.prompt_id == prompt_id,
        )
    )
    cached = summary is not None
    if summary is None:
        result = llm.run(SUMMARIZE_PROMPT_NAME, SUMMARIZE_PROMPT_VERSION, quarter_data)
        summary = Summary(
            quarter_id=quarter.id,
            prompt_id=prompt_id,
            text=result.text,
            model=result.model,
            request_id=result.request_id,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
            latency_ms=result.latency_ms,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)

    return {
        "ticker": quarter_data["ticker"],
        "name": quarter_data["name"],
        "fiscal_year": quarter_data["fiscal_year"],
        "fiscal_quarter": quarter_data["fiscal_quarter"],
        "period_end": quarter_data["period_end"],
        "prompt_id": summary.prompt_id,
        "model": summary.model,
        "summary": summary.text,
        "usage": {
            "input_tokens": summary.input_tokens,
            "output_tokens": summary.output_tokens,
            "latency_ms": summary.latency_ms,
        },
        "cached": cached,
        "disclaimer": "Informational only, not investment advice.",
    }
