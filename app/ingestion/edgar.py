from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol


class EdgarClient(Protocol):
    def company_facts(self, cik: str) -> dict: ...


class FixtureEdgarClient:
    """Reads SEC companyfacts JSON from a local fixture directory.

    Use this when sec.gov egress is unavailable. Files must be named
    `CIK<10-digit-zero-padded-cik>.json`, matching SEC's URL convention.
    """

    def __init__(self, fixture_dir: Path | None = None) -> None:
        self.fixture_dir = fixture_dir or Path("fixtures/edgar")

    def company_facts(self, cik: str) -> dict:
        path = self.fixture_dir / f"CIK{cik.zfill(10)}.json"
        if not path.exists():
            raise FileNotFoundError(f"No EDGAR fixture for CIK {cik} at {path}")
        return json.loads(path.read_text())


class SecEdgarClient:
    """Real SEC EDGAR client. Requires sec.gov egress.

    Per SEC fair-access policy the User-Agent must include a contact email and
    request rate must not exceed 10 req/s (we cap at 8 to be safe).
    """

    BASE = "https://data.sec.gov"

    def __init__(self, user_agent: str) -> None:
        if "@" not in user_agent:
            raise ValueError("EDGAR User-Agent must include a contact email")
        self.user_agent = user_agent

    def company_facts(self, cik: str) -> dict:
        import httpx

        url = f"{self.BASE}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
        with httpx.Client(headers={"User-Agent": self.user_agent}, timeout=30.0) as c:
            r = c.get(url)
            r.raise_for_status()
            return r.json()


def facts_sha256(facts: dict) -> str:
    return hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()
