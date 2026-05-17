from fastapi import FastAPI

from app.observability.logging import configure_logging

configure_logging()

app = FastAPI(title="Quarterly Earnings Summarizer", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
