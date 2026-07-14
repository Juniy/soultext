# Soultext Server Starter
# Starts both backend and frontend development servers

param(
    [switch]$NoFrontend,
    [switch]$NoBackend
)

$BackendPort = 8000
$FrontendPort = 5173
$BackendPid = $null
$FrontendPid = $null

Write-Host "????????????????????????????????????????" -ForegroundColor Cyan
Write-Host "?     Soultext Server Manager v0.1    ?" -ForegroundColor Cyan
Write-Host "????????????????????????????????????????" -ForegroundColor Cyan
Write-Host ""
Write-Host "? Configuring LLM (Zen API / deepseek-v4-flash-free)..." -ForegroundColor Yellow
$env:SOULTEXT_LLM_API_KEY = "sk-6ZBQ3P1pM3iVLSzpdza1X6qw505PCCbBsfuQIhcBVNe6Qk8cGJHPGHCuoQlkenq3"
$env:SOULTEXT_LLM_BASE_URL = "https://opencode.ai/zen/v1"
$env:SOULTEXT_LLM_MODEL = "deepseek-v4-flash-free"
$env:SOULTEXT_LLM_PROVIDER = "custom"
Write-Host "  LLM configured: custom/deepseek-v4-flash-free" -ForegroundColor Green
Write-Host ""

# Kill existing processes on our ports
function Stop-ProcessOnPort($port) {
    $conn = netstat -ano | Select-String ":$port\s"
    foreach ($c in $conn) {
        $parts = $c.ToString().Trim() -split '\s+'
        if ($parts.Count -ge 5) {
            $pid = $parts[-1]
            try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
}

if (-not $NoBackend) {
    Write-Host "? Starting backend (FastAPI on port $BackendPort)..." -ForegroundColor Yellow
    Stop-ProcessOnPort $BackendPort
    $BackendJob = Start-Job -ScriptBlock {
        param($dir, $port)
        Set-Location $dir
        $env:SOULTEXT_LLM_API_KEY = ""
        python -m uvicorn backend.app:app --host 0.0.0.0 --port $port --reload
    } -ArgumentList (Get-Location).Path, $BackendPort
    Write-Host "  Backend job started: $($BackendJob.Id)" -ForegroundColor Green
}

if (-not $NoFrontend) {
    Write-Host "? Starting frontend (Vite on port $FrontendPort)..." -ForegroundColor Yellow
    Stop-ProcessOnPort $FrontendPort
    $FrontendJob = Start-Job -ScriptBlock {
        param($dir, $port)
        Set-Location $dir
        npx vite --host 0.0.0.0 --port $port
    } -ArgumentList (Join-Path (Get-Location).Path "frontend"), $FrontendPort
    Write-Host "  Frontend job started: $($FrontendJob.Id)" -ForegroundColor Green
}

Write-Host ""
Write-Host "? Configuring LLM (Zen API / deepseek-v4-flash-free)..." -ForegroundColor Yellow
$env:SOULTEXT_LLM_API_KEY = "sk-6ZBQ3P1pM3iVLSzpdza1X6qw505PCCbBsfuQIhcBVNe6Qk8cGJHPGHCuoQlkenq3"
$env:SOULTEXT_LLM_BASE_URL = "https://opencode.ai/zen/v1"
$env:SOULTEXT_LLM_MODEL = "deepseek-v4-flash-free"
$env:SOULTEXT_LLM_PROVIDER = "custom"
Write-Host "  LLM configured: custom/deepseek-v4-flash-free" -ForegroundColor Green
Write-Host ""
Write-Host "? Servers starting..." -ForegroundColor Green
Write-Host "  Backend:  http://localhost:$BackendPort" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:$FrontendPort" -ForegroundColor Cyan
Write-Host ""
Write-Host "? Configuring LLM (Zen API / deepseek-v4-flash-free)..." -ForegroundColor Yellow
$env:SOULTEXT_LLM_API_KEY = "sk-6ZBQ3P1pM3iVLSzpdza1X6qw505PCCbBsfuQIhcBVNe6Qk8cGJHPGHCuoQlkenq3"
$env:SOULTEXT_LLM_BASE_URL = "https://opencode.ai/zen/v1"
$env:SOULTEXT_LLM_MODEL = "deepseek-v4-flash-free"
$env:SOULTEXT_LLM_PROVIDER = "custom"
Write-Host "  LLM configured: custom/deepseek-v4-flash-free" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow

# Monitor and keep alive
try {
    while ($true) {
        Start-Sleep -Seconds 5
        if (-not $NoBackend) {
            $jb = Get-Job -Id $BackendJob.Id -ErrorAction SilentlyContinue
            if ($jb -and $jb.State -eq "Failed") {
                Write-Host "? Backend job failed, restarting..." -ForegroundColor Red
                Remove-Job -Id $BackendJob.Id -Force -ErrorAction SilentlyContinue
                Stop-ProcessOnPort $BackendPort
                $BackendJob = Start-Job -ScriptBlock {
                    param($dir, $port)
                    Set-Location $dir
                    python -m uvicorn backend.app:app --host 0.0.0.0 --port $port --reload
                } -ArgumentList (Get-Location).Path, $BackendPort
            }
        }
        if (-not $NoFrontend) {
            $jf = Get-Job -Id $FrontendJob.Id -ErrorAction SilentlyContinue
            if ($jf -and $jf.State -eq "Failed") {
                Write-Host "? Frontend job failed, restarting..." -ForegroundColor Red
                Remove-Job -Id $FrontendJob.Id -Force -ErrorAction SilentlyContinue
                Stop-ProcessOnPort $FrontendPort
                $FrontendJob = Start-Job -ScriptBlock {
                    param($dir, $port)
                    Set-Location $dir
                    npx vite --host 0.0.0.0 --port $port
                } -ArgumentList (Join-Path (Get-Location).Path "frontend"), $FrontendPort
            }
        }
    }
    # Check service health
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$BackendPort/" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($resp.StatusCode -eq 200) { Write-Host "? Backend: RUNNING" -ForegroundColor Green }
    } catch { Write-Host "? Backend: STARTING..." -ForegroundColor Yellow }
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$FrontendPort/" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($resp.StatusCode -eq 200) { Write-Host "? Frontend: RUNNING" -ForegroundColor Green }
    } catch { Write-Host "? Frontend: STARTING..." -ForegroundColor Yellow }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Get-Job | Stop-Job -ErrorAction SilentlyContinue
    Get-Job | Remove-Job -ErrorAction SilentlyContinue
}
