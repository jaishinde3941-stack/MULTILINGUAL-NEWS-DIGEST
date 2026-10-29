<#
.SYNOPSIS
    Stops all background Backend and Frontend processes on ports 8000 and 3000.
#>
Write-Host "[..] Scanning for processes on ports 8000 and 3000..." -ForegroundColor Yellow

$ports = @(8000, 3000)
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            Write-Host "[..] Terminating process on port $port (PID $($c.OwningProcess))..." -ForegroundColor Gray
            Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
        }
        Write-Host "[OK] Port $port is now free." -ForegroundColor Green
    } else {
        Write-Host "[OK] Port $port is already free." -ForegroundColor Green
    }
}

Write-Host "`n[OK] All project services have been stopped." -ForegroundColor Green

