"""Official Continental SmartRecruiters public-feed adapter."""

import re
from datetime import datetime
from html import unescape
from typing import Any

import requests

from job_recommendation_agent.domain.models import EmploymentType, Job

STUDENT_TERMS = ("praktik", "intern", "abschlussarbeit", "masterarbeit", "thesis")
TARGET_TERMS = (
    "data",
    "analytics",
    "analyse",
    "business intelligence",
    "digital",
    "quality",
    "process",
    "manufacturing",
    "automation",
    "artificial intelligence",
    "künstliche intelligenz",
    "machine learning",
)


class ContinentalCareerSource:
    """Fetch relevant German student jobs from Continental's official ATS feed."""

    def __init__(self, api_url: str, timeout_seconds: float = 15.0) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds

    def fetch_jobs(self) -> list[Job]:
        summaries = self._fetch_summaries()
        jobs: list[Job] = []
        for summary in summaries:
            title = str(summary.get("name", ""))
            searchable = title.casefold()
            if not any(term in searchable for term in STUDENT_TERMS):
                continue
            if not any(term in searchable for term in TARGET_TERMS):
                continue
            response = requests.get(
                f"{self.api_url}/{summary['id']}",
                timeout=self.timeout_seconds,
                headers={"User-Agent": "AIJobRecommendationAgent/0.1"},
            )
            response.raise_for_status()
            jobs.append(self._normalize(response.json()))
        return jobs

    def _fetch_summaries(self) -> list[dict[str, Any]]:
        summaries: dict[str, dict[str, Any]] = {}
        for query in ("intern", "praktikum", "thesis", "abschlussarbeit"):
            offset = 0
            while True:
                response = requests.get(
                    self.api_url,
                    params={"limit": 100, "offset": offset, "country": "de", "q": query},
                    timeout=self.timeout_seconds,
                    headers={"User-Agent": "AIJobRecommendationAgent/0.1"},
                )
                response.raise_for_status()
                payload = response.json()
                page = payload.get("content", [])
                for item in page:
                    summaries[str(item["id"])] = item
                offset += len(page)
                if not page or offset >= int(payload.get("totalFound", 0)):
                    break
        return list(summaries.values())

    @staticmethod
    def _normalize(item: dict[str, Any]) -> Job:
        title = str(item["name"])
        sections = item.get("jobAd", {}).get("sections", {})
        description = " ".join(
            _plain_text(str(sections.get(key, {}).get("text", "")))
            for key in ("jobDescription", "qualifications")
        ).strip()
        posted_at = datetime.fromisoformat(str(item["releasedDate"]).replace("Z", "+00:00"))
        location = item.get("location", {})
        employment_type = (
            EmploymentType.THESIS
            if any(
                term in title.casefold() for term in ("thesis", "masterarbeit", "abschlussarbeit")
            )
            else EmploymentType.INTERNSHIP
        )
        return Job(
            id=f"continental-{item['id']}",
            title=title,
            company="Continental",
            location=str(location.get("fullLocation", "Germany")),
            employment_type=employment_type,
            description=description,
            skills=[str(item.get("function", {}).get("label", ""))],
            source_name="Continental Career Portal",
            source_url=str(item.get("applyUrl") or item["postingUrl"]),
            posted_date=posted_at.date(),
            posted_at=posted_at,
            is_remote=bool(location.get("remote") or location.get("hybrid")),
        )


def _plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()
