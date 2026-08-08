# 📋 Quick Reference Guide

Fast lookup guide for common tasks and commands.

## Installation Commands

### Windows - Automated (Easiest)
```powershell
# Double-click setup.bat
# OR in PowerShell:
.\setup.ps1
```

### Windows - Manual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### macOS/Linux
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Running the Application

### Launch Portal
```powershell
.venv\Scripts\Activate.ps1
streamlit run src/job_recommendation_agent/ui/app.py
```

### Access URL
```
http://localhost:8501
```

### Use Different Port
```powershell
streamlit run src/job_recommendation_agent/ui/app.py --server.port 8502
```

---

## Development Commands

### Run Quality Checks
```powershell
ruff check .              # Linting
ruff format .             # Auto-format
mypy src tests            # Type checking
pytest                    # Run tests
pytest --cov              # Test coverage
```

### Test Specific File
```powershell
pytest tests/unit/test_ranking.py -v
```

### Database Cleanup
```powershell
sqlite3 data/jobs.db "DELETE FROM jobs WHERE posted_date < date('now', '-60 days');"
sqlite3 data/jobs.db "VACUUM;"
```

---

## Configuration

### Environment Variables (.env)
```bash
REQUEST_TIMEOUT_SECONDS=15.0    # API timeout
ARBEITNOW_PAGES=5               # Pages to fetch
DATABASE_PATH=data/jobs.db      # Database location
LOG_LEVEL=INFO                  # Logging level
```

### Job Sync Interval (in app.py)
```python
AUTO_SYNC_INTERVAL = timedelta(minutes=15)  # Check every 15 min
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| "Python not found" | Install Python 3.11+, add to PATH |
| Virtual env won't activate | Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Port 8501 in use | Use `--server.port 8502` |
| API timeouts | Increase `REQUEST_TIMEOUT_SECONDS` in .env |
| Jobs not loading | Click "Refresh live jobs", wait 60 sec |
| Slow portal | Reduce `ARBEITNOW_PAGES`, delete old jobs |

---

## File Structure

```
project/
├── README.md              # Full documentation (START HERE!)
├── SETUP_GUIDE.md         # Detailed installation
├── DOWNLOAD_AND_RUN.md    # Quick start guide
├── ARCHITECTURE_NOTES.md  # Algorithm details
├── QUICK_REFERENCE.md     # This file
│
├── setup.bat              # Windows automated setup
├── setup.ps1              # PowerShell automated setup
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project config
│
├── src/job_recommendation_agent/
│   ├── app.py             # Streamlit UI
│   ├── config.py          # Settings
│   ├── ranking.py         # Scoring algorithm ⭐
│   ├── sqlite_repository.py  # Database
│   ├── models.py          # Data structures
│   └── sources/           # Job fetchers
│       ├── amazon.py      # Amazon API
│       ├── bosch.py       # Bosch API
│       ├── arbeitnow.py   # Arbeitnow API
│       └── github.py      # GitHub/Remotive API ✨ NEW
│
├── tests/                 # Unit & integration tests
└── data/
    └── jobs.db            # SQLite database (auto-created)
```

---

## Scoring Algorithm (Quick Reference)

```
Job Score = Keywords + Employment Type + Company + Remote + User Feedback

Keywords:          0-100+ points (search target terms)
Employment Type:   +0 to +8 (Internship/Werkstudent boost)
Company Tier 1:    +15 (Bosch, VW, Siemens)
Company Tier 2:    +10 (SAP, TeamViewer)
Company Tier 3:    +5 (Amazon, Microsoft)
Remote:            +1 (remote work)
User Likes:        +3 per matching term
User Dislikes:     -3 per matching term

Result:
0-5 pts    = Not relevant
6-30 pts   = Somewhat relevant
31-50 pts  = Good fit
51-75 pts  = Excellent fit
76+ pts    = Perfect match
```

---

## Job Sources

| Source | API | Update | Coverage |
|--------|-----|--------|----------|
| Arbeitnow | Public | Real-time | Germany |
| Bosch | SmartRecruiters | Real-time | Bosch Group |
| Continental | SmartRecruiters | Real-time | Continental AG |
| Amazon | Official | Real-time | EMEA |
| GitHub/Remotive | Public | Real-time | Global (tech) |
| LinkedIn | Manual | Manual | Global |

---

## Keyboard Shortcuts

### In PowerShell
| Action | Command |
|--------|---------|
| Activate venv | `.venv\Scripts\Activate.ps1` |
| Exit venv | `deactivate` |
| Clear screen | `cls` |
| List files | `ls` or `dir` |
| Navigate | `cd path` |

### In Streamlit
| Action | Method |
|--------|--------|
| Refresh | Press `R` key |
| Rerun | Press `C` key |
| Menu | Press `X` key (top-right) |

---

## Environment Checklist

Before running:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Virtual env created (`.venv` folder exists)
- [ ] Virtual env activated (prompt shows `.venv`)
- [ ] Dependencies installed (`pip list`)
- [ ] `.env` file exists (copy from `.env.example`)
- [ ] Database path accessible
- [ ] Internet connected
- [ ] Port 8501 available

---

## Database Queries

### Check job count
```sql
SELECT COUNT(*) FROM jobs;
```

### Find jobs by company
```sql
SELECT title, company FROM jobs WHERE company LIKE 'Bosch%';
```

### Get user ratings
```sql
SELECT job_id, feedback, rating FROM reviews;
```

### Delete old jobs
```sql
DELETE FROM jobs WHERE posted_date < date('now', '-60 days');
```

### Check database size
```powershell
# Windows
dir data/jobs.db
ls -l data/jobs.db  # Linux/Mac
```

---

## Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| **README.md** | Full project docs | Everyone (START HERE) |
| **SETUP_GUIDE.md** | Installation guide | Users installing |
| **DOWNLOAD_AND_RUN.md** | Quick start | Non-technical users |
| **ARCHITECTURE_NOTES.md** | Algorithm details | Developers |
| **QUICK_REFERENCE.md** | This guide | Quick lookup |

---

## API Rate Limits

| API | Limit | Window |
|-----|-------|--------|
| Arbeitnow | 50 req | 1 minute |
| Amazon | 100 req | 1 minute |
| Bosch/Continental | 200 req | 1 minute |
| GitHub/Remotive | Unlimited | N/A |

---

## Performance Tuning

### Faster Sync
```bash
ARBEITNOW_PAGES=2           # Fewer jobs
REQUEST_TIMEOUT_SECONDS=10  # Shorter timeout
```

### More Jobs
```bash
ARBEITNOW_PAGES=10          # All available
REQUEST_TIMEOUT_SECONDS=30  # More patience
```

### Balanced (Default)
```bash
ARBEITNOW_PAGES=5
REQUEST_TIMEOUT_SECONDS=15
```

---

## Version Info

- **App Version**: 0.1.0
- **Python Required**: 3.11+
- **Streamlit**: 1.36+
- **Status**: Production Ready
- **Last Updated**: 2026-08-08

---

## Getting Help

| Issue | Resource |
|-------|----------|
| Installation | SETUP_GUIDE.md → Troubleshooting |
| How it works | ARCHITECTURE_NOTES.md |
| Quick start | DOWNLOAD_AND_RUN.md |
| Full docs | README.md |
| Code errors | Terminal output, GitHub Issues |

---

## Common Tasks

### Change database location
Edit `.env`:
```bash
DATABASE_PATH=/path/to/jobs.db
```

### Use different Python
```powershell
py -3.12 -m venv .venv
```

### Debug app
```powershell
streamlit run src/job_recommendation_agent/ui/app.py --logger.level=debug
```

### Export data
```powershell
sqlite3 data/jobs.db ".dump" > backup.sql
```

### Restore data
```powershell
sqlite3 data/jobs.db < backup.sql
```

---

**Need more help? See README.md or SETUP_GUIDE.md**