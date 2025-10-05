# AgriSight New Features Testing Guide

This guide provides comprehensive testing instructions for all the newly implemented features in AgriSight.

## 🚀 Quick Start

### Prerequisites
1. **Start Docker Desktop** - Ensure Docker Desktop is running
2. **Navigate to project directory** - `cd agrisight`
3. **Start all services** - `docker-compose up --build -d`

### Automated Testing
Run the comprehensive test suite:
```bash
python test_new_features.py
```

## 🧪 Manual Testing Guide

### 1. Health Check Endpoints

Test the new health monitoring system:

```bash
# Basic health check
curl http://localhost:8000/health/

# Detailed health check (includes database, Redis, Celery)
curl http://localhost:8000/health/detailed/
```

**Expected Results:**
- ✅ Status: "healthy"
- ✅ All services (database, Redis, Celery) show "healthy"
- ✅ Security headers present (X-Frame-Options, CSP, etc.)

### 2. Real Satellite Data Processing

Test the new satellite processing functionality:

#### 2.1 Processing Statistics
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/satellite-processing/statistics/
```

#### 2.2 Vegetation Data Retrieval
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/satellite-processing/vegetation/REGION_ID/
```

#### 2.3 Trend Analysis
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"region_id": "REGION_ID", "months_back": 12}' \
  http://localhost:8000/api/v1/satellite-processing/trend-analysis/
```

**Expected Results:**
- ✅ Real vegetation index calculations (NDVI, EVI, NDWI, SAVI)
- ✅ Historical baseline comparison
- ✅ Automated stress detection
- ✅ Celery background processing

### 3. Machine Learning Models

Test the new ML models functionality:

#### 3.1 Create ML Model
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Stress Detection Model",
    "model_type": "stress_detection",
    "algorithm": "random_forest",
    "version": "1.0.0",
    "description": "Test model for agricultural stress detection"
  }' \
  http://localhost:8000/api/v1/ml-models/models/
```

#### 3.2 Start Model Training
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_config": {"validation_split": 0.2},
    "data_sources": ["mock_training_data"]
  }' \
  http://localhost:8000/api/v1/ml-models/models/MODEL_ID/train/
```

#### 3.3 Make Predictions
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_features": {
      "NDVI_mean": 0.65,
      "EVI_mean": 0.55,
      "NDWI_mean": 0.25,
      "SAVI_mean": 0.60
    }
  }' \
  http://localhost:8000/api/v1/ml-models/models/MODEL_ID/predict/
```

**Expected Results:**
- ✅ Model creation and training
- ✅ Real-time predictions with confidence scores
- ✅ Feature importance analysis
- ✅ Performance metrics tracking

### 4. Security Features

Test the new security middleware:

#### 4.1 Rate Limiting
```bash
# Make multiple rapid requests to test rate limiting
for i in {1..10}; do
  curl http://localhost:8000/api/v1/geospatial/regions/
  sleep 0.1
done
```

#### 4.2 Security Headers
```bash
curl -I http://localhost:8000/api/schema/
```

**Expected Results:**
- ✅ Rate limiting: 429 status after 100 requests/hour
- ✅ Security headers present:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Content-Security-Policy: default-src 'self'`

### 5. Error Handling & Logging

Test comprehensive error handling:

#### 5.1 404 Error Handling
```bash
curl http://localhost:8000/api/v1/nonexistent-endpoint/
```

#### 5.2 Validation Error Handling
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}' \
  http://localhost:8000/api/v1/geospatial/regions/
```

**Expected Results:**
- ✅ Proper HTTP status codes (404, 400, 500)
- ✅ Structured error responses
- ✅ Request/response logging

### 6. Celery Background Tasks

Test asynchronous processing:

#### 6.1 Check Celery Worker Status
```bash
docker-compose logs celery_worker
```

#### 6.2 Check Celery Beat Status
```bash
docker-compose logs celery_beat
```

**Expected Results:**
- ✅ Celery worker processing tasks
- ✅ Celery beat scheduling periodic tasks
- ✅ Background satellite data processing
- ✅ ML model training in background

## 🔍 Troubleshooting

### Common Issues

#### 1. Docker Desktop Not Running
**Error:** `unable to get image 'nginx:alpine': error during connect`
**Solution:** Start Docker Desktop manually

#### 2. Database Connection Issues
**Error:** `django.db.utils.OperationalError: could not connect to server`
**Solution:** 
```bash
docker-compose down --volumes
docker-compose up --build -d
```

#### 3. Celery Worker Not Processing Tasks
**Error:** Tasks stuck in PENDING state
**Solution:**
```bash
docker-compose restart celery_worker
```

#### 4. Missing Dependencies
**Error:** `ModuleNotFoundError: No module named 'joblib'`
**Solution:** Check requirements.txt includes all new dependencies

### Debug Commands

#### Check Service Status
```bash
docker-compose ps
```

#### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs celery_worker
docker-compose logs postgres
```

#### Check Database
```bash
docker-compose exec postgres psql -U agrisight_user -d agrisight
```

#### Check Redis
```bash
docker-compose exec redis redis-cli ping
```

## 📊 Performance Testing

### Load Testing
```bash
# Install Apache Bench
# Test API endpoints under load
ab -n 100 -c 10 http://localhost:8000/api/v1/geospatial/regions/
```

### Memory Usage
```bash
# Check container resource usage
docker stats
```

## ✅ Feature Verification Checklist

### Core Features
- [ ] Health check endpoints working
- [ ] User authentication and registration
- [ ] Organization management
- [ ] Region management with geospatial data
- [ ] Satellite data processing
- [ ] ML model training and prediction
- [ ] Celery background tasks
- [ ] Security headers and rate limiting
- [ ] Error handling and logging

### New Features
- [ ] Real satellite data processing (not mock data)
- [ ] Comprehensive ML models (stress detection, crop classification, anomaly detection)
- [ ] Production-ready security middleware
- [ ] Advanced error handling with proper HTTP status codes
- [ ] Request/response logging and monitoring
- [ ] Health check endpoints for all services

### Integration
- [ ] All services start successfully
- [ ] Database migrations complete
- [ ] Static files collected
- [ ] Celery tasks execute properly
- [ ] API documentation accessible at `/api/docs/`
- [ ] Frontend connects to backend successfully

## 🎯 Success Criteria

All tests should pass with:
- ✅ **100% test success rate** from automated test suite
- ✅ **All health checks** showing "healthy" status
- ✅ **Security headers** present on all responses
- ✅ **Rate limiting** working correctly
- ✅ **ML models** training and making predictions
- ✅ **Satellite processing** running without mock data
- ✅ **Background tasks** executing properly
- ✅ **Error handling** returning appropriate HTTP status codes

## 📝 Test Results Documentation

After running tests, document results:
1. **Test execution time**
2. **Pass/fail counts**
3. **Performance metrics**
4. **Any errors or warnings**
5. **Service health status**

This ensures all new features are production-ready and working correctly!
