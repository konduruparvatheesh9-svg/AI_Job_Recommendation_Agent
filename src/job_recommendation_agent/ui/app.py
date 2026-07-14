"""Streamlit portal for browsing and managing internship applications."""

from collections import Counter
from datetime import UTC, datetime, timedelta

import streamlit as st

from job_recommendation_agent.config import Settings
from job_recommendation_agent.domain.models import Feedback, Job, JobReview
from job_recommendation_agent.matching.ranking import (
    fresh_internships,
    match_reasons,
    matches_target_position,
    order_with_feedback,
    relevance_score,
)
from job_recommendation_agent.persistence.sqlite_repository import SQLiteJobRepository
from job_recommendation_agent.services.demo_data import demo_jobs
from job_recommendation_agent.sources.company_careers.catalog import PRIORITY_CAREER_PORTALS
from job_recommendation_agent.sources.public_apis.arbeitnow import ArbeitnowSource


@st.cache_resource
def repository() -> SQLiteJobRepository:
    """Initialize the shared local repository once per Streamlit process."""

    settings = Settings()
    job_repository = SQLiteJobRepository(settings.database_path)
    job_repository.initialize()
    if not job_repository.list_jobs():
        job_repository.upsert_jobs(demo_jobs())
    return job_repository


def sync_live_jobs() -> tuple[int, str | None]:
    """Fetch current early-career listings and retain them locally."""

    settings = Settings()
    source = ArbeitnowSource(
        settings.arbeitnow_api_url,
        settings.request_timeout_seconds,
        settings.arbeitnow_pages,
    )
    try:
        jobs = source.fetch_jobs()
    except Exception as error:  # Streamlit must remain usable during API outages.
        return 0, str(error)
    repository().upsert_jobs(jobs)
    return len(jobs), None


def filter_jobs(jobs: list[Job]) -> list[Job]:
    """Render filters and return matching jobs."""

    search = st.sidebar.text_input("Search", placeholder="Data, Berlin, Bosch...")
    remote_only = st.sidebar.checkbox("Remote or hybrid only")
    query = search.casefold().strip()
    return [
        job
        for job in jobs
        if (not remote_only or job.is_remote)
        and (
            not query
            or query
            in " ".join(
                [job.title, job.company, job.location, job.description, *job.skills]
            ).casefold()
        )
    ]


def render_metrics(jobs: list[Job], reviews: dict[str, JobReview]) -> None:
    """Show a compact application summary."""

    relevant_reviews = [reviews[job.id] for job in jobs if job.id in reviews]
    counts = Counter(review.feedback for review in relevant_reviews)
    columns = st.columns(5)
    columns[0].metric("Opportunities", len(jobs))
    columns[1].metric("Reviewed", len(relevant_reviews))
    columns[2].metric("Liked", counts[Feedback.LIKE])
    columns[3].metric("Disliked", counts[Feedback.DISLIKE])
    columns[4].metric("Applied", sum(review.applied for review in relevant_reviews))


def render_official_portals() -> None:
    """Show employer-operated career pages grouped by supplied priority tier."""

    with st.expander("Preferred company career portals"):
        st.caption(
            "These open the companies' official career systems. Search for Internship or "
            "Praktikum and confirm the posting date before applying."
        )
        for tier in (1, 2, 3):
            st.markdown(f"**Tier {tier}**")
            columns = st.columns(2)
            tier_portals = [portal for portal in PRIORITY_CAREER_PORTALS if portal.tier == tier]
            for index, portal in enumerate(tier_portals):
                with columns[index % 2]:
                    st.link_button(
                        f"{portal.company} careers",
                        portal.url,
                        use_container_width=True,
                    )
                    st.caption(portal.roles)


def job_description_only(description: str) -> str:
    """Prefer duties and responsibilities over introductory company copy."""

    text = description.strip()
    lowered = text.casefold()
    start_markers = (
        "your role",
        "your responsibilities",
        "responsibilities",
        "what you will do",
        "what you'll do",
        "your tasks",
        "aufgaben",
        "deine rolle",
    )
    end_markers = (
        "your profile",
        "your qualifications",
        "requirements",
        "qualifikation",
        "dein profil",
        "benefits",
        "about the company",
    )
    starts = [lowered.find(marker) for marker in start_markers if marker in lowered]
    start = min(starts) if starts else 0
    ends = [
        lowered.find(marker, start + 20)
        for marker in end_markers
        if lowered.find(marker, start + 20) >= 0
    ]
    end = min(ends) if ends else len(text)
    excerpt = text[start:end].strip()
    return excerpt[:1800] or text[:1800]


def render_job(job: Job, review: JobReview | None) -> None:
    """Render one job and its persistent status controls."""

    badge = " - DEMO" if job.is_demo else ""
    with st.expander(f"{job.title} - {job.company}{badge}"):
        st.caption(
            f"{job.location} | {job.employment_type.value}"
            f" | {'Remote/hybrid' if job.is_remote else 'On-site'}"
            f" | Match score {relevance_score(job)}"
        )
        st.markdown("**Job description and responsibilities**")
        st.write(job_description_only(job.description))
        if job.skills:
            st.write("**Skills:** " + ", ".join(job.skills))
        reasons = match_reasons(job)
        st.write(
            "**Why it matches your profile:** "
            + (", ".join(reasons) if reasons else "Early-career internship")
        )
        posted = job.posted_at.isoformat(timespec="minutes") if job.posted_at else "Unknown"
        st.write(f"**Application source:** {job.source_name}")
        st.caption(f"Posted: {posted} | Employer: {job.company}")
        st.link_button(f"Open and apply via {job.source_name}", str(job.source_url), type="primary")

        current_feedback = review.feedback if review else Feedback.NONE
        current_applied = review.applied if review else False
        current_reason = review.dislike_reason if review else ""
        current_notes = review.notes if review else ""

        applied = st.checkbox(
            "I applied for this job", value=current_applied, key=f"applied-{job.id}"
        )
        feedback = st.radio(
            "Do you like this job?",
            list(Feedback),
            index=list(Feedback).index(current_feedback),
            format_func=lambda value: value.value,
            horizontal=True,
            key=f"feedback-{job.id}",
        )
        dislike_reason = ""
        if feedback is Feedback.DISLIKE:
            reasons_list = [
                "Select a reason",
                "Role does not match my skills",
                "Location is not suitable",
                "German language requirement is too high",
                "Internship duration or start date does not fit",
                "Not enough data or analytics work",
                "Company or industry is not preferred",
                "Other",
            ]
            default = current_reason if current_reason in reasons_list else reasons_list[0]
            dislike_reason = st.selectbox(
                "Why do you not like it?",
                reasons_list,
                index=reasons_list.index(default),
                key=f"reason-{job.id}",
            )
            if dislike_reason == "Other":
                dislike_reason = st.text_input(
                    "Your reason", value=current_reason, key=f"other-reason-{job.id}"
                )
        notes = st.text_area(
            "Optional notes", value=current_notes, max_chars=1000, key=f"notes-{job.id}"
        )
        if st.button("Save status", type="primary", key=f"save-{job.id}"):
            if feedback is Feedback.DISLIKE and dislike_reason in {"", "Select a reason"}:
                st.error("Please select or enter a reason for disliking this job.")
            else:
                repository().save_review(
                    job.id,
                    feedback=feedback,
                    applied=applied,
                    dislike_reason=dislike_reason,
                    notes=notes,
                )
                st.success("Job status saved and lists updated.")
                st.rerun()


def render_job_list(jobs: list[Job], reviews: dict[str, JobReview], empty_message: str) -> None:
    """Render a status-specific job list."""

    if not jobs:
        st.info(empty_message)
        return
    for job in jobs:
        render_job(job, reviews.get(job.id))


def main() -> None:
    """Run the internship application portal."""

    st.set_page_config(
        page_title="Internship Application Portal", page_icon="briefcase", layout="wide"
    )
    st.title("Personalized Internship Application Portal")
    st.write(
        "Best-match internships, Praktikum, and thesis roles in Data Analytics, Business "
        "Intelligence, Digital Transformation, Industrial Systems, and Process Improvement."
    )
    st.info(
        "Live listings come from a documented public API. Confirm availability and the "
        "complete requirements on the original application page."
    )

    job_repository = repository()
    if st.sidebar.button("Refresh live jobs", type="primary"):
        with st.spinner("Fetching current listings..."):
            count, error = sync_live_jobs()
        if error:
            st.sidebar.error(f"Refresh failed: {error}")
        else:
            st.sidebar.success(f"Imported {count} early-career jobs.")
            st.rerun()

    all_jobs = job_repository.list_jobs()
    live_jobs = [job for job in all_jobs if not job.is_demo and matches_target_position(job)]
    _, age_window = fresh_internships(live_jobs)
    cutoff = datetime.now(UTC) - timedelta(hours=age_window)
    jobs = [
        job
        for job in live_jobs
        if job.employment_type.value in {"Internship / Praktikum", "Thesis / Abschlussarbeit"}
        and job.posted_at is not None
        and job.posted_at >= cutoff
    ]
    reviews = job_repository.list_reviews()

    st.sidebar.link_button(
        "Search LinkedIn manually - 24h",
        "https://www.linkedin.com/jobs/search/?f_TPR=r86400&keywords=internship%20data%20analytics%20Germany",
    )
    st.sidebar.caption("LinkedIn results are not imported or scraped.")

    ordered_jobs = order_with_feedback(jobs, reviews)
    render_metrics(ordered_jobs, reviews)
    render_official_portals()
    filtered_jobs = filter_jobs(ordered_jobs)

    to_review = [
        job
        for job in filtered_jobs
        if job.id not in reviews
        or reviews[job.id].feedback is Feedback.NONE
        or reviews[job.id].applied
    ][:10]
    liked = [
        job
        for job in filtered_jobs
        if reviews.get(job.id) and reviews[job.id].feedback is Feedback.LIKE
    ]
    disliked = [
        job
        for job in filtered_jobs
        if reviews.get(job.id) and reviews[job.id].feedback is Feedback.DISLIKE
    ]
    applied = [job for job in filtered_jobs if reviews.get(job.id) and reviews[job.id].applied]

    queue_tab, liked_tab, disliked_tab, applied_tab = st.tabs(
        [
            f"To review ({len(to_review)})",
            f"Liked ({len(liked)})",
            f"Disliked ({len(disliked)})",
            f"Applied ({len(applied)})",
        ]
    )
    with queue_tab:
        st.subheader(f"Internship, Praktikum and thesis queue - last {age_window} hours")
        st.caption(
            "Unanswered jobs remain here. Liked and disliked jobs move to their lists. "
            "Applied jobs always remain visible here."
        )
        render_job_list(to_review, reviews, "No unanswered internships are available.")
    with liked_tab:
        render_job_list(liked, reviews, "You have not liked any jobs yet.")
    with disliked_tab:
        render_job_list(disliked, reviews, "You have not disliked any jobs yet.")
    with applied_tab:
        render_job_list(applied, reviews, "You have not marked any jobs as applied yet.")


if __name__ == "__main__":
    main()
