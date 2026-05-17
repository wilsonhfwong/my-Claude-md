from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.companies import get_db
from app.db.session import Base
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # StaticPool keeps the single in-memory SQLite shared across connections;
    # without it each new connection gets a fresh empty database.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionTest = sessionmaker(engine, expire_on_commit=False, autoflush=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = SessionTest()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_aapl_q2_2025_returns_known_metrics(client: TestClient) -> None:
    r = client.get("/companies/AAPL/quarters/2025/Q2")
    assert r.status_code == 200
    body = r.json()
    assert body["ticker"] == "AAPL"
    assert body["name"] == "Apple Inc."
    assert body["period_end"] == "2025-03-29"
    by_name = {m["name"]: m for m in body["metrics"]}
    assert Decimal(by_name["eps_diluted"]["value"]) == Decimal("1.65")
    assert Decimal(by_name["revenue"]["value"]) == Decimal("95359000000")
    assert body["disclaimer"] == "Informational only, not investment advice."


def test_repeat_call_does_not_duplicate_metrics(client: TestClient) -> None:
    r1 = client.get("/companies/AAPL/quarters/2025/Q2")
    r2 = client.get("/companies/AAPL/quarters/2025/Q2")
    assert len(r1.json()["metrics"]) == 2
    assert len(r2.json()["metrics"]) == 2


def test_unknown_ticker_returns_404(client: TestClient) -> None:
    r = client.get("/companies/ZZZZ/quarters/2025/Q2")
    assert r.status_code == 404


def test_unknown_quarter_returns_404(client: TestClient) -> None:
    r = client.get("/companies/AAPL/quarters/2099/Q1")
    assert r.status_code == 404


def test_bad_fq_returns_400(client: TestClient) -> None:
    r = client.get("/companies/AAPL/quarters/2025/Q9")
    assert r.status_code == 400


def test_html_page_renders(client: TestClient) -> None:
    r = client.get("/web/companies/AAPL/quarters/2025/Q2")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    body = r.text
    assert "Apple Inc." in body
    assert "1.65" in body
    assert "95359000000" in body
    assert "Informational only, not investment advice." in body
