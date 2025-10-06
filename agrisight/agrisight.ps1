# AgriSight Platform - PowerShell Commands
# Alternative to Makefile for Windows PowerShell users

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "AgriSight Platform - Available Commands:" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Docker Operations:" -ForegroundColor Yellow
    Write-Host "  .\agrisight.ps1 build          - Build all Docker containers"
    Write-Host "  .\agrisight.ps1 up             - Start all services"
    Write-Host "  .\agrisight.ps1 down           - Stop all services"
    Write-Host "  .\agrisight.ps1 restart        - Restart all services"
    Write-Host ""
    Write-Host "Monitoring:" -ForegroundColor Yellow
    Write-Host "  .\agrisight.ps1 logs           - Show logs for all services"
    Write-Host "  .\agrisight.ps1 status         - Show status of all containers"
    Write-Host "  .\agrisight.ps1 health-check   - Check health of all services"
    Write-Host ""
    Write-Host "Database:" -ForegroundColor Yellow
    Write-Host "  .\agrisight.ps1 migrate        - Run Django database migrations"
    Write-Host "  .\agrisight.ps1 createsuperuser - Create Django superuser"
    Write-Host "  .\agrisight.ps1 backup-db      - Backup database"
    Write-Host ""
    Write-Host "Development:" -ForegroundColor Yellow
    Write-Host "  .\agrisight.ps1 test           - Run all tests"
    Write-Host "  .\agrisight.ps1 setup          - Initial setup for new environment"
    Write-Host ""
    Write-Host "Maintenance:" -ForegroundColor Yellow
    Write-Host "  .\agrisight.ps1 clean          - Clean Docker system"
    Write-Host ""
    Write-Host "For more commands, install Make for Windows or use docker-compose directly."
}

function Invoke-Build {
    Write-Host "Building all Docker containers..." -ForegroundColor Blue
    docker-compose build
}

function Invoke-Up {
    Write-Host "Starting all services..." -ForegroundColor Blue
    docker-compose up -d
}

function Invoke-Down {
    Write-Host "Stopping all services..." -ForegroundColor Blue
    docker-compose down
}

function Invoke-Restart {
    Write-Host "Restarting all services..." -ForegroundColor Blue
    docker-compose restart
}

function Invoke-Logs {
    Write-Host "Showing logs for all services..." -ForegroundColor Blue
    docker-compose logs -f
}

function Invoke-Status {
    Write-Host "Showing status of all containers..." -ForegroundColor Blue
    docker-compose ps
}

function Invoke-HealthCheck {
    Write-Host "Checking service health..." -ForegroundColor Blue
    Write-Host "==========================" -ForegroundColor Blue
    
    Write-Host "Frontend (Port 3000):" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Not responding" -ForegroundColor Red
    }
    
    Write-Host "Backend (Port 8000):" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -UseBasicParsing -TimeoutSec 5
        Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Not responding" -ForegroundColor Red
    }
    
    Write-Host "HAProxy (Port 8080):" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 5
        Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Not responding" -ForegroundColor Red
    }
}

function Invoke-Migrate {
    Write-Host "Running Django database migrations..." -ForegroundColor Blue
    docker-compose exec backend python manage.py migrate
}

function Invoke-CreateSuperUser {
    Write-Host "Creating Django superuser..." -ForegroundColor Blue
    docker-compose exec backend python manage.py createsuperuser
}

function Invoke-Test {
    Write-Host "Running all tests..." -ForegroundColor Blue
    docker-compose exec backend python manage.py test
}

function Invoke-BackupDb {
    Write-Host "Backing up database..." -ForegroundColor Blue
    if (!(Test-Path "backups")) {
        New-Item -ItemType Directory -Name "backups"
    }
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    docker-compose exec postgres pg_dump -U agrisight_user agrisight_db > "backups\agrisight_backup_$timestamp.sql"
    Write-Host "Database backup created in backups\ directory" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Host "Cleaning Docker system..." -ForegroundColor Blue
    docker system prune -f
}

function Invoke-Setup {
    Write-Host "Setting up AgriSight platform..." -ForegroundColor Blue
    docker-compose up -d postgres redis
    Start-Sleep -Seconds 10
    docker-compose exec backend python manage.py migrate
    docker-compose exec backend python manage.py collectstatic --noinput
    docker-compose up -d
    Write-Host "Setup complete! Run '.\agrisight.ps1 createsuperuser' to create an admin user." -ForegroundColor Green
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "build" { Invoke-Build }
    "up" { Invoke-Up }
    "down" { Invoke-Down }
    "restart" { Invoke-Restart }
    "logs" { Invoke-Logs }
    "status" { Invoke-Status }
    "health-check" { Invoke-HealthCheck }
    "migrate" { Invoke-Migrate }
    "createsuperuser" { Invoke-CreateSuperUser }
    "test" { Invoke-Test }
    "backup-db" { Invoke-BackupDb }
    "clean" { Invoke-Clean }
    "setup" { Invoke-Setup }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help 
    }
}
