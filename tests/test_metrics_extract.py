from decimal import Decimal

from app.summarize.metrics import extract_metrics, period_end_from_metrics


def _facts(eps_val: float, rev_val: float) -> dict:
    return {
        "facts": {
            "us-gaap": {
                "EarningsPerShareDiluted": {
                    "units": {
                        "USD/shares": [
                            {
                                "end": "2025-03-29",
                                "val": eps_val,
                                "fy": 2025,
                                "fp": "Q2",
                                "form": "10-Q",
                            }
                        ]
                    }
                },
                "Revenues": {
                    "units": {
                        "USD": [
                            {
                                "end": "2025-03-29",
                                "val": rev_val,
                                "fy": 2025,
                                "fp": "Q2",
                                "form": "10-Q",
                            }
                        ]
                    }
                },
            }
        }
    }


def test_extract_metrics_returns_decimals() -> None:
    out = extract_metrics(_facts(1.65, 95_359_000_000), fy=2025, fp="Q2")
    assert out["eps_diluted"]["value"] == Decimal("1.65")
    assert out["eps_diluted"]["unit"] == "USD/shares"
    assert out["revenue"]["value"] == Decimal("95359000000")
    assert out["revenue"]["unit"] == "USD"


def test_extract_metrics_skips_wrong_period() -> None:
    out = extract_metrics(_facts(1.65, 95_359_000_000), fy=2025, fp="Q3")
    assert out == {}


def test_period_end_helper() -> None:
    out = extract_metrics(_facts(1.65, 95_359_000_000), fy=2025, fp="Q2")
    assert period_end_from_metrics(out) == "2025-03-29"


def test_revenue_tag_fallback() -> None:
    # Try a facts dict that only has the modern ASC 606 tag.
    facts = {
        "facts": {
            "us-gaap": {
                "RevenueFromContractWithCustomerExcludingAssessedTax": {
                    "units": {
                        "USD": [
                            {
                                "end": "2025-03-29",
                                "val": 95_359_000_000,
                                "fy": 2025,
                                "fp": "Q2",
                                "form": "10-Q",
                            }
                        ]
                    }
                }
            }
        }
    }
    out = extract_metrics(facts, fy=2025, fp="Q2")
    assert out["revenue"]["value"] == Decimal("95359000000")
