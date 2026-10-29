@echo off
title Multilingual News Digest - Backend API (Port 8000)
cd /d "%~dp0"

if exist ".\venv\Scripts\activate.bat" (
    call .\venv\Scripts\activate.bat
)

echo Starting FastAPI Backend server on http://127.0.0.1:8000 ...
python -m uvicorn app.main:app --reload --port 8000
if %errorlevel% neq 0 (
    echo [ERROR] Backend failed to start.
    pause
)

