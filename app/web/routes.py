from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.companies import DbDep, EdgarDep, get_quarter

_templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(
        "<h1>Quarterly Earnings Summarizer</h1>"
        "<p>Try "
        '<a href="/web/companies/AAPL/quarters/2025/Q2">AAPL FY2025 Q2</a>'
        " &middot; "
        '<a href="/companies/AAPL/quarters/2025/Q2">JSON</a> &middot; '
        '<a href="/docs">API docs</a></p>'
    )


@router.get("/web/companies/{ticker}/quarters/{fy}/{fq}", response_class=HTMLResponse)
def quarter_page(
    request: Request,
    ticker: str,
    fy: int,
    fq: str,
    db: DbDep,
    edgar: EdgarDep,
) -> HTMLResponse:
    data = get_quarter(ticker=ticker, fy=fy, fq=fq, db=db, edgar=edgar)
    return templates.TemplateResponse(request=request, name="quarter.html", context={"data": data})
