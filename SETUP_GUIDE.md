# 📚 Installation & Setup Guide

Complete step-by-step guide for installing and running the AI Job Recommendation Agent.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start (Automated)](#quick-start-automated)
- [Manual Setup (Step-by-Step)](#manual-setup-step-by-step)
- [Configuration](#configuration)
- [First Launch](#first-launch)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+) |
| **Python** | 3.11 or higher |
| **RAM** | 2 GB minimum |
| **Disk Space** | 500 MB for virtual environment + 100 MB for database |
| **Internet** | Required for initial setup and job syncing |

### Recommended Specifications

| Component | Recommendation |
|-----------|-----------------|
| **OS** | Windows 10/11, macOS 12+, or Ubuntu 20.04+ |
| **Python** | 3.12 or 3.13 (latest) |
| **RAM** | 4 GB or more |
| **Disk Space** | 1 GB total |
| **Internet** | Fast connection (10 Mbps+) |

### Check Python Installation

```powershell
python --version
# Should output: Python 3.11.x or higher

# If not found, try:
py --version
py -3.11 --version
```

---

## Quick Start (Automated)

### For Windows Users

#### Using Batch Script (Easiest)

1. **Download the repository**
   - Click `<> Code` button (green)
   - Select `Download ZIP`
   - Extract to your desired location

2. **Run setup.bat**
   - Navigate to the extracted folder
   - Double-click `setup.bat`
   - **Do NOT close** the terminal until complete
   - Should take 2-5 minutes

3. **Launch the portal**
   ```powershell
   streamlit run src/job_recommendation_agent/ui/app.py
   ```

#### Using PowerShell Script

1. Extract repository as above

2. Run PowerShell script
   ```powershell
   # Open PowerShell in the repository folder
   .\setup.ps1
   ```
   
   If you get permission error:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\setup.ps1
   ```

3. Launch portal (same as above)

### For macOS/Linux Users

1. **Install Homebrew** (macOS only)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3.11+**
   ```bash
   # macOS
   brew install python@3.11
   
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3.11 python3.11-venv python3.11-dev
   ```

3. **Clone and setup repository**
   ```bash
   git clone https://github.com/your-username/ai-job-recommendation-agent.git
   cd ai-job-recommendation-agent
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```

4. **Launch**
   ```bash
   streamlit run src/job_recommendation_agent/ui/app.py
   ```

---

## Manual Setup (Step-by-Step)

### Step 1: Verify Python Installation

```powershell
python --version
# Expected output: Python 3.11.0 or higher
# If you see Python 2.x, you need Python 3.11+
```

If Python is not installed or version is wrong:
- Download from [python.org](https://www.python.org/downloads/)
- Run installer
- **✅ CHECK "Add Python to PATH"** during installation
- **✅ CHECK "Install pip"**
- Restart your computer

### Step 2: Download/Clone Repository

#### Option A: Using Git (Recommended)

```powershell
git clone https://github.com/your-username/ai-job-recommendation-agent.git
cd ai-job-recommendation-agent
```

**Don't have Git?**
- Download from [git-scm.com](https://git-scm.com/)
- Run installer with default options

#### Option B: Download ZIP

1. Go to GitHub repository
2. Click `<> Code` → `Download ZIP`
3. Extract ZIP file
4. Open PowerShell in extracted folder

### Step 3: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1
```

**Common Error**: "running scripts is disabled on this system"

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then run:
.venv\Scripts\Activate.ps1
```

**Signs of successful activation**:
- Command prompt changes to: `(.venv) C:\path\to\project>`
- Or in PowerShell: `(.venv) PS C:\path\to\project>`

### Step 4: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

You should see output like:
```
Successfully installed pip-24.x.x
```

### Step 5: Install Dependencies

#### Full Installation (Recommended for developers)

```powershell
python -m pip install -e ".[dev]"
```

This installs:
- Core: pandas, streamlit, pydantic, requests
- Dev tools: mypy, pytest, ruff (for quality checks)

#### Minimal Installation (Users only)

```powershell
python -m pip install -r requirements.txt
```

This installs only:
- pandas, streamlit, pydantic, requests

### Step 6: Configure Environment

```powershell
# Copy example configuration
Copy-Item .env.example .env

# (Optional) Edit configuration
notepad .env
```

**Edit `.env` if you want to**:
- Change database location
- Adjust API timeouts
- Modify sync intervals
- Use different sources

### Step 7: Verify Installation

```powershell
# Check all packages installed
python -c "import streamlit; import pandas; import pydantic; import requests; print('✓ All packages installed successfully')"
```

Expected output:
```
✓ All packages installed successfully
```

### Step 8: Launch Portal

```powershell
streamlit run src/job_recommendation_agent/ui/app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

✅ **A browser window should open automatically!**

---

## Configuration

### Environment File (.env)

Edit `.env` to customize behavior:

```bash
# === Application Environment ===
APP_ENV=development
# Options: development, test, production
# development = detailed logs, relaxed constraints
# production = minimal logs, strict validation

# === Database ===
DATABASE_PATH=data/jobs.db
# Location where SQLite database is stored
# Change if you want different location
# (must have write permissions)

# === Logging ===
LOG_LEVEL=INFO
# Options: DEBUG (very verbose), INFO, WARNING, ERROR, CRITICAL
# DEBUG shows every API call and database operation

# === API Performance ===
REQUEST_TIMEOUT_SECONDS=15.0
# How long to wait for API response (seconds)
# Increase to 30 if getting timeouts
# Decrease to 5 for faster (but may fail on slow APIs)
# Range: 5-60 seconds

# === Arbeitnow Portal ===
ARBEITNOW_API_URL=https://www.arbeitnow.com/api/job-board-api
# URL of Arbeitnow job board (usually don't change)

ARBEITNOW_PAGES=5
# How many pages to fetch from Arbeitnow
# Each page = ~20-30 jobs
# 1 page = fast but fewer jobs
# 10 pages = slow but comprehensive
# Recommended: 3-5

# === Company API URLs ===
BOSCH_API_URL=https://api.smartrecruiters.com/v1/companies/BoschGroup/postings
CONTINENTAL_API_URL=https://api.smartrecruiters.com/v1/companies/Continental/postings
AMAZON_JOBS_API_URL=https://www.amazon.jobs/en/search.json
# Official company APIs (usually don't change)
```

### Common Configuration Scenarios

#### Scenario 1: Fast, Minimal Setup
```bash
ARBEITNOW_PAGES=2           # Fewer jobs but fast
REQUEST_TIMEOUT_SECONDS=10  # Faster timeout
LOG_LEVEL=WARNING           # Less noise
```

#### Scenario 2: Comprehensive, Thorough
```bash
ARBEITNOW_PAGES=10          # All jobs
REQUEST_TIMEOUT_SECONDS=30  # More patience for slow APIs
LOG_LEVEL=DEBUG             # See everything
```

#### Scenario 3: Production/Stable
```bash
ARBEITNOW_PAGES=5           # Balanced
REQUEST_TIMEOUT_SECONDS=20  # Reasonable
LOG_LEVEL=INFO              # Standard logging
DATABASE_PATH=/data/jobs.db # Custom location
```

---

## First Launch

### What Happens Automatically

1. **Database Creation** (~1 second)
   ```
   ✓ Created data/jobs.db
   ✓ Created tables: jobs, reviews, metadata
   ✓ Database ready for data
   ```

2. **Demo Data Insertion** (~0.5 seconds)
   ```
   ✓ Inserted 3 demo jobs
   ✓ Clearly marked as [DEMO]
   ✓ Fallback data if sync fails
   ```

3. **Initial Sync** (~30-60 seconds)
   - Fetches from all sources:
     - Arbeitnow Portal (10-15 sec)
     - Bosch Careers (2-3 sec)
     - Continental Careers (2-3 sec)
     - Amazon Jobs (3-5 sec)
     - GitHub/Remotive (2-3 sec)
   - Normalizes all jobs
   - Stores in local database

4. **Portal Ready**
   ```
   ✓ Sync complete: X jobs imported
   ✓ Portal ready at http://localhost:8501
   ```

### First Actions in Portal

1. **View Demo Jobs**
   - Should see 3 sample jobs
   - Try clicking them
   - Check the interface

2. **Refresh Live Jobs**
   - Click "🔄 Refresh live jobs" button
   - Wait 30-60 seconds
   - See real job listings appear

3. **Rate a Job**
   - Click "👍 Like" on any job
   - Portal learns your preferences
   - Recommendations improve

4. **Check Sync Status**
   - Look for timestamp at bottom
   - Shows when data was last updated
   - Usually updates every 15 minutes

---

## Verification

### Quick Verification

```powershell
# 1. Check Python version
python --version
# Should show: Python 3.11.x or higher

# 2. Check packages
python -c "
import streamlit
import pandas
import pydantic
import requests
print('✓ All core packages OK')
"

# 3. Check database
# When app runs, should create data/jobs.db
dir data
# Should show: jobs.db exists
```

### Running Tests (Developers)

```powershell
# Activate environment first
.venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run specific test
pytest tests/unit/test_ranking.py

# See coverage
pytest --cov=job_recommendation_agent
```

### Checking Installation Completeness

Checklist:
- [ ] Python 3.11+ installed
- [ ] Virtual environment created (.venv folder exists)
- [ ] Virtual environment activated (prompt shows `.venv`)
- [ ] pip upgraded
- [ ] Dependencies installed (pip list shows streamlit, pandas, etc.)
- [ ] .env file created
- [ ] Portal starts without errors
- [ ] Database created (data/jobs.db exists)
- [ ] Can refresh live jobs
- [ ] Can rate jobs
- [ ] Can add notes

---

## Troubleshooting

### Installation Troubleshooting

#### "Python command not found"

**Error**:
```
'python' is not recognized as an internal or external command
```

**Solutions**:
1. Check if Python is installed: `py --version`
2. If not installed:
   - Download from [python.org](https://www.python.org/downloads/)
   - Run installer with "Add Python to PATH" ✅ checked
   - Restart computer
3. Use `py` instead of `python`:
   ```powershell
   py -3.11 -m venv .venv
   py -m pip install -e ".[dev]"
   ```

#### Virtual Environment Won't Activate

**Error**:
```
PowerShell: running scripts is disabled on this system
Command Prompt: (no error, but .venv not activated)
```

**Solution for PowerShell**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

**Solution for Command Prompt**:
```cmd
.venv\Scripts\activate.bat
```

#### pip install Fails

**Error**:
```
ERROR: Could not install packages due to EnvironmentError: [WinError 5] Access is denied
```

**Solution**:
1. Make sure virtual environment is activated
2. Make sure you have write permission to folder
3. Try upgrading pip first: `python -m pip install --upgrade pip`
4. Try install again

#### "No module named 'streamlit'"

**Error**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**Causes**:
1. Virtual environment not activated
2. Dependencies not installed
3. Using wrong Python version

**Solution**:
```powershell
# Check activation
# Should see (.venv) in prompt

# Reinstall
python -m pip install streamlit pandas pydantic requests
```

### Runtime Troubleshooting

#### Portal Doesn't Start

**Error**:
```
Address already in use
```

**Solution**:
```powershell
# Use different port
streamlit run src/job_recommendation_agent/ui/app.py --server.port 8502

# Or kill process on 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### No Jobs Appearing

**Checklist**:
1. ✓ Click "🔄 Refresh live jobs"
2. ✓ Wait 30-60 seconds
3. ✓ Check internet connection
4. ✓ Look for error messages in terminal
5. ✓ Check if demo jobs appear (blue [DEMO] tag)

**If still empty**:
```powershell
# Check database
sqlite3 data/jobs.db "SELECT COUNT(*) FROM jobs;"

# Check logs (in terminal output)
# Look for error messages

# Rebuild database
rm data/jobs.db
# Rerun app to recreate
```

#### API Timeouts

**Error**:
```
requests.exceptions.Timeout: Connection timeout
```

**Solutions**:
1. Increase timeout in .env:
   ```
   REQUEST_TIMEOUT_SECONDS=30.0  # was 15.0
   ```

2. Check internet connection
3. Try again later (APIs may be rate-limited)
4. Reduce ARBEITNOW_PAGES to 2-3

#### Slow Performance

**Symptoms**:
- Portal takes 10+ seconds to load
- Rating jobs is slow
- Syncing takes >2 minutes

**Solutions**:
1. Reduce ARBEITNOW_PAGES: `ARBEITNOW_PAGES=2`
2. Reduce jobs in database:
   ```powershell
   sqlite3 data/jobs.db
   > DELETE FROM jobs WHERE posted_date < date('now', '-30 days');
   > VACUUM;
   ```
3. Increase sync interval to 60 minutes
4. Close other programs

#### Database Locked

**Error**:
```
sqlite3.OperationalError: database is locked
```

**Causes**:
- Two instances of app running
- Database corrupted

**Solutions**:
1. Close portal completely
2. Check for duplicate terminal windows
3. Delete database and rebuild:
   ```powershell
   rm data/jobs.db
   # Rerun app
   ```

### Getting More Help

1. **Check logs**: Terminal shows detailed messages
2. **Review files**:
   - README.md - Full documentation
   - ARCHITECTURE_NOTES.md - Algorithm details
   - DOWNLOAD_AND_RUN.md - Quick start
3. **Common issues**:
   - Python version too old (need 3.11+)
   - Virtual environment not activated
   - Port already in use
   - Internet connection lost

---

## Uninstallation

### Remove Portal (Keep Data)

```powershell
# Deactivate virtual environment
deactivate

# Delete virtual environment
rm -r .venv
```

Portal is now removed. All your data remains in `data/jobs.db`.

### Complete Removal (With Data)

```powershell
# Deactivate
deactivate

# Delete everything
rm -r .venv
rm -r data
rm .env
```

**Note**: This is permanent. Backup important data first.

### Reinstall (Fresh Start)

```powershell
# Remove old installation
rm -r .venv
rm data/jobs.db

# Reinstall
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Run
streamlit run src/job_recommendation_agent/ui/app.py
```

---

## What's Next?

- 📖 Read [README.md](README.md) for full features
- 🧠 Check [ARCHITECTURE_NOTES.md](ARCHITECTURE_NOTES.md) for algorithm details
- 🚀 Try [DOWNLOAD_AND_RUN.md](DOWNLOAD_AND_RUN.md) for quick start
- 💻 Start developing: Read [Development](#development) in README

---

**Version**: 0.1.0  
**Last Updated**: 2026-08-08  
**Status**: Actively Maintained  
**Support**: GitHub Issues & Discussions

### Prerequisites

- **Python 3.11 or higher** (download from [python.org](https://www.python.org/downloads/))
- **Git** (download from [git-scm.com](https://git-scm.com/))
- A text editor or IDE (VS Code recommended)

### Step-by-Step Installation

#### 1. Clone or Download the Repository

```powershell
# Clone the repository
git clone https://github.com/your-username/ai-job-recommendation-agent.git
cd ai-job-recommendation-agent
```

Or download as ZIP and extract.

#### 2. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install project with dependencies
python -m pip install -e ".[dev]"
```

This installs:
- Core dependencies: pandas, pydantic, requests, streamlit
- Development tools: mypy, pytest, ruff (for code quality)

#### 4. Configuration

```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env with your settings (optional)
notepad .env
```

#### 5. Verify Installation

```powershell
# Run quality checks
ruff check .
ruff format --check .
mypy src tests
pytest
```

#### 6. Launch the Portal

```powershell
streamlit run src/job_recommendation_agent/ui/app.py
```

The app will open at `http://localhost:8501`

---

## Alternative: Use requirements.txt

If you prefer a simpler installation without the dev tools:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run src/job_recommendation_agent/ui/app.py
```

---

## What Happens on First Run?

1. **Database Creation**: `data/jobs.db` is automatically created
2. **Demo Data**: 3 sample jobs are inserted as fallback data
3. **Live Sync**: Click "🔄 Refresh live jobs" to fetch real positions from:
   - Arbeitnow (Public API)
   - Bosch Career Portal
   - Continental Career Portal
   - Amazon Jobs API
   - GitHub & Remotive Jobs

---

## Supported Job Types

- Internships (Praktikum)
- Working Student (Werkstudent)
- Graduate Programs
- Thesis/Final Project Positions
- Entry-Level Roles

**Focused Industries:**
- Quality Management / Industrial Manufacturing
- Data Analysis / Data Science
- IT Infrastructure / Cloud & DevOps

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.11 or higher |
| RAM | Minimum 2GB (4GB+ recommended) |
| Disk Space | ~500MB for virtual environment |
| Internet | Required for live job fetching |
| OS | Windows 10+, macOS 10.14+, Linux |

---

## Troubleshooting

### Python Not Found
```powershell
# Check Python installation
python --version

# If not recognized, add to PATH or use:
py -3.11 --version
py -3.11 -m venv .venv
```

### Virtual Environment Not Activating
```powershell
# For PowerShell, you may need to change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.venv\Scripts\Activate.ps1
```

### Port 8501 Already in Use
```powershell
streamlit run src/job_recommendation_agent/ui/app.py --server.port 8502
```

### API Connection Errors
- Check your internet connection
- Verify APIs are not rate-limited (some limit to 50-100 requests/hour)
- Jobs are cached locally, so you can still browse cached data

---

## Project Structure

```
ai-job-recommendation-agent/
├── src/job_recommendation_agent/
│   ├── domain/           # Job models & data structures
│   ├── matching/         # Ranking & recommendation logic
│   ├── persistence/      # Database (SQLite)
│   ├── services/         # Demo data & utilities
│   ├── sources/          # Job fetchers from multiple APIs
│   └── ui/               # Streamlit web interface
├── tests/                # Unit & integration tests
├── data/                 # Jobs database (auto-created)
├── pyproject.toml        # Project configuration
├── README.md             # Project overview
└── SETUP_GUIDE.md        # This file
```

---

## Next Steps After Setup

1. **Configure Resume/CV**: The agent filters jobs based on your profile
2. **Adjust Filters**: Set preferred companies and job types
3. **Sync Jobs**: Click "Refresh live jobs" regularly
4. **Rate Jobs**: Mark jobs as "Like", "Dislike", or "Applied"
5. **Export Data**: View application history and ratings

---

## Development & Contributing

To contribute to this project:

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Make changes to code
# Run quality checks before committing
ruff check .
ruff format .
mypy src tests
pytest

# Commit with Git
git add .
git commit -m "Your changes"
git push origin main
```

---

## Support & Issues

- Report bugs on GitHub Issues
- Check FAQ in README.md
- Review logs in the terminal output

---

**Version**: 0.1.0  
**License**: MIT  
**Last Updated**: 2026-08-08
