FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

## Install system dependencies for GeoDjango and GDAL
## Use noninteractive frontend and --no-install-recommends to reduce memory/disk pressure
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
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
       libpango-1.0-0 \
       libpangoft2-1.0-0 \
       libpangocairo-1.0-0 \
       libcairo2 \
       libgdk-pixbuf2.0-0 \
       libffi-dev \
       shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# Set work directory
WORKDIR /app

# Install uv and Python dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY requirements.txt /app/
RUN UV_SYSTEM_PYTHON=1 uv pip install --system -r requirements.txt

# Copy project
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "agrisight.wsgi:application"]

