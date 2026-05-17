from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///data/app.db"
    blob_store_root: Path = Path("data/blobs")

    redis_url: str = "redis://localhost:6379/0"

    default_model: str = "anthropic/claude-sonnet-4-6"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None

    # SEC EDGAR requires a descriptive User-Agent with a contact address;
    # requests without one are throttled or blocked.
    edgar_user_agent: str = "FinSummary contact@example.com"

    audio_provider: str = "quartr"
    audio_api_key: str | None = None

    agent_cost_cap_usd: float = 50.0
    agent_max_iterations_per_week: int = 50


settings = Settings()
