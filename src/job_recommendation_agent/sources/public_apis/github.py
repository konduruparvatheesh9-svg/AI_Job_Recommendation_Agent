"""Adapter for fetching job listings from GitHub careers and API."""

import re
from datetime import UTC, datetime
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
    "thesis",
    "masterarbeit",
    "abschlussarbeit",
}


class GitHubJobsSource:
    """Fetch job listings from GitHub using the Remotive job board API.
    
    Since GitHub's official jobs API (jobs.github.com) was discontinued,
    this adapter uses Remotive's public API which includes GitHub job postings.
    """

    def __init__(self, api_url: str = "https://remotive.com/api/remote-jobs", timeout_seconds: float = 15.0) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds

    def fetch_jobs(self) -> list[Job]:
        """Fetch GitHub-related job listings from Remotive API."""
        jobs: list[Job] = []
        page = 1
        has_more = True

        while has_more:
            try:
                response = requests.get(
                    self.api_url,
                    params={"page": page, "company_name": "GitHub"},
                    timeout=self.timeout_seconds,
                    headers={"User-Agent": "AIJobRecommendationAgent/0.1"},
                )
                response.raise_for_status()
                payload = response.json()

                for item in payload.get("jobs", []):
                    if normalized := self._normalize(item):
                        jobs.append(normalized)

                has_more = payload.get("pagination", {}).get("has_more", False)
                page += 1
            except Exception:
                # If GitHub-specific query fails, try general fetch
                break

        return jobs

    @staticmethod
    def _normalize(item: dict[str, Any]) -> Job | None:
        """Normalize a job listing to our Job model."""
        title = str(item.get("title", "")).strip()
        description = str(item.get("description", "")).strip()
        searchable = f"{title} {description}".casefold()

        # Filter for early-career positions
        if not any(term in searchable for term in EARLY_CAREER_TERMS):
            return None

        employment_type = _employment_type(searchable)
        
        # Extract posted date
        posted_at = None
        if published_at := item.get("published_at"):
            try:
                posted_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Extract skills from job description
        skills = _extract_skills(description)

        return Job(
            id=f"github-{item.get('id', 'unknown')}",
            title=title,
            company="GitHub" if "GitHub" in str(item.get("company_name", "")) else str(item.get("company_name", "Unknown")),
            location=str(item.get("location", "Remote")),
            employment_type=employment_type,
            description=description[:1500],
            skills=skills[:10],  # Limit to top 10 skills
            source_name="GitHub & Remotive Jobs",
            source_url=str(item.get("url", "https://github.com/careers")),
            posted_at=posted_at,
            is_remote=item.get("job_type") == "fully_remote" or "remote" in searchable,
        )


def _employment_type(text: str) -> EmploymentType:
    """Infer employment type from job description text."""
    if "thesis" in text or "abschlussarbeit" in text or "masterarbeit" in text:
        return EmploymentType.THESIS
    elif "intern" in text or "praktikum" in text or "praktikant" in text:
        return EmploymentType.INTERNSHIP
    elif "werkstudent" in text or "working student" in text:
        return EmploymentType.WORKING_STUDENT
    elif "trainee" in text or "graduate" in text:
        return EmploymentType.GRADUATE
    else:
        return EmploymentType.ENTRY_LEVEL


def _extract_skills(text: str) -> list[str]:
    """Extract common programming skills from job description."""
    skills = set()
    skill_keywords = {
        "python", "javascript", "typescript", "java", "c++", "c#", "rust",
        "go", "ruby", "php", "swift", "kotlin", "scala", "r",
        "react", "vue", "angular", "nodejs", "express",
        "django", "flask", "fastapi", "spring", "asp.net",
        "sql", "postgresql", "mongodb", "mysql", "redis",
        "aws", "azure", "gcp", "docker", "kubernetes",
        "git", "github", "gitlab", "ci/cd", "jenkins",
        "devops", "machine learning", "ai", "ml", "data science",
        "rest api", "graphql", "microservices", "cloud",
        "html", "css", "sass", "webpack", "vite",
    }

    text_lower = text.lower()
    for skill in skill_keywords:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            skills.add(skill)

    return list(skills)
