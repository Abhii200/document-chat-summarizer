@echo off
echo Starting DocuMind Application...
echo.

REM Check if backend .env exists
if not exist "backend\.env" (
    echo ❌ Backend .env file not found!
    echo Please copy backend\.env.example to backend\.env and configure your API key
    echo.
    pause
    exit /b 1
)

REM Check if frontend .env exists
if not exist "frontend\.env" (
    echo ⚠️  Frontend .env file not found. Creating from template...
    copy "frontend\.env.example" "frontend\.env"
)

echo [1/2] Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python main.py"

echo [2/2] Starting Frontend Development Server...
cd ../frontend
start "Frontend Server" cmd /k "npm start"

echo.
echo ✅ Both servers are starting!
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
