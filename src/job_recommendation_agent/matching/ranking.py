"""Transparent ranking tailored to Parvatheesh's resume and target roles."""

from dataclasses import dataclass
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

@dataclass(frozen=True)
class TargetRole:
    """One preferred internship family and the title variants it accepts."""

    name: str
    stars: int
    aliases: tuple[str, ...]


TARGET_ROLES = (
    TargetRole(
        "Data Analytics Intern",
        5,
        ("data analytics", "data analyst", "data analysis", "datenanalyse"),
    ),
    TargetRole(
        "Business Intelligence Intern",
        5,
        ("business intelligence", "bi intern", "bi praktik", "reporting analyst"),
    ),
    TargetRole(
        "Product Analytics Intern",
        5,
        ("product analytics", "product analyst", "product data analyst"),
    ),
    TargetRole(
        "Digital Transformation Intern",
        5,
        ("digital transformation", "digitalization", "digitalisation", "digital factory"),
    ),
    TargetRole(
        "Industrial Data Analytics Intern",
        5,
        (
            "industrial data",
            "production analytics",
            "manufacturing data",
            "quality analytics",
        ),
    ),
    TargetRole(
        "AI/Data Intern",
        4,
        (
            "ai intern",
            "data & ai",
            "data and ai",
            "artificial intelligence",
            "machine learning",
            "generative ai",
            "agentic ai",
            "prototyping & data",
        ),
    ),
    TargetRole(
        "Business Analyst Intern",
        4,
        ("business analyst", "business analytics", "business analysis"),
    ),
    TargetRole(
        "Market Intelligence Intern",
        4,
        ("market intelligence", "market analytics", "competitive intelligence"),
    ),
    TargetRole(
        "Product Management Intern (Data-focused)",
        4,
        ("product management", "product strategy", "data product"),
    ),
    TargetRole(
        "Industry 4.0 / Smart Manufacturing Intern",
        4,
        (
            "industry 4.0",
            "industrie 4.0",
            "smart manufacturing",
            "manufacturing ai",
            "ai in manufacturing",
            "automation of process",
        ),
    ),
)

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
    "reporting analyst",
    "software developer",
    "software engineer",
    "python developer",
    "java developer",
    "backend developer",
    "system engineer",
    "systems engineer",
    "infrastructure engineer",
    "it infrastructure",
    "it operations",
    "cloud support",
    "sql developer",
    "database analyst",
    "quality data",
    "manufacturing quality",
    "process engineer",
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
        "amazon",
        "ibm",
        "accenture",
        "capgemini",
        "zeiss",
        "microsoft",
    },
}


def matches_target_position(job: Job) -> bool:
    """Require a supplied target role phrase or a precise equivalent in the title."""

    title = job.title.casefold()
    exact_match = target_role(job) is not None or any(
        term in title for term in TARGET_POSITION_TERMS
    )
    semantic_variant = (
        "data" in title or " ai " in f" {title} " or "artificial intelligence" in title
    )
    return exact_match or semantic_variant


def target_role(job: Job) -> TargetRole | None:
    """Classify a listing into the first matching preferred role family."""

    title = job.title.casefold().strip()
    for role in TARGET_ROLES:
        if title == role.name.casefold():
            return role
    matches: list[tuple[int, int, TargetRole]] = []
    for index, role in enumerate(TARGET_ROLES):
        for alias in role.aliases:
            if alias in title:
                matches.append((len(alias), -index, role))
    if not matches:
        return None
    return max(matches, key=lambda match: (match[0], match[1]))[2]


def diverse_role_queue(
    jobs: list[Job],
    reviews: dict[str, JobReview],
    limit: int = 10,
    max_per_company: int = 3,
) -> list[Job]:
    """Balance role coverage while enforcing a strict employer diversity cap."""

    ordered: list[Job] = []
    seen_postings: set[tuple[str, str, date | None, str]] = set()
    for job in order_with_feedback(jobs, reviews):
        role = target_role(job)
        posting = (
            job.company.casefold().strip(),
            job.location.casefold().strip(),
            job.posted_date,
            role.name if role is not None else job.title.casefold().strip(),
        )
        if posting not in seen_postings:
            ordered.append(job)
            seen_postings.add(posting)
    selected: list[Job] = []
    selected_ids: set[str] = set()
    company_counts: dict[str, int] = {}

    def add(job: Job) -> None:
        selected.append(job)
        selected_ids.add(job.id)
        company = job.company.casefold().strip()
        company_counts[company] = company_counts.get(company, 0) + 1

    for role in TARGET_ROLES:
        match = next(
            (
                job
                for job in ordered
                if target_role(job) == role
                and company_counts.get(job.company.casefold().strip(), 0)
                < min(2, max_per_company)
            ),
            None,
        )
        if match is not None:
            add(match)
        if len(selected) == limit:
            return selected

    # Give each additional employer one opportunity before repeating companies.
    for job in ordered:
        company = job.company.casefold().strip()
        if job.id not in selected_ids and company not in company_counts:
            add(job)
        if len(selected) == limit:
            return selected

    # Fill remaining slots without allowing one employer to dominate the queue.
    for job in ordered:
        company = job.company.casefold().strip()
        if job.id not in selected_ids and company_counts.get(company, 0) < max_per_company:
            add(job)
        if len(selected) == limit:
            return selected
    return selected


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
        elif review.feedback in {Feedback.DISLIKE, Feedback.REJECTED}:
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
    windows: tuple[int, ...] = (24, 48, 72, 168, 336, 720, 2160),
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
