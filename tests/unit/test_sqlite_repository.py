"""Tests for local job and review persistence."""

from pathlib import Path

from job_recommendation_agent.domain.models import Feedback
from job_recommendation_agent.persistence.sqlite_repository import SQLiteJobRepository
from job_recommendation_agent.services.demo_data import demo_jobs


def test_repository_persists_jobs_and_reviews(tmp_path: Path) -> None:
    repository = SQLiteJobRepository(tmp_path / "test.db")
    repository.initialize()
    repository.upsert_jobs(demo_jobs())

    jobs = repository.list_jobs()
    repository.save_review(
        jobs[0].id,
        feedback=Feedback.LIKE,
        applied=True,
        dislike_reason="",
        notes="Strong fit",
        rating=5,
    )
    review = repository.list_reviews()[jobs[0].id]

    assert len(jobs) == 3
    assert review.rating == 5
    assert review.feedback is Feedback.LIKE
    assert review.applied is True
    assert review.notes == "Strong fit"


def test_repository_persists_metadata(tmp_path: Path) -> None:
    repository = SQLiteJobRepository(tmp_path / "metadata.db")
    repository.initialize()

    assert repository.get_metadata("last_sync") is None
    repository.set_metadata("last_sync", "2026-07-14T12:00:00+00:00")

    assert repository.get_metadata("last_sync") == "2026-07-14T12:00:00+00:00"
