# Backend Error Handling Setup Guide

This document explains how to integrate and use the error handling system in the AgriSight backend.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Error Types and Codes](#error-types-and-codes)
5. [Best Practices](#best-practices)
6. [Testing](#testing)

## Installation

The error handling system is already included in the backend. The main components are:

- **`core/error_handling.py`** - Error classes, codes, and response formatting
- **`core/error_middleware.py`** - Request/response middleware for error handling
- **Settings integration** - Configuration in Django settings

## Configuration

### 1. Update Django Settings

Add the error handling configuration to your `settings.py`:

```python
# settings.py

# Add to MIDDLEWARE
MIDDLEWARE = [
    # ... other middleware ...
    'apps.core.error_middleware.TraceIDMiddleware',  # Add first
    'apps.core.error_middleware.ErrorLoggingMiddleware',
    'apps.core.error_middleware.RequestResponseLoggingMiddleware',
    'apps.core.error_middleware.CORSErrorHandlingMiddleware',  # Add last
    # ... rest of middleware ...
]

# Configure REST Framework exception handler
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.core.error_handling.api_exception_handler',
    # ... other settings ...
}

# Configure logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}
```

## Usage

### Basic Error Handling in Views

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.error_handling import (
    create_validation_error,
    create_auth_error,
    create_not_found_error,
    SuccessResponse,
    ErrorCode,
)
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get authenticated user's profile."""
    try:
        user = request.user
        data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        
        response = SuccessResponse(
            data=data,
            message="Profile retrieved successfully"
        )
        return response.to_response()
    
    except Exception as e:
        raise create_not_found_error("User profile")

@api_view(['POST'])
def register(request):
    """Register a new user."""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validation
        if not email or not password:
            raise create_validation_error(
                message="Email and password are required",
                field_errors={
                    'email': 'This field is required.' if not email else None,
                    'password': 'This field is required.' if not password else None,
                }
            )
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            raise create_validation_error(
                message="User with this email already exists",
                code=ErrorCode.USER_ALREADY_EXISTS,
                field_errors={'email': 'Email already registered'}
            )
        
        # Create user
        user = User.objects.create_user(email=email, password=password)
        
        response = SuccessResponse(
            data={'id': user.id, 'email': user.email},
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )
        return response.to_response()
    
    except APIErrorException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise create_external_service_error("User registration")
```

### Class-Based Views

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.error_handling import (
    SuccessResponse,
    create_permission_error,
    create_not_found_error,
)
from .models import Organization

class OrganizationDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, org_id):
        """Get organization details."""
        try:
            org = Organization.objects.get(id=org_id)
            
            # Check permission
            if not request.user.organizations.filter(id=org_id).exists():
                raise create_permission_error(
                    message="You don't have access to this organization"
                )
            
            data = {
                'id': org.id,
                'name': org.name,
                'location': org.location,
            }
            
            return SuccessResponse(data=data).to_response()
        
        except Organization.DoesNotExist:
            raise create_not_found_error(resource="Organization")
```

### Handling External Service Errors

```python
from apps.core.error_handling import (
    create_external_service_error,
    create_timeout_error,
    ErrorCode,
)
import requests
from requests.exceptions import Timeout, ConnectionError

def fetch_sentinel_data(area_id, date_range):
    """Fetch Sentinel Hub data with error handling."""
    try:
        url = "https://sentinelhub.com/api/..."
        response = requests.get(url, timeout=30)
        
        if response.status_code == 503:
            raise create_external_service_error(
                service="Sentinel Hub",
                code=ErrorCode.SENTINEL_HUB_ERROR
            )
        
        return response.json()
    
    except Timeout:
        raise create_timeout_error(
            operation="Sentinel data retrieval",
            timeout_seconds=30
        )
    
    except ConnectionError:
        raise create_external_service_error(
            service="Sentinel Hub",
            code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE
        )
```

### Handling Validation Errors

```python
from apps.core.error_handling import create_validation_error, ErrorCode

def validate_geospatial_data(geom, area):
    """Validate geospatial input."""
    errors = {}
    
    if not geom:
        errors['geometry'] = 'Geometry is required'
    elif not is_valid_geometry(geom):
        errors['geometry'] = 'Invalid geometry format'
    
    if not area:
        errors['area'] = 'Area is required'
    elif area < 0:
        errors['area'] = 'Area must be positive'
    
    if errors:
        raise create_validation_error(
            message="Invalid geospatial data",
            field_errors=errors,
            code=ErrorCode.INVALID_GEOMETRY
        )
    
    return True
```

## Error Types and Codes

### HTTP Status Codes

The error handling system uses standard HTTP status codes:

- **200-299**: Success
- **400**: Bad Request (validation, invalid input)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (permission denied)
- **404**: Not Found
- **409**: Conflict (resource already exists)
- **429**: Too Many Requests (rate limited)
- **500**: Server Error
- **503**: Service Unavailable (external service)
- **504**: Gateway Timeout

### Error Codes

Error codes help the frontend handle errors appropriately:

**Authentication (1xxx)**
- `1001`: INVALID_CREDENTIALS - Wrong email/password
- `1002`: USER_INACTIVE - User account is inactive
- `1003`: USER_NOT_FOUND - User doesn't exist
- `1004`: INVALID_TOKEN - JWT or session token invalid
- `1005`: EXPIRED_TOKEN - Token has expired
- `1006`: PERMISSION_DENIED - User lacks permission
- `1007`: EMAIL_NOT_VERIFIED - Email not verified
- `1008`: MFA_REQUIRED - Multi-factor authentication required

**User Management (2xxx)**
- `2001`: USER_ALREADY_EXISTS - Email already registered
- `2002`: USER_NOT_FOUND - User doesn't exist
- `2003`: USER_PROFILE_INCOMPLETE - Missing required profile info
- `2004`: EMAIL_NOT_VERIFIED - Email verification pending
- `2005`: USER_SUSPENDED - User account suspended

**Validation (3xxx)**
- `3001`: INVALID_INPUT - Invalid input data
- `3002`: INVALID_EMAIL - Invalid email format
- `3003`: INVALID_PASSWORD - Password doesn't meet requirements
- `3004`: INVALID_DATE_FORMAT - Invalid date format
- `3005`: MISSING_REQUIRED_FIELD - Required field missing
- `3006`: FILE_TOO_LARGE - File size exceeds limit
- `3007`: UNSUPPORTED_FILE_TYPE - File type not supported

**Data Operations (4xxx)**
- `4001`: RESOURCE_NOT_FOUND - Requested resource not found
- `4002`: RESOURCE_ALREADY_EXISTS - Resource already exists
- `4003`: RESOURCE_LOCKED - Resource is locked
- `4004`: INVALID_STATE_TRANSITION - Invalid state change
- `4005`: OPERATION_NOT_ALLOWED - Operation not allowed
- `4006`: DATA_CONSISTENCY_ERROR - Data consistency issue

**Geospatial (5xxx)**
- `5001`: INVALID_GEOMETRY - Invalid geometry
- `5002`: INVALID_COORDINATES - Invalid coordinates
- `5003`: AREA_OUT_OF_BOUNDS - Area outside service bounds
- `5004`: GEOSPATIAL_PROCESSING_ERROR - Processing error

**Satellite Data (6xxx)**
- `6001`: SATELLITE_DATA_NOT_AVAILABLE - No data available
- `6002`: INVALID_DATE_RANGE - Invalid date range
- `6003`: INSUFFICIENT_CLOUD_COVERAGE - Too much cloud cover
- `6004`: SENTINEL_HUB_ERROR - Sentinel Hub API error
- `6005`: EARTH_ENGINE_ERROR - Google Earth Engine error
- `6006`: DATA_RETRIEVAL_ERROR - Data retrieval error

**ML Models (7xxx)**
- `7001`: MODEL_NOT_FOUND - Model not found
- `7002`: MODEL_PREDICTION_ERROR - Prediction failed
- `7003`: INVALID_MODEL_INPUT - Invalid model input
- `7004`: MODEL_TIMEOUT - Model prediction timeout

**External Services (8xxx)**
- `8001`: EXTERNAL_SERVICE_UNAVAILABLE - Service unavailable
- `8002`: EXTERNAL_SERVICE_ERROR - Service error
- `8003`: RATE_LIMIT_EXCEEDED - Rate limit exceeded
- `8004`: TIMEOUT - Request timeout

## Best Practices

### 1. Always Use Appropriate Error Types

```python
# ✓ GOOD - Use specific error types
if not email:
    raise create_validation_error(
        message="Email is required",
        field_errors={'email': 'This field is required.'}
    )

# ✗ BAD - Generic error
if not email:
    raise Exception("Email is required")
```

### 2. Include Field-Level Errors for Validation

```python
# ✓ GOOD - Detailed validation errors
errors = {}
if not validate_email(email):
    errors['email'] = 'Invalid email format'
if len(password) < 8:
    errors['password'] = 'Password must be at least 8 characters'

if errors:
    raise create_validation_error(
        message="Validation failed",
        field_errors=errors
    )

# ✗ BAD - Generic message
if not validate_email(email) or len(password) < 8:
    raise create_validation_error("Invalid input")
```

### 3. Log Errors Appropriately

```python
# ✓ GOOD - Log with context
try:
    data = fetch_external_data(url)
except Exception as e:
    logger.error(
        f"Failed to fetch data from {url}",
        exc_info=True,
        extra={'url': url, 'user_id': request.user.id}
    )
    raise create_external_service_error("Data retrieval")

# ✗ BAD - No logging context
try:
    data = fetch_external_data(url)
except Exception:
    raise create_external_service_error("Data retrieval")
```

### 4. Use Success Responses for Consistency

```python
# ✓ GOOD - Consistent response format
def create_organization(request):
    org = Organization.objects.create(...)
    return SuccessResponse(
        data={'id': org.id, 'name': org.name},
        message="Organization created",
        status_code=status.HTTP_201_CREATED
    ).to_response()

# ✗ BAD - Inconsistent response format
def create_organization(request):
    org = Organization.objects.create(...)
    return Response({'success': True, 'org': org})
```

### 5. Handle Rate Limiting

```python
from apps.core.error_handling import create_rate_limit_error
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/h', method='POST')
@api_view(['POST'])
def expensive_operation(request):
    """Rate limited operation."""
    if request.limited:
        raise create_rate_limit_error(
            retry_after=3600,  # 1 hour
            message="API rate limit exceeded"
        )
    
    # Perform operation
    return SuccessResponse(data={}).to_response()
```

## Testing

### Testing Error Handling

```python
from django.test import TestCase
from rest_framework.test import APIClient
from apps.core.error_handling import ErrorCode
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationErrorTests(TestCase):
    """Test authentication error handling."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_invalid_credentials_error(self):
        """Test invalid credentials error."""
        response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['error']['code'], ErrorCode.AUTH_INVALID_CREDENTIALS)
        self.assertFalse(data['success'])
    
    def test_user_not_found_error(self):
        """Test user not found error."""
        response = self.client.get('/api/auth/user/')
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['error']['type'], 'UNAUTHORIZED')
    
    def test_permission_denied_error(self):
        """Test permission denied error."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete('/api/organizations/999/')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['error']['code'], ErrorCode.AUTH_PERMISSION_DENIED)
    
    def test_validation_error_with_field_errors(self):
        """Test validation error with field-level errors."""
        response = self.client.post('/api/auth/register/', {
            'email': '',
            'password': ''
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], ErrorCode.INVALID_INPUT)
        self.assertIn('email', data['error']['field_errors'])
        self.assertIn('password', data['error']['field_errors'])
```

### Testing Error Responses

```python
from apps.core.error_handling import ErrorResponse, ErrorCode

class ErrorResponseTests(TestCase):
    """Test error response formatting."""
    
    def test_error_response_format(self):
        """Test error response has correct format."""
        error_response = ErrorResponse(
            message="Test error",
            code=ErrorCode.SYSTEM_ERROR,
            status_code=500
        )
        
        data = error_response.to_dict()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['message'], "Test error")
        self.assertEqual(data['error']['code'], ErrorCode.SYSTEM_ERROR)
        self.assertIn('timestamp', data['error'])
    
    def test_error_response_with_field_errors(self):
        """Test error response with field-level errors."""
        error_response = ErrorResponse(
            message="Validation error",
            code=ErrorCode.INVALID_INPUT,
            status_code=400,
            field_errors={
                'email': 'Invalid email',
                'password': 'Password too short'
            }
        )
        
        data = error_response.to_dict()
        self.assertEqual(len(data['error']['field_errors']), 2)
```

## Summary

The backend error handling system provides:

1. **Standardized error responses** with consistent format
2. **Specific error codes** for client-side handling
3. **Categorized error types** for intelligent handling
4. **Request tracking** with trace IDs
5. **Comprehensive logging** with context
6. **Validation support** with field-level errors

This ensures robust error handling across the entire backend.
