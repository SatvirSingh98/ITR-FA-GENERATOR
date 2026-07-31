@echo off
REM Schedule FA Generator - Auto Setup Check + Run

echo ================================================================
echo   Schedule FA Generator - Auto-Discovery Mode
echo ================================================================
echo.

REM ============================================================
REM STEP 1: PRE-FLIGHT CHECKS
REM ============================================================

echo [1/5] Checking config.json...
if not exist config.json (
    if exist config.example.json (
        echo   [i] First run detected - creating config.json from example...
        copy config.example.json config.json >nul
        echo   [OK] Created config.json
        echo   [!] IMPORTANT: Edit config.json with your account details if needed
        echo.
    ) else (
        echo   [ERROR] config.json not found!
        echo   [i] Copy config.example.json to config.json and edit it
        echo.
        pause
        exit /b 1
    )
)

python -c "import json; json.load(open('config.json'))" 2>nul
if errorlevel 1 (
    echo   [ERROR] config.json has invalid JSON syntax
    echo.
    pause
    exit /b 1
)

REM Account number is optional - will be extracted from ClientStatement PDF
echo   [OK] Config is valid
echo.

echo [2/5] Checking inputs folder...
if not exist inputs\ (
    echo   [i] Creating inputs folder...
    mkdir inputs
)
if not exist inputs\ByStatus_expanded.xlsx (
    echo   [WARNING] ByStatus_expanded.xlsx not found in inputs/
    echo   [i] Export from E*TRADE and place in inputs/ folder
    echo.
    pause
    exit /b 1
)
if not exist inputs\G^&L_Expanded.xlsx (
    echo   [i] G^&L_Expanded.xlsx not found - this is OK
    echo   [i] This file is only needed if you sold stocks in this FY
)
echo   [OK] E*TRADE files found
echo.

echo [3/5] Checking outputs folder...
if not exist outputs\ (
    echo   [i] Creating outputs folder...
    mkdir outputs
) else (
    echo   [i] Cleaning previous outputs...
    del /Q outputs\* >nul 2>&1
)
echo   [OK] Outputs folder ready
echo.

echo [4/5] Checking Python environment...

REM Check if venv exists
if not exist venv\Scripts\python.exe (
    REM Check if Python is available
    python --version >nul 2>&1
    if errorlevel 1 (
        echo   [ERROR] Python not found on system!
        echo   Please install Python 3.11+ from python.org
        echo   Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )

    REM Check Python version
    python -c "import sys; exit(0 if (sys.version_info.major == 3 and sys.version_info.minor >= 11) or sys.version_info.major > 3 else 1)" 2>nul
    if errorlevel 1 (
        for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
        echo   [ERROR] Python is too old - requires 3.11+
        echo   Download from: https://python.org/downloads/
        pause
        exit /b 1
    )

    REM Create venv
    echo   [i] Creating Python environment - first run only...
    python -m venv venv
    if errorlevel 1 (
        echo   [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

REM Check if packages are installed
venv\Scripts\python.exe -c "import pandas, selenium, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo   [i] First-time setup detected - installing packages...
    echo   [i] This may take 2-5 minutes, please wait...
    echo.

    REM Upgrade pip
    venv\Scripts\python.exe -m pip install --upgrade pip --quiet

    REM Install packages
    venv\Scripts\python.exe -m pip install -r requirements.txt

    if errorlevel 1 (
        echo   [ERROR] Package installation failed!
        echo   [i] Check your internet connection and try again.
        echo.
        pause
        exit /b 1
    )

    echo   [OK] Packages installed successfully
    echo.
)
echo   [OK] Python environment ready
echo.

echo [5/5] Pre-flight checks complete!
echo.
echo ================================================================

REM ============================================================
REM STEP 2: RUN GENERATOR
REM ============================================================

echo.
echo What will happen:
echo   - Read E*TRADE files from inputs/
echo   - Auto-discover company symbols
echo   - Fetch company details from Yahoo Finance
echo   - Auto-detect countries (USA, Canada, UK, etc.)
echo   - Scrape stock prices for full year
echo   - Download SBI TTBR exchange rates
echo   - Generate 4 output files in outputs/
echo.
echo This will take 1-2 minutes (web scraping)
echo Chrome browser will open in background
echo.

echo [*] Starting Schedule FA generation...
venv\Scripts\python.exe itr_fa_engine.py > output_summary.txt 2>&1

if errorlevel 1 (
    echo.
    echo [ERROR] Script failed! Check output_summary.txt for details.
    echo.
    pause
    exit /b 1
)

echo [OK] Script completed. Output saved to output_summary.txt

REM ============================================================
REM STEP 3: SUCCESS
REM ============================================================

echo.
echo ================================================================
echo   SUCCESS! Schedule FA Generated
echo ================================================================
echo.
echo Check the outputs/ folder for:
echo   - schedule_fa_2025-26.json  (Review with CA)
echo   - schedule_fa_2025-26.xlsx  (Review with CA)
echo   - schedule_fa_2025-26_table_a2.csv  (Upload to ITR portal)
echo   - schedule_fa_2025-26_table_a3.csv  (Upload to ITR portal)
echo.
echo Next steps:
echo   1. Review Excel file for accuracy
echo   2. Share with your CA for verification
echo   3. Upload CSV to ITR e-filing portal
echo.
echo ================================================================
echo   Logged output_summary.txt
echo ================================================================
echo.
pause