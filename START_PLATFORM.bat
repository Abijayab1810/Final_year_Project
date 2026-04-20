@echo off
REM Start Luggage Detection Platform - Windows Batch Script
REM This script starts both the FastAPI backend and Streamlit frontend

echo.
echo ========================================
echo  Luggage Detection Platform - Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import streamlit; import fastapi; import ultralytics" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo  Starting Services...
echo ========================================
echo.
echo This will open TWO windows:
echo   1. FastAPI Backend (Port 8000)
echo   2. Streamlit Frontend (Port 8501)
echo.
echo IMPORTANT: Keep BOTH windows open while testing!
echo.
pause

REM Start FastAPI backend in new window
echo Starting FastAPI Backend...
start "Luggage Detection - API Backend" cmd /k python api_auth.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start Streamlit frontend in new window
echo Starting Streamlit Frontend...
start "Luggage Detection - Web Dashboard" cmd /k streamlit run app_auth.py --logger.level=info

REM Display access information
echo.
echo ========================================
echo  ✅ Platform Started Successfully!
echo ========================================
echo.
echo Access the platform:
echo   🌐 Dashboard:  http://localhost:8501
echo   🔧 API Docs:  http://localhost:8000/docs
echo.
echo First Time Setup:
echo   1. Go to http://localhost:8501
echo   2. Click "Sign Up" tab
echo   3. Create your account
echo   4. Login
echo   5. Add a camera in "Camera Management"
echo.
echo To Stop: Close both windows or press Ctrl+C in each window
echo.
pause
