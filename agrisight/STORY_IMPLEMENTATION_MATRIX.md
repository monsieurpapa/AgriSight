# AgriSight Story-to-Implementation Matrix (RBAC Focus)

This matrix maps each user story to current backend endpoints, frontend screens, and RBAC access rules as implemented in the codebase.

Legend:
- FE Route: React route in `agrisight/frontend/src/App.jsx`
- BE Endpoint: Django route from `agrisight/backend/agrisight/urls.py` and app `urls.py`
- RBAC: Permission enforced in FE route guard (`PermissionRoute`) + expected backend authorization (currently DRF `IsAuthenticated` with model/query filtering by org/role where implemented)

## Epic 1: User Authentication & Access Management

1.1 User Registration  
FE: `/register` (`Register.jsx`)  
BE: `POST /api/auth/registration/`  
RBAC: Public. No permission required.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Register.jsx`, `agrisight/backend/apps/authentication/views.py`, `agrisight/backend/agrisight/settings.py`, `agrisight/backend/apps/authentication/serializers.py`, `agrisight/backend/apps/authentication/tests.py`, `agrisight/AUTHENTICATION_ARCHITECTURE.md`, `agrisight/AUTHENTICATION_SYNCHRONIZATION.md`

1.2 User Login  
FE: `/login` (`Login.jsx`)  
BE: `POST /api/auth/login/`, `GET /api/auth/user/`, `GET /api/auth/config/`, `GET /api/auth/csrf/`  
RBAC: Public. Session established; redirect uses role-based default path.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Login.jsx`, `agrisight/frontend/src/contexts/AuthContext.jsx`, `agrisight/backend/apps/authentication/views.py`, `agrisight/backend/apps/authentication/tests.py`, `agrisight/AUTHENTICATION_ARCHITECTURE.md`

1.3 Password Recovery  
FE: `/forgot-password` (`ForgotPassword.jsx`), `/reset-password` (`ResetPassword.jsx`)  
BE: `POST /api/auth/password/reset/`, `POST /api/auth/password/reset/confirm/`  
RBAC: Public.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/ForgotPassword.jsx`, `agrisight/frontend/src/pages/ResetPassword.jsx`, `agrisight/backend/apps/authentication/views.py`, `agrisight/backend/agrisight/settings.py`, `agrisight/backend/apps/authentication/tests.py`, `agrisight/AUTHENTICATION_ARCHITECTURE.md`

1.4 Profile Management  
FE: `/profile` (`Profile.jsx`), `/settings` (`Settings.jsx`)  
BE: `GET /api/auth/user/`, `PATCH /api/auth/user/`, `POST /api/auth/password/change/`  
RBAC: Authenticated. No special permission.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Profile.jsx`, `agrisight/frontend/src/pages/Settings.jsx`, `agrisight/backend/apps/authentication/views.py`, `agrisight/backend/apps/authentication/tests.py`, `agrisight/AUTHENTICATION_ARCHITECTURE.md`

---

## Epic 2: Dashboard & Overview

2.1 Main Dashboard  
FE: `/` (`Dashboard.jsx`)  
BE: `GET /api/v1/geospatial/regions/`, `GET /api/v1/reports-alerts/alerts/`, `GET /api/v1/reports-alerts/reports/`, `GET /api/v1/satellite-processing/statistics/`, `GET /api/v1/analytics/stress-events/summary/`, `GET /api/v1/analytics/conflict-events/summary/`  
RBAC: FE requires `view_data`. Backend: authenticated; per-region/org scoping should be enforced in queryset logic.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Dashboard.jsx`, `agrisight/frontend/src/lib/api.js`, `agrisight/backend/apps/satellite_processing/views.py`, `agrisight/backend/apps/analytics/views.py`, `agrisight/backend/apps/geospatial/views.py`, `agrisight/backend/apps/reports_alerts/views.py`, `agrisight/backend/apps/analytics/tests.py`, `agrisight/backend/apps/geospatial/tests.py`, `agrisight/backend/apps/satellite_processing/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

2.2 Vegetation Trends Visualization  
FE: `/` (`Dashboard.jsx`)  
BE: `GET /api/v1/satellite-processing/vegetation/<region_id>/`  
RBAC: FE requires `view_data`; backend should scope to accessible regions.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Dashboard.jsx`, `agrisight/backend/apps/satellite_processing/urls.py`, `agrisight/backend/apps/satellite_processing/views.py`, `agrisight/backend/apps/satellite_processing/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

2.3 Region Health Status  
FE: `/` (`Dashboard.jsx`)  
BE: same as 2.1 + analytics summaries  
RBAC: FE `view_data`; backend should scope per region/org.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Dashboard.jsx`, `agrisight/backend/apps/analytics/views.py`, `agrisight/backend/apps/geospatial/views.py`, `agrisight/backend/apps/analytics/tests.py`, `agrisight/backend/apps/geospatial/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

2.4 Recent Activity Feed  
FE: `/` (`Dashboard.jsx`)  
BE: same as 2.1 + WebSocket feed  
RBAC: FE `view_data`; backend: authenticated + scoped.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Dashboard.jsx`, `agrisight/frontend/src/contexts/WebSocketContext.jsx`, `agrisight/backend/apps/core/consumers.py`, `agrisight/backend/apps/analytics/tests.py`, `agrisight/backend/apps/satellite_processing/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

---

## Epic 3: Interactive Mapping

3.1 Interactive Map View  
FE: `/map` (`MapView.jsx`)  
BE: `GET /api/v1/geospatial/regions/`, `GET /api/v1/analytics/stress-events/`  
RBAC: FE `view_data`; backend should scope to accessible regions.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/MapView.jsx`, `agrisight/frontend/src/lib/api.js`, `agrisight/backend/apps/geospatial/urls.py`, `agrisight/backend/apps/analytics/urls.py`, `agrisight/backend/apps/analytics/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

3.2 Region Selection & Details  
FE: `/map` (`MapView.jsx`)  
BE: `GET /api/v1/geospatial/regions/<id>/`, `GET /api/v1/satellite-processing/vegetation/<region_id>/`  
RBAC: FE `view_data`; backend should scope to accessible regions.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/MapView.jsx`, `agrisight/backend/apps/geospatial/views.py`, `agrisight/backend/apps/satellite_processing/views.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

3.3 Layer Controls  
FE: `/map` (`MapView.jsx`)  
BE: Same as 3.1/3.2  
RBAC: FE `view_data`.  
Status: Implemented (code + docs + UX)  
Evidence: `agrisight/frontend/src/pages/MapView.jsx`, `agrisight/FRONTEND_IMPLEMENTATION.md`

3.4 Stress Event Visualization  
FE: `/map` (`MapView.jsx`), `/stress-events` (`StressEvents.jsx`)  
BE: `GET /api/v1/analytics/stress-events/`  
RBAC: FE `view_stress_events`; backend should scope by region/org.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/MapView.jsx`, `agrisight/frontend/src/pages/StressEvents.jsx`, `agrisight/backend/apps/analytics/views.py`, `agrisight/backend/apps/analytics/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

---

## Epic 4: Analytics & Reporting

4.1 Stress Events Analysis  
FE: `/analytics` (`Analytics.jsx`), `/stress-events` (`StressEvents.jsx`)  
BE: `GET /api/v1/analytics/stress-events/`, `GET /api/v1/analytics/stress-events/summary/`  
RBAC: FE `view_analytics` (analytics), `view_stress_events` (stress list). Backend should scope.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Analytics.jsx`, `agrisight/frontend/src/pages/StressEvents.jsx`, `agrisight/backend/apps/analytics/views.py`, `agrisight/backend/apps/analytics/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

4.2 Conflict Events Analysis  
FE: `/analytics` (`Analytics.jsx`)  
BE: `GET /api/v1/analytics/conflict-events/`, `GET /api/v1/analytics/conflict-events/summary/`  
RBAC: FE `view_analytics`.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Analytics.jsx`, `agrisight/backend/apps/analytics/views.py`, `agrisight/backend/apps/analytics/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

4.3 Multi-Temporal Trend Analysis  
FE: `/analytics` (`Analytics.jsx`)  
BE: `GET /api/v1/satellite-processing/trend-analysis/`  
RBAC: FE `view_analytics`.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Analytics.jsx`, `agrisight/backend/apps/satellite_processing/views.py`, `agrisight/backend/apps/satellite_processing/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

4.4 Custom Report Generation  
FE: `/reports` (`Reports.jsx`)  
BE: `GET/POST/PUT/DELETE /api/v1/reports-alerts/reports/`, `GET /api/v1/reports-alerts/reports/<id>/download/`  
RBAC: FE `generate_reports`; backend should scope by org/region.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Reports.jsx`, `agrisight/backend/apps/reports_alerts/views.py`, `agrisight/backend/apps/reports_alerts/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

---

## Epic 5: Real-Time Monitoring & Alerts

5.1 Real-Time Data Updates  
FE: WebSocket via `WebSocketContext.jsx`  
BE: `ws://.../ws/` (`apps/core/consumers.py`)  
RBAC: Authenticated; server should validate user + filter channels to permitted data.  
Status: Implemented (code + docs + UX)  
Evidence: `agrisight/frontend/src/contexts/WebSocketContext.jsx`, `agrisight/frontend/src/hooks/useWebSocket.js`, `agrisight/backend/apps/core/consumers.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

5.2 Stress Event Alerts  
FE: `/alerts` (`Alerts.jsx`)  
BE: `GET /api/v1/reports-alerts/alerts/`, `POST /api/v1/reports-alerts/alerts/<id>/mark-read/`, `POST /api/v1/reports-alerts/alerts/mark-all-read/`  
RBAC: FE `view_data`; backend should scope to accessible regions.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Alerts.jsx`, `agrisight/backend/apps/reports_alerts/views.py`, `agrisight/backend/apps/reports_alerts/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

5.3 Processing Task Monitoring  
FE: `/` (`Dashboard.jsx`), `/satellite` (`SatelliteData.jsx`)  
BE: `GET /api/v1/satellite-processing/status/<task_id>/`, `GET /api/v1/satellite-processing/statistics/`  
RBAC: FE `view_data`; backend should scope to accessible tasks.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/SatelliteData.jsx`, `agrisight/backend/apps/satellite_processing/views.py`, `agrisight/backend/apps/satellite_processing/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

5.4 System Health Monitoring  
FE: `/admin/performance` (`AdminPerformance.jsx`)  
BE: `GET /api/health/`, `GET /api/health/detailed/`  
RBAC: FE `admin_access`; backend should restrict to admin.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/AdminPerformance.jsx`, `agrisight/backend/apps/core/views.py`, `agrisight/backend/apps/core/urls.py`, `agrisight/backend/apps/core/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

---

## Epic 6: Data Management & Export

6.1 Data Export  
FE: `/exports` (`Exports.jsx`), `/reports` (`Reports.jsx`)  
BE: `GET /api/v1/reports-alerts/reports/<id>/download/`  
RBAC: FE `export_data` (exports), `generate_reports` (reports).
Status: Implemented (code + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Exports.jsx`, `agrisight/frontend/src/pages/Reports.jsx`, `agrisight/FRONTEND_IMPLEMENTATION.md`, `agrisight/backend/apps/reports_alerts/views.py`

6.2 Historical Data Access  
FE: `/satellite`, `/vegetation`, `/analytics`  
BE: `GET /api/v1/geospatial/satellite-images/`, `GET /api/v1/geospatial/vegetation-indices/`  
RBAC: FE `view_data` or `view_analytics`.
Status: Implemented (code + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Exports.jsx`, `agrisight/frontend/src/pages/SatelliteData.jsx`, `agrisight/frontend/src/pages/Analytics.jsx`, `agrisight/backend/apps/geospatial/views.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

6.3 Data Validation & Quality Control  
FE: `/admin/performance` (partial), no dedicated UI found  
BE: Not explicitly implemented  
RBAC: Admin-only; not fully implemented.
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Exports.jsx`, `agrisight/backend/apps/geospatial/views.py`, `agrisight/backend/apps/geospatial/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

---

## Epic 7: User Management & Administration

7.1 User Role Management  
FE: `/admin/users` (`Users.jsx`), `/admin/settings` (`AdminSettings.jsx`)  
BE: `GET/POST/PUT/DELETE /api/v1/users/`  
RBAC: FE `admin_access`. Backend: admin/government scoped.  
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Users.jsx`, `agrisight/backend/apps/users/views.py`, `agrisight/backend/apps/users/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

7.2 Organization Management  
FE: `/organizations` (`Organizations.jsx`)  
BE: `GET/POST/PUT/DELETE /api/v1/organizations/`, `GET /api/v1/organizations/current/`  
RBAC: FE `manage_organizations`; backend should scope to admin/government.
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/Organizations.jsx`, `agrisight/backend/apps/organizations/views.py`, `agrisight/backend/apps/organizations/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

7.3 API Key Management  
FE: `/admin/api-keys` (`ApiKeys.jsx`)  
BE: `GET/POST/PUT/DELETE /api/v1/api-keys/keys/`, `POST /api/v1/api-keys/keys/<id>/regenerate/`, `GET /api/v1/api-keys/logs/`  
RBAC: FE `admin_access`; backend scopes by org with admin override.
Status: Implemented (code + tests + docs + UX)  
Evidence: `agrisight/frontend/src/pages/ApiKeys.jsx`, `agrisight/backend/apps/api_keys_logs/views.py`, `agrisight/backend/apps/api_keys_logs/tests.py`, `agrisight/FRONTEND_IMPLEMENTATION.md`

---

## Epic 8: Public Access & Demonstration

8.1 Public Landing Page  
FE: `/landing` (`Landing.jsx`)  
BE: None  
RBAC: Public.

8.2 Public Demo  
FE: `/demo` (`PublicDemo.jsx`)  
BE: None (static data)  
RBAC: Public.

8.3 Public Documentation  
FE: `/support`, `/terms`, `/privacy`  
BE: `GET /api/schema/`, `/api/docs/`, `/api/redoc/`  
RBAC: Public.

---

## Epic 9: Mobile & Responsive Design

9.1 Mobile Dashboard  
FE: `/` responsive UI  
BE: same as Epic 2  
RBAC: `view_data`. Offline support not implemented.

9.2 Mobile Map View  
FE: `/map` responsive UI  
BE: same as Epic 3  
RBAC: `view_data`. GPS integration not implemented.

---

## Epic 10: Integration & API Access

10.1 RESTful API Access  
FE: Not applicable  
BE: `/api/v1/*`  
RBAC: Auth + role permissions; API key support exists under `/api/v1/api-keys/` but not wired in FE.

10.2 Webhook Integration  
FE: Not implemented  
BE: Not implemented  
RBAC: Admin-only; missing.

10.3 Third-Party Data Integration  
FE: Not implemented  
BE: Not implemented  
RBAC: Admin-only; missing.

---

## Notes / Gaps to Address (RBAC Emphasis)
- Backend views mostly rely on `IsAuthenticated` and need consistent permission classes + org/region scoping.
- API key flows exist in backend but no frontend UI is mapped.
- Role management/audit trail endpoints are not present.
- WebSocket channels should enforce per-user visibility (channels currently accept all authenticated users).
