from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "The Lenny Growth Assistant"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+asyncpg://lenny:lenny@localhost:5432/lenny"
    )

    llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"

    anthropic_api_key: str | None = None
    anthropic_model: str | None = None

    top_k: int = 8
    rerank_top_k: int = 5

    embedding_provider: str = "ollama"
    ollama_embedding_model: str = ""

    artifact_sanitization_enabled: bool = True
    artifact_iframe_sandbox: bool = True

    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()