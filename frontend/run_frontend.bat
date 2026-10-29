@echo off
title Multilingual News Digest - Frontend UI (Port 3000)
cd /d "%~dp0"

echo Starting Next.js Frontend server on http://localhost:3000 ...
npm run dev
if %errorlevel% neq 0 (
    echo [ERROR] Frontend failed to start.
    pause
)

