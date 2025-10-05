@echo off
REM AgriSight Start and Test Script for Windows
REM This script starts Docker Compose and runs comprehensive tests

echo 🚀 AgriSight Start and Test Script
echo ==================================

REM Check if Docker is running
echo 📋 Checking Docker status...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo    Start Docker Desktop from Start Menu or Desktop
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose is not installed
    pause
    exit /b 1
)
echo ✅ docker-compose is available

REM Clean up any existing containers
echo 🧹 Cleaning up existing containers...
docker-compose down --volumes --remove-orphans

REM Start all services
echo 🚀 Starting AgriSight services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check service status
echo 📊 Checking service status...
docker-compose ps

REM Wait for database to be ready
echo 🗄️  Waiting for database to be ready...
:wait_db
docker-compose exec -T postgres pg_isready -U agrisight_user -d agrisight >nul 2>&1
if errorlevel 1 (
    echo    Database not ready, waiting...
    timeout /t 5 /nobreak >nul
    goto wait_db
)
echo ✅ Database is ready

REM Wait for backend to be ready
echo 🔧 Waiting for backend to be ready...
:wait_backend
curl -s http://localhost:8000/health/ >nul 2>&1
if errorlevel 1 (
    echo    Backend not ready, waiting...
    timeout /t 5 /nobreak >nul
    goto wait_backend
)
echo ✅ Backend is ready

REM Run database migrations
echo 📦 Running database migrations...
docker-compose exec -T backend python manage.py makemigrations --noinput
docker-compose exec -T backend python manage.py migrate --noinput

REM Collect static files
echo 📁 Collecting static files...
docker-compose exec -T backend python manage.py collectstatic --noinput

REM Run comprehensive tests
echo 🧪 Running comprehensive feature tests...
python test_new_features.py
if errorlevel 1 (
    echo ❌ Some tests failed. Check the output above.
    pause
    exit /b 1
)

REM Display service URLs
echo.
echo 🌐 Service URLs:
echo    Frontend:     http://localhost:3000
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/api/docs/
echo    Health Check: http://localhost:8000/health/
echo    HAProxy:      http://localhost:8080
echo    HAProxy Stats: http://localhost:8404/stats

echo.
echo 🎉 AgriSight is ready! All new features have been tested.
echo.
echo 📝 To stop services: docker-compose down
echo 📝 To view logs:     docker-compose logs -f
echo 📝 To restart:       docker-compose restart

pause
