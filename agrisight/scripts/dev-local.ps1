# AgriSight - local dev stack for manual QA (Windows / PowerShell, needs Docker Desktop + Node/pnpm)
# Usage (from the agrisight folder):   powershell -ExecutionPolicy Bypass -File scripts\dev-local.ps1
# Opens: frontend http://localhost:5173  | API http://localhost:8000/api/docs/ | admin http://localhost:8000/admin/
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "1/4 Starting postgres, redis and backend containers..." -ForegroundColor Cyan
docker compose up -d --build postgres redis backend

Write-Host "2/4 Waiting for backend health (first build can take 10+ minutes)..." -ForegroundColor Cyan
$ok = $false
for ($i = 0; $i -lt 240; $i++) {
  try { if ((Invoke-WebRequest -UseBasicParsing http://localhost:8000/health/ -TimeoutSec 3).StatusCode -eq 200) { $ok = $true; break } } catch {}
  Start-Sleep -Seconds 5
}
if (-not $ok) { docker compose logs --tail 80 backend; throw "Backend did not become healthy" }

Write-Host "3/4 Seeding QA users + DRC demo data..." -ForegroundColor Cyan
Get-Content "$PSScriptRoot\qa_seed_demo.py" -Raw | docker compose exec -T backend python manage.py shell

Write-Host "4/4 Starting Vite dev server on http://localhost:5173 ..." -ForegroundColor Cyan
Set-Location "$root\frontend"
if (-not (Test-Path .env)) { "VITE_API_BASE_URL=http://localhost:8000`nVITE_WS_URL=ws://localhost:8000/ws/" | Set-Content .env }
pnpm install --no-frozen-lockfile
Write-Host "Login: admin@agrisight.test / AgriTest#2026  (or field@agrisight.test)" -ForegroundColor Green
Write-Host "API rate limit: API_RATE_LIMIT_REQUESTS (default 1000/hour per IP) - raise it in docker-compose if needed." -ForegroundColor Yellow
pnpm dev
