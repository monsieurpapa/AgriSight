#!/bin/bash

# AgriSight Start and Test Script
# This script starts Docker Compose and runs comprehensive tests

set -e  # Exit on any error

echo "🚀 AgriSight Start and Test Script"
echo "=================================="

# Check if Docker is running
echo "📋 Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    echo "   On Windows: Start Docker Desktop from Start Menu"
    echo "   On Mac: Start Docker Desktop from Applications"
    echo "   On Linux: sudo systemctl start docker"
    exit 1
fi
echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi
echo "✅ docker-compose is available"

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down --volumes --remove-orphans

# Start all services
echo "🚀 Starting AgriSight services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Wait for database to be ready
echo "🗄️  Waiting for database to be ready..."
until docker-compose exec -T postgres pg_isready -U agrisight_user -d agrisight; do
    echo "   Database not ready, waiting..."
    sleep 5
done
echo "✅ Database is ready"

# Wait for backend to be ready
echo "🔧 Waiting for backend to be ready..."
until curl -s http://localhost:8000/health/ > /dev/null; do
    echo "   Backend not ready, waiting..."
    sleep 5
done
echo "✅ Backend is ready"

# Run database migrations
echo "📦 Running database migrations..."
docker-compose exec -T backend python manage.py makemigrations --noinput
docker-compose exec -T backend python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

# Run comprehensive tests
echo "🧪 Running comprehensive feature tests..."
if command -v python3 &> /dev/null; then
    python3 test_new_features.py
elif command -v python &> /dev/null; then
    python test_new_features.py
else
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Display service URLs
echo ""
echo "🌐 Service URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/api/docs/"
echo "   Health Check: http://localhost:8000/health/"
echo "   HAProxy:      http://localhost:8080"
echo "   HAProxy Stats: http://localhost:8404/stats"

echo ""
echo "🎉 AgriSight is ready! All new features have been tested."
echo ""
echo "📝 To stop services: docker-compose down"
echo "📝 To view logs:     docker-compose logs -f"
echo "📝 To restart:       docker-compose restart"
