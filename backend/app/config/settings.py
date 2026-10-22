"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ────────────────────────────────────────────
    APP_NAME: str = "Autonomous AI Market Research Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ─── Server ─────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ─── Security ───────────────────────────────────────────────
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── Database ───────────────────────────────────────────────
    DATABASE_URL: str = Field(...)
    DB_ECHO: bool = False

    # ─── Google Gemini ──────────────────────────────────────────
    GEMINI_API_KEY: str = Field(...)
    # Auto-updating alias — always resolves to the current GA lightweight model
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    GEMINI_TEMPERATURE: float = 0.2

    # ─── Tavily ─────────────────────────────────────────────────
    TAVILY_API_KEY: str = Field(...)
    TAVILY_MAX_RESULTS: int = 10
    TAVILY_SEARCH_DEPTH: str = "advanced"

    # ─── Playwright ─────────────────────────────────────────────
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000
    PLAYWRIGHT_MAX_CONCURRENT: int = 5

    # ─── Redis / Celery ─────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ─── Email ──────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@marketresearch.ai"
    SMTP_USE_TLS: bool = True

    # ─── Research Defaults ──────────────────────────────────────
    MAX_COMPETITORS: int = 5
    MAX_ARTICLES_PER_COMPETITOR: int = 10
    MAX_RESEARCH_DURATION_MINUTES: int = 15
    EMBEDDING_DIMENSION: int = 768

    # ─── Rate Limiting ──────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    # ─── Feature Expansion — Sentiment ─────────────────────────
    SENTIMENT_ENABLED: bool = True

    # ─── Feature Expansion — Chat / RAG ────────────────────────
    CHAT_MAX_CONTEXT_TOKENS: int = 8000
    CHAT_MAX_HISTORY: int = 20

    # ─── Feature Expansion — Scheduled Runs ────────────────────
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TICK_SECONDS: int = 300

    # ─── Feature Expansion — Change Detection ──────────────────
    DIFF_SIGNIFICANCE_THRESHOLD: int = 6

    # ─── Feature Expansion — One-Pager ─────────────────────────
    ONEPAGER_MAX_WORDS: int = 250

    # ─── Feature Expansion — Financial Intelligence ────────────
    CRUNCHBASE_API_KEY: Optional[str] = None
    FINANCIAL_DATA_PROVIDER: str = "tavily"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def cors_origins_list(self) -> List[str]:
        v = self.CORS_ORIGINS.strip()
        if v.startswith("[") and v.endswith("]"):
            import json
            return json.loads(v)
        return [origin.strip() for origin in v.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()