# API Guide

AgriSight provides a RESTful API for programmatic access to satellite intelligence and agricultural metrics.

## 🔐 Authentication

AgriSight uses **JWT-in-HTTP-Only-Cookies** for browser-based sessions. For external API consumers, specify the `Authorization` header.

```bash
Authorization: Bearer <your_jwt_token>
```

---

## 📍 Core Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/geospatial/regions/` | GET | List all monitored regions. |
| `/api/v1/satellite-processing/process/` | POST | Trigger satellite data ingestion for a region. |
| `/api/v1/analytics/stress-events/` | GET | Get vegetation stress events. |
| `/api/v1/reports-alerts/alerts/` | GET | List system alerts. |

## 📊 Response Format
All responses are returned in JSON format.

```json
{
  "status": "success",
  "data": { ... },
  "metadata": {
    "count": 10,
    "next": "...",
    "previous": null
  }
}
```

---

## 🛠️ Errors & Rate Limiting

### Error Handling
Errors follow a standardized JSON structure:
```json
{
  "error": "Not Found",
  "detail": "The requested region ID does not exist.",
  "code": 404
}
```

### Rate Limiting
- **Default**: 100 requests per hour per IP (Configurable in `settings.py`).
- **Headers**: Check `X-RateLimit-Limit` and `X-RateLimit-Remaining` for current status.

## 📖 Interactive Documentation
Visit the following URLs (when the stack is running) for interactive Swagger/Redoc:
- **Swagger UI**: `http://localhost/api/v1/schema/swagger-ui/`
- **ReDoc**: `http://localhost/api/v1/schema/redoc/`
