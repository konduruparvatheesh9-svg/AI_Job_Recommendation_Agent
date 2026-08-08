"""Application configuration loaded from environment variables."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    database_path: Path = Path("data/jobs.db")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    request_timeout_seconds: float = Field(default=15.0, gt=0, le=60)
    arbeitnow_api_url: str = "https://www.arbeitnow.com/api/job-board-api"
    arbeitnow_pages: int = Field(default=5, ge=1, le=10)
    bosch_api_url: str = "https://api.smartrecruiters.com/v1/companies/BoschGroup/postings"
    continental_api_url: str = (
        "https://api.smartrecruiters.com/v1/companies/Continental/postings"
    )
    amazon_jobs_api_url: str = "https://www.amazon.jobs/en/search.json"
