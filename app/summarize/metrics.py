from __future__ import annotations

from decimal import Decimal

# Revenue is filed under different us-gaap tags depending on issuer and year;
# try the modern ASC 606 tag first, then fall back to legacy names.
_REVENUE_TAGS: tuple[str, ...] = (
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
)
_EPS_TAGS: tuple[str, ...] = ("EarningsPerShareDiluted",)


def _find_fact(
    facts: dict, tags: tuple[str, ...], fy: int, fp: str, form: str
) -> tuple[Decimal, str, str | None] | None:
    """Return (value, unit, period_end) for the first matching fact across tags."""
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        units = gaap.get(tag, {}).get("units", {})
        for unit_label, unit_facts in units.items():
            for f in unit_facts:
                if f.get("fy") == fy and f.get("fp") == fp and f.get("form") == form:
                    return Decimal(str(f["val"])), unit_label, f.get("end")
    return None


def extract_metrics(facts: dict, fy: int, fp: str, form: str = "10-Q") -> dict:
    """Extract EPS (diluted) and Revenue for a given fiscal year/quarter.

    `fp` follows SEC's convention: "Q1", "Q2", "Q3", or "FY".
    Returns a dict mapping metric name to {"value": Decimal, "unit": str,
    "period_end": "YYYY-MM-DD" | None}; missing metrics are simply absent.
    """
    out: dict[str, dict] = {}
    eps = _find_fact(facts, _EPS_TAGS, fy, fp, form)
    if eps:
        out["eps_diluted"] = {"value": eps[0], "unit": eps[1], "period_end": eps[2]}
    rev = _find_fact(facts, _REVENUE_TAGS, fy, fp, form)
    if rev:
        out["revenue"] = {"value": rev[0], "unit": rev[1], "period_end": rev[2]}
    return out


def period_end_from_metrics(metrics: dict) -> str | None:
    for payload in metrics.values():
        if payload.get("period_end"):
            return payload["period_end"]
    return None
