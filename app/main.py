from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.companies import router as companies_router
from app.db.session import init_db
from app.llm import LiteLLMRouter, PromptRegistry
from app.observability.logging import configure_logging
from app.web.routes import router as web_router

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.llm_router = LiteLLMRouter(PromptRegistry())
    yield


app = FastAPI(title="Quarterly Earnings Summarizer", version="0.1.0", lifespan=lifespan)
app.include_router(companies_router)
app.include_router(web_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
