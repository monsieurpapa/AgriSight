# AgriSight API Documentation

## Overview

The AgriSight API provides comprehensive access to agricultural monitoring data, satellite imagery processing, and analytics capabilities. The API follows RESTful principles and uses session-based authentication.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.agrisight.com`

## Authentication

AgriSight uses session-based authentication with CSRF protection.

### Getting Started

1. **Register/Login**: Use the authentication endpoints to create an account or log in
2. **CSRF Token**: Obtain a CSRF token for state-changing requests
3. **Session Cookie**: Maintain session cookies for authenticated requests

### CSRF Token

```http
GET /api/auth/csrf/
```

**Response:**
```json
{
  "csrfToken": "your-csrf-token-here"
}
```

## API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/registration/
Content-Type: application/json
X-CSRFToken: your-csrf-token

{
  "username": "user@example.com",
  "email": "user@example.com",
  "password1": "securepassword123",
  "password2": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json
X-CSRFToken: your-csrf-token

{
  "username": "user@example.com",
  "password": "securepassword123"
}
```

#### Logout
```http
POST /api/auth/logout/
X-CSRFToken: your-csrf-token
```

### Geospatial Data

#### Get Regions
```http
GET /api/v1/geospatial/regions/
```

**Response:**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Goma Agricultural Zone",
      "area_hectares": 24530.5,
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[29.0, 0.0], [29.1, 0.0], ...]]
      },
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Region Details
```http
GET /api/v1/geospatial/regions/{id}/
```

#### Get Vegetation Indices
```http
GET /api/v1/geospatial/vegetation-indices/?region_id={id}&days=30
```

**Response:**
```json
[
  {
    "id": 1,
    "index_type": "NDVI",
    "mean_value": 0.65,
    "min_value": 0.45,
    "max_value": 0.85,
    "std_deviation": 0.12,
    "satellite_image": {
      "id": "uuid",
      "acquisition_date": "2024-01-15T10:30:00Z",
      "region": "uuid"
    }
  }
]
```

### Satellite Processing

#### Trigger Processing
```http
POST /api/v1/satellite-processing/process/
Content-Type: application/json
X-CSRFToken: your-csrf-token

{
  "region_id": "uuid",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

#### Get Processing Status
```http
GET /api/v1/satellite-processing/status/{task_id}/
```

#### Get Region Vegetation Data
```http
GET /api/v1/satellite-processing/vegetation/{region_id}/?days=30&index_type=NDVI
```

#### Get Processing Statistics
```http
GET /api/v1/satellite-processing/statistics/
```

### Analytics

#### Get Stress Events
```http
GET /api/v1/analytics/stress-events/?region_id={id}&severity=high&days=30
```

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": "uuid",
      "stress_type": "drought",
      "severity": "high",
      "detection_date": "2024-01-15T10:30:00Z",
      "confidence_score": 0.85,
      "affected_area_hectares": 1250.5,
      "region": {
        "id": "uuid",
        "name": "Goma Agricultural Zone"
      }
    }
  ]
}
```

#### Get Stress Event Summary
```http
GET /api/v1/analytics/stress-events/summary/?days=30
```

**Response:**
```json
{
  "total_events": 25,
  "events_by_type": {
    "drought": 10,
    "flood": 8,
    "pest": 5,
    "disease": 2
  },
  "events_by_severity": {
    "high": 5,
    "medium": 12,
    "low": 8
  },
  "total_affected_area": 15670.5,
  "recent_events": [...]
}
```

#### Get Conflict Events
```http
GET /api/v1/analytics/conflict-events/?region_id={id}&intensity=high
```

#### Get Conflict Event Summary
```http
GET /api/v1/analytics/conflict-events/summary/?days=30
```

### Reports and Alerts

#### Get Alerts
```http
GET /api/v1/reports-alerts/alerts/?status=active&severity=high
```

#### Get Reports
```http
GET /api/v1/reports-alerts/reports/?region_id={id}&date_from=2024-01-01
```

#### Create Report
```http
POST /api/v1/reports-alerts/reports/
Content-Type: application/json
X-CSRFToken: your-csrf-token

{
  "title": "Monthly Agricultural Report",
  "description": "Comprehensive analysis for January 2024",
  "region_ids": ["uuid1", "uuid2"],
  "date_from": "2024-01-01",
  "date_to": "2024-01-31"
}
```

### Machine Learning Models

#### Get ML Models
```http
GET /api/v1/ml-models/
```

#### Get Model Details
```http
GET /api/v1/ml-models/{id}/
```

#### Trigger Model Training
```http
POST /api/v1/ml-models/{id}/train/
X-CSRFToken: your-csrf-token
```

## WebSocket API

### Connection

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/');
```

### Authentication

Send authentication message after connection:

```javascript
ws.send(JSON.stringify({
  type: 'auth',
  token: 'your-session-token'
}));
```

### Subscriptions

#### Subscribe to General Updates
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'general_updates'
}));
```

#### Subscribe to Region Updates
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'region_updates',
  region_id: 'uuid'
}));
```

#### Subscribe to Processing Updates
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'processing_updates',
  task_id: 'task-uuid'
}));
```

### Message Types

#### Stress Event Update
```json
{
  "type": "stress_event",
  "payload": {
    "id": "uuid",
    "stress_type": "drought",
    "severity": "high",
    "detection_date": "2024-01-15T10:30:00Z",
    "region": {
      "id": "uuid",
      "name": "Goma Agricultural Zone"
    }
  }
}
```

#### Processing Update
```json
{
  "type": "processing_update",
  "payload": {
    "task_id": "uuid",
    "status": "completed",
    "progress": 100,
    "message": "Processing completed successfully"
  }
}
```

#### System Alert
```json
{
  "type": "system_alert",
  "payload": {
    "id": "alert-id",
    "type": "system_maintenance",
    "message": "Scheduled maintenance in 1 hour",
    "severity": "info"
  }
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": "Error message",
  "details": "Detailed error information",
  "code": "ERROR_CODE"
}
```

## Rate Limiting

- **General API**: 100 requests per hour per IP
- **Authentication**: 10 requests per hour per IP
- **WebSocket**: No rate limiting (connection-based)

## Pagination

List endpoints support pagination:

```http
GET /api/v1/geospatial/regions/?page=2&page_size=20
```

**Response:**
```json
{
  "count": 100,
  "next": "http://api.agrisight.com/api/v1/geospatial/regions/?page=3",
  "previous": "http://api.agrisight.com/api/v1/geospatial/regions/?page=1",
  "results": [...]
}
```

## Filtering and Search

Most list endpoints support filtering:

```http
GET /api/v1/analytics/stress-events/?region_id=uuid&severity=high&date_from=2024-01-01&date_to=2024-01-31
```

## Data Formats

### Date/Time
- All dates are in ISO 8601 format: `2024-01-15T10:30:00Z`
- Timezone is UTC unless specified

### Geographic Data
- Coordinates use WGS84 (EPSG:4326)
- GeoJSON format for geometries
- Areas in hectares

### Vegetation Indices
- NDVI: -1 to 1 (typically 0 to 1 for vegetation)
- EVI: -1 to 1
- NDWI: -1 to 1
- SAVI: -1 to 1

## SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install agrisight-js-sdk
```

```javascript
import { AgriSightClient } from 'agrisight-js-sdk';

const client = new AgriSightClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

const regions = await client.regions.list();
```

### Python
```bash
pip install agrisight-python-sdk
```

```python
from agrisight import AgriSightClient

client = AgriSightClient(
    base_url='http://localhost:8000',
    api_key='your-api-key'
)

regions = client.regions.list()
```

## Examples

### Complete Workflow Example

```javascript
// 1. Authenticate
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password'
  })
});

// 2. Get regions
const regionsResponse = await fetch('/api/v1/geospatial/regions/');
const regions = await regionsResponse.json();

// 3. Get vegetation data for first region
const regionId = regions.results[0].id;
const vegetationResponse = await fetch(
  `/api/v1/satellite-processing/vegetation/${regionId}/?days=30`
);
const vegetationData = await vegetationResponse.json();

// 4. Set up WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

## Support

For API support and questions:
- **Documentation**: [API Docs](http://localhost:8000/api/docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/AgriSight/issues)
- **Email**: api-support@agrisight.com

---

*Last updated: January 2024*
