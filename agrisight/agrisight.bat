@echo off
REM AgriSight Platform - Windows Batch Commands
REM Alternative to Makefile for Windows users

setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="health-check" goto health-check
if "%1"=="migrate" goto migrate
if "%1"=="createsuperuser" goto createsuperuser
if "%1"=="test" goto test
if "%1"=="backup-db" goto backup-db
if "%1"=="clean" goto clean
if "%1"=="setup" goto setup
goto help

:help
echo AgriSight Platform - Available Commands:
echo ========================================
echo.
echo Docker Operations:
echo   agrisight.bat build          - Build all Docker containers
echo   agrisight.bat up             - Start all services
echo   agrisight.bat down           - Stop all services
echo   agrisight.bat restart        - Restart all services
echo.
echo Monitoring:
echo   agrisight.bat logs           - Show logs for all services
echo   agrisight.bat status         - Show status of all containers
echo   agrisight.bat health-check   - Check health of all services
echo.
echo Database:
echo   agrisight.bat migrate        - Run Django database migrations
echo   agrisight.bat createsuperuser - Create Django superuser
echo   agrisight.bat backup-db      - Backup database
echo.
echo Development:
echo   agrisight.bat test           - Run all tests
echo   agrisight.bat setup          - Initial setup for new environment
echo.
echo Maintenance:
echo   agrisight.bat clean          - Clean Docker system
echo.
echo For more commands, install Make for Windows or use docker-compose directly.
goto end

:build
echo Building all Docker containers...
docker-compose build
goto end

:up
echo Starting all services...
docker-compose up -d
goto end

:down
echo Stopping all services...
docker-compose down
goto end

:restart
echo Restarting all services...
docker-compose restart
goto end

:logs
echo Showing logs for all services...
docker-compose logs -f
goto end

:status
echo Showing status of all containers...
docker-compose ps
goto end

:health-check
echo Checking service health...
echo ==========================
echo Frontend (Port 3000):
curl -s -o nul -w "%%{http_code}" http://localhost:3000 2>nul || echo Not responding
echo.
echo Backend (Port 8000):
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/health/ 2>nul || echo Not responding
echo.
echo HAProxy (Port 8080):
curl -s -o nul -w "%%{http_code}" http://localhost:8080 2>nul || echo Not responding
goto end

:migrate
echo Running Django database migrations...
docker-compose exec backend python manage.py migrate
goto end

:createsuperuser
echo Creating Django superuser...
docker-compose exec backend python manage.py createsuperuser
goto end

:test
echo Running all tests...
docker-compose exec backend python manage.py test
goto end

:backup-db
echo Backing up database...
if not exist backups mkdir backups
docker-compose exec postgres pg_dump -U agrisight_user agrisight_db > backups\agrisight_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql
echo Database backup created in backups\ directory
goto end

:clean
echo Cleaning Docker system...
docker system prune -f
goto end

:setup
echo Setting up AgriSight platform...
docker-compose up -d postgres redis
timeout /t 10 /nobreak >nul
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose up -d
echo Setup complete! Run 'agrisight.bat createsuperuser' to create an admin user.
goto end

:end
endlocal
