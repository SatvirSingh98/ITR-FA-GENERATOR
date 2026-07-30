@echo off
REM First-time setup for ITR FA Generator

echo ================================================================
echo   ITR FA Generator - First Time Setup
echo ================================================================
echo.
echo This script will:
echo   1. Check Python virtual environment
echo   2. Install required packages (pandas, selenium, openpyxl, etc.)
echo   3. Create folders (inputs, outputs)
echo   4. Create config.json from example
echo.
echo Run this ONCE when you first download this tool.
echo After setup, use GENERATE_ITR_FA.bat to run the generator.
echo.
echo ================================================================
echo.
pause

REM ============================================================
REM STEP 1: Check Python venv
REM ============================================================

echo [1/4] Checking Python virtual environment...
if not exist venv\Scripts\python.exe (
    echo   [ERROR] Python venv not found!
    echo.
    echo   This tool requires Python 3.14+ with venv.
    echo   Please install Python and create venv first.
    echo.
    pause
    exit /b 1
)
venv\Scripts\python.exe --version
echo   [OK] Python venv found
echo.

REM ============================================================
REM STEP 2: Install packages
REM ============================================================

echo [2/4] Installing required Python packages...
echo   (This may take 2-5 minutes, please wait...)
echo.

REM Upgrade pip first
venv\Scripts\python.exe -m pip install --upgrade pip --quiet

REM Install from requirements.txt
venv\Scripts\python.exe -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo   [ERROR] Package installation failed!
    echo   Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo   [OK] Packages installed successfully
echo.

REM ============================================================
REM STEP 3: Create folders
REM ============================================================

echo [3/4] Creating necessary folders...
if not exist inputs (
    mkdir inputs
    echo   [OK] Created inputs/ folder
) else (
    echo   [OK] inputs/ folder exists
)

if not exist outputs (
    mkdir outputs
    echo   [OK] Created outputs/ folder
) else (
    echo   [OK] outputs/ folder exists
)
echo.

REM ============================================================
REM STEP 4: Check config file
REM ============================================================

echo [4/4] Checking configuration...
if not exist config.json (
    if exist config.example.json (
        echo   [i] Copying config.example.json to config.json...
        copy config.example.json config.json >nul
        echo   [OK] Created config.json from example
        echo   [!] IMPORTANT: Edit config.json with your account number!
    ) else (
        echo   [WARNING] config.example.json not found
        echo   [i] You'll need to create config.json manually
    )
) else (
    echo   [OK] config.json exists
)
echo.

REM ============================================================
REM STEP 5: Success message
REM ============================================================

echo ================================================================
echo   Setup Complete!
echo ================================================================
echo.
echo What was installed:
echo   - pandas, openpyxl (Excel processing)
echo   - selenium (web scraping)
echo   - requests (HTTP downloads)
echo.
echo Folders created:
echo   - inputs/  (Place E*TRADE files here)
echo   - outputs/ (Generated files appear here)
echo.
echo Next steps:
echo   1. Edit config.json with your E*TRADE account number
echo   2. Export files from E*TRADE:
echo      - ByStatus_expanded.xlsx
echo      - G^&L_Expanded.xlsx
echo   3. Place files in inputs/ folder
echo   4. Run GENERATE_ITR_FA.bat
echo.
echo See START_HERE.txt for quick start guide.
echo See README.md for complete documentation.
echo.
pause
