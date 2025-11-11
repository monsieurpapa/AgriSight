# Error Handling Testing Guide

This guide provides comprehensive testing strategies for validating error handling across the AgriSight application.

## Table of Contents

1. [Frontend Error Testing](#frontend-error-testing)
2. [Backend Error Testing](#backend-error-testing)
3. [Integration Testing](#integration-testing)
4. [Error Simulation Tools](#error-simulation-tools)
5. [Manual Testing Checklist](#manual-testing-checklist)

## Frontend Error Testing

### Testing ErrorBoundary

```javascript
// tests/components/error/ErrorBoundary.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary from '../../../components/error/ErrorBoundary';

// Suppress console.error for tests
beforeAll(() => {
  jest.spyOn(console, 'error').mockImplementation(() => {});
});

afterAll(() => {
  console.error.mockRestore();
});

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('displays error UI when child component throws', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
    expect(screen.getByText(/Go Home/i)).toBeInTheDocument();
  });

  it('displays error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    const ThrowError = () => {
      throw new Error('Test error message');
    };

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Error Details/i)).toBeInTheDocument();
    expect(screen.getByText(/Test error message/i)).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('allows retry by clearing error state', async () => {
    const user = userEvent.setup();
    let shouldThrow = true;

    const ConditionalError = () => {
      if (shouldThrow) {
        throw new Error('Test error');
      }
      return <div>Success</div>;
    };

    const { rerender } = render(
      <ErrorBoundary>
        <ConditionalError />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();

    // Simulate retry by clicking button
    shouldThrow = false;
    const retryButton = screen.getByText(/Try Again/i);
    await user.click(retryButton);

    rerender(
      <ErrorBoundary>
        <ConditionalError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});
```

### Testing ErrorContext

```javascript
// tests/contexts/ErrorContext.test.js
import { renderHook, act } from '@testing-library/react';
import { ErrorProvider, useError, ERROR_SEVERITY, ERROR_TYPES } from '../../../contexts/ErrorContext';

describe('ErrorContext', () => {
  const wrapper = ({ children }) => <ErrorProvider>{children}</ErrorProvider>;

  it('initializes with empty errors', () => {
    const { result } = renderHook(() => useError(), { wrapper });
    
    expect(result.current.errors).toEqual([]);
    expect(result.current.activeError).toBeNull();
  });

  it('adds error to the error list', () => {
    const { result } = renderHook(() => useError(), { wrapper });
    
    act(() => {
      result.current.addError(new Error('Test error'));
    });

    expect(result.current.errors).toHaveLength(1);
    expect(result.current.errors[0].message).toContain('Test error');
  });

  it('removes error by ID', () => {
    const { result } = renderHook(() => useError(), { wrapper });
    
    act(() => {
      result.current.addError(new Error('Test error'));
    });

    const errorId = result.current.errors[0].id;

    act(() => {
      result.current.removeError(errorId);
    });

    expect(result.current.errors).toHaveLength(0);
  });

  it('clears all errors', () => {
    const { result } = renderHook(() => useError(), { wrapper });
    
    act(() => {
      result.current.addError(new Error('Error 1'));
      result.current.addError(new Error('Error 2'));
    });

    expect(result.current.errors).toHaveLength(2);

    act(() => {
      result.current.clearErrors();
    });

    expect(result.current.errors).toHaveLength(0);
  });

  it('categorizes network errors correctly', () => {
    const { result } = renderHook(() => useError(), { wrapper });
    
    const networkError = new Error('Network failed');
    networkError.type = 'NETWORK_ERROR';

    act(() => {
      result.current.addError(networkError);
    });

    expect(result.current.errors[0].type).toBe(ERROR_TYPES.NETWORK);
    expect(result.current.errors[0].severity).toBe(ERROR_SEVERITY.ERROR);
  });

  it('handles retry with exponential backoff', async () => {
    const { result } = renderHook(() => useError(), { wrapper });
    
    let attempts = 0;
    const retryFn = jest.fn(async () => {
      attempts++;
      if (attempts < 2) {
        throw new Error('Temporary failure');
      }
    });

    const success = await act(async () => {
      return result.current.handleRetry(retryFn);
    });

    expect(success).toBe(true);
    expect(attempts).toBe(2);
  });
});
```

### Testing Error Notification

```javascript
// tests/components/error/ErrorNotification.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorNotification from '../../../components/error/ErrorNotification';

describe('ErrorNotification', () => {
  it('displays error message', () => {
    const error = {
      id: '1',
      message: 'Test error message',
      severity: 'ERROR',
      type: 'NETWORK'
    };

    render(
      <ErrorNotification 
        error={error} 
        onDismiss={() => {}} 
      />
    );

    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('dismisses when close button is clicked', async () => {
    const user = userEvent.setup();
    const onDismiss = jest.fn();
    const error = {
      id: '1',
      message: 'Test error',
      severity: 'ERROR'
    };

    render(
      <ErrorNotification 
        error={error} 
        onDismiss={onDismiss} 
      />
    );

    const closeButton = screen.getByLabelText('Dismiss');
    await user.click(closeButton);

    expect(onDismiss).toHaveBeenCalled();
  });

  it('auto-dismisses based on severity', async () => {
    const onDismiss = jest.fn();
    const error = {
      id: '1',
      message: 'Info message',
      severity: 'INFO'
    };

    jest.useFakeTimers();

    render(
      <ErrorNotification 
        error={error} 
        onDismiss={onDismiss} 
      />
    );

    // INFO severity should auto-dismiss after 5s
    jest.advanceTimersByTime(5000);

    expect(onDismiss).toHaveBeenCalled();

    jest.useRealTimers();
  });
});
```

## Backend Error Testing

### Testing Error Responses

```python
# backend/apps/core/tests/test_error_handling.py
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.core.error_handling import (
    ErrorResponse,
    ErrorCode,
    ErrorType,
    create_validation_error,
    create_auth_error,
)
from django.contrib.auth import get_user_model

User = get_user_model()

class ErrorResponseTests(TestCase):
    """Test error response formatting."""
    
    def test_error_response_format(self):
        """Test error response has correct structure."""
        error_response = ErrorResponse(
            message="Test error",
            code=ErrorCode.SYSTEM_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        data = error_response.to_dict()
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertEqual(data['error']['message'], "Test error")
        self.assertEqual(data['error']['code'], ErrorCode.SYSTEM_ERROR)
        self.assertEqual(data['error']['type'], ErrorType.SERVER_ERROR)
        self.assertIn('timestamp', data['error'])
    
    def test_error_response_with_field_errors(self):
        """Test error response with validation errors."""
        field_errors = {
            'email': 'Invalid email format',
            'password': 'Password too short'
        }
        
        error_response = ErrorResponse(
            message="Validation failed",
            code=ErrorCode.INVALID_INPUT,
            status_code=status.HTTP_400_BAD_REQUEST,
            field_errors=field_errors
        )
        
        data = error_response.to_dict()
        
        self.assertEqual(data['error']['field_errors'], field_errors)


class AuthenticationErrorTests(APITestCase):
    """Test authentication error handling."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_missing_authentication(self):
        """Test missing authentication error."""
        response = self.client.get('/api/user/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['type'], ErrorType.UNAUTHORIZED)
    
    def test_invalid_token(self):
        """Test invalid token error."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get('/api/user/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertIn(data['error']['code'], [ErrorCode.INVALID_TOKEN, ErrorCode.AUTH_INVALID_TOKEN])


class ValidationErrorTests(APITestCase):
    """Test validation error handling."""
    
    def test_missing_required_fields(self):
        """Test missing required fields error."""
        response = self.client.post('/api/auth/register/', {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['error']['code'], ErrorCode.INVALID_INPUT)
        self.assertIn('field_errors', data['error'])
    
    def test_invalid_email_validation(self):
        """Test invalid email format error."""
        response = self.client.post('/api/auth/register/', {
            'email': 'not-an-email',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('email', data['error']['field_errors'])


class RateLimitErrorTests(APITestCase):
    """Test rate limit error handling."""
    
    def test_rate_limit_response(self):
        """Test rate limit error response format."""
        # This would need rate limiting decorator configured
        # Make multiple requests to trigger rate limit
        # Then verify response
        pass


class ExternalServiceErrorTests(APITestCase):
    """Test external service error handling."""
    
    @patch('apps.satellite_processing.services.fetch_satellite_data')
    def test_external_service_unavailable(self, mock_fetch):
        """Test external service unavailable error."""
        from apps.core.error_handling import create_external_service_error
        
        mock_fetch.side_effect = create_external_service_error("Sentinel Hub")
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/satellite/fetch/', {
            'area_id': 1,
            'date_range': {'start': '2024-01-01', 'end': '2024-01-31'}
        })
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        data = response.json()
        self.assertEqual(data['error']['type'], ErrorType.EXTERNAL_SERVICE_ERROR)
```

## Integration Testing

### Testing Error Flow

```javascript
// tests/integration/error-handling.test.js
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../../App';
import apiClient from '../../../lib/apiClient';
import * as errorContext from '../../../contexts/ErrorContext';

jest.mock('../../../lib/apiClient');

describe('Error Handling Integration', () => {
  it('handles API error and displays notification', async () => {
    const user = userEvent.setup();
    
    // Mock API error
    apiClient.get.mockRejectedValue({
      status: 500,
      message: 'Server error',
      type: 'SERVER_ERROR'
    });

    render(<App />);

    // Trigger action that causes API error
    const button = screen.getByRole('button', { name: /load data/i });
    await user.click(button);

    // Verify error notification appears
    await waitFor(() => {
      expect(screen.getByText(/Server error/i)).toBeInTheDocument();
    });
  });

  it('retries failed request', async () => {
    const user = userEvent.setup();
    
    let attempt = 0;
    apiClient.post.mockImplementation(async () => {
      attempt++;
      if (attempt === 1) {
        throw new Error('Network error');
      }
      return { success: true };
    });

    render(<App />);

    // Trigger action
    const button = screen.getByRole('button', { name: /submit/i });
    await user.click(button);

    // Wait for retry
    await waitFor(() => {
      expect(attempt).toBe(2);
    }, { timeout: 3000 });
  });

  it('redirects to login on 401 error', async () => {
    apiClient.get.mockRejectedValue({
      status: 401,
      message: 'Unauthorized'
    });

    // Mock location
    delete window.location;
    window.location = { href: '' };

    render(<App />);

    await waitFor(() => {
      expect(window.location.href).toBe('/login');
    });
  });
});
```

## Error Simulation Tools

### Frontend Error Simulator

```javascript
// utils/errorSimulator.js
/**
 * Simulate different types of errors for testing
 */

export const simulateError = (type, options = {}) => {
  const errors = {
    NETWORK: () => {
      const error = new Error('Network error');
      error.type = 'NETWORK_ERROR';
      error.status = 0;
      throw error;
    },
    
    TIMEOUT: () => {
      const error = new Error('Request timeout');
      error.code = 'ECONNABORTED';
      error.type = 'TIMEOUT';
      throw error;
    },
    
    AUTH: () => {
      const error = new Error('Unauthorized');
      error.status = 401;
      error.type = 'UNAUTHORIZED';
      throw error;
    },
    
    VALIDATION: () => {
      const error = new Error('Validation error');
      error.status = 400;
      error.type = 'VALIDATION_ERROR';
      error.field_errors = options.fieldErrors || {
        email: 'Invalid email'
      };
      throw error;
    },
    
    SERVER: () => {
      const error = new Error('Server error');
      error.status = 500;
      error.type = 'SERVER_ERROR';
      throw error;
    },
    
    RATE_LIMIT: () => {
      const error = new Error('Rate limited');
      error.status = 429;
      error.type = 'RATE_LIMITED';
      error.retry_after = options.retryAfter || 60;
      throw error;
    }
  };

  if (errors[type]) {
    errors[type]();
  } else {
    throw new Error(`Unknown error type: ${type}`);
  }
};

// Usage in components for development/testing
if (process.env.NODE_ENV === 'development') {
  window.simulateError = simulateError;
}
```

### Backend Error Simulator

```python
# backend/apps/core/utils/error_simulator.py
"""
Utilities for simulating different error types in development.
"""

from apps.core.error_handling import (
    create_validation_error,
    create_auth_error,
    create_not_found_error,
    create_external_service_error,
    ErrorCode,
)
from django.conf import settings

def simulate_error(error_type, **kwargs):
    """Simulate different error types."""
    
    if not settings.DEBUG:
        raise RuntimeError("Error simulation only available in DEBUG mode")
    
    simulations = {
        'VALIDATION': lambda: create_validation_error(
            message=kwargs.get('message', 'Validation error'),
            field_errors=kwargs.get('field_errors', {'field': 'Invalid value'})
        ),
        'AUTH': lambda: create_auth_error(
            message=kwargs.get('message', 'Authentication failed'),
            code=kwargs.get('code', ErrorCode.AUTH_INVALID_CREDENTIALS)
        ),
        'NOT_FOUND': lambda: create_not_found_error(
            resource=kwargs.get('resource', 'Resource')
        ),
        'EXTERNAL_SERVICE': lambda: create_external_service_error(
            service=kwargs.get('service', 'External service'),
            message=kwargs.get('message')
        ),
    }
    
    if error_type in simulations:
        raise simulations[error_type]()
    else:
        raise ValueError(f"Unknown error type: {error_type}")
```

## Manual Testing Checklist

### Network Error Tests

- [ ] Disconnect internet and attempt to make API call
  - [ ] Verify network error message displayed
  - [ ] Verify retry button is available
  - [ ] Verify reconnecting and retrying works

- [ ] Simulate slow network and wait for timeout
  - [ ] Verify timeout error message displayed
  - [ ] Verify automatic retry occurs
  - [ ] Verify exponential backoff is used

### Authentication Error Tests

- [ ] Log out and attempt to access protected resource
  - [ ] Verify 401 error displayed
  - [ ] Verify redirected to login page
  - [ ] Verify can log back in and access resource

- [ ] Attempt login with wrong credentials
  - [ ] Verify 401 error with specific message
  - [ ] Verify error persists on page
  - [ ] Verify can retry with correct credentials

- [ ] Let session token expire
  - [ ] Verify automatic redirect to login
  - [ ] Verify clear error message about session expiry

### Validation Error Tests

- [ ] Submit form with missing required fields
  - [ ] Verify field-level error messages displayed
  - [ ] Verify form is not submitted
  - [ ] Verify can fix errors and resubmit

- [ ] Submit form with invalid email
  - [ ] Verify email-specific error message
  - [ ] Verify other fields are preserved
  - [ ] Verify can fix and resubmit

### Rate Limit Tests

- [ ] Make repeated requests rapidly
  - [ ] Verify 429 error after limit
  - [ ] Verify "retry after" message
  - [ ] Verify button disabled until time passes

### Server Error Tests

- [ ] Trigger 500 server error
  - [ ] Verify generic server error message
  - [ ] Verify retry button available
  - [ ] Verify retry attempts work (if error resolves)

- [ ] Trigger 503 service unavailable
  - [ ] Verify "service unavailable" message
  - [ ] Verify appropriate retry timing

### Recovery Tests

- [ ] Start with network error, then recover
  - [ ] Verify error displays
  - [ ] Simulate network recovery
  - [ ] Verify "Try Again" button works
  - [ ] Verify request succeeds

- [ ] Start with validation error, then fix
  - [ ] Verify validation error displays
  - [ ] Fix validation issues
  - [ ] Verify form submits successfully

## Summary

Comprehensive error testing ensures:
1. **Error messages** are clear and helpful
2. **Retry logic** works correctly with exponential backoff
3. **Error states** are properly handled and displayed
4. **User recovery paths** are clear and available
5. **Error categorization** guides appropriate user actions

Test these scenarios regularly to maintain error handling quality.
