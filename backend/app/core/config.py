from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    project_name: str = "GAN Studio"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    environment: Literal["local", "staging", "production"] = "local"

    secret_key: str = Field(default="change-me-in-production", min_length=16)
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    database_url: str = "sqlite:///./storage/gan_studio.db"
    redis_url: str = "redis://redis:6379/0"
    broker_url: str = "redis://redis:6379/1"
    result_backend: str = "redis://redis:6379/2"

    frontend_url: str = "http://localhost:3000"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    local_storage_dir: Path = BASE_DIR / "storage" / "images"
    model_registry_dir: Path = BASE_DIR / "storage" / "models"
    dataset_dir: Path = BASE_DIR / "storage" / "datasets"

    aws_s3_enabled: bool = False
    aws_s3_bucket: str | None = None
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    default_device: str = "cpu"
    max_upload_size_mb: int = 20
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.local_storage_dir.mkdir(parents=True, exist_ok=True)
    settings.model_registry_dir.mkdir(parents=True, exist_ok=True)
    settings.dataset_dir.mkdir(parents=True, exist_ok=True)
    return settings

