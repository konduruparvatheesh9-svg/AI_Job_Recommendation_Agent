"""Tests for transparent recommendation ranking."""

from datetime import UTC, datetime, timedelta

from job_recommendation_agent.matching.ranking import (
    TARGET_ROLES,
    diverse_role_queue,
    fresh_internships,
    match_reasons,
    matches_target_position,
    relevance_score,
    target_role,
    top_jobs_on_timeline,
)
from job_recommendation_agent.services.demo_data import demo_jobs


def test_top_jobs_are_displayed_in_ascending_date_order() -> None:
    jobs = top_jobs_on_timeline(demo_jobs(), limit=3)

    assert [job.posted_date for job in jobs] == [
        demo_jobs()[2].posted_date,
        demo_jobs()[1].posted_date,
        demo_jobs()[0].posted_date,
    ]


def test_ai_job_has_positive_relevance_score() -> None:
    assert relevance_score(demo_jobs()[0]) > 0


def test_match_reasons_explain_resume_overlap() -> None:
    assert "Python" in match_reasons(demo_jobs()[0])


def test_internship_window_expands_until_results_can_fill_limit() -> None:
    now = datetime(2026, 7, 11, 8, tzinfo=UTC)
    jobs = demo_jobs()
    internship = jobs[0].model_copy(update={"posted_at": now - timedelta(hours=30)})

    selected, hours = fresh_internships([internship, *jobs[1:]], limit=1, now=now)

    assert selected == [internship]
    assert hours == 48


def test_only_supplied_position_families_are_selected() -> None:
    jobs = demo_jobs()

    assert (
        matches_target_position(jobs[0].model_copy(update={"title": "Marketing Intern"})) is False
    )
    assert (
        matches_target_position(jobs[0].model_copy(update={"title": "Data Analytics Intern"}))
        is True
    )


def test_all_requested_role_names_are_classified() -> None:
    job = demo_jobs()[0]

    for role in TARGET_ROLES:
        candidate = job.model_copy(update={"id": role.name, "title": role.name})
        assert target_role(candidate) == role


def test_queue_prefers_different_target_role_families() -> None:
    template = demo_jobs()[0]
    jobs = [
        template.model_copy(update={"id": "data-1", "title": "Data Analytics Intern"}),
        template.model_copy(update={"id": "data-2", "title": "Data Analyst Internship"}),
        template.model_copy(
            update={"id": "bi-1", "title": "Business Intelligence Intern"}
        ),
    ]

    selected = diverse_role_queue(jobs, {}, limit=2)

    selected_roles = [target_role(job) for job in selected]
    assert {role.name for role in selected_roles if role is not None} == {
        "Data Analytics Intern",
        "Business Intelligence Intern",
    }


def test_queue_enforces_company_cap() -> None:
    template = demo_jobs()[0]
    jobs = [
        template.model_copy(
            update={
                "id": str(index),
                "title": f"Data Analyst Intern {index}",
                "location": f"City {index}, Germany",
            }
        )
        for index in range(6)
    ]

    selected = diverse_role_queue(jobs, {}, limit=10, max_per_company=3)

    assert len(selected) == 3
