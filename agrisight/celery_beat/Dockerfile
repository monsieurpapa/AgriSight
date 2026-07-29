FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (GDAL/GEOS/PROJ and build tools)
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libgeos-dev \
    libspatialite-dev \
    spatialite-bin \
    libsqlite3-mod-spatialite \
    postgresql-client \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install uv and dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY backend/requirements.txt /app/requirements.txt
RUN UV_SYSTEM_PYTHON=1 uv pip install --system -r requirements.txt

# Copy backend code (needed for Django models and settings)
COPY backend /app/

# Copy beat-specific files
COPY celery_beat/beat_config.py /app/

# Run Celery Beat
CMD ["celery", "-A", "agrisight.celery", "beat", "--loglevel=info", "--scheduler=django_celery_beat.schedulers:DatabaseScheduler"]

