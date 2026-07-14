"""SQLite persistence for normalized jobs and user reviews."""

import json
import sqlite3
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path

from job_recommendation_agent.domain.models import (
    EmploymentType,
    Feedback,
    Job,
    JobReview,
)


class SQLiteJobRepository:
    """Store and retrieve jobs and reviews in a local SQLite database."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    employment_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    skills_json TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    posted_date TEXT,
                    posted_at TEXT,
                    is_remote INTEGER NOT NULL,
                    is_demo INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    job_id TEXT PRIMARY KEY REFERENCES jobs(id) ON DELETE CASCADE,
                    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                    feedback TEXT NOT NULL,
                    applied INTEGER NOT NULL DEFAULT 0,
                    dislike_reason TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(jobs)").fetchall()
            }
            if "posted_at" not in columns:
                connection.execute("ALTER TABLE jobs ADD COLUMN posted_at TEXT")
            review_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(reviews)").fetchall()
            }
            if "applied" not in review_columns:
                connection.execute(
                    "ALTER TABLE reviews ADD COLUMN applied INTEGER NOT NULL DEFAULT 0"
                )
            if "dislike_reason" not in review_columns:
                connection.execute(
                    "ALTER TABLE reviews ADD COLUMN dislike_reason TEXT NOT NULL DEFAULT ''"
                )

    def upsert_jobs(self, jobs: Iterable[Job]) -> None:
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO jobs (
                    id, title, company, location, employment_type, description,
                    skills_json, source_name, source_url, posted_date, posted_at,
                    is_remote, is_demo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title, company=excluded.company,
                    location=excluded.location,
                    employment_type=excluded.employment_type,
                    description=excluded.description, skills_json=excluded.skills_json,
                    source_name=excluded.source_name, source_url=excluded.source_url,
                    posted_date=excluded.posted_date, posted_at=excluded.posted_at,
                    is_remote=excluded.is_remote,
                    is_demo=excluded.is_demo
                """,
                [self._job_to_row(job) for job in jobs],
            )

    def list_jobs(self) -> list[Job]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM jobs ORDER BY posted_date DESC, company, title"
            ).fetchall()
        return [self._row_to_job(row) for row in rows]

    def list_reviews(self) -> dict[str, JobReview]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM reviews").fetchall()
        return {
            row["job_id"]: JobReview(
                job_id=row["job_id"],
                rating=row["rating"],
                feedback=Feedback(row["feedback"]),
                applied=bool(row["applied"]),
                dislike_reason=row["dislike_reason"],
                notes=row["notes"],
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        }

    def save_review(
        self,
        job_id: str,
        feedback: Feedback,
        applied: bool,
        dislike_reason: str,
        notes: str,
        rating: int | None = None,
    ) -> None:
        updated_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO reviews (
                    job_id, rating, feedback, applied, dislike_reason, notes, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    rating=excluded.rating, feedback=excluded.feedback,
                    applied=excluded.applied, dislike_reason=excluded.dislike_reason,
                    notes=excluded.notes, updated_at=excluded.updated_at
                """,
                (
                    job_id,
                    rating,
                    feedback.value,
                    int(applied),
                    dislike_reason.strip(),
                    notes.strip(),
                    updated_at,
                ),
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _job_to_row(job: Job) -> tuple[object, ...]:
        return (
            job.id,
            job.title,
            job.company,
            job.location,
            job.employment_type.value,
            job.description,
            json.dumps(job.skills),
            job.source_name,
            str(job.source_url),
            job.posted_date.isoformat() if job.posted_date else None,
            job.posted_at.isoformat() if job.posted_at else None,
            int(job.is_remote),
            int(job.is_demo),
        )

    @staticmethod
    def _row_to_job(row: sqlite3.Row) -> Job:
        return Job(
            id=row["id"],
            title=row["title"],
            company=row["company"],
            location=row["location"],
            employment_type=EmploymentType(row["employment_type"]),
            description=row["description"],
            skills=json.loads(row["skills_json"]),
            source_name=row["source_name"],
            source_url=row["source_url"],
            posted_date=date.fromisoformat(row["posted_date"]) if row["posted_date"] else None,
            posted_at=datetime.fromisoformat(row["posted_at"]) if row["posted_at"] else None,
            is_remote=bool(row["is_remote"]),
            is_demo=bool(row["is_demo"]),
        )
