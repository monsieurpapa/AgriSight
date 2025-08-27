FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install uv and dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY celery_beat/requirements.txt /app/requirements.txt
RUN UV_SYSTEM_PYTHON=1 uv pip install --system -r requirements.txt

# Copy backend code (needed for Django models and settings)
COPY backend /app/

# Copy beat-specific files
COPY celery_beat/beat_config.py /app/

# Run Celery Beat
CMD ["celery", "-A", "agrisight.celery", "beat", "--loglevel=info", "--scheduler=django_celery_beat.schedulers:DatabaseScheduler"]

