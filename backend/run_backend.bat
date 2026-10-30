@echo off
title Multilingual News Digest - Backend API (Port 8000)
cd /d "%~dp0"

:: Explicitly lock to the backend virtual environment
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
    set "PIP_EXE=%~dp0venv\Scripts\pip.exe"
    call "%~dp0venv\Scripts\activate.bat"
) else if exist ".\venv\Scripts\python.exe" (
    set "PYTHON_EXE=.\venv\Scripts\python.exe"
    set "PIP_EXE=.\venv\Scripts\pip.exe"
    call ".\venv\Scripts\activate.bat"
) else (
    set "PYTHON_EXE=python"
    set "PIP_EXE=pip"
)

:: Optional argument to install/update dependencies using the same venv
if "%1"=="--install" (
    echo [*] Installing dependencies from requirements.txt using %PIP_EXE% ...
    "%PIP_EXE%" install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
)

echo Starting FastAPI Backend server on http://127.0.0.1:8000 using %PYTHON_EXE% ...
"%PYTHON_EXE%" -m uvicorn app.main:app --reload --port 8000
if %errorlevel% neq 0 (
    echo [ERROR] Backend failed to start.
    pause
)

