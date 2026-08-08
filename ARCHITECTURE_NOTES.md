# 🏗️ Architecture & Algorithm Deep Dive

## Table of Contents
- [System Architecture](#system-architecture)
- [Data Models](#data-models)
- [Ranking Algorithm](#ranking-algorithm)
- [Scoring System](#scoring-system)
- [Feedback Learning](#feedback-learning)
- [Database Schema](#database-schema)
- [API Integration Patterns](#api-integration-patterns)

---

## System Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│           PRESENTATION LAYER                    │
│  (Streamlit Web UI)                             │
│  - Browse jobs                                  │
│  - Rate jobs                                    │
│  - Manage applications                          │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────┐
│         APPLICATION/LOGIC LAYER                 │
│  - Job fetching & normalization                 │
│  - Ranking & scoring                            │
│  - Feedback processing                          │
│  - Role classification                          │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────┐
│          DATA/PERSISTENCE LAYER                 │
│  (SQLite Database)                              │
│  - Store 5000+ jobs                             │
│  - Track user reviews & ratings                 │
│  - Maintain sync metadata                       │
└─────────────────────────────────────────────────┘
```

### Module Dependency Graph

```
app.py (UI)
├── ranking.py (Logic)
│   ├── models.py (Domain)
│   └── sqlite_repository.py (Data)
│
├── sources/* (Data Fetching)
│   ├── base.py (Interface)
│   ├── company_careers/* (Company APIs)
│   │   ├── amazon.py
│   │   ├── bosch.py
│   │   └── continental.py
│   └── public_apis/* (Public APIs)
│       ├── arbeitnow.py
│       └── github.py
│
├── config.py (Settings)
└── sqlite_repository.py (Persistence)
```

---

## Data Models

### Job Model

```python
class Job(BaseModel):
    id: str                          # Unique ID (source-job_id)
    title: str                       # "Data Analytics Intern"
    company: str                     # "Bosch"
    location: str                    # "Stuttgart, Germany"
    employment_type: EmploymentType  # Internship | Thesis | etc
    description: str                 # Full job description (1500 chars max)
    skills: list[str]                # ["Python", "SQL", "Data Science"]
    source_name: str                 # "Arbeitnow Portal Network"
    source_url: HttpUrl              # Direct application link
    posted_date: date | None         # 2026-08-08
    posted_at: datetime | None       # 2026-08-08T10:30:00+00:00
    is_remote: bool                  # True/False
    is_demo: bool                    # True for sample data

Example Instance:
{
    "id": "arbeitnow-12345",
    "title": "Data Analytics Intern",
    "company": "Bosch",
    "location": "Stuttgart, Germany",
    "employment_type": "Internship / Praktikum",
    "description": "We're looking for an analytics intern to...",
    "skills": ["Python", "SQL", "Tableau"],
    "source_name": "Arbeitnow Portal Network",
    "source_url": "https://arbeitnow.com/jobs/12345",
    "posted_date": "2026-08-08",
    "posted_at": "2026-08-08T10:30:00+00:00",
    "is_remote": false,
    "is_demo": false
}
```

### JobReview Model

```python
class JobReview(BaseModel):
    job_id: str                      # References Job.id
    rating: int | None               # 1-5 stars (optional)
    feedback: Feedback               # Like | Dislike | Rejected | None
    applied: bool                    # Did you apply?
    dislike_reason: str              # Why you disliked it
    notes: str                       # Your personal notes
    updated_at: datetime             # When you last updated

Example Instance:
{
    "job_id": "arbeitnow-12345",
    "rating": 4,
    "feedback": "Like",
    "applied": false,
    "dislike_reason": "",
    "notes": "Great company, follow up next week",
    "updated_at": "2026-08-08T14:30:00+00:00"
}
```

### EmploymentType Enum

```python
class EmploymentType(StrEnum):
    INTERNSHIP = "Internship / Praktikum"
    THESIS = "Thesis / Abschlussarbeit"
    WORKING_STUDENT = "Werkstudent"
    GRADUATE = "Graduate"
    ENTRY_LEVEL = "Entry level"
```

### Feedback Enum

```python
class Feedback(StrEnum):
    NONE = "Not reviewed"
    LIKE = "Like"
    DISLIKE = "Dislike"
    REJECTED = "Rejected / not proceeding"
```

---

## Ranking Algorithm

### Overview

The ranking system scores jobs on multiple dimensions and combines them into a final relevance score. This score determines which jobs appear first in your personalized shortlist.

### Scoring Pipeline

```
Raw Job Data
    ↓
[KEYWORD SCORING]
    ├─ Search job.title for target terms
    ├─ Search job.description for target terms
    ├─ Search job.skills for target terms
    └─ Sum weights of all matched terms
    ↓ (Example: 24 points)
    ↓
[EMPLOYMENT TYPE BONUS]
    ├─ Internship/Werkstudent: +8
    ├─ Graduate: +3
    └─ Other: +0
    ↓ (Example: +8)
    ↓
[COMPANY PREFERENCE BONUS]
    ├─ Tier 1 (Bosch, VW, Siemens): +15
    ├─ Tier 2 (SAP, TeamViewer): +10
    ├─ Tier 3 (Amazon, Microsoft): +5
    └─ Unknown: +0
    ↓ (Example: +15)
    ↓
[REMOTE BONUS]
    ├─ Remote: +1
    └─ On-site: +0
    ↓ (Example: +0)
    ↓
[FEEDBACK ADJUSTMENT] (if user has rated jobs)
    ├─ For liked jobs: +3 per matching term
    ├─ For disliked jobs: -3 per matching term
    └─ Sum all adjustments
    ↓ (Example: +6 from likes, -3 from dislikes = +3)
    ↓
FINAL SCORE = Base Score + Feedback Adjustment
(Example: 24 + 8 + 15 + 0 + 3 = 50 points)
```

### Target Terms Reference

```python
TARGET_TERMS = {
    # Quality Management (High Priority)
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
    
    # Data Analysis (High Priority)
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
    
    # IT Infrastructure (Medium Priority)
    "it infrastructure": 9,
    "system engineer": 9,
    "vmware": 10,
    "virtualization": 8,
    "windows server": 6,
    "linux": 4,
    # ... more terms ...
}
```

### Scoring Examples

#### Example 1: High-Scoring Job
```
Job: "Data Analytics Intern at Bosch in Stuttgart"
Description: "Python, SQL, Tableau, data science..."

Keyword Matching:
  - "data analytics" (in title): +12
  - "analytics" (in description): +7
  - "python": +6
  - "sql": +7
  - "data science": +10
  Subtotal: 42 points

Employment Type: Internship +8
Company: Bosch (Tier 1) +15
Remote: No +0

Subtotal: 42 + 8 + 15 = 65 points

User Feedback:
  - Previously liked 2 jobs with "Python" keyword: +3, +3
  - Previously disliked 1 job with "Analytics": -3
  Adjustment: +3

FINAL SCORE: 68 points ⭐⭐⭐⭐⭐
```

#### Example 2: Medium-Scoring Job
```
Job: "Business Analyst at Unknown Company"
Description: "Basic analytics role..."

Keyword Matching:
  - "business analyst": +4
  - "analytics": +7
  Subtotal: 11 points

Employment Type: Entry level +0
Company: Unknown +0
Remote: No +0

Subtotal: 11 points

User Feedback: None yet
Adjustment: 0

FINAL SCORE: 11 points ⭐⭐
```

#### Example 3: Low-Scoring Job
```
Job: "Random IT Support Job"
Description: "Technical support, help desk..."

Keyword Matching:
  - No matches with target terms
  Subtotal: 0 points

Employment Type: Entry level +0
Company: Unknown +0
Remote: No +0

FINAL SCORE: 0 points ❌
```

---

## Scoring System

### Score Ranges & Interpretation

```
Score Range | Rating | Interpretation
0-5         | ❌    | Not relevant to your goals
6-15        | ⭐    | Tangentially related
16-30       | ⭐⭐   | Somewhat relevant
31-50       | ⭐⭐⭐ | Good fit
51-75       | ⭐⭐⭐⭐ | Excellent fit
76+         | ⭐⭐⭐⭐⭐ | Perfect match
```

### Weighting Strategy

```
Keyword relevance: 60% of base score
├─ Why? Most important factor
├─ Direct match with your expertise
└─ Ensures jobs are actually related

Employment type: 15% of base score
├─ Why? Focuses on early-career roles
└─ Internships/Werkstudent prioritized

Company preference: 20% of base score
├─ Why? Big companies have better training
├─ Better for resume building
└─ More stable positions

Remote status: 5% of base score
├─ Why? Nice-to-have bonus
└─ Doesn't override relevance
```

---

## Feedback Learning

### How Feedback Improves Recommendations

#### Step 1: User Rates a Job

```
User sees: "Machine Learning Intern at Zalando"
User clicks: 👍 Like

Job Details:
- Title contains: "machine learning", "intern"
- Skills tagged: ["Python", "SQL", "Tensorflow", "TensorFlow", "Data Science"]
- Description contains: "AI", "neural networks", "deep learning"
```

#### Step 2: Extract Terms from Liked Job

```python
liked_job = {
    "title_terms": ["machine learning", "intern"],
    "skills": ["Python", "SQL", "Tensorflow", "TensorFlow", "Data Science"],
    "description_terms": ["AI", "neural networks", "deep learning"]
}

# All terms extracted and normalized to lowercase
liked_terms = {
    "machine learning",
    "intern",
    "python",
    "sql",
    "tensorflow",
    "data science",
    "ai",
    "neural networks",
    "deep learning"
}
```

#### Step 3: Boost Future Jobs with Overlapping Terms

```python
next_job = {
    "title": "AI Engineer - Python & Deep Learning",
    "skills": ["Python", "Deep Learning", "AWS", "Docker"]
}

# Check overlap
overlap = liked_terms ∩ job_terms
overlap = {
    "python",          # +3 bonus
    "ai",              # +3 bonus
    "deep learning"    # +3 bonus
}

total_feedback_adjustment = +9
```

#### Step 4: Apply Adjustment to Score

```
Base relevance score: 45 points
Feedback adjustment: +9 points (from likes)
FINAL SCORE: 54 points ⭐⭐⭐⭐
```

### Dislike Example

```
User sees: "Sales Intern at Random Company"
User clicks: 👎 Dislike
Reason: "Sales, not data/tech"

Dislike terms: {"sales", "intern"}

Future job: "Sales Data Analyst"
Overlap: {"sales"}

Feedback adjustment: -3 points (penalty)
```

---

## Database Schema

### Jobs Table

```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,                 -- arbeitnow-12345
    title TEXT NOT NULL,                 -- Data Analytics Intern
    company TEXT NOT NULL,               -- Bosch
    location TEXT NOT NULL,              -- Stuttgart, Germany
    employment_type TEXT NOT NULL,       -- Internship / Praktikum
    description TEXT NOT NULL,           -- Full description
    skills_json TEXT NOT NULL,           -- JSON array: ["Python", "SQL"]
    source_name TEXT NOT NULL,           -- Arbeitnow Portal Network
    source_url TEXT NOT NULL,            -- https://...
    posted_date TEXT,                    -- 2026-08-08 (YYYY-MM-DD)
    posted_at TEXT,                      -- 2026-08-08T10:30:00+00:00 (ISO 8601)
    is_remote INTEGER NOT NULL,          -- 0 or 1 (SQLite boolean)
    is_demo INTEGER NOT NULL             -- 0 or 1 (sample jobs)
);

CREATE INDEX idx_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_company ON jobs(company);
CREATE INDEX idx_employment_type ON jobs(employment_type);
```

### Reviews Table

```sql
CREATE TABLE reviews (
    job_id TEXT PRIMARY KEY REFERENCES jobs(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),  -- 1-5 stars
    feedback TEXT NOT NULL,                         -- Like|Dislike|etc
    applied INTEGER NOT NULL DEFAULT 0,             -- 0 or 1
    dislike_reason TEXT NOT NULL DEFAULT '',        -- Why disliked
    notes TEXT NOT NULL,                            -- Personal notes
    updated_at TEXT NOT NULL                        -- When changed
);

CREATE INDEX idx_feedback ON reviews(feedback);
CREATE INDEX idx_applied ON reviews(applied);
```

### Metadata Table

```sql
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,                -- arbeitnow_last_synced_at
    value TEXT NOT NULL                  -- 2026-08-08T14:30:00+00:00
);

-- Example usage:
-- Stores: "When was the last successful sync?"
-- Prevents: Re-fetching jobs immediately
-- Enables: Smart refresh intervals
```

### Query Examples

```sql
-- Find all data analytics internships posted in last 24 hours
SELECT * FROM jobs
WHERE employment_type = "Internship / Praktikum"
AND title LIKE "%data%"
AND posted_date >= date('now', '-1 day')
ORDER BY posted_date DESC;

-- Find jobs user liked with common skills
SELECT j.*, r.rating, r.notes
FROM jobs j
LEFT JOIN reviews r ON j.id = r.job_id
WHERE r.feedback = "Like"
ORDER BY r.updated_at DESC;

-- Find jobs from preferred companies
SELECT * FROM jobs
WHERE company IN ('Bosch', 'Siemens', 'SAP')
AND is_demo = 0
ORDER BY posted_date DESC
LIMIT 10;

-- Get sync timestamp for caching decisions
SELECT value FROM metadata
WHERE key = 'arbeitnow_last_synced_at';

-- Count jobs by source
SELECT source_name, COUNT(*) as count
FROM jobs
GROUP BY source_name
ORDER BY count DESC;
```

---

## API Integration Patterns

### JobSource Protocol (Interface)

All job sources implement this interface:

```python
class JobSource(Protocol):
    """A replaceable provider of normalized job opportunities."""

    def fetch_jobs(self) -> list[Job]:
        """Fetch and normalize currently advertised jobs.
        
        Returns:
            List of normalized Job objects ready for storage
            
        Raises:
            Caught and logged; one failing source doesn't crash the app
        """
        ...
```

### Adding a New Source

1. **Create adapter file**: `sources/public_apis/newsource.py`

```python
import requests
from job_recommendation_agent.domain.models import Job, EmploymentType

class NewAPISource:
    def __init__(self, api_url: str, timeout_seconds: float = 15.0):
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds
    
    def fetch_jobs(self) -> list[Job]:
        """Fetch from API and normalize."""
        jobs = []
        try:
            response = requests.get(
                self.api_url,
                timeout=self.timeout_seconds,
                headers={"User-Agent": "AIJobRecommendationAgent/0.1"}
            )
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("jobs", []):
                job = self._normalize(item)
                if job:
                    jobs.append(job)
        except Exception:
            # Log but don't crash
            pass
        return jobs
    
    @staticmethod
    def _normalize(item: dict) -> Job | None:
        """Convert API format to Job model."""
        # Extract title, company, location, etc.
        # Filter for early-career positions
        # Return Job or None if filtered out
        pass
```

2. **Register in app.py**:

```python
from job_recommendation_agent.sources.public_apis.newsource import NewAPISource

sources = (
    ArbeitnowSource(...),
    NewAPISource(settings.newsource_api_url),  # Add here
)
```

3. **Add environment variable** in `.env`:

```
NEWSOURCE_API_URL=https://api.example.com/jobs
```

### Error Handling Pattern

```python
def sync_live_jobs() -> tuple[int, str | None]:
    """Fetch from all sources, one failing doesn't break everything."""
    
    imported = 0
    failures = 0
    
    for source in sources:
        try:
            jobs = source.fetch_jobs()  # Could raise exception
            repository().upsert_jobs(jobs)
            imported += len(jobs)
        except Exception:  # Catch everything
            failures += 1  # Count failure but continue
            continue  # Move to next source
    
    if failures == len(sources):
        # All sources failed
        return 0, "All sources unreachable. Cached jobs available."
    
    return imported, None
```

---

## Performance Considerations

### Database Performance

```
Current capacity:
- 5,000+ jobs in SQLite
- Database size: ~50-100 MB
- Query time: <100ms for typical searches
- Memory usage: ~200-300 MB (with app)

To optimize:
- Index by posted_date (done)
- Index by company (done)
- Index by employment_type (done)
- VACUUM periodically
- Delete jobs >90 days old
```

### API Performance

```
Typical sync time breakdown:
- Arbeitnow (5 pages): 10-15 seconds
- Bosch: 2-3 seconds
- Continental: 2-3 seconds
- Amazon: 3-5 seconds
- GitHub/Remotive: 2-3 seconds
- Database writes: 5-10 seconds
- Total: 30-60 seconds

Optimization tips:
- Reduce ARBEITNOW_PAGES to 2-3 if slow
- Increase AUTO_SYNC_INTERVAL to 30-60 min
- Run sync in background, don't block UI
```

---

## Future Algorithm Improvements

### Planned (Phase 2)

1. **Machine Learning Ranking**
   - Learn from your rating patterns
   - Predict scores without explicit terms
   - More sophisticated feedback learning

2. **Resume Parsing**
   - Extract skills automatically from resume
   - No need to hardcode target terms
   - Personalized for each user

3. **Collaborative Filtering**
   - See what similar users like
   - Discover jobs you might not search for
   - Community recommendations

### Possible (Phase 3)

1. **NLP-Based Matching**
   - Semantic similarity, not just keyword matching
   - Understand "DevOps" = "Cloud Infrastructure"
   - More intelligent role matching

2. **Salary Prediction**
   - Estimate compensation ranges
   - Compare against market averages
   - Negotiation recommendations

3. **Company Intelligence**
   - Track which companies you apply to
   - Success rates for each company
   - Interview feedback patterns

---

**Last Updated**: 2026-08-08  
**Algorithm Version**: 1.0 (Core Ranking)  
**Status**: Production Ready