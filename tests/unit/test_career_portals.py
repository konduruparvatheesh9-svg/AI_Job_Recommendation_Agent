"""Tests for verified official career portal configuration."""

from job_recommendation_agent.sources.company_careers.catalog import PRIORITY_CAREER_PORTALS


def test_priority_portals_are_unique_https_links() -> None:
    companies = [portal.company for portal in PRIORITY_CAREER_PORTALS]

    assert len(PRIORITY_CAREER_PORTALS) == 30
    assert len(companies) == len(set(companies))
    assert all(portal.url.startswith("https://") for portal in PRIORITY_CAREER_PORTALS)
