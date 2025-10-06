# AgriSight API Synchronization Guide

## Overview

This document outlines the comprehensive API synchronization between frontend and backend, including error handling, endpoint mapping, and best practices for maintaining consistency.

## API Endpoint Mapping

### Authentication Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `authAPI.getConfig()` | `/api/auth/config/` | GET | Get authentication configuration |
| `authAPI.login()` | `/api/auth/login/` | POST | User login |
| `authAPI.logout()` | `/api/auth/logout/` | POST | User logout |
| `authAPI.getCurrentUser()` | `/api/auth/user/` | GET | Get current user details |
| `authAPI.register()` | `/api/auth/registration/` | POST | User registration |
| `authAPI.changePassword()` | `/api/auth/password/change/` | POST | Change password |
| `authAPI.requestPasswordReset()` | `/api/auth/password/reset/` | POST | Request password reset |
| `authAPI.confirmPasswordReset()` | `/api/auth/password/reset/confirm/` | POST | Confirm password reset |
| `authAPI.verifyEmail()` | `/api/auth/registration/verify-email/` | POST | Verify email address |
| `authAPI.resendEmailVerification()` | `/api/auth/registration/resend-email/` | POST | Resend email verification |
| `authAPI.googleLogin()` | `/api/auth/google/` | POST | Google OAuth login |
| `authAPI.facebookLogin()` | `/api/auth/facebook/` | POST | Facebook OAuth login |
| `authAPI.githubLogin()` | `/api/auth/github/` | POST | GitHub OAuth login |

### Geospatial Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `geospatialAPI.getRegions()` | `/api/v1/geospatial/regions/` | GET | List all regions |
| `geospatialAPI.getRegion(id)` | `/api/v1/geospatial/regions/{id}/` | GET | Get specific region |
| `geospatialAPI.getVegetationIndices()` | `/api/v1/geospatial/vegetation-indices/` | GET | List vegetation indices |
| `geospatialAPI.getSatelliteImages()` | `/api/v1/geospatial/satellite-images/` | GET | List satellite images |
| `geospatialAPI.getCrops()` | `/api/v1/geospatial/crops/` | GET | List crops |

### Analytics Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `analyticsAPI.getStressEvents()` | `/api/v1/analytics/stress-events/` | GET | List stress events |
| `analyticsAPI.getStressEventSummary()` | `/api/v1/analytics/stress-events/summary/` | GET | Get stress event summary |
| `analyticsAPI.getConflictEvents()` | `/api/v1/analytics/conflict-events/` | GET | List conflict events |
| `analyticsAPI.getConflictEventSummary()` | `/api/v1/analytics/conflict-events/summary/` | GET | Get conflict event summary |

### Satellite Processing Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `satelliteProcessingAPI.triggerProcessing()` | `/api/v1/satellite-processing/process/` | POST | Trigger satellite processing |
| `satelliteProcessingAPI.getProcessingStatus()` | `/api/v1/satellite-processing/status/{task_id}/` | GET | Get processing status |
| `satelliteProcessingAPI.getRegionVegetationData()` | `/api/v1/satellite-processing/vegetation/{region_id}/` | GET | Get region vegetation data |
| `satelliteProcessingAPI.getTrendAnalysis()` | `/api/v1/satellite-processing/trend-analysis/` | GET | Get trend analysis |
| `satelliteProcessingAPI.getProcessingStatistics()` | `/api/v1/satellite-processing/statistics/` | GET | Get processing statistics |
| `satelliteProcessingAPI.getSatelliteImageDetails()` | `/api/v1/satellite-processing/image/{image_id}/` | GET | Get satellite image details |
| `satelliteProcessingAPI.manualDataIngestion()` | `/api/v1/satellite-processing/ingest/` | POST | Manual data ingestion |

### Reports & Alerts Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `reportsAPI.getReports()` | `/api/v1/reports-alerts/reports/` | GET | List reports |
| `reportsAPI.getReport(id)` | `/api/v1/reports-alerts/reports/{id}/` | GET | Get specific report |
| `reportsAPI.createReport()` | `/api/v1/reports-alerts/reports/` | POST | Create report |
| `reportsAPI.updateReport()` | `/api/v1/reports-alerts/reports/{id}/` | PUT | Update report |
| `reportsAPI.deleteReport()` | `/api/v1/reports-alerts/reports/{id}/` | DELETE | Delete report |
| `reportsAPI.downloadReport()` | `/api/v1/reports-alerts/reports/{id}/download/` | GET | Download report |
| `alertsAPI.getAlerts()` | `/api/v1/reports-alerts/alerts/` | GET | List alerts |
| `alertsAPI.getAlert(id)` | `/api/v1/reports-alerts/alerts/{id}/` | GET | Get specific alert |
| `alertsAPI.markAlertAsRead()` | `/api/v1/reports-alerts/alerts/{id}/mark-read/` | POST | Mark alert as read |
| `alertsAPI.markAllAlertsAsRead()` | `/api/v1/reports-alerts/alerts/mark-all-read/` | POST | Mark all alerts as read |
| `alertsAPI.getUnreadCount()` | `/api/v1/reports-alerts/alerts/unread-count/` | GET | Get unread alert count |
| `alertsAPI.getRecentAlerts()` | `/api/v1/reports-alerts/alerts/recent/` | GET | Get recent alerts |

### Organizations Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `organizationsAPI.getOrganizations()` | `/api/v1/organizations/` | GET | List organizations |
| `organizationsAPI.getOrganization(id)` | `/api/v1/organizations/{id}/` | GET | Get specific organization |
| `organizationsAPI.getCurrentOrganization()` | `/api/v1/organizations/current/` | GET | Get current organization |
| `organizationsAPI.createOrganization()` | `/api/v1/organizations/` | POST | Create organization |
| `organizationsAPI.updateOrganization()` | `/api/v1/organizations/{id}/` | PUT | Update organization |
| `organizationsAPI.deleteOrganization()` | `/api/v1/organizations/{id}/` | DELETE | Delete organization |
| `organizationsAPI.getSubscriptionPlans()` | `/api/v1/organizations/subscription-plans/` | GET | List subscription plans |
| `organizationsAPI.getSubscriptionPlan(id)` | `/api/v1/organizations/subscription-plans/{id}/` | GET | Get specific subscription plan |

### Users Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `usersAPI.getUsers()` | `/api/v1/users/` | GET | List users |
| `usersAPI.getUser(id)` | `/api/v1/users/{id}/` | GET | Get specific user |
| `usersAPI.getCurrentUser()` | `/api/v1/users/me/` | GET | Get current user |
| `usersAPI.updateCurrentUser()` | `/api/v1/users/me/update/` | PATCH | Update current user |
| `usersAPI.createUser()` | `/api/v1/users/` | POST | Create user |
| `usersAPI.updateUser()` | `/api/v1/users/{id}/` | PUT | Update user |
| `usersAPI.deleteUser()` | `/api/v1/users/{id}/` | DELETE | Delete user |

### ML Models Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `mlModelsAPI.getModels()` | `/api/v1/ml-models/models/` | GET | List ML models |
| `mlModelsAPI.getModel(id)` | `/api/v1/ml-models/models/{id}/` | GET | Get specific model |
| `mlModelsAPI.createModel()` | `/api/v1/ml-models/models/` | POST | Create model |
| `mlModelsAPI.updateModel()` | `/api/v1/ml-models/models/{id}/` | PUT | Update model |
| `mlModelsAPI.deleteModel()` | `/api/v1/ml-models/models/{id}/` | DELETE | Delete model |
| `mlModelsAPI.startTraining()` | `/api/v1/ml-models/models/{id}/train/` | POST | Start model training |
| `mlModelsAPI.makePrediction()` | `/api/v1/ml-models/models/{id}/predict/` | POST | Make prediction |
| `mlModelsAPI.getModelPerformance()` | `/api/v1/ml-models/models/{id}/performance/` | GET | Get model performance |
| `mlModelsAPI.getTrainingJobs()` | `/api/v1/ml-models/training-jobs/` | GET | List training jobs |
| `mlModelsAPI.getTrainingJob(id)` | `/api/v1/ml-models/training-jobs/{id}/` | GET | Get specific training job |
| `mlModelsAPI.getTrainingStatus()` | `/api/v1/ml-models/training-jobs/{id}/status/` | GET | Get training status |
| `mlModelsAPI.getPredictions()` | `/api/v1/ml-models/predictions/` | GET | List predictions |
| `mlModelsAPI.getPrediction(id)` | `/api/v1/ml-models/predictions/{id}/` | GET | Get specific prediction |
| `mlModelsAPI.compareModels()` | `/api/v1/ml-models/compare-models/` | POST | Compare models |
| `mlModelsAPI.getFeatureImportance()` | `/api/v1/ml-models/feature-importance/{model_id}/` | GET | Get feature importance |

### API Keys Endpoints
| Frontend Call | Backend Endpoint | Method | Description |
|---------------|------------------|---------|-------------|
| `apiKeysAPI.getAPIKeys()` | `/api/v1/api-keys/keys/` | GET | List API keys |
| `apiKeysAPI.getAPIKey(id)` | `/api/v1/api-keys/keys/{id}/` | GET | Get specific API key |
| `apiKeysAPI.createAPIKey()` | `/api/v1/api-keys/keys/` | POST | Create API key |
| `apiKeysAPI.updateAPIKey()` | `/api/v1/api-keys/keys/{id}/` | PUT | Update API key |
| `apiKeysAPI.deleteAPIKey()` | `/api/v1/api-keys/keys/{id}/` | DELETE | Delete API key |
| `apiKeysAPI.getAnalyticsLogs()` | `/api/v1/api-keys/logs/` | GET | List analytics logs |

## Error Handling System

### Error Components
- **APIError Component**: Displays API-specific errors with retry options
- **ErrorPage Component**: Generic error pages for different HTTP statuses
- **ErrorBoundary Component**: Catches React component errors

### API Client Features
- **Automatic CSRF Token Handling**: Manages CSRF tokens for session authentication
- **Request/Response Interceptors**: Handles common patterns like token refresh
- **Error Standardization**: Converts all errors to consistent format
- **Retry Logic**: Automatic retry for transient failures

## Synchronization Status

### ✅ Completed
- All API endpoints mapped between frontend and backend
- Comprehensive error handling system implemented
- Enhanced API client with CSRF token handling
- Error boundaries and error pages implemented
- API synchronization documented

### 🔄 In Progress
- Frontend integration with real APIs (Priority 1)
- WebSocket implementation for real-time updates
- Advanced error handling for edge cases

---

*This document should be updated whenever API endpoints change or new error handling patterns are implemented.*
