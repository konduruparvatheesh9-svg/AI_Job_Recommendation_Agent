"""Tests for application configuration."""

from job_recommendation_agent.config import Settings


def test_settings_have_safe_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.database_path.as_posix() == "data/jobs.db"
    assert settings.request_timeout_seconds == 15.0
