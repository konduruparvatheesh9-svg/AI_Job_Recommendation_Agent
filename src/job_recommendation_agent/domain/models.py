"""Validated domain models used across sources, storage, and UI."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class EmploymentType(StrEnum):
    """Supported early-career employment categories."""

    INTERNSHIP = "Internship / Praktikum"
    THESIS = "Thesis / Abschlussarbeit"
    WORKING_STUDENT = "Werkstudent"
    GRADUATE = "Graduate"
    ENTRY_LEVEL = "Entry level"


class Feedback(StrEnum):
    """User preference recorded for a job."""

    NONE = "Not reviewed"
    LIKE = "Like"
    DISLIKE = "Dislike"
    REJECTED = "Rejected / not proceeding"


class Job(BaseModel):
    """A normalized job opportunity from any authorized source."""

    id: str
    title: str
    company: str
    location: str
    employment_type: EmploymentType
    description: str
    skills: list[str] = Field(default_factory=list)
    source_name: str
    source_url: HttpUrl
    posted_date: date | None = None
    posted_at: datetime | None = None
    is_remote: bool = False
    is_demo: bool = False


class JobReview(BaseModel):
    """A user's evaluation of one job opportunity."""

    job_id: str
    rating: int | None = Field(default=None, ge=1, le=5)
    feedback: Feedback = Feedback.NONE
    applied: bool = False
    dislike_reason: str = ""
    notes: str = ""
    updated_at: datetime
