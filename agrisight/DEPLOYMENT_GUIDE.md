# AgriSight Platform - Deployment Guide

## Quick Start Deployment

### 1. Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- 20GB available disk space

### 2. Initial Setup

```bash
# Extract the project
unzip agrisight-platform.zip
cd agrisight

# Copy environment file
cp .env .env.local

# Edit environment variables (optional for development)
nano .env.local
```

### 3. Start the Platform

```bash
# Build and start all services
docker-compose up --build -d

# Wait for services to start (about 2-3 minutes)
docker-compose logs -f backend

# When you see "Booting worker with pid", the backend is ready
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec backend python manage.py migrate

# Create a superuser account
docker-compose exec backend python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata sample_data.json
```

### 5. Access the Platform

- **Main Application**: http://localhost
- **API Documentation**: http://localhost/api/docs/
- **Admin Interface**: http://localhost/admin/
- **HAProxy Stats**: http://localhost:8404/stats

## Service Architecture

The platform runs the following services:

1. **postgres**: PostgreSQL 15 with PostGIS extension
2. **redis**: Redis 7 for caching and message brokering
3. **backend**: Django application server
4. **celery_worker**: Background task processor
5. **celery_beat**: Scheduled task scheduler
6. **frontend**: React development server
7. **nginx**: Reverse proxy and static file server
8. **haproxy**: Load balancer and high availability
9. **docker**: Docker-in-Docker for CI/CD

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_NAME=agrisight
DB_USER=agrisight_user
DB_PASSWORD=agrisight_password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Production Configuration

For production deployment:

1. **Security Settings**:
   ```bash
   DEBUG=False
   SECRET_KEY=generate-a-strong-secret-key
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

2. **Database Settings**:
   - Use managed PostgreSQL service
   - Enable SSL connections
   - Set up regular backups

3. **SSL/TLS**:
   - Configure SSL certificates in nginx
   - Enable HTTPS redirects
   - Update CORS settings

## Monitoring and Maintenance

### Health Checks

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs celery_worker

# Monitor resource usage
docker stats
```

### Database Maintenance

```bash
# Create database backup
docker-compose exec postgres pg_dump -U agrisight_user agrisight > backup.sql

# Restore database
docker-compose exec -T postgres psql -U agrisight_user agrisight < backup.sql

# Run database migrations
docker-compose exec backend python manage.py migrate
```

### Scaling

To scale Celery workers:

```bash
# Scale to 3 worker instances
docker-compose up --scale celery_worker=3 -d
```

## Troubleshooting

### Common Issues

1. **Services won't start**:
   ```bash
   # Check logs
   docker-compose logs
   
   # Rebuild containers
   docker-compose down
   docker-compose up --build
   ```

2. **Database connection errors**:
   ```bash
   # Restart PostgreSQL
   docker-compose restart postgres
   
   # Check PostgreSQL logs
   docker-compose logs postgres
   ```

3. **Permission errors**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Performance Optimization

1. **Database**:
   - Add database indexes for frequently queried fields
   - Configure PostgreSQL memory settings
   - Enable query optimization

2. **Caching**:
   - Configure Redis memory limits
   - Implement application-level caching
   - Use CDN for static files

3. **Application**:
   - Increase Gunicorn workers
   - Configure connection pooling
   - Enable gzip compression

## Security Considerations

### Production Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS encryption
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup and disaster recovery plan

### API Security

- Token-based authentication
- Rate limiting
- Input validation
- CORS configuration
- API key management

## Support

For technical issues:
1. Check the logs: `docker-compose logs`
2. Review the troubleshooting section
3. Check GitHub issues
4. Contact support team

## Next Steps

After successful deployment:

1. **Configure Organizations**: Set up your first organization and subscription plan
2. **Add Regions**: Define geographic regions for monitoring
3. **Set Up Users**: Create user accounts and assign permissions
4. **Configure Alerts**: Set up automated alert rules
5. **Test API**: Use the API documentation to test endpoints
6. **Customize Frontend**: Modify the React frontend as needed

The platform is now ready for satellite data ingestion and agricultural monitoring!

