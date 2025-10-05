FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for GeoDjango and GDAL
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

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# Set work directory
WORKDIR /app

# Install uv and dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY backend/requirements.txt /app/requirements.txt
RUN UV_SYSTEM_PYTHON=1 uv pip install --system -r requirements.txt

# Copy backend code (needed for Django models and settings)
COPY backend /app/

# Copy worker-specific files
COPY celery_worker/tasks.py /app/
COPY celery_worker/tasks_sentinel_hub.py /app/

# Run Celery worker
CMD ["celery", "-A", "agrisight.celery", "worker", "--loglevel=info", "--concurrency=2"]

