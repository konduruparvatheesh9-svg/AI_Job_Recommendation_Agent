# AI Job Recommendation Agent - Automated Setup Script (PowerShell)
# This script automates the installation process on Windows

param(
    [switch]$SkipPythonCheck = $false
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Job Recommendation Agent - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking for Python 3.11+..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "[ERROR] Python 3.11+ is required (found $pythonVersion)" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        Write-Host "[OK] Found $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please download Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 1: Creating Virtual Environment..." -ForegroundColor Yellow

if (Test-Path ".venv") {
    Write-Host "[OK] Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Activating Virtual Environment..." -ForegroundColor Yellow

& .\.venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] Virtual environment activated" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow

python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] pip upgrade had issues, continuing anyway..." -ForegroundColor Yellow
} else {
    Write-Host "[OK] pip is up to date" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Installing Dependencies..." -ForegroundColor Yellow
Write-Host "This may take 2-5 minutes..." -ForegroundColor Gray

if (Test-Path "pyproject.toml") {
    python -m pip install -e . --quiet
} else {
    Write-Host "[INFO] Using requirements.txt" -ForegroundColor Cyan
    python -m pip install -r requirements.txt --quiet
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] All dependencies installed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Verifying Installation..." -ForegroundColor Yellow

python -c "import streamlit; import pandas; import pydantic; import requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Some dependencies may not be installed correctly" -ForegroundColor Yellow
} else {
    Write-Host "[OK] All required packages are available" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the Job Recommendation Portal:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  streamlit run src/job_recommendation_agent/ui/app.py" -ForegroundColor White
Write-Host ""
Write-Host "A browser window should open automatically at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "To activate the virtual environment in future sessions:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1  (PowerShell)" -ForegroundColor White
Write-Host "  .venv\Scripts\activate.bat  (Command Prompt)" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
