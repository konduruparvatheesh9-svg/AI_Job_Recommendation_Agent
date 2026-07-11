"""Contracts implemented by authorized job sources."""

from typing import Protocol

from job_recommendation_agent.domain.models import Job


class JobSource(Protocol):
    """A replaceable provider of normalized job opportunities."""

    def fetch_jobs(self) -> list[Job]:
        """Fetch and normalize currently advertised jobs."""
        ...
