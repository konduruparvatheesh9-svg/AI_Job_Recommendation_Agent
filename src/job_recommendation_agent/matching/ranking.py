"""Transparent ranking tailored to Parvatheesh's resume and target roles."""

from datetime import UTC, date, datetime, timedelta

from job_recommendation_agent.domain.models import EmploymentType, Feedback, Job, JobReview

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

TARGET_POSITION_TERMS = (
    "data analyst",
    "data analytics",
    "data science",
    "business intelligence",
    "business analyst",
    "product analyst",
    "product analytics",
    "analytics engineer",
    "ai intern",
    "artificial intelligence",
    "machine learning",
    "industry 4.0",
    "smart manufacturing",
    "digital factory",
    "production analytics",
    "industrial ai",
    "manufacturing data",
    "automation analytics",
    "quality analytics",
    "quality management",
    "process optimization",
    "process optimisation",
    "process improvement",
    "product management",
    "product strategy",
    "market intelligence",
    "digital transformation",
    "datenanalyse",
    "data & ai",
    "prototyping & data",
)

PREFERRED_COMPANY_TIERS = {
    1: {
        "bosch",
        "volkswagen",
        "cariad",
        "munich re",
        "siemens",
        "infineon",
        "zf",
        "schaeffler",
        "continental",
        "henkel",
    },
    2: {
        "teamviewer",
        "personio",
        "celonis",
        "datev",
        "sap",
        "puma",
        "mercedes-benz",
        "bmw",
        "audi",
        "porsche",
    },
    3: {
        "zalando",
        "hellofresh",
        "delivery hero",
        "n26",
        "trade republic",
        "flix",
        "getyourguide",
        "contentful",
        "sumup",
        "mytheresa",
    },
}


def matches_target_position(job: Job) -> bool:
    """Require a supplied target role phrase or a precise equivalent in the title."""

    title = job.title.casefold()
    exact_match = any(term in title for term in TARGET_POSITION_TERMS)
    semantic_variant = (
        "data" in title or " ai " in f" {title} " or "artificial intelligence" in title
    )
    return exact_match or semantic_variant


def company_preference_bonus(company: str) -> int:
    """Reward companies from the supplied three-tier preference list."""

    normalized = company.casefold()
    for tier, names in PREFERRED_COMPANY_TIERS.items():
        if any(name in normalized for name in names):
            return {1: 15, 2: 10, 3: 5}[tier]
    return 0


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
    return score + company_preference_bonus(job.company)


def feedback_score(job: Job, jobs: list[Job], reviews: dict[str, JobReview]) -> int:
    """Adjust relevance using terms found in previously liked and disliked jobs."""

    candidate_terms = {value.casefold() for value in [job.title, *job.skills]}
    adjustment = 0
    jobs_by_id = {candidate.id: candidate for candidate in jobs}
    for job_id, review in reviews.items():
        reviewed_job = jobs_by_id.get(job_id)
        if reviewed_job is None or review.feedback is Feedback.NONE:
            continue
        reviewed_terms = {value.casefold() for value in [reviewed_job.title, *reviewed_job.skills]}
        overlap = len(candidate_terms & reviewed_terms)
        if review.feedback is Feedback.LIKE:
            adjustment += overlap * 3
        elif review.feedback is Feedback.DISLIKE:
            adjustment -= overlap * 3
    return relevance_score(job) + adjustment


def order_with_feedback(jobs: list[Job], reviews: dict[str, JobReview]) -> list[Job]:
    """Order jobs by learned preference while keeping newer jobs ahead on ties."""

    return sorted(
        jobs,
        key=lambda job: (
            feedback_score(job, jobs, reviews),
            job.posted_at or datetime.min.replace(tzinfo=UTC),
        ),
        reverse=True,
    )


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
        if job.employment_type in {EmploymentType.INTERNSHIP, EmploymentType.THESIS}
        and job.posted_at is not None
    ]
    for hours in windows:
        cutoff = current_time - timedelta(hours=hours)
        eligible = [job for job in internships if job.posted_at and job.posted_at >= cutoff]
        if len(eligible) >= limit or hours == windows[-1]:
            return top_jobs_on_timeline(eligible, limit), hours
    return [], windows[-1]
