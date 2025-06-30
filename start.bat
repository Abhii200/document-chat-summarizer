@echo off
title DocuMind - AI Document Summarizer
color 0A

echo ================================================================
echo                    DocuMind - AI Document Summarizer
echo ================================================================
echo.

REM Check if backend .env exists
if not exist "backend\.env" (
    echo ❌ Backend .env file not found!
    echo Please copy backend\.env.example to backend\.env and configure your API key
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "backend\openr\Scripts\activate.bat" (
    echo ⚠️  Virtual environment not found. Creating one...
    cd backend
    python -m venv openr
    call openr\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
)

REM Check if frontend .env exists
if not exist "frontend\.env" (
    echo ⚠️  Frontend .env file not found. Creating from template...
    copy "frontend\.env.example" "frontend\.env"
)

echo [1/2] Starting Backend Server...
start "DocuMind Backend" cmd /k "cd /d backend && openr\Scripts\activate && python main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Development Server...
start "DocuMind Frontend" cmd /k "cd /d frontend && npm start"

echo.
echo ================================================================
echo                        DocuMind Started!
echo ================================================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs  
echo Frontend:     http://localhost:3000
echo.
echo Both servers are running in separate windows.
echo Close this window when you're done.
echo ================================================================
echo.
pause
