# Error Handling Quick Reference

Quick lookup guide for error handling in AgriSight.

## Frontend Quick Start

### Using Error Context
```javascript
import { useError } from './contexts/ErrorContext';

const { addError, handleRetry, errors } = useError();

// Add error
addError(new Error('Something went wrong'));

// Retry with backoff
const success = await handleRetry(async () => {
  await fetchData();
});
```

### Displaying Errors in Components
```javascript
import APIError from './components/error/APIError';

{error && (
  <APIError 
    error={error}
    onRetry={handleRetry}
    title="Failed to load"
  />
)}
```

### Error Logger
```javascript
import errorLogger from './lib/errorLogger';

// Log error
errorLogger.logError(error, { context: 'user_action' });

// Log message
errorLogger.warn('Warning message', { details: '...' });

// Export logs for debugging
errorLogger.exportLogs();
```

## Backend Quick Start

### Using Error Handling
```python
from apps.core.error_handling import (
    create_validation_error,
    create_not_found_error,
    SuccessResponse,
    ErrorCode
)

# In views
@api_view(['POST'])
def my_view(request):
    try:
        # Validation
        if not request.data.get('email'):
            raise create_validation_error(
                field_errors={'email': 'Required'}
            )
        
        # Business logic
        result = process_data(request.data)
        
        # Success response
        return SuccessResponse(
            data=result,
            message="Success"
        ).to_response()
    
    except APIErrorException:
        raise
```

### Common Error Patterns

**Not Found**
```python
from apps.core.error_handling import create_not_found_error
raise create_not_found_error(resource="Organization")
```

**Permission Denied**
```python
from apps.core.error_handling import create_permission_error
raise create_permission_error()
```

**Validation Error**
```python
from apps.core.error_handling import create_validation_error
raise create_validation_error(
    message="Invalid data",
    field_errors={'field': 'error message'}
)
```

**External Service**
```python
from apps.core.error_handling import create_external_service_error
raise create_external_service_error("Sentinel Hub")
```

**Rate Limit**
```python
from apps.core.error_handling import create_rate_limit_error
raise create_rate_limit_error(retry_after=60)
```

**Timeout**
```python
from apps.core.error_handling import create_timeout_error
raise create_timeout_error("Data fetch", timeout_seconds=30)
```

## Error Codes Reference

### Authentication (1xxx)
| Code | Error |
|------|-------|
| 1001 | Invalid credentials |
| 1002 | User inactive |
| 1003 | User not found |
| 1004 | Invalid token |
| 1005 | Token expired |
| 1006 | Permission denied |
| 1007 | Email not verified |
| 1008 | MFA required |

### User Management (2xxx)
| Code | Error |
|------|-------|
| 2001 | User already exists |
| 2002 | User not found |
| 2003 | Profile incomplete |
| 2004 | Email not verified |
| 2005 | User suspended |

### Validation (3xxx)
| Code | Error |
|------|-------|
| 3001 | Invalid input |
| 3002 | Invalid email |
| 3003 | Invalid password |
| 3004 | Invalid date format |
| 3005 | Missing required field |
| 3006 | File too large |
| 3007 | Unsupported file type |

### Data Operations (4xxx)
| Code | Error |
|------|-------|
| 4001 | Resource not found |
| 4002 | Resource already exists |
| 4003 | Resource locked |
| 4004 | Invalid state transition |
| 4005 | Operation not allowed |
| 4006 | Data consistency error |

### Geospatial (5xxx)
| Code | Error |
|------|-------|
| 5001 | Invalid geometry |
| 5002 | Invalid coordinates |
| 5003 | Area out of bounds |
| 5004 | Geospatial processing error |

### Satellite Data (6xxx)
| Code | Error |
|------|-------|
| 6001 | Data not available |
| 6002 | Invalid date range |
| 6003 | Insufficient cloud coverage |
| 6004 | Sentinel Hub error |
| 6005 | Earth Engine error |
| 6006 | Data retrieval error |

### ML Models (7xxx)
| Code | Error |
|------|-------|
| 7001 | Model not found |
| 7002 | Prediction error |
| 7003 | Invalid model input |
| 7004 | Model timeout |

### External Services (8xxx)
| Code | Error |
|------|-------|
| 8001 | Service unavailable |
| 8002 | Service error |
| 8003 | Rate limit exceeded |
| 8004 | Timeout |

## Error Types

Frontend error types for categorization:

```javascript
ERROR_TYPES = {
  NETWORK: 'NETWORK',              // Network connectivity
  TIMEOUT: 'TIMEOUT',              // Request timeout
  AUTH: 'AUTH',                    // Authentication
  VALIDATION: 'VALIDATION',        // Input validation
  SERVER: 'SERVER',                // 5xx errors
  CLIENT: 'CLIENT',                // 4xx errors
  UNKNOWN: 'UNKNOWN'               // Unknown
}
```

## Error Severity

Frontend notification severity levels:

```javascript
ERROR_SEVERITY = {
  INFO: 'INFO',           // Blue, dismisses after 5s
  WARNING: 'WARNING',     // Yellow, dismisses after 7s
  ERROR: 'ERROR',         // Red, dismisses after 10s
  CRITICAL: 'CRITICAL'    // Dark red, no auto-dismiss
}
```

## HTTP Status Codes

| Code | Meaning | Error Type |
|------|---------|-----------|
| 400 | Bad Request | VALIDATION |
| 401 | Unauthorized | AUTH |
| 403 | Forbidden | AUTH |
| 404 | Not Found | NOT_FOUND |
| 409 | Conflict | CONFLICT |
| 429 | Too Many Requests | RATE_LIMITED |
| 500 | Server Error | SERVER |
| 503 | Service Unavailable | EXTERNAL_SERVICE |
| 504 | Gateway Timeout | SERVER |

## Testing Errors

### Frontend Test Template
```javascript
it('handles error correctly', async () => {
  const { result } = renderHook(() => useError(), { wrapper: ErrorProvider });
  
  act(() => {
    result.current.addError(new Error('Test'));
  });
  
  expect(result.current.errors).toHaveLength(1);
});
```

### Backend Test Template
```python
def test_validation_error(self):
    response = self.client.post('/api/endpoint/', {})
    
    self.assertEqual(response.status_code, 400)
    data = response.json()
    self.assertEqual(data['error']['code'], ErrorCode.INVALID_INPUT)
```

## Development Tools

### Browser Console (Frontend)
```javascript
// View all error logs
errorLogger.getSessionLogs()

// Simulate errors
simulateError('NETWORK')
simulateError('TIMEOUT')
simulateError('AUTH')

// Export logs
errorLogger.exportLogs()
```

### Backend Management
```bash
# View error logs
tail -f logs/error.log

# Check specific error codes
grep "6004" logs/error.log  # Sentinel Hub errors
```

## Debugging Tips

### Check Trace ID
```javascript
// Frontend
const logs = errorLogger.getSessionLogs();
const traceId = logs[0].traceId;  // Find in logs

// Backend
grep "trace-id" logs/error.log    # Find in backend logs
```

### View Field Errors
```python
# In error response
{
  "error": {
    "field_errors": {
      "email": "Invalid format",
      "password": "Too short"
    }
  }
}
```

### Enable Debug Logging
```javascript
// Frontend
errorLogger.configure({
  enableConsoleLogging: true,
  logLevel: 'DEBUG'
});
```

## Common Scenarios

### User Not Found
```
Frontend: 404 error → create_not_found_error("User")
Response: "User not found" (code: 4001)
UI Action: Show "Go Home" button
```

### Authentication Failed
```
Frontend: 401 error → Redirect to /login
Backend: Raises create_auth_error()
Response: "Invalid credentials" (code: 1001)
```

### Validation Failed
```
Frontend: 400 error → Show form errors
Backend: Raises create_validation_error(field_errors={...})
Response: Includes field_errors with per-field messages
```

### External Service Down
```
Frontend: 503 error → Show "try again later"
Backend: Raises create_external_service_error()
Response: "Service unavailable" (code: 8001)
Retry: After 60 seconds
```

### Rate Limited
```
Frontend: 429 error → Show "try again in X seconds"
Backend: Raises create_rate_limit_error(retry_after=60)
Response: Includes retry_after: 60
Retry: Automatic after delay
```

## Documentation Links

- **Full Frontend Guide**: `ERROR_HANDLING_GUIDE.md`
- **Backend Setup**: `BACKEND_ERROR_HANDLING_SETUP.md`
- **Testing Guide**: `ERROR_TESTING_GUIDE.md`
- **Implementation Summary**: `ERROR_HANDLING_IMPLEMENTATION_SUMMARY.md`

## Support

### Getting Help
1. Check error code in this quick reference
2. Check full documentation
3. Check browser console/backend logs
4. Export and review error logs
5. Contact development team with trace ID

### Reporting Errors
Include:
- Error code and message
- Trace ID
- Steps to reproduce
- Expected vs actual behavior
- Screenshots/logs
