# Operations Manual

This document outlines the operational procedures for maintaining the AgriSight platform in production.

## 💾 Disaster Recovery & Backups

### Database Backups
Automated backups are handled by the `agrisight/scripts/backup_db.sh` script.

- **Schedule**: Recommended daily via cron.
- **Retention**: Local script retains the last 7 days of backups.
- **Storage**: Backups are stored in `agrisight/backups` (ensure this volume is synced to off-site storage).

**Manual Backup Trigger**:
```bash
./agrisight/scripts/backup_db.sh
```

### Media Files
User-uploaded media and processed satellite data should be backed up using cloud provider tools (e.g., AWS S3 versioning) if external storage is used. For local volumes, utilize `rsync` or similar block-level backup tools.

---

## 🔍 Monitoring & Observability

### Celery Tasks (Flower)
Monitor background satellite processing and alerting tasks in real-time.
- **URL**: `http://localhost:5555`
- **Utility**: check task success rates, execution times, and worker health.

### Logging
Standard logs are aggregated by Docker.
- **Backend Logs**: `docker-compose logs -f backend`
- **Persistent Logs**: Stored in `agrisight/backend/logs/agrisight.log`.

### Error Tracking (Sentry)
Sentry is configured to catch unhandled exceptions in both the Django backend and React frontend.
- **Dashboard**: Check your configured Sentry project for crash reports and performance bottlenecks.
- **Alerts**: Critical errors trigger notifications to the engineering team.

---

## ⚖️ Scaling & Performance

### Horizontal Scaling
The system is designed to scale horizontally using HAProxy.
- **Web Tier**: Scale the `backend` and `frontend` services in `docker-compose.yml`.
- **Worker Tier**: Add more `celery_worker` instances to handle spikes in satellite data ingestion.

### Database Performance
- **Connection Pooling**: `CONN_MAX_AGE` is set to 600s to minimize handshake overhead.
- **Indexing**: PostGIS spatial indices are active on the `Region` and `SatelliteImage` models.

---

## 🛡️ Security Maintenance
- **Patch Management**: Regularly run `docker-compose pull` to get the latest security updates for base images.
- **Audit Trails**: Monitor the `HistoricalRecords` in the Django Admin for suspicious data modifications.
- **API Keys**: Rotate developer API keys every 90 days.
