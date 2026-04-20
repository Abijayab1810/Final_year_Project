@echo off
REM Quick Start Script for Windows
REM This script helps you get started with Docker deployment

echo.
echo =========================================
echo  Abandoned Luggage Detection System
echo  Docker Quick Start
echo =========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not installed
    echo Please install Docker Desktop which includes Docker Compose
    pause
    exit /b 1
)

echo Docker and Docker Compose are installed!
echo.

echo Select an option:
echo 1. Build and start all services
echo 2. Start services
echo 3. Stop services
echo 4. View logs
echo 5. Run API client example
echo 6. Clean up and remove containers
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    echo Building and starting services...
    docker-compose build
    docker-compose up -d
    echo.
    echo Services started!
    echo - API: http://localhost:8000
    echo - API Docs: http://localhost:8000/docs
    echo - Streamlit: http://localhost:8501
    echo - Nginx: http://localhost:80
    echo.
    echo Check status with: docker-compose ps
    echo View logs with: docker-compose logs -f
) else if "%choice%"=="2" (
    echo Starting services...
    docker-compose up -d
    docker-compose ps
) else if "%choice%"=="3" (
    echo Stopping services...
    docker-compose down
    echo Services stopped
) else if "%choice%"=="4" (
    echo Showing logs (Ctrl+C to exit)...
    docker-compose logs -f
) else if "%choice%"=="5" (
    echo Running API client example...
    python api_client_example.py
) else if "%choice%"=="6" (
    echo Removing all containers and volumes...
    docker-compose down -v
    echo Cleanup complete
) else (
    echo Invalid choice
)

pause
