@echo off
REM AI Job Recommendation Agent - Automated Setup Script
REM This script automates the installation process on Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo AI Job Recommendation Agent - Setup
echo ========================================
echo.

REM Check if Python is installed
echo Checking for Python 3.11+...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo Please download Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

REM Check if it's Python 3.11+
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    echo [ERROR] Python 3.11+ is required (found %PYTHON_VERSION%)
    pause
    exit /b 1
)

if %MAJOR% EQU 3 if %MINOR% LSS 11 (
    echo [ERROR] Python 3.11+ is required (found %PYTHON_VERSION%)
    pause
    exit /b 1
)

echo.
echo Step 1: Creating Virtual Environment...
if exist .venv (
    echo [OK] Virtual environment already exists
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo Step 2: Activating Virtual Environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] pip upgrade had issues, continuing anyway...
)
echo [OK] pip is up to date

echo.
echo Step 4: Installing Dependencies...
echo This may take 2-5 minutes...
if exist pyproject.toml (
    python -m pip install -e . --quiet
) else (
    echo [INFO] Using requirements.txt
    python -m pip install -r requirements.txt --quiet
)
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] All dependencies installed successfully

echo.
echo Step 5: Verifying Installation...
python -c "import streamlit; import pandas; import pydantic; import requests" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Some dependencies may not be installed correctly
) else (
    echo [OK] All required packages are available
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the Job Recommendation Portal:
echo.
echo   streamlit run src/job_recommendation_agent/ui/app.py
echo.
echo A browser window should open automatically at:
echo   http://localhost:8501
echo.
echo To activate the virtual environment in future sessions:
echo   .venv\Scripts\Activate.ps1  (PowerShell)
echo   .venv\Scripts\activate.bat  (Command Prompt)
echo.
pause
