import json
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://docflow:docflow@localhost:5432/docflow"
    upload_dir: Path = Path("./data/uploads")
    text_dir: Path = Path("./data/extracted_text")
    max_upload_bytes: int = 10 * 1024 * 1024
    allowed_mime_types: tuple[str, ...] = ("application/pdf",)
    extraction_provider: str = "demo"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    cors_origins: list[str] = ["http://localhost:3000"]
    ocr_enabled: bool = True
    processing_timeout_seconds: int = 120
    rounding_tolerance: str = "0.02"
    app_name: str = "DocFlow AI"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return json.loads(value)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
