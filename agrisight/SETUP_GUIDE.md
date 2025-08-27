# AgriSight Setup Guide with Sentinel Hub Integration

## Prerequisites

Before setting up AgriSight with Sentinel Hub integration, ensure you have:

1. **Docker and Docker Compose** installed
2. **Git** for version control
3. **Sentinel Hub account** with API credentials

## Step 1: Sentinel Hub Account Setup

### 1.1 Create Copernicus Data Space Account

1. Visit [https://dataspace.copernicus.eu/](https://dataspace.copernicus.eu/)
2. Click "Register" and create a new account
3. Verify your email address
4. Log in to your account

### 1.2 Create OAuth Client

1. Navigate to the **APIs** section in your dashboard
2. Click **"Create new OAuth client"**
3. Fill in the details:
   - **Name:** AgriSight Platform
   - **Description:** Agricultural monitoring platform for DRC
   - **Redirect URIs:** (leave empty for server-to-server)
   - **Grant Types:** Select "Client Credentials"
4. Click **"Create"**
5. **Save your credentials:**
   - Client ID (e.g., `sh-12345678-1234-1234-1234-123456789abc`)
   - Client Secret (e.g., `abcdef123456789...`)

### 1.3 Verify API Access

Test your credentials using curl:

```bash
curl -X POST \
  https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET'
```

You should receive a JSON response with an `access_token`.

## Step 2: AgriSight Platform Setup

### 2.1 Clone and Configure

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd agrisight

# Copy environment template
cp .env.example .env
```

### 2.2 Configure Environment Variables

Edit the `.env` file with your settings:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings
DB_NAME=agrisight
DB_USER=agrisight_user
DB_PASSWORD=agrisight_password
DB_HOST=postgres
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://redis:6379/1

# Celery Settings
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Frontend Settings
REACT_APP_API_URL=http://localhost/api

# Sentinel Hub Configuration (IMPORTANT!)
SENTINEL_HUB_CLIENT_ID=your_client_id_from_step_1.2
SENTINEL_HUB_CLIENT_SECRET=your_client_secret_from_step_1.2
SENTINEL_HUB_BASE_URL=https://sh.dataspace.copernicus.eu/api/v1
SENTINEL_HUB_OAUTH_URL=https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token
```

### 2.3 Build and Start Services

```bash
# Build all services
docker-compose build

# Start the platform
docker-compose up -d

# Check service status
docker-compose ps
```

Expected output:
```
Name                    Command               State           Ports
------------------------------------------------------------------------
agrisight_backend_1     gunicorn agrisight.wsgi:ap...   Up      8000/tcp
agrisight_celery_1      celery -A tasks worker --l...   Up
agrisight_celery_beat_1 celery -A tasks beat --lev...   Up
agrisight_frontend_1    npm start                       Up      3000/tcp
agrisight_haproxy_1     haproxy -f /usr/local/etc/...   Up      0.0.0.0:80->80/tcp
agrisight_nginx_1       nginx -g daemon off;            Up      80/tcp
agrisight_postgres_1    docker-entrypoint.sh postgres  Up      5432/tcp
agrisight_redis_1       docker-entrypoint.sh redis...  Up      6379/tcp
```

### 2.4 Initialize Database

```bash
# Run database migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata fixtures/sample_data.json
```

## Step 3: Verify Sentinel Hub Integration

### 3.1 Test API Connection

```bash
# Run the Sentinel Hub integration test
docker-compose exec backend python test_sentinel_hub_standalone.py
```

Expected output:
```
Running Sentinel Hub Integration Tests (Standalone)
============================================================
Testing evalscript generation...
✓ NDVI evalscript generation works
✓ EVI evalscript generation works
...
✅ All tests passed!
```

### 3.2 Test Real API Call

Create a test script to verify real API access:

```bash
# Enter the backend container
docker-compose exec backend python manage.py shell
```

In the Django shell:

```python
from apps.sentinel_hub.client import SentinelHubClient
from datetime import datetime, timedelta

# Initialize client
client = SentinelHubClient()

# Test authentication
try:
    token = client._get_access_token()
    print(f"✅ Authentication successful! Token: {token[:20]}...")
except Exception as e:
    print(f"❌ Authentication failed: {e}")

# Test a small area request (Kinshasa, DRC)
bbox = [15.0, -4.5, 15.1, -4.4]  # Small 0.1x0.1 degree area
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
time_range = (
    start_date.strftime("%Y-%m-%dT00:00:00Z"),
    end_date.strftime("%Y-%m-%dT23:59:59Z")
)

try:
    response = client.get_vegetation_index(
        bbox=bbox,
        time_range=time_range,
        index_type='ndvi',
        width=64,  # Small size for testing
        height=64,
        max_cloud_coverage=80.0  # High threshold for testing
    )
    print(f"✅ NDVI request successful! Response size: {len(response.content)} bytes")
except Exception as e:
    print(f"❌ NDVI request failed: {e}")
```

## Step 4: Create Sample Data

### 4.1 Create Organizations and Regions

Access the Django admin interface at `http://localhost/admin/` and create:

1. **Organizations:**
   - Name: "UN World Food Programme"
   - Type: "humanitarian"
   - Subscription Plan: "professional"

2. **Regions:**
   - Name: "Goma Agricultural Zone"
   - Geometry: Polygon covering Goma area
   - Organizations: Link to WFP

### 4.2 Trigger Data Ingestion

```bash
# Manually trigger satellite data ingestion
docker-compose exec backend python manage.py shell
```

```python
from apps.sentinel_hub.tasks_sentinel_hub import ingest_sentinel_data_enhanced
from apps.geospatial.models import Region

# Get a region
region = Region.objects.first()

# Trigger ingestion for the last 7 days
from datetime import datetime, timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

task = ingest_sentinel_data_enhanced.delay(
    str(region.id),
    start_date.strftime("%Y-%m-%dT00:00:00Z"),
    end_date.strftime("%Y-%m-%dT23:59:59Z")
)

print(f"Task ID: {task.id}")
```

### 4.3 Monitor Processing

```bash
# Check Celery logs
docker-compose logs -f celery

# Check task status in Django shell
from celery.result import AsyncResult
result = AsyncResult('your-task-id-here')
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

## Step 5: Access the Platform

### 5.1 Web Interface

- **Frontend:** http://localhost/
- **Admin Interface:** http://localhost/admin/
- **API Documentation:** http://localhost/api/docs/

### 5.2 API Endpoints

Key API endpoints for Sentinel Hub integration:

```bash
# List regions
curl http://localhost/api/regions/

# Get vegetation indices for a region
curl http://localhost/api/regions/{id}/vegetation-indices/

# Get agricultural stress events
curl http://localhost/api/stress-events/

# Trigger manual processing
curl -X POST http://localhost/api/regions/{id}/process/
```

## Step 6: Production Deployment

### 6.1 Security Configuration

For production deployment:

1. **Change default passwords:**
   ```bash
   # Generate secure secret key
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   
   # Update .env file
   SECRET_KEY=your-generated-secret-key
   DEBUG=False
   ```

2. **Configure HTTPS:**
   - Update nginx configuration for SSL
   - Obtain SSL certificates (Let's Encrypt recommended)
   - Update ALLOWED_HOSTS in settings

3. **Database security:**
   - Use strong database passwords
   - Restrict database access
   - Enable database encryption

### 6.2 Monitoring Setup

1. **Application monitoring:**
   ```bash
   # Add monitoring services to docker-compose.yml
   # Consider: Prometheus, Grafana, ELK stack
   ```

2. **Log management:**
   ```bash
   # Configure log rotation
   # Set up centralized logging
   # Monitor error rates
   ```

3. **Performance monitoring:**
   ```bash
   # Monitor API response times
   # Track Sentinel Hub usage
   # Monitor resource utilization
   ```

## Troubleshooting

### Common Issues

#### 1. Sentinel Hub Authentication Errors

**Error:** `401 Unauthorized`

**Solution:**
- Verify client ID and secret in `.env` file
- Check if credentials are correctly set in Copernicus Data Space
- Ensure OAuth client has "Client Credentials" grant type

#### 2. No Satellite Data Available

**Error:** `400 Bad Request` or empty responses

**Solution:**
- Check if the requested time range has available imagery
- Increase `max_cloud_coverage` parameter
- Verify bbox coordinates are valid
- Try a different time period

#### 3. Processing Timeouts

**Error:** Task timeouts or slow responses

**Solution:**
- Reduce image resolution (width/height parameters)
- Process smaller areas
- Implement request queuing
- Check Sentinel Hub processing unit limits

#### 4. Database Connection Issues

**Error:** `django.db.utils.OperationalError`

**Solution:**
- Ensure PostgreSQL service is running
- Check database credentials in `.env`
- Verify PostGIS extension is installed
- Check network connectivity between services

### Getting Help

1. **Check logs:**
   ```bash
   docker-compose logs backend
   docker-compose logs celery
   ```

2. **Verify configuration:**
   ```bash
   docker-compose exec backend python manage.py check
   ```

3. **Test individual components:**
   ```bash
   docker-compose exec backend python test_sentinel_hub_standalone.py
   ```

4. **Contact support:**
   - AgriSight platform issues: [Create GitHub issue]
   - Sentinel Hub API issues: [Copernicus Data Space support]

## Next Steps

After successful setup:

1. **Configure monitoring regions** for your areas of interest
2. **Set up automated reporting** for stakeholders
3. **Customize alert thresholds** based on local conditions
4. **Train users** on the platform interface
5. **Establish data backup** and disaster recovery procedures

## Resources

- [Sentinel Hub Documentation](https://docs.sentinel-hub.com/)
- [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostGIS Documentation](https://postgis.net/documentation/)

