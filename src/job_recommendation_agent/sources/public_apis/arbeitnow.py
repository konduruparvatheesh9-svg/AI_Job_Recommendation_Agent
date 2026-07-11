"""Adapter for Arbeitnow's documented public job-board API."""

import re
from datetime import UTC, datetime
from html import unescape
from typing import Any

import requests

from job_recommendation_agent.domain.models import EmploymentType, Job

EARLY_CAREER_TERMS = {
    "intern",
    "internship",
    "praktikum",
    "praktikant",
    "working student",
    "werkstudent",
    "graduate",
    "trainee",
    "entry level",
    "junior",
    "berufseinsteiger",
    "ausbildung",
}


class ArbeitnowSource:
    """Fetch Germany-focused listings without scraping protected websites."""

    def __init__(self, api_url: str, timeout_seconds: float = 15.0, pages: int = 5) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds
        self.pages = pages

    def fetch_jobs(self) -> list[Job]:
        jobs: list[Job] = []
        for page in range(1, self.pages + 1):
            response = requests.get(
                self.api_url,
                params={"page": page},
                timeout=self.timeout_seconds,
                headers={"User-Agent": "AIJobRecommendationAgent/0.1"},
            )
            response.raise_for_status()
            payload = response.json()
            jobs.extend(
                normalized
                for item in payload.get("data", [])
                if (normalized := self._normalize(item)) is not None
            )
            if not payload.get("links", {}).get("next"):
                break
        return jobs

    @staticmethod
    def _normalize(item: dict[str, Any]) -> Job | None:
        title = str(item.get("title", "")).strip()
        job_types = [str(value) for value in item.get("job_types", [])]
        searchable = f"{title} {' '.join(job_types)}".casefold()
        if not any(term in searchable for term in EARLY_CAREER_TERMS):
            return None

        employment_type = _employment_type(searchable)
        timestamp = int(item["created_at"]) if item.get("created_at") else None
        posted_at = datetime.fromtimestamp(timestamp, UTC) if timestamp else None
        description = _plain_text(str(item.get("description", "")))
        return Job(
            id=f"arbeitnow-{item['slug']}",
            title=title,
            company=str(item.get("company_name", "Unknown company")),
            location=str(item.get("location", "Germany")),
            employment_type=employment_type,
            description=description[:1500],
            skills=[str(tag) for tag in item.get("tags", [])],
            source_name="Arbeitnow public API",
            source_url=str(item["url"]),
            posted_date=posted_at.date() if posted_at else None,
            posted_at=posted_at,
            is_remote=bool(item.get("remote", False)),
            is_demo=False,
        )


def _employment_type(searchable: str) -> EmploymentType:
    if "werkstudent" in searchable or "working student" in searchable:
        return EmploymentType.WORKING_STUDENT
    if any(term in searchable for term in ("intern", "praktikum", "praktikant")):
        return EmploymentType.INTERNSHIP
    if "graduate" in searchable or "trainee" in searchable:
        return EmploymentType.GRADUATE
    return EmploymentType.ENTRY_LEVEL


def _plain_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(without_tags)).strip()
