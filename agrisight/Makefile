# AgriSight Platform Makefile
# Comprehensive maintenance and operations commands

.PHONY: help build up down restart logs clean test lint format migrate collectstatic createsuperuser shell backup restore health-check

# Default target
help: ## Show this help message
	@echo "AgriSight Platform - Available Commands:"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker Operations
build: ## Build all Docker containers
	docker-compose build

build-no-cache: ## Build all Docker containers without cache
	docker-compose build --no-cache

up: ## Start all services in detached mode
	docker-compose up -d

up-build: ## Build and start all services
	docker-compose up --build -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

restart-backend: ## Restart only backend service
	docker-compose restart backend

restart-frontend: ## Restart only frontend service
	docker-compose restart frontend

restart-db: ## Restart database service
	docker-compose restart postgres

# Logs and Monitoring
logs: ## Show logs for all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-db: ## Show database logs
	docker-compose logs -f postgres

logs-celery: ## Show Celery worker logs
	docker-compose logs -f celery_worker

logs-celery-beat: ## Show Celery beat logs
	docker-compose logs -f celery_beat

logs-redis: ## Show Redis logs
	docker-compose logs -f redis

# Status and Health Checks
status: ## Show status of all containers
	docker-compose ps

health-check: ## Check health of all services
	@echo "Checking service health..."
	@echo "=========================="
	@echo "Frontend (Port 3000):"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "Not responding"
	@echo ""
	@echo "Backend (Port 8000):"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health/ || echo "Not responding"
	@echo ""
	@echo "HAProxy (Port 8080):"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 || echo "Not responding"
	@echo ""
	@echo "HAProxy Stats (Port 8404):"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8404 || echo "Not responding"

# Database Operations
migrate: ## Run Django database migrations
	docker-compose exec backend python manage.py migrate

makemigrations: ## Create new Django migrations
	docker-compose exec backend python manage.py makemigrations

migrate-zero: ## Reset all migrations (DANGEROUS - use with caution)
	docker-compose exec backend python manage.py migrate --fake-initial

db-reset: ## Reset database (DANGEROUS - removes all data)
	docker-compose down -v
	docker-compose up -d postgres
	sleep 10
	docker-compose exec backend python manage.py migrate
	docker-compose exec backend python manage.py createsuperuser

# Django Management
collectstatic: ## Collect static files
	docker-compose exec backend python manage.py collectstatic --noinput

createsuperuser: ## Create Django superuser
	docker-compose exec backend python manage.py createsuperuser

shell: ## Open Django shell
	docker-compose exec backend python manage.py shell

dbshell: ## Open database shell
	docker-compose exec backend python manage.py dbshell

check: ## Run Django system checks
	docker-compose exec backend python manage.py check

# Development and Testing
test: ## Run all tests
	docker-compose exec backend python manage.py test

test-coverage: ## Run tests with coverage
	docker-compose exec backend coverage run --source='.' manage.py test
	docker-compose exec backend coverage report
	docker-compose exec backend coverage html

lint-backend: ## Lint backend code
	docker-compose exec backend flake8 .
	docker-compose exec backend black --check .
	docker-compose exec backend isort --check-only .

lint-frontend: ## Lint frontend code
	docker-compose exec frontend npm run lint

format-backend: ## Format backend code
	docker-compose exec backend black .
	docker-compose exec backend isort .

format-frontend: ## Format frontend code
	docker-compose exec frontend npm run format

# Celery Operations
celery-worker: ## Start Celery worker
	docker-compose exec celery_worker celery -A agrisight worker --loglevel=info

celery-beat: ## Start Celery beat scheduler
	docker-compose exec celery_beat celery -A agrisight beat --loglevel=info

celery-flower: ## Start Celery Flower monitoring
	docker-compose exec celery_worker celery -A agrisight flower

celery-purge: ## Purge all Celery tasks
	docker-compose exec celery_worker celery -A agrisight purge

# Backup and Restore
backup-db: ## Backup database
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U agrisight_user agrisight_db > backups/agrisight_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created in backups/ directory"

backup-media: ## Backup media files
	@mkdir -p backups
	tar -czf backups/media_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz -C agrisight/backend media/
	@echo "Media backup created in backups/ directory"

backup-all: ## Backup database and media files
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U agrisight_user agrisight_db > backups/agrisight_backup_$(shell date +%Y%m%d_%H%M%S).sql
	tar -czf backups/media_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz -C agrisight/backend media/
	@echo "Complete backup created in backups/ directory"

restore-db: ## Restore database from backup (usage: make restore-db BACKUP_FILE=backup.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "Usage: make restore-db BACKUP_FILE=backup.sql"; exit 1; fi
	docker-compose exec -T postgres psql -U agrisight_user -d agrisight_db < $(BACKUP_FILE)
	@echo "Database restored from $(BACKUP_FILE)"

# Security and Maintenance
security-check: ## Run security checks
	docker-compose exec backend python manage.py check --deploy
	docker-compose exec backend safety check

update-deps: ## Update Python dependencies
	docker-compose exec backend pip list --outdated
	docker-compose exec frontend npm outdated

clean-docker: ## Clean Docker system (removes unused containers, networks, images)
	docker system prune -f

clean-volumes: ## Remove all Docker volumes (DANGEROUS - removes all data)
	docker-compose down -v
	docker volume prune -f

clean-all: ## Clean everything (DANGEROUS - removes all containers, images, volumes)
	docker-compose down -v
	docker system prune -af
	docker volume prune -f

# Production Operations
prod-build: ## Build for production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Start production services
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down: ## Stop production services
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Monitoring and Debugging
monitor: ## Monitor all services
	@echo "Monitoring AgriSight services..."
	@echo "================================"
	@while true; do \
		clear; \
		echo "AgriSight Service Monitor - $(date)"; \
		echo "================================"; \
		docker-compose ps; \
		echo ""; \
		echo "Resource Usage:"; \
		docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"; \
		sleep 5; \
	done

debug-backend: ## Debug backend service
	docker-compose exec backend python manage.py runserver 0.0.0.0:8000 --settings=agrisight.settings_debug

debug-frontend: ## Debug frontend service
	docker-compose exec frontend npm run dev

# API Testing
test-api: ## Test API endpoints
	@echo "Testing API endpoints..."
	@echo "========================"
	@echo "Health Check:"
	@curl -s http://localhost:8000/api/health/ | head -5
	@echo ""
	@echo "API Info:"
	@curl -s http://localhost:8000/api/info/ | head -5

# Documentation
docs: ## Generate API documentation
	docker-compose exec backend python manage.py spectacular --file schema.yml
	@echo "API schema generated: schema.yml"

# Quick Setup
setup: ## Initial setup for new environment
	@echo "Setting up AgriSight platform..."
	docker-compose up -d postgres redis
	sleep 10
	docker-compose exec backend python manage.py migrate
	docker-compose exec backend python manage.py collectstatic --noinput
	docker-compose up -d
	@echo "Setup complete! Run 'make createsuperuser' to create an admin user."

# Environment Management
env-check: ## Check environment variables
	@echo "Checking environment configuration..."
	@echo "===================================="
	@docker-compose config

# Performance Testing
load-test: ## Run basic load test
	@echo "Running basic load test..."
	@for i in {1..10}; do \
		curl -s -o /dev/null -w "Request $$i: %{http_code} - %{time_total}s\n" http://localhost:8000/api/health/; \
	done

# Quick Commands
quick-restart: ## Quick restart (stop, build, start)
	docker-compose down && docker-compose up --build -d

quick-logs: ## Quick view of recent logs
	docker-compose logs --tail=50

quick-status: ## Quick status check
	docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Maintenance Tasks
maintenance: ## Run maintenance tasks
	@echo "Running maintenance tasks..."
	docker-compose exec backend python manage.py collectstatic --noinput
	docker-compose exec backend python manage.py migrate
	docker-compose exec backend python manage.py clearsessions
	@echo "Maintenance complete!"

# Emergency Commands
emergency-stop: ## Emergency stop all services
	docker-compose kill
	docker-compose rm -f

emergency-restart: ## Emergency restart all services
	docker-compose kill
	docker-compose rm -f
	docker-compose up -d

# Development Helpers
dev-shell: ## Open development shell with all services
	docker-compose exec backend bash

dev-logs: ## Follow logs for development
	docker-compose logs -f backend frontend

dev-reset: ## Reset development environment
	docker-compose down -v
	docker-compose up --build -d
	sleep 15
	docker-compose exec backend python manage.py migrate
	docker-compose exec backend python manage.py collectstatic --noinput
	@echo "Development environment reset complete!"
