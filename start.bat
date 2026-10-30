@echo off
setlocal enabledelayedexpansion
title Multilingual News Digest - One-Click Launcher

echo ======================================================================
echo           MULTILINGUAL NEWS DIGEST - ONE-CLICK LAUNCHER
echo ======================================================================
echo.

:: ----------------------------------------------------------------------
:: 1. Determine Project Directory
:: ----------------------------------------------------------------------
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

if exist "%SCRIPT_DIR%\backend" if exist "%SCRIPT_DIR%\frontend" (
    set "PROJECT_DIR=%SCRIPT_DIR%"
) else if exist "%SCRIPT_DIR%\multilingual_news_digest\backend" (
    set "PROJECT_DIR=%SCRIPT_DIR%\multilingual_news_digest"
) else (
    echo [ERROR] Could not locate backend and frontend project directories!
    pause
    exit /b 1
)

:: ----------------------------------------------------------------------
:: 2. Check Prerequisites (Python, Node.js, npm, Ollama)
:: ----------------------------------------------------------------------
echo [1/4] Checking prerequisites...

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not found in PATH! Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not found in PATH!
    pause
    exit /b 1
)

:: Python / Virtualenv
set "PYTHON_EXE="
set "PIP_EXE="
if exist "%PROJECT_DIR%\backend\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_DIR%\backend\venv\Scripts\python.exe"
    set "PIP_EXE=%PROJECT_DIR%\backend\venv\Scripts\pip.exe"
    :: Ensure newspaper and required dependencies are installed in existing venv
    "%PROJECT_DIR%\backend\venv\Scripts\python.exe" -c "import newspaper" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [*] Installing missing backend dependencies in venv...
        "%PROJECT_DIR%\backend\venv\Scripts\pip.exe" install -r "%PROJECT_DIR%\backend\requirements.txt"
    )
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else if exist "C:\Users\%USERNAME%\anaconda3\python.exe" (
        set "PYTHON_EXE=C:\Users\%USERNAME%\anaconda3\python.exe"
    ) else if exist "C:\ProgramData\anaconda3\python.exe" (
        set "PYTHON_EXE=C:\ProgramData\anaconda3\python.exe"
    )
)

if not exist "%PROJECT_DIR%\backend\venv" (
    echo [*] Backend virtual environment not found. Setting up venv...
    if "%PYTHON_EXE%"=="" (
        echo [ERROR] Python was not found on your system!
        echo Please install Python 3.10+ or Anaconda.
        pause
        exit /b 1
    )
    "%PYTHON_EXE%" -m venv "%PROJECT_DIR%\backend\venv"
    echo [*] Installing backend dependencies...
    "%PROJECT_DIR%\backend\venv\Scripts\pip.exe" install -r "%PROJECT_DIR%\backend\requirements.txt"
)

:: Ollama CLI
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    ) else (
        echo [WARN] Ollama CLI was not found in PATH or standard installation directories.
        echo To enable local AI models, download Ollama from: https://ollama.com/download
    )
)

echo [OK] Prerequisites and environments verified.
echo.

:: ----------------------------------------------------------------------
:: 3. Configure and Start Ollama Service
:: ----------------------------------------------------------------------
echo [2/4] Checking Ollama AI Service...

curl.exe -s -m 2 http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 goto :OLLAMA_IS_RUNNING

echo [*] Ollama service not running. Starting ollama serve...
start "Ollama AI Service (Port 11434)" /min cmd /c "ollama serve"

echo [*] Waiting for Ollama readiness on http://localhost:11434...
set "OLLAMA_COUNT=0"
:OLLAMA_WAIT_LOOP
ping -n 2 127.0.0.1 >nul
curl.exe -s -m 1 http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 goto :OLLAMA_READY

set /a OLLAMA_COUNT+=1
if %OLLAMA_COUNT% geq 15 goto :OLLAMA_TIMEOUT
goto :OLLAMA_WAIT_LOOP

:OLLAMA_TIMEOUT
echo [WARN] Ollama did not respond within 15 seconds.
echo Backend will continue using its smart heuristic offline fallback.
goto :CHECK_MODEL

:OLLAMA_READY
echo [OK] Ollama service started successfully!
goto :CHECK_MODEL

:OLLAMA_IS_RUNNING
echo [OK] Ollama service is already active on http://localhost:11434 [reusing existing instance].

:CHECK_MODEL
set "OLLAMA_MODEL=llama3.2"
if exist "%PROJECT_DIR%\backend\.env" (
    for /f "tokens=2 delims==" %%A in ('findstr /b "OLLAMA_MODEL=" "%PROJECT_DIR%\backend\.env"') do (
        set "OLLAMA_MODEL=%%A"
    )
)

curl.exe -s http://127.0.0.1:11434/api/tags | findstr /i /c:"%OLLAMA_MODEL%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Configured AI model '%OLLAMA_MODEL%' is installed in Ollama.
) else (
    echo [WARN] Configured AI model '%OLLAMA_MODEL%' is NOT yet downloaded!
    echo To download it, run in a separate terminal:
    echo     ollama pull %OLLAMA_MODEL%
    echo Smart heuristic fallback will be used until the model is pulled.
)
echo.

:: ----------------------------------------------------------------------
:: 4. Start Backend API Server
:: ----------------------------------------------------------------------
echo [3/4] Checking Backend API Server...

curl.exe -s -m 2 http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend API is already running on http://127.0.0.1:8000 [reusing existing instance].
    goto :FRONTEND_STEP
)

echo [*] Starting FastAPI backend on http://127.0.0.1:8000...
start "Multilingual News Digest - Backend API (Port 8000)" "%PROJECT_DIR%\backend\run_backend.bat"

echo [*] Waiting for Backend API readiness...
set "BACKEND_COUNT=0"
:BACKEND_WAIT_LOOP
ping -n 2 127.0.0.1 >nul
curl.exe -s -m 1 http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel% equ 0 goto :BACKEND_READY

set /a BACKEND_COUNT+=1
if %BACKEND_COUNT% geq 12 goto :BACKEND_READY
goto :BACKEND_WAIT_LOOP

:BACKEND_READY
echo [OK] Backend API is active!

:FRONTEND_STEP
echo.

:: ----------------------------------------------------------------------
:: 5. Start Frontend Application
:: ----------------------------------------------------------------------
echo [4/4] Checking Frontend Application...

if not exist "%PROJECT_DIR%\frontend\node_modules" (
    echo [*] Installing frontend dependencies [npm install]...
    cd /d "%PROJECT_DIR%\frontend"
    call npm install
    cd /d "%PROJECT_DIR%"
)

curl.exe -s -m 2 http://localhost:3000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend UI is already running on http://localhost:3000 [reusing existing instance].
    goto :FINAL_SUMMARY
)

echo [*] Starting Next.js frontend on http://localhost:3000...
start "Multilingual News Digest - Frontend UI (Port 3000)" "%PROJECT_DIR%\frontend\run_frontend.bat"

echo [*] Waiting for Frontend UI readiness...
set "FRONTEND_COUNT=0"
:FRONTEND_WAIT_LOOP
ping -n 2 127.0.0.1 >nul
curl.exe -s -m 1 http://localhost:3000/ >nul 2>&1
if %errorlevel% equ 0 goto :FRONTEND_READY

set /a FRONTEND_COUNT+=1
if %FRONTEND_COUNT% geq 15 goto :FRONTEND_READY
goto :FRONTEND_WAIT_LOOP

:FRONTEND_READY
echo [OK] Frontend UI is active!

:FINAL_SUMMARY
echo.
echo ======================================================================
echo                ALL SYSTEM SERVICES ARE UP AND READY!
echo ======================================================================
echo.
echo   * Frontend Web UI:    http://localhost:3000
echo   * Backend REST API:   http://127.0.0.1:8000
echo   * Interactive Docs:   http://127.0.0.1:8000/docs
echo   * Ollama Service:     http://localhost:11434
echo   * Configured Model:   %OLLAMA_MODEL%
echo.
echo ======================================================================
echo.
echo Opening http://localhost:3000 in your default browser...
start http://localhost:3000
echo.
echo Press any key to exit this launcher window [services will stay running].
echo To stop all services, run stop.bat.
pause >nul
