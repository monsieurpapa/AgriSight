# Architecture & Workflows

AgriSight is built with a decoupled architecture focusing on scalability, reliability, and geospatial precision.

## System Overview

```mermaid
graph TD
    User((User)) -->|HTTPS| Proxy[HAProxy]
    Proxy -->|Load Balance| Nginx[Nginx]
    Nginx -->|Static/PWA| Frontend[React PWA]
    Nginx -->|API Requests| Backend[Django API]
    
    Backend -->|PostGIS Queries| DB[(PostgreSQL)]
    Backend -->|Enqueue Tasks| Redis[Redis]
    Redis -->|Process| Worker[Celery Worker]
    
    Worker -->|Fetch Data| Sentinel[Sentinel Hub API]
    Worker -->|Store Metrics| DB
    
    Worker -->|Real-time Events| Redis
    Redis -->|Push| WS[WebSocket Server]
    WS -->|Live Updates| Frontend
```

---

## Core Workflows

### 1. Authentication Handshake (JWT-in-Cookies)
The system uses HTTP-Only cookies to protect against XSS while maintaining a stateless backend.

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend (React)
    participant B as Backend (Django)
    
    U->>F: Enter Credentials
    F->>B: POST /api/auth/login/
    Note over B: Validate User
    B-->>F: 200 OK + Set-Cookie (Access & Refresh)
    Note right of F: Browsers stores HTTP-Only cookies
    
    F->>B: GET /api/v1/data/
    Note over B: Middleware extracts JWT from Cookie
    B-->>F: Authenticated Data
```

### 2. Satellite Data Pipeline
How satellite imagery becomes actionable agricultural insights.

```mermaid
sequenceDiagram
    participant S as Scheduler (Celery Beat)
    participant W as Worker
    participant SH as Sentinel Hub
    participant P as PostGIS
    
    S->>W: Trigger "Sync Region" Task
    W->>SH: Request multi-spectral bands (NIR, Red, etc)
    SH-->>W: Raw GeoTIFF data
    W->>W: Calculate Indices (NDVI, EVI)
    W->>W: Cloud Masking & Correction
    W->>P: Save Stats & Raster Metadata
    Note over P: Spatial indexing active
```

### 3. Real-time Anomaly Detection
The flow from detection to user notification.

```mermaid
graph LR
    Detection[Analytics Engine] -->|Anomaly Found| Alert[Create Alert Record]
    Alert -->|Publish| Channel[Redis Pub/Sub]
    Channel -->|Broadcast| WS[WebSocket Server]
    WS -->|Notification| Browser[React UI]
    Alert -->|Email| Notification[Email Service]
```

---

## Module breakdown

### Backend (Django Apps)
- `apps.geospatial`: PostGIS models for regions and satellite metadata.
- `apps.satellite_processing`: Task logic for calculating vegetation indices.
- `apps.analytics`: Stress detection algorithms and trend analysis.
- `apps.core`: Base models (SoftDelete, Timestamped) and custom middleware.

### Frontend (React)
- `src/pages`: Main view logic (Dashboard, MapView).
- `src/lib/apiClient`: Centralized Axios instance with refresh interceptors.
- `src/components/ui`: Radix-based design system.
- `src/contexts`: Global state for Auth, WebSockets, and Errors.
