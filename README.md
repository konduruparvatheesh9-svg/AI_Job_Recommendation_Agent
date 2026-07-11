# AI Job Recommendation Agent

A modular Python 3.11 application for recommending internships, Praktikum,
Werkstudent positions, and graduate jobs in Germany.

## Phase 1

This phase establishes the package structure, typed configuration, automated
quality checks, and replaceable data-source boundaries. Live data collection and
recommendation ranking will be added in later phases.

Supported source categories are:

- official company career pages, subject to their terms and robots policies;
- documented public job APIs;
- a replaceable LinkedIn adapter that does not perform unauthorized scraping.

## Local setup

Python 3.11 is required.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the quality checks:

```powershell
ruff check .
ruff format --check .
mypy src tests
pytest
```

Copy `.env.example` to `.env` for local configuration. Do not commit `.env` or
SQLite database files.

## Run the portal

```powershell
streamlit run src/job_recommendation_agent/ui/app.py
```

The first launch creates `data/jobs.db` and inserts three fictional, clearly
labeled fallback jobs. Use **Refresh live jobs** to import current early-career
listings from the documented Arbeitnow public API. The best ten jobs are matched
against the supplied resume across Quality Management/industrial manufacturing,
Data Analysis/Data Science, and IT Infrastructure/VMware. Results are displayed
from oldest to newest and include the source and direct application URL. The
portal displays internships only, starting with the past 24 hours and expanding
to 48, 72, and then 168 hours only when required to fill the shortlist. A manual
LinkedIn 24-hour search is provided, but LinkedIn is not scraped or imported. Always
confirm availability on the original source page. Ratings, likes, dislikes, and
notes are saved locally in SQLite.

The portal also includes verified official career-search links for ZEISS, Bosch,
Siemens, Infineon, SAP, GlobalFoundries, ASML, BMW Group, Microsoft, and Amazon.
Dynamic company portals are linked directly unless they expose a documented public
feed suitable for lawful automated ingestion.
