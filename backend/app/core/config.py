from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+asyncpg://codecontext:change-me@localhost:5432/codecontext"
    )
    data_dir: str = "./data"
    cors_origins: list[str] = ["http://localhost:3000"]
    max_ingest_file_bytes: int = 1_048_576
    openai_api_key: str | None = None
    embedding_enabled: bool = False
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 64
    llm_enabled: bool = False
    llm_model: str = "gpt-4o-mini"
    llm_max_tokens: int = 2048
    llm_timeout_seconds: float = 120.0

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
