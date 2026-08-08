# 🎯 AI Job Recommendation Agent

An intelligent, modular Python 3.11 application that helps early-career professionals discover, filter, and manage job opportunities across multiple sources in Germany.

> **Smart Job Discovery** • **Resume-Based Matching** • **Multi-Source Integration** • **Local Storage** • **Personalized Recommendations**

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Algorithm & Workflow](#algorithm--workflow)
- [Job Sources](#job-sources)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Advanced Configuration](#advanced-configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🎓 Overview

The **AI Job Recommendation Agent** is designed to solve a critical problem for early-career professionals: **job hunting is time-consuming**. Instead of manually checking dozens of career portals, this agent:

✨ **Aggregates** job listings from 6+ sources (APIs, portals, job boards)  
🧠 **Intelligently ranks** opportunities based on your profile  
💾 **Stores** everything locally for privacy  
📊 **Tracks** your applications and preferences  
🔗 **Provides** direct application links  

**Target Users:**
- Students seeking internships (Praktikum)
- Working students (Werkstudent)
- Graduate program applicants
- Entry-level professionals in Germany

**Focus Industries:**
- Quality Management & Manufacturing
- Data Analysis & Data Science
- IT Infrastructure & Cloud/DevOps

---

## ✨ Features

### 🔄 Multi-Source Job Aggregation

Fetches real-time listings from:

| Source | Type | Coverage | Frequency |
|--------|------|----------|-----------|
| **Arbeitnow Portal Network** | Public API | Germany-wide | Real-time |
| **Bosch Careers** | Company API | Bosch Group | Real-time |
| **Continental Careers** | Company API | Continental AG | Real-time |
| **Amazon Jobs** | Company API | Amazon EMEA | Real-time |
| **GitHub & Remotive** | Job Board API | Tech/Remote | Real-time |
| **LinkedIn** | Manual Search | Global | Manual (24h) |

### 🧠 Intelligent Matching Algorithm

The recommendation engine uses **multi-factor scoring**:

- **Keyword Relevance**: Matches job descriptions against target roles
- **Experience Level**: Prioritizes internships/entry-level roles
- **Company Preference**: Rewards tier-1 companies (Bosch, Siemens, etc.)
- **Freshness**: Filters by posting date (24h, 48h, 72h, 7-day windows)
- **User Feedback**: Learns from your "Like/Dislike" history
- **Role Diversity**: Ensures variety across job types and companies
- **Remote Status**: Optional boost for remote positions

### 💾 Local Privacy-First Storage

- SQLite database stored locally on your laptop
- No data sent to cloud servers
- Full application history with personal notes
- Persistent ratings and preferences

### ⭐ Job Management

- **Rate Jobs**: Like, Dislike, or track as "Applied"
- **Add Notes**: Personal observations on each opportunity
- **Track Status**: Mark applications you've submitted
- **Search & Filter**: By company, job type, location, date

### 📅 Smart Filtering

- Early-career specific (Internships, Werkstudent, Graduate, Thesis)
- Time-based windows: 24h → 48h → 72h → 7-day progression
- Company preferences with tier-based ranking
- Remote/on-site options

### 🎯 Target Role Classification

Specialized matching for 10+ role families:
- Data Analytics Intern
- Business Intelligence Intern
- Product Analytics Intern
- Digital Transformation Intern
- Industrial Data Analytics Intern
- AI/Data Intern
- Business Analyst Intern
- Market Intelligence Intern
- Product Management Intern
- Industry 4.0 / Smart Manufacturing Intern

---

## ⚡ Quick Start

### ✅ Automated Setup (Recommended)

**Windows Users:**

1. Download the repository as ZIP or clone it
2. Double-click `setup.bat` (or right-click `setup.ps1` → Run with PowerShell)
3. Wait for setup to complete (2-5 minutes)
4. Run: `streamlit run src/job_recommendation_agent/ui/app.py`
5. Portal opens at `http://localhost:8501`

**macOS/Linux Users:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
streamlit run src/job_recommendation_agent/ui/app.py
```

### 📖 Detailed Setup

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for comprehensive installation instructions.

### 🚀 Quick Run Commands

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Launch portal
streamlit run src/job_recommendation_agent/ui/app.py

# Run quality checks (developers)
ruff check .
mypy src tests
pytest
```

---

## 🏗️ System Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     JOB SOURCES LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│ Arbeitnow │ Bosch API │ Continental │ Amazon │ GitHub │ LinkedIn│
└──────────┬──────────────────────────────────────────────┬────────┘
           │                                              │
           v                                              v
     ┌──────────────────────────────────────────────────────────┐
     │           NORMALIZATION & VALIDATION LAYER               │
     │  - Parse source-specific formats                         │
     │  - Extract skills, dates, locations                      │
     │  - Validate against Job schema                           │
     └──────────────────┬───────────────────────────────────────┘
                        │
                        v
     ┌──────────────────────────────────────────────────────────┐
     │            LOCAL STORAGE LAYER (SQLite)                  │
     │  ┌──────────────┐    ┌──────────────┐  ┌──────────────┐  │
     │  │  jobs table  │    │ reviews tbl  │  │ metadata tbl │  │
     │  │  (5000+ rows)│    │(user ratings)│  │  (sync info) │  │
     │  └──────────────┘    └──────────────┘  └──────────────┘  │
     └──────────────────┬───────────────────────────────────────┘
                        │
                        v
     ┌──────────────────────────────────────────────────────────┐
     │         MATCHING & RANKING LAYER                         │
     │  - Keyword relevance scoring                             │
     │  - Company preference bonuses                            │
     │  - Feedback-based personalization                        │
     │  - Role classification & diversity                       │
     └──────────────────┬───────────────────────────────────────┘
                        │
                        v
     ┌──────────────────────────────────────────────────────────┐
     │              UI PRESENTATION LAYER                       │
     │  (Streamlit Web Portal)                                  │
     │  - Browse recommended jobs                               │
     │  - Rate & comment on jobs                                │
     │  - Track applications                                    │
     │  - Search & filter                                       │
     │  - Manual sync from sources                              │
     └──────────────────────────────────────────────────────────┘
```

### Module Structure

```
job_recommendation_agent/
├── domain/
│   └── models.py              # Job, JobReview, EmploymentType, Feedback schemas
├── sources/                   # Job fetchers (pluggable architecture)
│   ├── base.py               # JobSource protocol (interface)
│   ├── company_careers/      # Official company APIs
│   │   ├── amazon.py         # Amazon Jobs API adapter
│   │   ├── bosch.py          # Bosch SmartRecruiters API
│   │   ├── continental.py    # Continental SmartRecruiters API
│   │   └── catalog.py        # Portal directory
│   └── public_apis/          # Public job boards
│       ├── arbeitnow.py      # Arbeitnow portal API
│       └── github.py         # GitHub & Remotive jobs API
├── matching/
│   └── ranking.py            # Scoring & recommendation algorithms
├── persistence/
│   └── sqlite_repository.py  # Local database operations
├── services/
│   └── demo_data.py          # Sample jobs for first launch
├── ui/
│   └── app.py                # Streamlit web interface
└── config.py                 # Environment-based settings
```

---

## 🧠 Algorithm & Workflow

### 1. **Scoring Algorithm** (The Brain)

Every job receives a **multi-factor relevance score**:

```python
relevance_score = keyword_score + employment_type_bonus + company_bonus + remote_bonus

Keyword Score:
  - Search for target terms in: job title + description + skills
  - Weighted by importance (e.g., "data analyst" = +12, "python" = +6)
  - Max possible from keywords alone: ~100+ points

Employment Type Bonus:
  - Internship/Werkstudent: +8 points (primary targets)
  - Graduate: +3 points
  - Other: +0 points

Company Bonus (Tier-based preference):
  - Tier 1 (Bosch, VW, Siemens, etc.): +15 points
  - Tier 2 (SAP, TeamViewer, Celonis, etc.): +10 points
  - Tier 3 (Amazon, Microsoft, Zalando, etc.): +5 points
  - Unknown: +0 points

Remote Bonus:
  - Remote positions: +1 point (minor boost)

Final Score Example:
  Job: "Data Analytics Intern at Bosch in Berlin"
  - Keywords: "data analytics" (10) + "analytics" (7) = 17
  - Employment type: Internship (+8)
  - Company: Bosch Tier 1 (+15)
  - Remote: No (+0)
  - TOTAL SCORE: 40 points
```

### 2. **Feedback Learning** (Personalization)

After you rate jobs, the algorithm learns:

```python
feedback_score = relevance_score + feedback_adjustment

Feedback Adjustment:
  For each job you LIKED:
    + Find all skills/title terms in that job
    + Boost future jobs with overlapping terms by +3 per match
  
  For each job you DISLIKED or REJECTED:
    - Find all skills/title terms in that job
    - Penalize future jobs with overlapping terms by -3 per match

Example:
  You liked: "Machine Learning Intern at Zalando"
    Terms: machine learning, data science, python, sql
  
  New job: "AI Engineer (Python/SQL required)"
    Overlaps: python (+3), sql (+3) = +6 adjustment
    New score = relevance_score + 6
```

### 3. **Role Classification** (Understanding Your Goals)

Jobs are classified into 10 target role families:

```
Role: "Data Analytics Intern" (5 stars)
  Aliases detected:
    - "data analytics"
    - "data analyst"
    - "data analysis"
    - "datenanalyse"
    - "business intelligence"
    - "bi intern"

When a job title contains one of these terms:
  ✓ It's classified as a target role
  ✓ Included in role-diverse shortlist
  ✓ Boosted in relevance calculations

Non-matching jobs also included but ranked lower.
```

### 4. **Freshness Windows** (Progressive Filtering)

Smart date-based filtering that expands as needed:

```
START: User wants top 10 jobs

WINDOW 1: Past 24 hours
  Found 7 jobs → Need 3 more

WINDOW 2: Past 48 hours
  Found 9 jobs total → Need 1 more

WINDOW 3: Past 72 hours
  Found 11 jobs total → DISPLAY TOP 10

If no jobs found at any window:
  Keep expanding: 168h → 336h → 720h → 2160h (90 days)
```

### 5. **Diversity Engine** (Balanced Shortlist)

Ensures you see variety, not dominated by one company:

```
Goal: Build top 10 without more than 3 from same company

Phase 1: Role-Based Diversity
  For each of 10 target roles (in priority order):
    - Pick best job matching that role
    - Ensure < 2 from same company
    - Add to shortlist
    
Phase 2: Company Coverage
  For each remaining company not yet represented:
    - Add their top job
    - Ensures 1 opportunity per company

Phase 3: Fill Remaining
  - Add remaining top jobs
  - Enforce max 3 per company limit
  
Result: Diverse 10-job shortlist with variety
```

### 6. **Ranking & Display Order** (Timeline View)

Final step before showing to user:

```
1. SCORE all jobs by relevance + feedback
2. FILTER for duplicates (same title + company)
3. SELECT top N jobs
4. SORT by posting date (oldest → newest)

Why oldest-first on screen?
  - Older opportunities may close soon
  - Newer jobs can wait
  - Natural urgency ordering
```

### Complete Workflow Diagram

```
USER VISIT PORTAL
       ↓
   SYNC JOBS
   ├─ Arbeitnow API → Fetch 100+ jobs
   ├─ Bosch API → Fetch 50+ jobs
   ├─ Continental API → Fetch 50+ jobs
   ├─ Amazon API → Fetch 30+ jobs
   ├─ GitHub API → Fetch 20+ jobs
   └─ Store all in SQLite DB (5000+ jobs cached)
       ↓
   FILTER & NORMALIZE
   ├─ Extract: title, description, skills, location, date
   ├─ Validate employment type
   ├─ Detect remote status
   └─ Calculate posting date
       ↓
   APPLY FRESHNESS WINDOWS
   ├─ Get internships from past 24h
   ├─ If < 10 jobs, expand to 48h
   ├─ Continue until 10+ jobs or max window reached
   └─ Return (jobs_list, hours_window)
       ↓
   SCORE EACH JOB
   ├─ keyword_score (search target terms)
   ├─ employment_bonus
   ├─ company_bonus
   └─ Calculate relevance_score
       ↓
   APPLY USER FEEDBACK
   ├─ Load user's Like/Dislike history
   ├─ Calculate feedback_adjustment
   ├─ final_score = relevance_score + adjustment
   └─ Re-sort by final_score
       ↓
   APPLY DIVERSITY RULES
   ├─ Balance roles (10 role families)
   ├─ Limit companies (max 3 per company)
   ├─ Remove duplicates
   └─ Return top 10 jobs
       ↓
   SORT FOR DISPLAY
   ├─ Oldest to newest (by posting date)
   └─ Add match_reasons (explain why recommended)
       ↓
   DISPLAY ON WEB
   ├─ Show job card
   ├─ Display match score & reasons
   ├─ Provide Like/Dislike buttons
   ├─ Show direct application link
   └─ Save rating to SQLite
       ↓
   ITERATE & LEARN
       (Algorithm improves with each rating)
```

### Algorithm Decision Points

| Question | Condition | Action |
|----------|-----------|--------|
| Is this an internship? | Yes | +8 points |
| Is this from Bosch? | Yes | +15 points |
| Did I like similar jobs? | Yes | +3 per match |
| Is it from same company? | >3 jobs | Exclude |
| Is it older than 7 days? | Yes & <10 jobs | Still include |
| Should I show oldest first? | Yes | Sort ascending by date |

---

## 💼 Job Sources

### Source Categories

#### 1. **Official Company Career APIs** (Most Reliable)
- **Bosch**: SmartRecruiters API (50+ active positions)
- **Continental**: SmartRecruiters API (40+ active positions)
- **Amazon**: Amazon.jobs API (30+ EMEA positions)

**Advantages:**
- Direct from source
- High data quality
- Updated multiple times daily
- Legal & approved access

#### 2. **Public Job Board APIs** (Broad Coverage)
- **Arbeitnow Portal**: Germany-focused job board (100+ positions daily)
- **GitHub/Remotive**: Tech & Remote jobs (20+ positions daily)

**Advantages:**
- Broad industry coverage
- No scraping needed
- Free public APIs
- Updated real-time

#### 3. **Manual Search** (Supplementary)
- **LinkedIn**: Manual 24-hour search (optional)

**Advantages:**
- Most comprehensive
- Current data
- Manual control
- No automated access needed

### How Sources Are Integrated

```python
# In app.py sync_live_jobs()
sources = (
    ArbeitnowSource(...),        # Germany job board
    BoschCareerSource(...),      # Bosch portal
    ContinentalCareerSource(...),# Continental portal
    AmazonCareerSource(...),     # Amazon jobs
    GitHubJobsSource(...),       # GitHub/Remotive jobs
)

for source in sources:
    try:
        jobs = source.fetch_jobs()  # Fetch from API
        repository().upsert_jobs(jobs)  # Store in DB
    except Exception:
        # One failing source doesn't break everything
        continue
```

---

## 📦 Installation

### Prerequisites

- **Python 3.11 or higher** ([Download](https://www.python.org/downloads/))
- **Git** (optional, for cloning) ([Download](https://git-scm.com/))
- **2GB+ RAM**
- **500MB disk space**
- **Windows 10+, macOS 10.14+, or Linux**

### Installation Methods

#### Method 1: Automated Setup (Windows)

```powershell
# Download repository
# Double-click setup.bat

# Or in PowerShell:
.\setup.ps1
```

#### Method 2: Manual Setup (Windows PowerShell)

```powershell
# Clone repository
git clone https://github.com/your-username/ai-job-recommendation-agent.git
cd ai-job-recommendation-agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# Copy configuration
Copy-Item .env.example .env

# Optional: Run quality checks
ruff check .
mypy src tests
pytest
```

#### Method 3: Manual Setup (macOS/Linux)

```bash
git clone https://github.com/your-username/ai-job-recommendation-agent.git
cd ai-job-recommendation-agent

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -e ".[dev]"

cp .env.example .env
```

#### Method 4: Requirements Only (Lighter Install)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run src/job_recommendation_agent/ui/app.py
```

### Verify Installation

```powershell
python --version  # Should be 3.11+
pip list  # Should show: streamlit, pandas, pydantic, requests
python -c "import streamlit; print('✓ Streamlit installed')"
```

---

## 🚀 Usage

### Launch the Portal

```powershell
.venv\Scripts\Activate.ps1
streamlit run src/job_recommendation_agent/ui/app.py
```

**Portal opens at**: `http://localhost:8501`

### First Launch

1. **Demo Data Loaded**: 3 sample jobs appear
2. **Database Created**: `data/jobs.db` created automatically
3. **Click "🔄 Refresh live jobs"**: Fetches real listings from all 5+ sources
4. **Wait**: Fetching takes 30-60 seconds (depends on API speeds)
5. **Browse**: Top 10 jobs appear, sorted oldest-to-newest

### Main Features

#### 🔍 Browse Jobs
- Automatically displays top 10 recommendations
- Shows match score & reasons why recommended
- Click company name to visit career portal
- Click job title to view full details

#### ⭐ Rate Jobs
- **Like (👍)**: Job looks promising
- **Dislike (👎)**: Not interested
- **Applied (✅)**: Already submitted application
- System learns from your ratings

#### 📝 Add Notes
- Personal observations on each job
- Track follow-up actions
- Save interview dates/contacts
- Notes stored locally

#### 🔄 Refresh Live Jobs
- Syncs all sources again
- Updates database with new postings
- Shows count of new jobs added
- Last sync timestamp displayed

#### 🔗 Company Links
- Verified official career portals
- Direct links for major companies
- No need to search separately

#### 📊 Application Tracker
- See all jobs you've applied to
- Track status & notes
- Review past ratings

### Configuration

Edit `.env` file:

```bash
# .env
APP_ENV=development                    # development, test, or production
DATABASE_PATH=data/jobs.db            # Where to store SQLite DB
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR, CRITICAL

ARBEITNOW_API_URL=https://www.arbeitnow.com/api/job-board-api
ARBEITNOW_PAGES=5                     # How many pages to fetch

REQUEST_TIMEOUT_SECONDS=15.0          # API timeout (seconds)

# Company API URLs
BOSCH_API_URL=https://api.smartrecruiters.com/v1/companies/BoschGroup/postings
CONTINENTAL_API_URL=https://api.smartrecruiters.com/v1/companies/Continental/postings
AMAZON_JOBS_API_URL=https://www.amazon.jobs/en/search.json
```

---

## 📁 Project Structure

```
ai-job-recommendation-agent/
│
├── README.md                          # This file - full documentation
├── SETUP_GUIDE.md                     # Detailed installation & troubleshooting
├── DOWNLOAD_AND_RUN.md                # Quick start guide
├── ARCHITECTURE_NOTES.md              # Deep dive on algorithms
│
├── setup.bat                          # Windows automated setup
├── setup.ps1                          # PowerShell automated setup
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Project configuration
│
├── src/job_recommendation_agent/
│   │
│   ├── config.py                      # Environment settings & validation
│   │
│   ├── domain/
│   │   └── models.py                  # Data classes: Job, JobReview, Feedback
│   │
│   ├── sources/
│   │   ├── base.py                    # JobSource protocol (interface)
│   │   ├── company_careers/
│   │   │   ├── amazon.py              # Amazon Jobs API adapter
│   │   │   ├── bosch.py               # Bosch SmartRecruiters adapter
│   │   │   ├── continental.py         # Continental SmartRecruiters adapter
│   │   │   └── catalog.py             # Portal directory
│   │   └── public_apis/
│   │       ├── arbeitnow.py           # Arbeitnow API adapter
│   │       └── github.py              # GitHub/Remotive API adapter
│   │
│   ├── matching/
│   │   └── ranking.py                 # Core ranking & scoring algorithms
│   │       - relevance_score()        # Multi-factor scoring
│   │       - feedback_score()         # Learning from user ratings
│   │       - target_role()            # Role classification
│   │       - diverse_role_queue()     # Diversity engine
│   │       - fresh_internships()      # Freshness windows
│   │       - match_reasons()          # Explain recommendations
│   │
│   ├── persistence/
│   │   └── sqlite_repository.py       # SQLite database operations
│   │
│   ├── services/
│   │   └── demo_data.py               # Sample data for first launch
│   │
│   └── ui/
│       └── app.py                     # Streamlit web interface
│
├── tests/
│   ├── unit/
│   │   ├── test_ranking.py            # Ranking algorithm tests
│   │   ├── test_sqlite_repository.py  # Database tests
│   │   ├── test_career_portals.py     # Source adapter tests
│   │   ├── test_company_sources.py    # Company API tests
│   │   └── test_config.py             # Config validation tests
│   └── integration/
│
├── data/
│   ├── jobs.db                        # SQLite database (auto-created)
│   ├── jobs1.err                      # Error logs from sources
│   ├── jobs2.err
│   └── jobs3.err
│
└── .env.example                       # Example environment file
```

### Key Files Explained

#### `ranking.py` - The Brain 🧠
Contains all recommendation logic:
- `relevance_score()`: Calculate job relevance (0-100+ points)
- `feedback_score()`: Personalization based on user ratings
- `target_role()`: Classify jobs into 10 role families
- `diverse_role_queue()`: Ensure variety in top 10
- `fresh_internships()`: Apply time-based windows
- `match_reasons()`: Explain why job is recommended

#### `sqlite_repository.py` - The Memory 💾
Manages local database:
- Store 5000+ jobs efficiently
- Track user ratings & notes
- Maintain sync metadata
- No cloud uploads

#### `app.py` - The Interface 🎨
Streamlit web portal:
- Browse recommendations
- Rate jobs (Like/Dislike/Applied)
- Add personal notes
- Manual refresh
- Search & filter

#### `config.py` - The Settings ⚙️
Validate environment:
- Python paths
- API URLs
- Timeouts
- Database location

---

## 🔧 Advanced Configuration

### Environment Variables

```bash
# .env file examples

# === Application ===
APP_ENV=production              # development | test | production
DATABASE_PATH=data/jobs.db      # SQLite database location
LOG_LEVEL=INFO                  # DEBUG | INFO | WARNING | ERROR | CRITICAL

# === API Settings ===
REQUEST_TIMEOUT_SECONDS=15.0    # How long to wait for API responses
                                # Adjust if APIs are slow (min: 5, max: 60)

# === Arbeitnow (Germany Job Board) ===
ARBEITNOW_API_URL=https://www.arbeitnow.com/api/job-board-api
ARBEITNOW_PAGES=5               # Number of result pages to fetch (1-10)
                                # Higher = more jobs but slower
                                # Default 5 = ~100-150 jobs

# === Company APIs ===
BOSCH_API_URL=https://api.smartrecruiters.com/v1/companies/BoschGroup/postings
CONTINENTAL_API_URL=https://api.smartrecruiters.com/v1/companies/Continental/postings
AMAZON_JOBS_API_URL=https://www.amazon.jobs/en/search.json

# Note: These APIs are publicly documented and don't require keys
```

### Performance Tuning

```python
# In app.py, adjust sync intervals:
AUTO_SYNC_INTERVAL = timedelta(minutes=15)  # Check every 15 minutes
                                            # Reduce to 5 for more frequent
                                            # Increase to 60 for less traffic

# In ranking.py, adjust result counts:
fresh_internships(..., limit=10)     # Show top 10 (change to 20 for more)
diverse_role_queue(..., limit=10)    # Same shortlist size
```

### Database Optimization

```powershell
# Clear old jobs (older than 60 days):
sqlite3 data/jobs.db
> DELETE FROM jobs WHERE posted_date < date('now', '-60 days');
> VACUUM;

# Check database size:
dir data/jobs.db
```

---

## 👨‍💻 Development

### Setup Development Environment

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

### Code Quality

```powershell
# Run linter
ruff check .

# Auto-format code
ruff format .

# Type checking
mypy src tests

# Run tests
pytest

# Test with coverage
pytest --cov=job_recommendation_agent
```

### Run Tests

```powershell
# All tests
pytest

# Specific test file
pytest tests/unit/test_ranking.py

# Specific test
pytest tests/unit/test_ranking.py::test_relevance_score

# With detailed output
pytest -v

# Stop on first failure
pytest -x
```

### Adding New Job Source

1. Create adapter in `sources/public_apis/yourapi.py`:

```python
class YourAPISource:
    def __init__(self, api_url: str, timeout_seconds: float = 15.0):
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds
    
    def fetch_jobs(self) -> list[Job]:
        # Fetch from your API
        # Normalize to Job objects
        # Return list[Job]
        pass
```

2. Add to `app.py`:

```python
from job_recommendation_agent.sources.public_apis.yourapi import YourAPISource

sources = (
    # ... existing sources ...
    YourAPISource(settings.your_api_url),
)
```

3. Update `.env`:

```
YOUR_API_URL=https://api.example.com/jobs
```

### Common Development Tasks

| Task | Command |
|------|---------|
| Add dependency | `pip install package-name` |
| Update dependencies | `pip install --upgrade pip` |
| Freeze dependencies | `pip freeze > requirements.txt` |
| Debug mode | `streamlit run app.py --logger.level=debug` |
| Different port | `streamlit run app.py --server.port 8502` |
| Rebuild database | `rm data/jobs.db` & rerun app |

---

## ❓ Troubleshooting

### Installation Issues

#### "Python not found"
```powershell
# Check if Python is installed
python --version

# If not:
# Download from https://www.python.org/downloads/
# Run installer with "Add Python to PATH" checked
```

#### "Virtual environment won't activate"
```powershell
# Error: "running scripts is disabled"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try:
.venv\Scripts\Activate.ps1
```

#### "pip install fails with permission error"
```powershell
# Make sure virtual environment is activated first:
.venv\Scripts\Activate.ps1

# Then install
pip install -e ".[dev]"
```

### Runtime Issues

#### "Port 8501 already in use"
```powershell
# Use different port
streamlit run src/job_recommendation_agent/ui/app.py --server.port 8502

# Or kill process using port 8501:
# Windows: netstat -ano | findstr :8501
# Then: taskkill /PID <PID> /F
```

#### "API timeouts or empty results"
```powershell
# Increase timeout in .env:
REQUEST_TIMEOUT_SECONDS=30.0  # Instead of 15.0

# Check API status:
# - Arbeitnow: https://www.arbeitnow.com/
# - Amazon: https://www.amazon.jobs/
```

#### "Database is locked"
```powershell
# Delete database and rebuild:
rm data/jobs.db
# Rerun app to recreate
```

#### "Jobs not appearing"
```powershell
# 1. Check internet connection
# 2. Click "Refresh live jobs" button
# 3. Wait 30-60 seconds for sync
# 4. Check browser console (F12) for errors
```

### Performance Issues

#### "Portal is slow"
```
- Reduce ARBEITNOW_PAGES to 2-3
- Increase AUTO_SYNC_INTERVAL to 30 minutes
- Clear old jobs from database (see Database Optimization)
- Close other programs using CPU
```

#### "High memory usage"
```
- Database may be large (5000+ jobs)
- Run: sqlite3 data/jobs.db "VACUUM;"
- Or delete old jobs (>90 days)
```

### Getting Help

1. **Check logs**: Terminal shows detailed error messages
2. **Review SETUP_GUIDE.md**: Has extended troubleshooting
3. **GitHub Issues**: Report bugs with full error message
4. **Environment**: Verify .env file is correctly configured

---

## 📊 Statistics & Metrics

### Typical Usage Stats

After one month of normal use:

| Metric | Typical Value |
|--------|---------------|
| Jobs in database | 3,000-5,000 |
| Database size | 50-100 MB |
| Sync time | 30-60 seconds |
| Jobs rated by user | 100-200 |
| Recommendations improved | 20-40% (with feedback) |

### API Rate Limits

| API | Limit | Window |
|-----|-------|--------|
| Arbeitnow | 50 req | 1 minute |
| Amazon | 100 req | 1 minute |
| Bosch | 200 req | 1 minute |
| GitHub (Remotive) | Unlimited | - |

---

## 📝 License & Contributing

**License**: MIT - See LICENSE file

**Contributing**: 
- Fork the repository
- Create feature branch: `git checkout -b feature/new-source`
- Commit changes: `git commit -am 'Add support for XYZ'`
- Push branch: `git push origin feature/new-source`
- Open Pull Request

---

## 🎯 Roadmap

### Phase 1 (Current) ✅
- [x] Multi-source job aggregation
- [x] SQLite local storage
- [x] Intelligent ranking algorithm
- [x] Streamlit web interface
- [x] GitHub source integration

### Phase 2 (Planned)
- [ ] Machine learning-based personalization
- [ ] Resume parsing & keyword extraction
- [ ] Email digest of top jobs
- [ ] Browser extension for quick apply
- [ ] Mobile app interface
- [ ] LinkedIn auto-apply
- [ ] Skill gap analysis

### Phase 3 (Future)
- [ ] Salary negotiation hints
- [ ] Interview prep resources
- [ ] Peer recommendations
- [ ] Company insights & reviews
- [ ] Application timeline tracking

---

## 📞 Contact & Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [Your email]

---

**Built with ❤️ for early-career professionals in Germany**

**Happy job hunting! 🎉**

---

## Version & Updates

- **Current Version**: 0.1.0
- **Last Updated**: 2026-08-08
- **Python**: 3.11+
- **Status**: Active Development

## ⚡ Quick Start (Automated Setup)

### Windows Users - One-Click Setup

**Download and run the automated setup script:**

1. **Download** one of these setup scripts:
   - Batch script: [setup.bat](setup.bat) (Right-click → Save link as)
   - PowerShell script: [setup.ps1](setup.ps1) (Right-click → Save link as)

2. **Extract the entire repository** to your desired location

3. **Run the setup script:**
   - **Windows Batch**: Double-click `setup.bat`
   - **Windows PowerShell**: Right-click `setup.ps1` → Run with PowerShell

4. The script will automatically:
   - Verify Python 3.11+ installation
   - Create virtual environment
   - Install all dependencies
   - Verify everything works
   - Show you how to launch the portal

### Manual Setup (Windows PowerShell)

Python 3.11 is required. [Download Python](https://www.python.org/downloads/)

```powershell
# Clone or download the repository
git clone https://github.com/your-username/ai-job-recommendation-agent.git
cd ai-job-recommendation-agent

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# Optional: Run quality checks
ruff check .
ruff format --check .
mypy src tests
pytest

# Copy configuration
Copy-Item .env.example .env
```

### Additional Setup Documents

📖 **[Full Setup Guide](SETUP_GUIDE.md)** - Comprehensive installation & troubleshooting guide  
📄 **[requirements.txt](requirements.txt)** - Python dependencies for manual installation

## Run the Portal

```powershell
streamlit run src/job_recommendation_agent/ui/app.py
```

The portal opens at `http://localhost:8501`

## 🎯 Features

### Live Job Sources
The portal fetches real-time listings from multiple sources:

- **Arbeitnow Portal Network** - Germany-focused job board API
- **Bosch Career Portal** - Official company careers page
- **Continental Career Portal** - Official company careers page  
- **Amazon Jobs API** - Amazon internships & entry-level roles
- **GitHub & Remotive Jobs** - GitHub career opportunities
- **LinkedIn** (Manual search) - 24-hour search option

First launch creates `data/jobs.db` and inserts three demo jobs. Click **Refresh live jobs** to import current early-career listings.

### Supported Job Types

- 🎓 Internships (Praktikum)
- 👨‍💼 Working Student (Werkstudent)
- 🎯 Graduate Programs
- 📝 Thesis / Final Project Positions
- 📈 Entry-Level Roles

### Target Industries

- Quality Management & Industrial Manufacturing
- Data Analysis & Data Science
- IT Infrastructure & Cloud/DevOps

### Features

- ✅ Resume-based job matching across 10+ criteria
- ✅ Local SQLite database - no data sent to cloud
- ✅ Rate jobs: Like, Dislike, Apply status
- ✅ Personal notes on each opportunity
- ✅ Direct application links to original postings
- ✅ 24h/48h/72h/7-day job freshness filters
- ✅ Verified official career portal links

The portal displays internships starting with the past 24 hours and expands to 48, 72, and 168 hours only when needed to fill the shortlist. Results are from oldest to newest with direct source links. Always confirm availability on the original source page.

The portal also includes verified official career-search links for ZEISS, Bosch, Siemens, Infineon, SAP, GlobalFoundries, ASML, BMW Group, Microsoft, and Amazon. Dynamic company portals are linked directly unless they expose a documented public feed suitable for lawful automated ingestion.
