"""Streamlit portal for browsing and reviewing job opportunities."""

from collections import Counter

import streamlit as st

from job_recommendation_agent.config import Settings
from job_recommendation_agent.domain.models import Feedback, Job, JobReview
from job_recommendation_agent.matching.ranking import (
    fresh_internships,
    match_reasons,
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

    search = st.sidebar.text_input("Search", placeholder="Python, Berlin, company...")
    types = sorted({job.employment_type.value for job in jobs})
    selected_types = st.sidebar.multiselect("Job type", types, default=types)
    remote_only = st.sidebar.checkbox("Remote or hybrid only")

    query = search.casefold().strip()
    return [
        job
        for job in jobs
        if job.employment_type.value in selected_types
        and (not remote_only or job.is_remote)
        and (
            not query
            or query
            in " ".join(
                [job.title, job.company, job.location, job.description, *job.skills]
            ).casefold()
        )
    ]


def render_metrics(jobs: list[Job], reviews: dict[str, JobReview]) -> None:
    """Show a compact review summary."""

    counts = Counter(review.feedback for review in reviews.values())
    columns = st.columns(4)
    columns[0].metric("Opportunities", len(jobs))
    columns[1].metric("Reviewed", len(reviews))
    columns[2].metric("Liked", counts[Feedback.LIKE])
    columns[3].metric("Disliked", counts[Feedback.DISLIKE])


def render_official_portals() -> None:
    """Show verified employer-operated career search pages."""

    with st.expander("Official priority-company career portals"):
        st.caption(
            "These links open the companies' own career systems. Search for Internship or "
            "Praktikum and confirm the posting date on the official page."
        )
        columns = st.columns(2)
        for index, portal in enumerate(PRIORITY_CAREER_PORTALS):
            columns[index % 2].link_button(
                f"Search {portal.company} internships",
                portal.url,
                use_container_width=True,
            )


def render_job(job: Job, review: JobReview | None) -> None:
    """Render one job and its persistent review form."""

    badge = " · DEMO" if job.is_demo else ""
    with st.expander(f"{job.title} — {job.company}{badge}", expanded=False):
        st.caption(
            f"{job.location} · {job.employment_type.value}"
            f" · {'Remote/hybrid' if job.is_remote else 'On-site'}"
            f" · Match score {relevance_score(job)}"
        )
        st.write(job.description)
        st.write("**Skills:** " + ", ".join(job.skills))
        reasons = match_reasons(job)
        st.write(
            "**Why it matches your resume:** "
            + (", ".join(reasons) if reasons else "Early-career role")
        )
        posted = job.posted_date.isoformat() if job.posted_date else "Unknown"
        st.write(f"**Application source:** {job.source_name}")
        st.caption(f"Posted: {posted} · Employer: {job.company}")
        st.link_button(f"Apply via {job.source_name}", str(job.source_url), type="primary")

        current_rating = review.rating if review and review.rating else 3
        current_feedback = review.feedback if review else Feedback.NONE
        current_notes = review.notes if review else ""
        with st.form(f"review-{job.id}"):
            rating = st.slider("Your rating", 1, 5, current_rating)
            feedback = st.radio(
                "Decision",
                list(Feedback),
                index=list(Feedback).index(current_feedback),
                format_func=lambda value: value.value,
                horizontal=True,
            )
            notes = st.text_area("Notes", value=current_notes, max_chars=1000)
            if st.form_submit_button("Save review", type="primary"):
                repository().save_review(job.id, rating, feedback, notes)
                st.success("Review saved.")
                st.rerun()


def main() -> None:
    """Run the job review portal."""

    st.set_page_config(page_title="Job Review Portal", page_icon="🇩🇪", layout="wide")
    st.title("AI Job Recommendation Portal")
    st.write(
        "Resume-matched opportunities for Quality Management, Data Analysis/Data Science, "
        "and IT Infrastructure. Rate each result to improve future recommendations."
    )
    st.info(
        "Live listings come from the documented Arbeitnow public API. Availability and "
        "application status must be confirmed on the original job page."
    )

    job_repository = repository()
    if st.sidebar.button("Refresh live jobs", type="primary"):
        with st.spinner("Fetching current listings..."):
            count, error = sync_live_jobs()
        if error:
            st.sidebar.error(f"Refresh failed: {error}")
        else:
            st.sidebar.success(f"Imported {count} early-career jobs.")

    all_jobs = job_repository.list_jobs()
    live_jobs = [job for job in all_jobs if not job.is_demo]
    jobs, age_window = fresh_internships(live_jobs)
    reviews = job_repository.list_reviews()
    st.sidebar.link_button(
        "Search LinkedIn manually · 24h",
        "https://www.linkedin.com/jobs/search/?f_TPR=r86400&keywords=internship%20data%20quality%20Germany",
    )
    st.sidebar.caption(
        "LinkedIn results are not imported. Open the search and review/apply on LinkedIn."
    )
    render_metrics(jobs, reviews)
    render_official_portals()
    filtered_jobs = filter_jobs(jobs)
    st.subheader(
        f"Top {len(filtered_jobs)} internships · last {age_window} hours · oldest to newest"
    )
    if not filtered_jobs:
        st.warning(
            "No matching internships were found in the public source within the last "
            f"{age_window} hours. Try Refresh live jobs or use the manual LinkedIn search."
        )
    for job in filtered_jobs:
        render_job(job, reviews.get(job.id))


if __name__ == "__main__":
    main()
