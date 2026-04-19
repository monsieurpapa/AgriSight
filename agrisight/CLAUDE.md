# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgriSight is a satellite-driven agricultural monitoring platform for food security in DRC conflict zones. It processes Sentinel-2/Landsat imagery, calculates vegetation indices (NDVI, EVI, NDWI, SAVI), and delivers real-time alerts via a Django + React stack.

## Common Commands

All operations go through the Makefile. On Windows use `agrisight.bat` or `agrisight.ps1` with the same targets.

```bash
# Start full stack
make up               # docker-compose up --build -d

# Stop
make down

# Logs
make logs-backend
make logs-frontend
make logs-celery

# Database
make migrate
make makemigrations
make db-reset         # drop + recreate + migrate (destructive)
make createsuperuser

# Testing
make test             # backend unit tests
make test-backend-full
make test-frontend    # vitest
make test-coverage

# Linting / formatting
make lint-backend     # flake8
make lint-frontend    # eslint
make format-backend   # black + isort
make format-frontend  # prettier

# Celery
make celery-worker
make celery-beat
make celery-flower    # Flower UI on :5555

# Health
make health-check
```

Running a single Django test:
```bash
docker-compose exec backend python manage.py test apps.<app_name>.tests.<TestClass>.<test_method>
```

Running a single Vitest test:
```bash
docker-compose exec frontend pnpm vitest run src/test/<file>.test.jsx
```

## Architecture

```
HAProxy (:8080) → Backend (Django/Gunicorn :8000)
                → Frontend (Nginx serving Vite dist/ :3000)
                → Nginx (:80) for static/media files
Backend → PostGIS (postgres :5432)
        → Redis (:6379, DB0=Celery broker, DB1=cache)
Backend ← Celery Worker (async satellite processing, reports)
        ← Celery Beat (scheduled tasks)
```

### Backend (`backend/`)

Django 4.2.7 + DRF + GeoDjango + Channels (WebSockets). 12 custom apps under `backend/apps/`:

| App | Responsibility |
|-----|---------------|
| `authentication` | JWT + session auth, OAuth2 (Google/Facebook/GitHub), rate-limited login (3/hour) |
| `users` | Custom `AbstractUser` with `user_type` (admin/humanitarian/cooperative/government/researcher) |
| `organizations` | Multi-tenant — most models have an org FK |
| `geospatial` | `Region` (MultiPolygonField), `SatelliteImage`, `VegetationIndex` GeoDjango models |
| `core` | Middleware pipeline, WebSocket consumers, health-check endpoint |
| `sentinel_hub` | Sentinel Hub SDK integration, batch processing |
| `satellite_processing` | Raster ops — GDAL, Rasterio, Fiona, Shapely, geopandas |
| `analytics` | Aggregated metrics and time-series |
| `reports_alerts` | Alert generation, report export |
| `ml_models` | Anomaly detection with scikit-learn |
| `api_keys_logs` | API key management + audit trails |

**URL layout**: `/api/auth/` and `/api/core/` are unversioned; all domain endpoints live under `/api/v1/`.

**Base model classes**: `TimeStampedModel` and `SoftDeleteModel` — use these for new models. `HistoricalRecords` tracks audit history.

**Middleware order** (`core/middleware.py`): `HealthCheck → RequestLogging → ErrorHandling → SecurityHeaders → RateLimit → APIVersion`.

### Frontend (`frontend/`)

React 18 + Vite 6 + React Router 7 + Tailwind CSS 4 + Radix UI. State via Context API (no Redux).

Key contexts in `src/contexts/`:
- `AuthContext.jsx` — user state, `useAuth()` hook, RBAC `hasPermission()` check
- `WebSocketContext.jsx` — live alert feeds
- `ErrorContext.jsx` — global toast/error notifications

**API client** (`src/lib/apiClient.js`): Axios instance with CSRF token injection, auto-retry (3× with exponential backoff for 408/429/5xx), auto-redirect to `/login` on 401, and standardized error objects.

**Auth flow**:
1. GET `/api/auth/csrf/` → store token in axios interceptor state
2. POST `/api/auth/login/` → session cookie set
3. All subsequent requests carry session + CSRF header

**Routing** (`src/App.jsx`): Protected routes check `useAuth()`. Permission-gated routes use `hasPermission()` from AuthContext.

**Build-time env vars** (must be set at `docker-compose build` time):
```
VITE_API_BASE_URL   # defaults to http://localhost:8000 in dev, / in prod container
VITE_WS_URL         # WebSocket base, e.g. ws://localhost:8000/ws/
```

### Async Processing

Long-running ops (satellite imagery ingestion, report generation, ML inference) go through Celery tasks — never block Django request threads. Tasks live in `tasks.py` within each app.

### PWA & Caching

Service worker (configured in `vite.config.js`) caches:
- Sentinel Hub tile requests: CacheFirst, 30-day TTL
- API endpoints: NetworkFirst, 24-hour fallback

## Environment Setup

Copy `.env.example` → `.env` and fill in:
```
SENTINEL_HUB_CLIENT_ID=...
SENTINEL_HUB_CLIENT_SECRET=...
SECRET_KEY=<strong random string for prod>
```
DB credentials (`agrisight_user` / `agrisight_password`) and Redis URLs are pre-set for local Docker use.

## Key Documentation Files

- `DEVELOPMENT_GUIDE.md` — detailed local setup and workflow
- `DEPLOYMENT_GUIDE.md` — production deployment
- `USER_STORIES.md` — product requirements
- `STORY_IMPLEMENTATION_MATRIX.md` — story-to-code mapping

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health

## Design System
Always read `DESIGN.md` before making any visual or UI decisions.
All font choices, colors, spacing, border-radius, and aesthetic direction are defined there.
Do not deviate without explicit user approval.
In QA mode, flag any code that doesn't match `DESIGN.md`.

Key rules to enforce automatically:
- Never use `#8b5cf6`, `#7c3aed`, or `#8884d8` — replace with amber `#d29922` for conflict data
- Never use Inter, Roboto, Arial, or Open Sans as primary font — use Plus Jakarta Sans / DM Sans / JetBrains Mono
- All numeric data values (NDVI, event counts, IPC scores, timestamps) must use `font-family: var(--font-mono)`
- IPC phase colors are semantic constants — never modify them for aesthetic reasons
