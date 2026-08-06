@echo off
setlocal EnableDelayedExpansion
REM ================================================================
REM ITR-FA-GENERATOR - Schedule FA Generator for ITR2
REM Copyright (C) 2025 Satvir Singh
REM
REM This program is free software: you can redistribute it and/or modify
REM it under the terms of the GNU General Public License as published by
REM the Free Software Foundation, either version 3 of the License, or
REM (at your option) any later version.
REM
REM This program is distributed in the hope that it will be useful,
REM but WITHOUT ANY WARRANTY; without even the implied warranty of
REM MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
REM GNU General Public License for more details.
REM
REM You should have received a copy of the GNU General Public License
REM along with this program. If not, see https://www.gnu.org/licenses/
REM ================================================================

echo ================================================================
echo   ITR-FA-GENERATOR - Schedule FA Generator for ITR2
echo   Copyright (C) 2025 Satvir Singh
echo   Licensed under GPL-3.0
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

REM Validate JSON syntax only if Python is available (full check happens later)
python --version >nul 2>&1
if not errorlevel 1 (
    python -c "import json; json.load(open('config.json'))" 2>nul
    if errorlevel 1 (
        echo   [ERROR] config.json has invalid JSON syntax
        echo.
        pause
        exit /b 1
    )
    echo   [OK] Config is valid
) else (
    echo   [OK] Config exists (will validate after Python setup)
)
echo.

echo [2/5] Checking E*TRADE inputs folder...
if not exist etrade_inputs\ (
    echo   [i] Creating etrade_inputs folder...
    mkdir etrade_inputs
)
echo   [i] Inputs folder ready
echo.

echo [3/5] Checking E*TRADE outputs folder...
if not exist etrade_outputs\ (
    echo   [i] Creating etrade_outputs folder...
    mkdir etrade_outputs
) else (
    echo   [i] Cleaning previous etrade_outputs...
    del /Q etrade_outputs\* >nul 2>&1
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

REM Always ensure packages from requirements.txt are installed/updated
REM Use pip install with --quiet to skip if already satisfied
echo   [i] Checking packages from requirements.txt...
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo   [ERROR] Package installation failed!
    echo   [i] Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo   [OK] Python environment ready
echo.

echo [5/5] Checking E*TRADE input files (uses Python for reliable detection^)...

REM Check all three files
venv\Scripts\python.exe -c "import os, glob, sys; b=os.path.exists('etrade_inputs/ByStatus_expanded.xlsx'); g=os.path.exists('etrade_inputs/G&L_Expanded.xlsx'); p=bool(glob.glob('etrade_inputs/ClientStatements_*.pdf')); print(f'{int(b)}{int(g)}{int(p)}')" > %TEMP%\file_check.txt 2>nul
set /p FILE_STATUS=<%TEMP%\file_check.txt
del %TEMP%\file_check.txt

REM Parse results (format: ByStatus G&L PDF, e.g., "111" = all present)
if "%FILE_STATUS%"=="000" (
    echo.
    echo   ======================================================================
    echo   [ERROR] No E*TRADE files found!
    echo.
    echo   Required files (at least one^):
    echo     - etrade_inputs/ByStatus_expanded.xlsx
    echo     - etrade_inputs/G^&L_Expanded.xlsx
    echo     - etrade_inputs/ClientStatements_*.pdf
    echo.
    echo   Please export files from E*TRADE and place in etrade_inputs/ folder
    echo   ======================================================================
    echo.
    pause
    exit /b 1
)

REM Show what's found and what's missing with warnings
echo.
if "%FILE_STATUS:~0,1%"=="1" (
    echo   [OK] ByStatus_expanded.xlsx found
) else (
    echo   [WARNING] ByStatus_expanded.xlsx NOT found
    echo             Table A3 will be EMPTY (no holdings to report^)
)

if "%FILE_STATUS:~1,1%"=="1" (
    echo   [OK] G^&L_Expanded.xlsx found
) else (
    echo   [WARNING] G^&L_Expanded.xlsx NOT found
    echo             Table A3 will be INCOMPLETE (missing sold shares^)
    echo             Capital Gains will be EMPTY (no sales to report^)
)

if "%FILE_STATUS:~2,1%"=="1" (
    echo   [OK] ClientStatements_*.pdf found
) else (
    echo   [WARNING] ClientStatements_*.pdf NOT found
    echo             Table A2 closing balance will be 0
)
echo.

REM Only pause if any file is missing
if not "%FILE_STATUS%"=="111" (
    echo   Press Ctrl+C to stop, or
    pause
    echo.
)

echo Pre-flight checks complete!
echo.
echo ================================================================

REM ============================================================
REM STEP 2: RUN GENERATOR
REM ============================================================

echo.
echo What will happen:
echo   - Read E*TRADE files from etrade_inputs/
echo   - Auto-discover company symbols
echo   - Fetch company details from Yahoo Finance
echo   - Auto-detect countries (USA, Canada, UK, etc.)
echo   - Scrape stock prices for full year
echo   - Download SBI TTBR exchange rates
echo   - Generate 4 output files in etrade_outputs/
echo.
echo This will take 1-2 minutes (web scraping)
echo Chrome browser will open in background
echo.

REM ============================================================
REM Ask for Income Range (only if G&L file exists)
REM Will calculate BOTH New and Old regime rates for comparison
REM ============================================================
if "%FILE_STATUS:~1,1%"=="1" (
    echo ======================================================================
    echo   SHORT-TERM CAPITAL GAINS TAX CALCULATION
    echo ======================================================================
    echo STCG on foreign stocks is taxed at your income tax slab rate.
    echo.
    echo The tool will calculate tax under BOTH regimes for comparison.
    echo.
    echo TIP: Check your Form-16 for "Total Taxable Income" to select the
    echo      correct bracket. Include salary + other income sources.
    echo.
    echo Select your expected TOTAL TAXABLE INCOME for this year:
    echo.
    echo   1. Up to Rs. 4 lakhs
    echo   2. Rs. 4-8 lakhs
    echo   3. Rs. 8-12 lakhs
    echo   4. Rs. 12-16 lakhs
    echo   5. Rs. 16-20 lakhs
    echo   6. Rs. 20-24 lakhs
    echo   7. Rs. 24-50 lakhs
    echo   8. Rs. 50 lakhs - 1 crore
    echo   9. Rs. 1-2 crores
    echo  10. Rs. 2-5 crores
    echo  11. Above Rs. 5 crores
    echo.
    echo NOTE: This is only for STCG calculation. LTCG is fixed at 12.5%%.
    echo ======================================================================
    echo.

    set /p INCOME_CHOICE="Enter your choice (1-11): "

    REM Validate input - MUST use delayed expansion ! since we're inside a code block
    if "!INCOME_CHOICE!"=="" (
        echo [ERROR] No choice entered!
        pause
        exit /b 1
    )
    echo.
) else (
    REM No G&L file - no sales, so no STCG calculation needed
    REM Pass empty value - Python will skip Capital Gains entirely
    set INCOME_CHOICE=
)

echo [*] Starting Schedule FA generation...
venv\Scripts\python.exe scripts\etrade\itr_fa_etrade.py --income-bracket %INCOME_CHOICE% > output_summary.txt 2>&1

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
echo Check the etrade_outputs/ folder for:
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