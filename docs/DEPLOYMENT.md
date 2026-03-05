# Deployment & CI/CD Guide

This document explains the AgriSight deployment lifecycle and how to manage the infrastructure.

## 🏗️ Deployment Architecture

AgriSight is containerized for consistent behavior across environments.

- **Storage**: PostgreSQL (PostGIS) for relational and spatial data, Redis for task queue.
- **Processing**: Celery Workers for satellite data.
- **App**: Gunicorn (Backend) and Nginx/Radix (Frontend), load balanced by HAProxy.

## 🚀 CI/CD Pipeline

The project uses **GitHub Actions** located in `.github/workflows/ci.yml`.

### Workflow Steps:
1. **Linting**: Both Python (Flake8) and JavaScript (ESLint) are checked.
2. **Backend Testing**: Runs `pytest` with a mock spatial database.
3. **Frontend Build**: Verifies the Vite/PWA build process.
4. **Container Scan**: (Planned) Vulnerability scanning for base images.

### Automated Quality Gates:
- Pull Requests must pass all CI checks before being merged into `develop`.
- Direct pushes to `main` are restricted.

---

## 🛠️ Production Setup

### 1. Provisioning
1. Choose a Linux VPS (Ubuntu 22.04+ recommended).
2. Install Docker and Docker Compose.
3. Ensure ports 80 and 443 are open.

### 2. Secrets Management
Define the following in your production `.env`:
- `SECRET_KEY`: Long, random string.
- `DEBUG`: `False`.
- `SENTINEL_HUB_CLIENT_ID`: Your production credentials.
- `SENTRY_DSN`: Error tracking DSN.
- `ALLOWED_HOSTS`: Your production domain.

### 3. SSL Configuration
AgriSight uses Nginx as a reverse proxy.

1. **Activate SSL**: Uncomment the SSL blocks in `agrisight/nginx/nginx.conf`.
2. **Certificates**: Place your SSL certificates in the designated project volume or use Certbot to manage them.

```bash
# Example Certbot command
docker run -it --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  certbot/certbot certonly --webroot ...
```

### 4. Zero-Downtime Updates
To update the application without downtime:
```bash
docker-compose pull
docker-compose up -d --no-deps --build backend frontend
```

---

## 📅 Maintenance Schedule
- **Weekly**: Check Flower for stuck tasks.
- **Monthly**: Review security advisories for dependencies (`npm audit`, `safety`).
- **Quarterly**: DB index optimization and archival of old satellite imagery metadata.
