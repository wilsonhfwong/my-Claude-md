from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Company, Filing, Metric, Quarter
from app.db.session import SessionLocal
from app.ingestion.edgar import EdgarClient, FixtureEdgarClient, facts_sha256
from app.summarize.metrics import extract_metrics, period_end_from_metrics

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


router = APIRouter(prefix="/companies", tags=["companies"])

DbDep = Annotated[Session, Depends(get_db)]
EdgarDep = Annotated[EdgarClient, Depends(get_edgar_client)]


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
