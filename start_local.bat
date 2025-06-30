@echo off
title DocuMind - Local Development
color 0A

echo ================================================================
echo                    DocuMind Development Setup
echo ================================================================
echo.
echo This script will help you run DocuMind locally on Windows
echo.
echo Prerequisites:
echo - Python 3.8+ installed
echo - Node.js 16+ installed
echo - Git installed
echo.
echo ================================================================
echo.

set /p choice="Do you want to start the backend server? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Starting backend in a new window...
    start "DocuMind Backend" cmd /k "cd /d backend && run_server.bat"
    timeout /t 3 /nobreak >nul
)

set /p choice="Do you want to start the frontend? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Starting frontend in a new window...
    start "DocuMind Frontend" cmd /k "cd /d frontend && run_frontend.bat"
    timeout /t 3 /nobreak >nul
)

echo.
echo ================================================================
echo                        Quick Access URLs
echo ================================================================
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo ================================================================
echo.
echo Both servers are now running in separate windows.
echo Close this window or press any key to continue...
pause >nul
