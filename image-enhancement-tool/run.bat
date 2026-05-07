@echo off
REM QUICK START GUIDE FOR WINDOWS
REM Run this batch file to set up and start the application

echo.
echo ==================================================
echo 0xFF Image Enhancement Toolkit - Quick Start
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERR Python is not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo OK Python found
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo OK Virtual environment created
) else (
    echo OK Virtual environment already exists
)

echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo OK Virtual environment activated

echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo OK Dependencies installed

echo.

REM Create sample image
if not exist "sample_images\sample.jpg" (
    echo Generating sample image...
    python create_sample.py
    echo OK Sample image created
) else (
    echo OK Sample image already exists
)

echo.
echo ==================================================
echo Starting application...
echo ==================================================
echo.
echo The app will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

REM Run the app
streamlit run app.py

pause
