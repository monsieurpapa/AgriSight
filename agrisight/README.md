# AgriSight Platform

This document is the operational README for the platform code in `agrisight/`.

## Stack
- Backend: Django 4.x, Django REST Framework, PostGIS
- Frontend: React 18, Vite, Tailwind, Radix UI
- Async: Celery + Redis
- Infra: Docker Compose, Nginx, HAProxy

## Running the Platform
From `agrisight/`:

```bash
# Build and start services
make up-build

# Check service status
make status

# Tail logs
make logs
```

## First-Time Setup
```bash
# Start core services and initialize
make setup

# Create an admin user
make createsuperuser
```

## Tests
```bash
# Backend test suite
make test-backend-full

# Frontend tests
make test-frontend
```

## Useful Commands
```bash
make help
make migrate
make collectstatic
make health-check
make down-clean
```

## Authentication Notes
- Session-based authentication (CSRF protected)
- Login endpoint: `/api/auth/login/`
- Current user endpoint: `/api/auth/user/`
- CSRF endpoint: `/api/auth/csrf/`

## Docs Index
See `DOCUMENTATION_INDEX.md` for the full documentation map.

## Windows Helpers
- `agrisight.ps1` (PowerShell)
- `agrisight.bat` (CMD)

## Environment
- Backend: `backend/.env`
- Frontend: `frontend/.env`

## Support
Create an issue with logs and reproduction steps when reporting problems.
