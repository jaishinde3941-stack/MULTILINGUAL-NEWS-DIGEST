<#
.SYNOPSIS
    Unified one-click and single-terminal runner for Multilingual News Digest.
.DESCRIPTION
    Orchestrates Ollama AI engine, FastAPI Backend, and Next.js Frontend.
    Supports running in separate windows or managing all services inside a single terminal session.
.PARAMETER SingleTerminal
    Runs all services managed within this single console window.
#>
[CmdletBinding()]
param (
    [switch]$SingleTerminal
)

$ErrorActionPreference = "Continue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "          MULTILINGUAL NEWS DIGEST - UNIFIED STARTUP SYSTEM           " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Resolve Project Root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path "$ScriptDir\backend" -PathType Container) {
    $ProjectDir = $ScriptDir
} elseif (Test-Path "$ScriptDir\multilingual_news_digest\backend" -PathType Container) {
    $ProjectDir = "$ScriptDir\multilingual_news_digest"
} else {
    Write-Error "[ERROR] Could not locate backend and frontend project directories."
    exit 1
}

# 2. Check Prerequisites
Write-Host "[1/4] Checking prerequisites..." -ForegroundColor Yellow

# Node.js and npm
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "[ERROR] Node.js is not found in PATH! Install from https://nodejs.org/"
    exit 1
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "[ERROR] npm is not found in PATH!"
    exit 1
}

# Python & Virtualenv
$VenvPython = "$ProjectDir\backend\venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[..] Backend virtual environment not found. Setting up venv..." -ForegroundColor Gray
    $SysPython = (Get-Command python -ErrorAction SilentlyContinue)?.Source
    if (-not $SysPython -and (Test-Path "C:\Users\$env:USERNAME\anaconda3\python.exe")) {
        $SysPython = "C:\Users\$env:USERNAME\anaconda3\python.exe"
    }
    if (-not $SysPython) {
        Write-Error "[ERROR] Python 3.10+ was not found on your system."
        exit 1
    }
    & $SysPython -m venv "$ProjectDir\backend\venv"
    & "$ProjectDir\backend\venv\Scripts\pip.exe" install -r "$ProjectDir\backend\requirements.txt"
}

# Frontend dependencies
if (-not (Test-Path "$ProjectDir\frontend\node_modules")) {
    Write-Host "[..] Installing frontend dependencies (npm install)..." -ForegroundColor Gray
    Push-Location "$ProjectDir\frontend"
    npm install
    Pop-Location
}

Write-Host "[OK] Environments and tools verified." -ForegroundColor Green
Write-Host ""

# 3. Check and Start Ollama
Write-Host "[2/4] Checking Ollama AI Service..." -ForegroundColor Yellow

$OllamaUrl = "http://localhost:11434"
$OllamaTagsUrl = "$OllamaUrl/api/tags"
$OllamaRunning = $false

try {
    $resp = Invoke-RestMethod -Uri $OllamaTagsUrl -Method Get -TimeoutSec 2 -ErrorAction Stop
    $OllamaRunning = $true
    Write-Host "[OK] Ollama service is already active on $OllamaUrl (reusing existing instance)." -ForegroundColor Green
} catch {
    Write-Host "[..] Ollama service not running. Starting 'ollama serve'..." -ForegroundColor Gray
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue

    Write-Host "[..] Waiting for Ollama to become ready..." -ForegroundColor Gray
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            $resp = Invoke-RestMethod -Uri $OllamaTagsUrl -Method Get -TimeoutSec 1 -ErrorAction Stop
            $OllamaRunning = $true
            Write-Host "[OK] Ollama service started successfully!" -ForegroundColor Green
            break
        } catch { }
    }
    if (-not $OllamaRunning) {
        Write-Host "[WARN] Ollama did not respond within 15 seconds. Backend will use smart heuristic fallback." -ForegroundColor Magenta
    }
}

# Model Check
$ConfigModel = "llama3.2"
$EnvPath = "$ProjectDir\backend\.env"
if (Test-Path $EnvPath) {
    Get-Content $EnvPath | ForEach-Object {
        if ($_ -match "^\s*OLLAMA_MODEL\s*=\s*(.+)$") {
            $ConfigModel = $matches[1].Trim()
        }
    }
}

if ($OllamaRunning) {
    try {
        $tagsData = Invoke-RestMethod -Uri $OllamaTagsUrl -Method Get -TimeoutSec 2
        $models = $tagsData.models | ForEach-Object { $_.name }
        $modelFound = $models | Where-Object { $_ -eq $ConfigModel -or $_ -like "$ConfigModel`:*" }
        if ($modelFound) {
            Write-Host "[OK] Configured model '$ConfigModel' is installed in Ollama." -ForegroundColor Green
        } else {
            Write-Host "[WARN] Model '$ConfigModel' is NOT yet downloaded!" -ForegroundColor Yellow
            Write-Host "       Run this command to download it: ollama pull $ConfigModel" -ForegroundColor Cyan
            Write-Host "       (Smart heuristic fallback will be used until pulled)" -ForegroundColor Gray
        }
    } catch { }
}
Write-Host ""

# 4. Check Backend (Port 8000)
Write-Host "[3/4] Checking Backend API Server..." -ForegroundColor Yellow
$BackendRunning = $false
try {
    $backendCheck = Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method Get -TimeoutSec 2 -ErrorAction Stop
    $BackendRunning = $true
    Write-Host "[OK] Backend API is already active on http://127.0.0.1:8000." -ForegroundColor Green
} catch {
    Write-Host "[..] Starting Backend API on http://127.0.0.1:8000..." -ForegroundColor Gray
    if ($SingleTerminal) {
        $BackendJob = Start-Job -ScriptBlock {
            param($bdir)
            Set-Location $bdir
            & ".\venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000
        } -ArgumentList "$ProjectDir\backend"
    } else {
        Start-Process cmd.exe -ArgumentList "/k cd /d `"$ProjectDir\backend`" && .\venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000" -WindowStyle Normal
    }

    # Wait for readiness
    for ($i = 0; $i -lt 12; $i++) {
        Start-Sleep -Seconds 1
        try {
            $backendCheck = Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method Get -TimeoutSec 1 -ErrorAction Stop
            $BackendRunning = $true
            Write-Host "[OK] Backend API is ready!" -ForegroundColor Green
            break
        } catch { }
    }
}
Write-Host ""

# 5. Check Frontend (Port 3000)
Write-Host "[4/4] Checking Frontend Application..." -ForegroundColor Yellow
$FrontendRunning = $false
try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    $FrontendRunning = $true
    Write-Host "[OK] Frontend UI is already active on http://localhost:3000." -ForegroundColor Green
} catch {
    Write-Host "[..] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Gray
    if ($SingleTerminal) {
        $FrontendJob = Start-Job -ScriptBlock {
            param($fdir)
            Set-Location $fdir
            npm run dev
        } -ArgumentList "$ProjectDir\frontend"
    } else {
        Start-Process cmd.exe -ArgumentList "/k cd /d `"$ProjectDir\frontend`" && npm run dev" -WindowStyle Normal
    }

    # Wait for readiness
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
            $FrontendRunning = $true
            Write-Host "[OK] Frontend UI is ready!" -ForegroundColor Green
            break
        } catch { }
    }
}
Write-Host ""

# 6. Status Dashboard & Browser Launch
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "                ALL SYSTEM SERVICES ARE UP AND READY!                 " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  * Frontend Web UI:    http://localhost:3000" -ForegroundColor White
Write-Host "  * Backend REST API:   http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  * Interactive Docs:   http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  * Ollama Service:     http://localhost:11434" -ForegroundColor White
Write-Host "  * Configured Model:   $ConfigModel" -ForegroundColor White
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""

Start-Process "http://localhost:3000"

if ($SingleTerminal) {
    Write-Host "[Single-Terminal Mode Active]" -ForegroundColor Cyan
    Write-Host "Press [O] to reopen browser, [Q] to stop all services and exit..." -ForegroundColor Yellow
    while ($true) {
        if ([console]::KeyAvailable) {
            $key = [console]::ReadKey($true)
            if ($key.Key -eq [ConsoleKey]::Q) {
                Write-Host "`nStopping background services..." -ForegroundColor Gray
                Stop-Job $BackendJob, $FrontendJob -ErrorAction SilentlyContinue
                Remove-Job $BackendJob, $FrontendJob -ErrorAction SilentlyContinue
                # Kill processes on 8000 & 3000
                Get-NetTCPConnection -LocalPort 8000, 3000 -ErrorAction SilentlyContinue |
                    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
                Write-Host "[OK] All background services stopped." -ForegroundColor Green
                break
            } elseif ($key.Key -eq [ConsoleKey]::O) {
                Start-Process "http://localhost:3000"
            }
        }
        Start-Sleep -Milliseconds 250
    }
} else {
    Write-Host "Services are running in their dedicated terminal windows." -ForegroundColor Gray
    Write-Host "To stop them at any time, run .\stop.ps1 or stop.bat." -ForegroundColor Gray
}

