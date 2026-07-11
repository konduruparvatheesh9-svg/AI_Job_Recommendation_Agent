"""Clearly labeled sample records for local UI development."""

from datetime import UTC, date, datetime

from job_recommendation_agent.domain.models import EmploymentType, Job


def demo_jobs() -> list[Job]:
    """Return fictional jobs; these are not current vacancies."""

    return [
        Job(
            id="demo-berlin-ml-intern",
            title="Machine Learning Intern",
            company="Demo Mobility GmbH",
            location="Berlin, Germany",
            employment_type=EmploymentType.INTERNSHIP,
            description="Support a data team with model evaluation and analytics prototypes.",
            skills=["Python", "Pandas", "Machine Learning"],
            source_name="Demo data",
            source_url="https://example.com/jobs/demo-berlin-ml-intern",
            posted_date=date(2026, 7, 10),
            posted_at=datetime(2026, 7, 10, 9, tzinfo=UTC),
            is_remote=False,
            is_demo=True,
        ),
        Job(
            id="demo-munich-data-working-student",
            title="Working Student Data & AI",
            company="Demo Systems AG",
            location="Munich, Germany",
            employment_type=EmploymentType.WORKING_STUDENT,
            description="Build reporting workflows and assist with responsible AI experiments.",
            skills=["Python", "SQL", "Power BI"],
            source_name="Demo data",
            source_url="https://example.com/jobs/demo-munich-data-working-student",
            posted_date=date(2026, 7, 9),
            posted_at=datetime(2026, 7, 9, 9, tzinfo=UTC),
            is_remote=True,
            is_demo=True,
        ),
        Job(
            id="demo-hamburg-graduate-engineer",
            title="Graduate Software Engineer",
            company="Demo Commerce SE",
            location="Hamburg, Germany",
            employment_type=EmploymentType.GRADUATE,
            description="Join a graduate rotation working on reliable Python services.",
            skills=["Python", "APIs", "Git"],
            source_name="Demo data",
            source_url="https://example.com/jobs/demo-hamburg-graduate-engineer",
            posted_date=date(2026, 7, 8),
            posted_at=datetime(2026, 7, 8, 9, tzinfo=UTC),
            is_remote=False,
            is_demo=True,
        ),
    ]
