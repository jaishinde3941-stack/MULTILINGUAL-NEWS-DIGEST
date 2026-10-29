@echo off
setlocal enabledelayedexpansion
title Multilingual News Digest - Stop Services

echo ======================================================================
echo           MULTILINGUAL NEWS DIGEST - STOPPING SERVICES
echo ======================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ports = @(8000, 3000);" ^
    "foreach ($port in $ports) {" ^
    "    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue;" ^
    "    if ($conns) {" ^
    "        foreach ($c in $conns) {" ^
    "            Write-Host ('[..] Stopping process on port ' + $port + ' (PID ' + $c.OwningProcess + ')...');" ^
    "            Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue;" ^
    "        }" ^
    "    } else {" ^
    "        Write-Host ('[OK] Port ' + $port + ' is already free.');" ^
    "    }" ^
    "}"

echo.
echo [OK] Backend and Frontend servers stopped.
echo (Ollama service has been left intact for other applications).
echo.
exit /b 0
