from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI Chatbot SaaS"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    vector_store: str = "faiss"
    vector_store_path: Path = BASE_DIR / "storage" / "vector_indexes"
    upload_dir: Path = BASE_DIR / "storage" / "uploads"
    max_upload_size_mb: int = 25
    rate_limit_per_minute: int = 60
    queue_backend: str = "dramatiq"
    enable_sync_task_fallback: bool = True
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@example.com"
    public_widget_origin: str = "http://localhost:5173"
    admin_dashboard_origin: str = "http://localhost:5174"
    allowed_hosts: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.vector_store_path.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
