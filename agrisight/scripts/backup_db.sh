#!/bin/bash
# Database backup script for AgriSight

set -e

BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/agrisight_db_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "Starting database backup to ${BACKUP_FILE}..."

# Export database using pg_dump
# Assumes PGHOST, PGUSER, PGPASSWORD are set or provided in environment
docker-compose exec -T postgres pg_dump -U agrisight_user agrisight | gzip > "${BACKUP_FILE}"

# Keep only the last 7 days of backups
find "${BACKUP_DIR}" -name "agrisight_db_*.sql.gz" -mtime +7 -delete

echo "Backup completed successfully."
