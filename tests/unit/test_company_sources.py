"""Tests for official company-career feed normalization."""

from job_recommendation_agent.domain.models import EmploymentType
from job_recommendation_agent.sources.company_careers.amazon import AmazonCareerSource
from job_recommendation_agent.sources.company_careers.bosch import BoschCareerSource
from job_recommendation_agent.sources.company_careers.continental import ContinentalCareerSource


def test_bosch_normalizes_official_job_detail() -> None:
    job = BoschCareerSource._normalize(
        {
            "id": "123",
            "name": "Praktikum Data Analytics",
            "releasedDate": "2026-07-15T10:00:00.000Z",
            "location": {"fullLocation": "Jena, Germany", "hybrid": True},
            "function": {"label": "Data Analytics"},
            "postingUrl": "https://jobs.smartrecruiters.com/BoschGroup/123",
            "applyUrl": "https://jobs.smartrecruiters.com/BoschGroup/123?apply=true",
            "jobAd": {
                "sections": {
                    "jobDescription": {"text": "<p>Analyze production data.</p>"},
                    "qualifications": {"text": "<p>Python and SQL.</p>"},
                }
            },
        }
    )

    assert job.company == "Bosch"
    assert job.employment_type is EmploymentType.INTERNSHIP
    assert job.is_remote is True
    assert "Python and SQL" in job.description


def test_amazon_normalizes_official_job() -> None:
    job = AmazonCareerSource._normalize(
        {
            "id": "456",
            "title": "Business Intelligence Engineer Intern",
            "posted_date": "July 15, 2026",
            "location": "DE, Berlin",
            "description": "<p>Build dashboards.</p>",
            "basic_qualifications": "SQL",
            "preferred_qualifications": "Python",
            "job_category": "Data Science",
            "job_path": "/en/jobs/456/example",
        }
    )

    assert job.company == "Amazon"
    assert job.source_url.host == "www.amazon.jobs"
    assert "Build dashboards" in job.description


def test_continental_normalizes_official_job() -> None:
    job = ContinentalCareerSource._normalize(
        {
            "id": "789",
            "name": "Mandatory Internship - Data Analyst",
            "releasedDate": "2026-07-15T08:00:00.000Z",
            "location": {"fullLocation": "Hannover, Germany", "hybrid": True},
            "function": {"label": "Data Analytics"},
            "postingUrl": "https://jobs.smartrecruiters.com/Continental/789",
            "applyUrl": "https://jobs.smartrecruiters.com/Continental/789?apply=true",
            "jobAd": {
                "sections": {
                    "jobDescription": {"text": "<p>Analyze sales data.</p>"},
                    "qualifications": {"text": "<p>Power BI and SQL.</p>"},
                }
            },
        }
    )

    assert job.company == "Continental"
    assert job.employment_type is EmploymentType.INTERNSHIP
    assert job.source_name == "Continental official careers"
