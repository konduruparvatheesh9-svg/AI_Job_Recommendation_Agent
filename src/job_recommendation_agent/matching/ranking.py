"""Transparent ranking tailored to Parvatheesh's resume and target roles."""

from datetime import UTC, date, datetime, timedelta

from job_recommendation_agent.domain.models import EmploymentType, Job

TARGET_TERMS = {
    # Quality, manufacturing, and scientific instrumentation
    "quality management": 12,
    "quality assurance": 10,
    "quality engineer": 10,
    "process improvement": 8,
    "root cause": 7,
    "manufacturing": 7,
    "semiconductor": 8,
    "measurement": 6,
    "instrumentation": 8,
    "iso 9001": 7,
    "compliance": 4,
    # Data analysis and data science
    "data analyst": 12,
    "data analysis": 10,
    "data science": 10,
    "analytics": 7,
    "business intelligence": 8,
    "power bi": 8,
    "sql": 7,
    "python": 6,
    "pandas": 5,
    "machine learning": 6,
    "statistics": 5,
    "kpi": 5,
    # Infrastructure and systems experience
    "it infrastructure": 9,
    "system engineer": 9,
    "systems engineer": 9,
    "vmware": 10,
    "virtualization": 8,
    "windows server": 6,
    "linux": 4,
    "it service": 4,
    "vulnerability": 5,
    "sccm": 6,
}


def relevance_score(job: Job) -> int:
    """Score a job against skills and goals evidenced by the resume."""

    searchable = " ".join([job.title, job.description, *job.skills]).casefold()
    score = sum(weight for term, weight in TARGET_TERMS.items() if term in searchable)
    if job.employment_type.value in {"Internship / Praktikum", "Werkstudent"}:
        score += 8
    elif job.employment_type.value == "Graduate":
        score += 3
    if job.is_remote:
        score += 1
    return score


def match_reasons(job: Job, limit: int = 5) -> list[str]:
    """Explain the strongest resume terms found in a listing."""

    searchable = " ".join([job.title, job.description, *job.skills]).casefold()
    matches = [(term, weight) for term, weight in TARGET_TERMS.items() if term in searchable]
    matches.sort(key=lambda match: (-match[1], match[0]))
    return [term.title() for term, _ in matches[:limit]]


def top_jobs_on_timeline(jobs: list[Job], limit: int = 10) -> list[Job]:
    """Select the strongest jobs, then display them oldest-to-newest."""

    ranked = sorted(
        jobs,
        key=lambda job: (relevance_score(job), job.posted_date or date.min),
        reverse=True,
    )
    unique: list[Job] = []
    seen: set[tuple[str, str]] = set()
    for job in ranked:
        identity = (job.title.casefold().strip(), job.company.casefold().strip())
        if identity not in seen:
            unique.append(job)
            seen.add(identity)
        if len(unique) == limit:
            break
    return sorted(unique, key=lambda job: (job.posted_date or date.min, job.title.casefold()))


def fresh_internships(
    jobs: list[Job],
    limit: int = 10,
    now: datetime | None = None,
    windows: tuple[int, ...] = (24, 48, 72, 168),
) -> tuple[list[Job], int]:
    """Fill an internship shortlist using progressively wider age windows."""

    current_time = now or datetime.now(UTC)
    internships = [
        job
        for job in jobs
        if job.employment_type is EmploymentType.INTERNSHIP and job.posted_at is not None
    ]
    for hours in windows:
        cutoff = current_time - timedelta(hours=hours)
        eligible = [job for job in internships if job.posted_at and job.posted_at >= cutoff]
        if len(eligible) >= limit or hours == windows[-1]:
            return top_jobs_on_timeline(eligible, limit), hours
    return [], windows[-1]
