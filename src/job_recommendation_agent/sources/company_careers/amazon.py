"""Official Amazon Jobs public-search adapter."""

import re
from datetime import UTC, datetime
from html import unescape
from typing import Any

import requests

from job_recommendation_agent.domain.models import EmploymentType, Job


class AmazonCareerSource:
    """Fetch German internship jobs from Amazon's official public search feed."""

    def __init__(self, api_url: str, timeout_seconds: float = 15.0) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds

    def fetch_jobs(self) -> list[Job]:
        params: dict[str, str | int] = {
            "base_query": "intern",
            "loc_query": "Germany",
            "result_limit": 100,
        }
        response = requests.get(
            self.api_url,
            params=params,
            timeout=self.timeout_seconds,
            headers={"User-Agent": "AIJobRecommendationAgent/0.1"},
        )
        response.raise_for_status()
        return [
            self._normalize(item)
            for item in response.json().get("jobs", [])
            if item.get("country_code") == "DEU" and _is_student_role(item)
        ]

    @staticmethod
    def _normalize(item: dict[str, Any]) -> Job:
        posted_at = datetime.strptime(str(item["posted_date"]), "%B %d, %Y").replace(tzinfo=UTC)
        description = _plain_text(
            " ".join(
                str(item.get(key, ""))
                for key in ("description", "basic_qualifications", "preferred_qualifications")
            )
        )
        return Job(
            id=f"amazon-{item['id']}",
            title=str(item["title"]),
            company="Amazon",
            location=str(item.get("location", "Germany")),
            employment_type=EmploymentType.INTERNSHIP,
            description=description,
            skills=[str(item.get("job_category", ""))],
            source_name="Amazon Jobs Portal",
            source_url=f"https://www.amazon.jobs{item['job_path']}",
            posted_date=posted_at.date(),
            posted_at=posted_at,
            is_remote="remote" in str(item.get("location", "")).casefold(),
        )


def _is_student_role(item: dict[str, Any]) -> bool:
    searchable = f"{item.get('title', '')} {item.get('business_category', '')}".casefold()
    return "intern" in searchable or "student" in searchable


def _plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()
