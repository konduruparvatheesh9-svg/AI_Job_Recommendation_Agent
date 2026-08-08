"""Streamlit portal for browsing and managing internship applications."""

from collections import Counter
from datetime import UTC, datetime, timedelta
from urllib.parse import quote_plus

import streamlit as st

from job_recommendation_agent.config import Settings
from job_recommendation_agent.domain.models import Feedback, Job, JobReview
from job_recommendation_agent.matching.ranking import (
    TARGET_ROLES,
    diverse_role_queue,
    fresh_internships,
    match_reasons,
    matches_target_position,
    order_with_feedback,
    relevance_score,
    target_role,
)
from job_recommendation_agent.persistence.sqlite_repository import SQLiteJobRepository
from job_recommendation_agent.services.demo_data import demo_jobs
from job_recommendation_agent.sources.company_careers.amazon import AmazonCareerSource
from job_recommendation_agent.sources.company_careers.bosch import BoschCareerSource
from job_recommendation_agent.sources.company_careers.catalog import PRIORITY_CAREER_PORTALS
from job_recommendation_agent.sources.company_careers.continental import ContinentalCareerSource
from job_recommendation_agent.sources.public_apis.arbeitnow import ArbeitnowSource
from job_recommendation_agent.sources.public_apis.github import GitHubJobsSource

SYNC_METADATA_KEY = "arbeitnow_last_synced_at"
AUTO_SYNC_INTERVAL = timedelta(minutes=15)


@st.cache_resource
def repository() -> SQLiteJobRepository:
    """Initialize the shared local repository once per Streamlit process."""

    settings = Settings()
    job_repository = SQLiteJobRepository(settings.database_path)
    job_repository.initialize()
    if not job_repository.list_jobs():
        job_repository.upsert_jobs(demo_jobs())
        sync_live_jobs()
    return job_repository


def sync_live_jobs() -> tuple[int, str | None]:
    """Fetch all supported public feeds and retain normalized jobs locally."""

    settings = Settings()
    sources = (
        ArbeitnowSource(
            settings.arbeitnow_api_url,
            settings.request_timeout_seconds,
            settings.arbeitnow_pages,
        ),
        BoschCareerSource(settings.bosch_api_url, settings.request_timeout_seconds),
        ContinentalCareerSource(
            settings.continental_api_url, settings.request_timeout_seconds
        ),
        AmazonCareerSource(settings.amazon_jobs_api_url, settings.request_timeout_seconds),
        GitHubJobsSource(timeout_seconds=settings.request_timeout_seconds),
    )
    imported = 0
    failures = 0
    for source in sources:
        try:
            jobs = source.fetch_jobs()
        except Exception:  # One unavailable source must not break the portal.
            failures += 1
            continue
        repository().upsert_jobs(jobs)
        imported += len(jobs)
    if failures == len(sources):
        return 0, "All live job sources are temporarily unreachable. Cached jobs remain available."
    repository().set_metadata(SYNC_METADATA_KEY, datetime.now(UTC).isoformat())
    return imported, None


def auto_sync_live_jobs() -> tuple[int, str | None, bool]:
    """Refresh on page load only when the cached feed is older than the interval."""

    last_synced_value = repository().get_metadata(SYNC_METADATA_KEY)
    if last_synced_value:
        last_synced = datetime.fromisoformat(last_synced_value)
        if datetime.now(UTC) - last_synced < AUTO_SYNC_INTERVAL:
            return 0, None, False
    count, error = sync_live_jobs()
    return count, error, True


@st.fragment(run_every=AUTO_SYNC_INTERVAL)
def render_live_sync_status() -> None:
    """Poll the live source while the browser session remains open."""

    with st.spinner("Checking for newly released positions..."):
        count, error, attempted = auto_sync_live_jobs()
    if attempted and error:
        st.warning(error)
    elif attempted:
        st.toast(f"Live sources updated with {count} relevant postings.")

    last_synced_value = repository().get_metadata(SYNC_METADATA_KEY)
    if last_synced_value:
        last_synced = datetime.fromisoformat(last_synced_value).astimezone()
        st.sidebar.caption(
            "Public feed last updated: " + last_synced.strftime("%Y-%m-%d %H:%M:%S %Z")
        )


def get_preferred_companies() -> set[str]:
    """Get list of preferred companies from session state."""
    if "preferred_companies" not in st.session_state:
        # Default: all companies available
        st.session_state.preferred_companies = set()
    return st.session_state.preferred_companies


def get_hidden_portals() -> set[str]:
    """Get list of hidden company portals from session state."""
    if "hidden_portals" not in st.session_state:
        st.session_state.hidden_portals = set()
    return st.session_state.hidden_portals


def render_portal_management(all_jobs: list[Job]) -> None:
    """Render UI to add/remove preferred company portals."""
    
    with st.sidebar.expander("🏢 Manage Company Filters"):
        st.write("**Add or remove companies to filter results**")
        
        # Get unique companies from all jobs
        all_companies = sorted(set(job.company for job in all_jobs))
        preferred = get_preferred_companies()
        
        # Display current selected companies
        if preferred:
            st.write(f"**Selected companies ({len(preferred)})**")
            cols = st.columns(2)
            for idx, company in enumerate(sorted(preferred)):
                with cols[idx % 2]:
                    if st.button(f"✓ {company}", key=f"remove_{company}", use_container_width=True):
                        st.session_state.preferred_companies.discard(company)
                        st.rerun()
        
        # Add new company
        st.write("**Add a company**")
        available = [c for c in all_companies if c not in preferred]
        
        if available:
            # Single company selection
            new_company = st.selectbox(
                "Select company to add",
                available,
                key="add_company_select",
                label_visibility="collapsed"
            )
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Add to filters", use_container_width=True):
                    st.session_state.preferred_companies.add(new_company)
                    st.rerun()
            
            with col2:
                if st.button("➕ Add all", use_container_width=True, help="Add all available companies"):
                    st.session_state.preferred_companies.update(all_companies)
                    st.rerun()
        else:
            # All companies already selected
            st.info("✓ All companies are already added!")
        
        if st.button("Clear all filters", use_container_width=True):
            st.session_state.preferred_companies = set()
            st.rerun()


def filter_jobs(jobs: list[Job]) -> list[Job]:
    """Render filters and return matching jobs."""

    # Advanced search filters
    st.sidebar.markdown("### 🔍 Advanced Search")
    
    job_title = st.sidebar.text_input(
        "Job title (optional)",
        placeholder="e.g., Data Analyst, Machine Learning...",
        key="search_title"
    )
    company_name = st.sidebar.text_input(
        "Company name (optional)",
        placeholder="e.g., Bosch, Amazon...",
        key="search_company"
    )
    skills_input = st.sidebar.text_input(
        "Skills (optional, comma-separated)",
        placeholder="e.g., Python, SQL, Excel...",
        key="search_skills"
    )
    
    # Basic filters
    remote_only = st.sidebar.checkbox("Remote or hybrid only")
    
    # Search button and external portal links
    st.sidebar.markdown("**Search options**")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        search_clicked = st.button("🔍 Search", use_container_width=True, key="search_btn")
    
    # Build query string for external searches
    query_parts = []
    if job_title.strip():
        query_parts.append(job_title.strip())
    if company_name.strip():
        query_parts.append(company_name.strip())
    if skills_input.strip():
        query_parts.append(skills_input.strip())
    
    query_string = " ".join(query_parts) if query_parts else "internship practicum"
    
    with col2:
        st.sidebar.caption("Or search externally:")
    
    # External search links
    search_cols = st.sidebar.columns(2)
    google_query = quote_plus(query_string + " internship germany")
    linkedin_query = quote_plus(query_string)
    
    with search_cols[0]:
        st.sidebar.link_button(
            "🌐 Google",
            f"https://www.google.com/search?q={google_query}&tbs=qdr:w",
            use_container_width=True,
            help="Search on Google for the past week"
        )
    
    with search_cols[1]:
        st.sidebar.link_button(
            "💼 LinkedIn",
            f"https://www.linkedin.com/jobs/search/?keywords={linkedin_query}&location=Germany",
            use_container_width=True,
            help="Search on LinkedIn"
        )
    
    # Store search state
    if search_clicked:
        st.session_state.search_active = True
        st.toast(f"🔍 Searching for: {query_string}")
    
    # Parse inputs
    job_title_query = job_title.casefold().strip()
    company_query = company_name.casefold().strip()
    skills_query = [s.strip().casefold() for s in skills_input.split(",") if s.strip()]
    preferred = get_preferred_companies()
    
    # Filter jobs
    filtered = []
    for job in jobs:
        # Check company filter
        if preferred and job.company not in preferred:
            continue
        
        # Check remote preference
        if remote_only and not job.is_remote:
            continue
        
        # Check job title
        if job_title_query and job_title_query not in job.title.casefold():
            continue
        
        # Check company name
        if company_query and company_query not in job.company.casefold():
            continue
        
        # Check skills (all must match)
        if skills_query:
            job_skills_lower = [s.casefold() for s in job.skills]
            if not all(any(skill in skill_lower for skill_lower in job_skills_lower) for skill in skills_query):
                continue
        
        filtered.append(job)
    
    # Show search summary if search was performed
    if search_clicked or job_title_query or company_query or skills_query:
        search_summary = []
        if job_title_query:
            search_summary.append(f"Title: {job_title}")
        if company_query:
            search_summary.append(f"Company: {company_name}")
        if skills_query:
            search_summary.append(f"Skills: {skills_input}")
        if remote_only:
            search_summary.append("Remote only")
        
        if search_summary:
            st.sidebar.success(f"✓ Found **{len(filtered)}** jobs\n\n" + " | ".join(search_summary))
    
    return filtered


def render_metrics(jobs: list[Job], reviews: dict[str, JobReview]) -> None:
    """Show a compact application summary."""

    relevant_reviews = [reviews[job.id] for job in jobs if job.id in reviews]
    counts = Counter(review.feedback for review in relevant_reviews)
    columns = st.columns(6)
    columns[0].metric("Opportunities", len(jobs))
    columns[1].metric("Reviewed", len(relevant_reviews))
    columns[2].metric("Liked", counts[Feedback.LIKE])
    columns[3].metric("Disliked", counts[Feedback.DISLIKE])
    columns[4].metric("Rejected", counts[Feedback.REJECTED])
    columns[5].metric("Applied", sum(review.applied for review in relevant_reviews))


def render_official_portals() -> None:
    """Show employer-operated career pages grouped by supplied priority tier."""

    hidden_portals = get_hidden_portals()
    
    with st.expander("Preferred company career portals"):
        st.caption(
            "These open the companies' official career systems. Search for Internship or "
            "Praktikum and confirm the posting date before applying."
        )
        
        # Show restore hidden portals option if any are hidden
        if hidden_portals:
            if st.button("Show all companies"):
                st.session_state.hidden_portals = set()
                st.rerun()
            st.caption(f"({len(hidden_portals)} company portals are hidden)")
        
        for tier in (1, 2, 3):
            st.markdown(f"**Tier {tier}**")
            tier_portals = [portal for portal in PRIORITY_CAREER_PORTALS if portal.tier == tier]
            # Filter out hidden portals
            visible_portals = [p for p in tier_portals if p.company not in hidden_portals]
            
            if not visible_portals:
                continue
            
            columns = st.columns(2)
            for index, portal in enumerate(visible_portals):
                with columns[index % 2]:
                    col1, col2 = st.columns([20, 1])
                    with col1:
                        st.link_button(
                            f"{portal.company} careers",
                            portal.url,
                            use_container_width=True,
                        )
                    with col2:
                        if st.button("✕", key=f"hide_{portal.company}", help=f"Hide {portal.company}"):
                            st.session_state.hidden_portals.add(portal.company)
                            st.rerun()
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


def render_job(job: Job, review: JobReview | None, scope: str) -> None:
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
            "I applied for this job",
            value=current_applied,
            key=f"{scope}-applied-{job.id}",
        )
        feedback = st.radio(
            "Do you like this job?",
            list(Feedback),
            index=list(Feedback).index(current_feedback),
            format_func=lambda value: value.value,
            horizontal=True,
            key=f"{scope}-feedback-{job.id}",
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
                key=f"{scope}-reason-{job.id}",
            )
            if dislike_reason == "Other":
                dislike_reason = st.text_input(
                    "Your reason",
                    value=current_reason,
                    key=f"{scope}-other-reason-{job.id}",
                )
        notes = st.text_area(
            "Optional notes",
            value=current_notes,
            max_chars=1000,
            key=f"{scope}-notes-{job.id}",
        )
        if st.button("Save status", type="primary", key=f"{scope}-save-{job.id}"):
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


def render_job_list(
    jobs: list[Job],
    reviews: dict[str, JobReview],
    empty_message: str,
    scope: str,
) -> None:
    """Render a status-specific job list."""

    if not jobs:
        st.info(empty_message)
        return
    for job in jobs:
        render_job(job, reviews.get(job.id), scope)


def render_search_slots(jobs: list[Job], slot_count: int) -> None:
    """Offer safe browser searches when feeds cannot supply ten real vacancies."""

    if slot_count <= 0:
        return
    covered_roles = {role.name for job in jobs if (role := target_role(job)) is not None}
    missing_roles = [role for role in TARGET_ROLES if role.name not in covered_roles]
    st.warning(
        f"Only {len(jobs)} verified matching vacancies are currently available. "
        f"Use the {slot_count} searches below to look for newly published roles; search "
        "results are not treated as vacancies until an authorized feed imports them."
    )
    for index, role in enumerate(missing_roles[:slot_count], start=1):
        stars = "★" * role.stars + "☆" * (5 - role.stars)
        query = quote_plus(f'"{role.name}" OR Praktikum Germany internship')
        st.markdown(f"**Search slot {index}: {role.name} {stars}**")
        columns = st.columns(2)
        columns[0].link_button(
            "Search the web now",
            f"https://www.google.com/search?q={query}&tbs=qdr:w",
            use_container_width=True,
        )
        linkedin_query = quote_plus(role.name)
        columns[1].link_button(
            "Search LinkedIn manually - 24h",
            "https://www.linkedin.com/jobs/search/"
            f"?f_TPR=r86400&keywords={linkedin_query}&location=Germany",
            use_container_width=True,
        )


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
    render_live_sync_status()

    if st.sidebar.button("Refresh live jobs", type="primary"):
        with st.spinner("Fetching current listings..."):
            count, error = sync_live_jobs()
        if error:
            st.sidebar.error(f"Refresh failed: {error}")
        else:
            st.sidebar.success(f"Imported {count} postings from supported live sources.")
            st.rerun()

    all_jobs = job_repository.list_jobs()
    live_jobs = [job for job in all_jobs if not job.is_demo and matches_target_position(job)]
    # Always include jobs from the past week (168 hours) to avoid empty queues
    age_window = 168  # 1 week in hours
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

    # Render portal management UI
    render_portal_management(all_jobs)

    ordered_jobs = order_with_feedback(jobs, reviews)
    render_metrics(ordered_jobs, reviews)
    render_official_portals()
    filtered_jobs = filter_jobs(ordered_jobs)

    unanswered = [
        job
        for job in filtered_jobs
        if job.id not in reviews
        or (reviews[job.id].feedback is Feedback.NONE and not reviews[job.id].applied)
    ]
    to_review = diverse_role_queue(unanswered, reviews, limit=10)
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
    rejected = [
        job
        for job in filtered_jobs
        if reviews.get(job.id) and reviews[job.id].feedback is Feedback.REJECTED
    ]
    applied = [job for job in filtered_jobs if reviews.get(job.id) and reviews[job.id].applied]

    queue_tab, liked_tab, disliked_tab, rejected_tab, applied_tab = st.tabs(
        [
            f"To review ({len(to_review)})",
            f"Liked ({len(liked)})",
            f"Disliked ({len(disliked)})",
            f"Rejected ({len(rejected)})",
            f"Applied ({len(applied)})",
        ]
    )
    with queue_tab:
        st.subheader(f"Internship, Praktikum and thesis queue - last {age_window} hours")
        st.caption(
            "Only jobs without a saved decision remain here. Liked, disliked, and applied "
            "jobs move to their corresponding status lists. A maximum of three unanswered "
            "jobs per employer prevents one company from dominating the queue."
        )
        render_job_list(to_review, reviews, "No unanswered internships are available.", "queue")
    with liked_tab:
        render_job_list(liked, reviews, "You have not liked any jobs yet.", "liked")
    with disliked_tab:
        render_job_list(disliked, reviews, "You have not disliked any jobs yet.", "disliked")
    with rejected_tab:
        render_job_list(
            rejected,
            reviews,
            "You have not rejected any jobs yet.",
            "rejected",
        )
    with applied_tab:
        render_job_list(
            applied,
            reviews,
            "You have not marked any jobs as applied yet.",
            "applied",
        )


if __name__ == "__main__":
    main()
