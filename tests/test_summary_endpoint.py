from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.companies import get_db, get_llm_router
from app.db.session import Base
from app.llm import FakeLLMRouter, PromptRegistry
from app.main import app


@pytest.fixture
def fake_llm() -> FakeLLMRouter:
    return FakeLLMRouter(PromptRegistry())


@pytest.fixture
def client(fake_llm: FakeLLMRouter) -> Generator[TestClient, None, None]:
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
    app.dependency_overrides[get_llm_router] = lambda: fake_llm
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_summary_endpoint_calls_llm_and_returns_text(
    client: TestClient, fake_llm: FakeLLMRouter
) -> None:
    fake_llm.set_response(
        "summarize_quarter",
        "Apple reported FY2025 Q2 revenue of $95.359B and diluted EPS of $1.65.",
    )
    r = client.get("/companies/AAPL/quarters/2025/Q2/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["ticker"] == "AAPL"
    assert body["prompt_id"] == "summarize_quarter:v1"
    assert "95.359B" in body["summary"]
    assert body["cached"] is False
    assert body["model"] == "anthropic/claude-sonnet-4-6"
    assert body["disclaimer"] == "Informational only, not investment advice."
    assert len(fake_llm.calls) == 1


def test_summary_renders_real_metrics_into_prompt(
    client: TestClient, fake_llm: FakeLLMRouter
) -> None:
    fake_llm.set_response("summarize_quarter", "x")
    client.get("/companies/AAPL/quarters/2025/Q2/summary")
    rendered = fake_llm.calls[0]["rendered_user"]
    assert "Apple Inc. (AAPL)" in rendered
    assert "FY2025 Q2" in rendered
    assert "2025-03-29" in rendered
    assert "1.65" in rendered
    assert "95359000000" in rendered


def test_summary_is_cached_across_calls(client: TestClient, fake_llm: FakeLLMRouter) -> None:
    fake_llm.set_response("summarize_quarter", "first call")
    r1 = client.get("/companies/AAPL/quarters/2025/Q2/summary")
    fake_llm.set_response("summarize_quarter", "second call — should not be used")
    r2 = client.get("/companies/AAPL/quarters/2025/Q2/summary")
    assert r1.json()["summary"] == "first call"
    assert r2.json()["summary"] == "first call"
    assert r1.json()["cached"] is False
    assert r2.json()["cached"] is True
    assert len(fake_llm.calls) == 1


def test_summary_html_page_renders(client: TestClient, fake_llm: FakeLLMRouter) -> None:
    fake_llm.set_response("summarize_quarter", "Headline summary paragraph.")
    r = client.get("/web/companies/AAPL/quarters/2025/Q2/summary")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    body = r.text
    assert "Headline summary paragraph." in body
    assert "summarize_quarter:v1" in body
    assert "anthropic/claude-sonnet-4-6" in body
    assert "Informational only, not investment advice." in body


def test_summary_404_for_unknown_ticker(client: TestClient) -> None:
    r = client.get("/companies/ZZZZ/quarters/2025/Q2/summary")
    assert r.status_code == 404
