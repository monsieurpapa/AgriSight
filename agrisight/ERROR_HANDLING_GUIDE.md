# Error Handling Guide - AgriSight Frontend

This document provides a comprehensive guide to error handling in the AgriSight frontend application.

## Table of Contents

1. [Overview](#overview)
2. [Error Handling Architecture](#error-handling-architecture)
3. [Core Components](#core-components)
4. [Error Context](#error-context)
5. [Error Categories](#error-categories)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)
8. [Testing Errors](#testing-errors)

## Overview

The AgriSight frontend implements a **multi-layered error handling system** that ensures:
- **Graceful degradation** when errors occur
- **User-friendly error messages** appropriate to the error type
- **Centralized error management** through React Context
- **Automatic error recovery** with retry logic
- **Development-friendly debugging** with detailed error information

The error handling system is built on three main pillars:
1. **ErrorBoundary** - Catches unhandled React component errors
2. **ErrorContext** - Manages application-level errors and state
3. **Error UI Components** - Display errors to users in appropriate ways

## Error Handling Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Application                          │
├─────────────────────────────────────────────────────────────┤
│                      ErrorBoundary                          │
│  (Catches unhandled React component errors)                │
├─────────────────────────────────────────────────────────────┤
│                    ErrorProvider (Context)                  │
│  (Manages application-level errors and state)              │
├─────────────────────────────────────────────────────────────┤
│                    Error UI Layer                           │
│  ┌──────────────────┬──────────────────┬──────────────────┐ │
│  │ ErrorBoundary    │ ErrorNotification │ ErrorPage        │ │
│  │ (React errors)   │ (Toast style)     │ (Full page)      │ │
│  └──────────────────┴──────────────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. ErrorBoundary Component

**Location**: `src/components/error/ErrorBoundary.jsx`

Catches errors anywhere in the React component tree and displays a fallback UI.

**Features**:
- Catches synchronous errors in lifecycle methods and render
- Displays error details in development mode
- Provides "Try Again" and "Go Home" buttons
- Tracks error count and identifies critical errors

**Usage**:
```jsx
// Wraps the entire application (already done in App.jsx)
<ErrorBoundary>
  {/* Your app components */}
</ErrorBoundary>
```

**When it triggers**:
- Rendering errors in components
- Lifecycle method errors
- Constructor errors
- Errors from state updates

**When it doesn't catch**:
- Event handlers (use try-catch instead)
- Asynchronous code (use ErrorContext instead)
- Server-side rendering

### 2. ErrorContext

**Location**: `src/contexts/ErrorContext.jsx`

Manages application-level errors and provides error handling utilities.

**Key Exports**:
- `ErrorProvider` - Context provider component
- `useError()` - Hook to access error management
- `ERROR_TYPES` - Error type constants
- `ERROR_SEVERITY` - Error severity levels
- `categorizeError()` - Error categorization function

**Error Types**:
```javascript
ERROR_TYPES = {
  NETWORK: 'NETWORK',      // Network connectivity issues
  TIMEOUT: 'TIMEOUT',      // Request timeouts
  AUTH: 'AUTH',            // Authentication/authorization errors
  VALIDATION: 'VALIDATION', // Input validation errors
  SERVER: 'SERVER',        // 5xx server errors
  CLIENT: 'CLIENT',        // 4xx client errors
  UNKNOWN: 'UNKNOWN'       // Unknown errors
}
```

**Error Severity Levels**:
```javascript
ERROR_SEVERITY = {
  INFO: 'INFO',           // Informational (auto-dismiss after 5s)
  WARNING: 'WARNING',     // Warning (auto-dismiss after 7s)
  ERROR: 'ERROR',         // Error (auto-dismiss after 10s)
  CRITICAL: 'CRITICAL'    // Critical (no auto-dismiss)
}
```

### 3. ErrorNotification Component

**Location**: `src/components/error/ErrorNotification.jsx`

Displays error notifications in a toast-like style at the top-right of the screen.

**Features**:
- Auto-dismissing notifications based on severity
- Stack multiple errors
- Smooth animations
- Semantic HTML with accessibility features

**Component**: `ErrorNotificationStack`
```jsx
// Displays all active errors as a stack
<ErrorNotificationStack />
```

### 4. ErrorPage Component

**Location**: `src/components/error/ErrorPage.jsx`

Full-page error display for HTTP error codes and network errors.

**Supported Status Codes**:
- 400 - Bad Request
- 401 - Authentication Required
- 403 - Access Denied
- 404 - Page Not Found
- 500 - Server Error
- 502 - Bad Gateway
- 503 - Service Unavailable
- 504 - Gateway Timeout
- NETWORK_ERROR - Connection Error

**Usage**:
```jsx
// In your routes
<Route path="/error/404" element={<ErrorPage status={404} />} />
<Route path="/error/500" element={<ErrorPage status={500} />} />
```

### 5. APIError Component

**Location**: `src/components/error/APIError.jsx`

Displays API-specific errors with contextual actions.

**Features**:
- Status-specific icons and messages
- Debug information in development mode
- Smart action buttons based on error type
- Inline display in components

**Usage**:
```jsx
import APIError from './components/error/APIError';

function MyComponent() {
  const [error, setError] = useState(null);

  const handleRetry = async () => {
    try {
      // Make API call
    } catch (err) {
      setError(err);
    }
  };

  if (error) {
    return (
      <APIError 
        error={error} 
        onRetry={handleRetry}
        title="Failed to load data"
      />
    );
  }

  return <div>Content</div>;
}
```

## Error Context

### Provider Setup

The ErrorProvider is already set up in `App.jsx`:

```jsx
<ErrorBoundary>
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <WebSocketProvider>
        <ErrorProvider>
          <Router>
            <ErrorNotificationStack />
            {/* Routes */}
          </Router>
        </ErrorProvider>
      </WebSocketProvider>
    </AuthProvider>
  </QueryClientProvider>
</ErrorBoundary>
```

### Using the Error Hook

```javascript
import { useError, ERROR_SEVERITY, ERROR_TYPES } from './contexts/ErrorContext';

function MyComponent() {
  const { addError, removeError, errors, handleRetry } = useError();

  // Add an error
  const handleError = (error) => {
    addError(error, {
      severity: ERROR_SEVERITY.ERROR,
      type: ERROR_TYPES.NETWORK
    });
  };

  // Remove an error
  const handleDismiss = (errorId) => {
    removeError(errorId);
  };

  // Handle retry with exponential backoff
  const handleRetryClick = async () => {
    const success = await handleRetry(async () => {
      // Code to retry
      await fetchData();
    });

    if (success) {
      console.log('Retry successful!');
    }
  };

  return (
    <div>
      {/* Component content */}
    </div>
  );
}
```

## Error Categories

### Network Errors

Triggered when network connectivity is lost or network requests fail.

```javascript
// Detected by:
// - error.type === 'NETWORK_ERROR'
// - error.message includes 'connect'
// - status === 0

const { addError } = useError();

try {
  await fetchData();
} catch (error) {
  // Automatically categorized as NETWORK error
  addError(error);
}
```

**User Message**: "Network connection failed. Please check your internet connection."

### Timeout Errors

Triggered when requests take too long to complete.

```javascript
// Detected by:
// - error.type === 'TIMEOUT'
// - error.code === 'ECONNABORTED'

const { addError } = useError();

try {
  await fetchDataWithTimeout(5000);
} catch (error) {
  if (error.code === 'ECONNABORTED') {
    addError(error); // Auto-categorized as TIMEOUT
  }
}
```

**User Message**: "Request timed out. Please try again."

### Authentication Errors (401)

Triggered when user authentication is invalid or expired.

```javascript
// Automatically handled by the application
// When a 401 is received:
// 1. User is logged out
// 2. Error notification is shown
// 3. User is redirected to login page

// To manually trigger:
const { addError } = useError();
addError(new Error('Unauthorized'), {
  status: 401
});
```

**User Message**: "Your session has expired. Please log in again."

### Authorization Errors (403)

Triggered when user lacks permission for a resource.

```javascript
// Detected by status === 403
// Categorized as AUTH with WARNING severity

const { addError } = useError();
addError(new Error('Forbidden'), {
  status: 403
});
```

**User Message**: "You do not have permission to perform this action."

### Validation Errors (400)

Triggered when request data is invalid.

```javascript
// Detected by status === 400
// Often includes details in error.data

const { addError } = useError();
const validationError = new Error('Invalid input');
validationError.status = 400;
validationError.data = {
  fields: {
    email: 'Invalid email format'
  }
};

addError(validationError);
```

**User Message**: "The request contains invalid data. Please check and try again."

### Server Errors (5xx)

Triggered when server encounters an error.

```javascript
// Detected by status >= 500
// Categorized as SERVER with CRITICAL severity

const { addError } = useError();
addError(new Error('Internal Server Error'), {
  status: 500
});
```

**User Message**: "Server error. Please try again later."

### Client Errors (4xx, except 400, 401, 403)

Triggered by various client-side HTTP errors.

```javascript
// Examples: 405 Method Not Allowed, 409 Conflict, etc.
// Categorized as CLIENT with WARNING severity

const { addError } = useError();
addError(new Error('Conflict'), {
  status: 409
});
```

## Usage Examples

### Example 1: API Call with Error Handling

```javascript
import { useError } from './contexts/ErrorContext';

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const { addError } = useError();

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/users');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      // ErrorContext automatically categorizes the error
      addError(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={fetchUsers} disabled={loading}>
        {loading ? 'Loading...' : 'Load Users'}
      </button>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
}
```

### Example 2: Form Submission with Validation

```javascript
import { useError, ERROR_SEVERITY } from './contexts/ErrorContext';

function LoginForm() {
  const { addError } = useError();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Client-side validation
    const email = e.target.email.value;
    if (!email.includes('@')) {
      addError(
        new Error('Please enter a valid email'),
        { severity: ERROR_SEVERITY.WARNING }
      );
      return;
    }

    // Server submission
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify({ email })
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      // Success handling
    } catch (error) {
      addError(error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" name="email" required />
      <button type="submit">Login</button>
    </form>
  );
}
```

### Example 3: Using Retry Logic

```javascript
import { useError } from './contexts/ErrorContext';

function DataComponent() {
  const { handleRetry, retryCount } = useError();

  const loadData = async () => {
    const success = await handleRetry(async () => {
      const response = await fetch('/api/data');
      if (!response.ok) throw new Error('Failed to load');
      return response.json();
    });

    if (!success) {
      console.log('Failed after retries:', retryCount);
    }
  };

  return (
    <button onClick={loadData}>
      Load Data (Attempt {retryCount})
    </button>
  );
}
```

### Example 4: Event Handler Error Handling

```javascript
function Button() {
  const { addError } = useError();

  // Always use try-catch in event handlers
  // ErrorBoundary doesn't catch them!
  const handleClick = async () => {
    try {
      await someAsyncOperation();
    } catch (error) {
      addError(error);
    }
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

### Example 5: Component Error Display

```javascript
import APIError from './components/error/APIError';

function DataDisplay() {
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const loadData = async () => {
    try {
      const response = await fetch('/api/data');
      if (!response.ok) {
        throw new Error('Failed to load');
      }
      setData(await response.json());
      setError(null);
    } catch (err) {
      setError(err);
    }
  };

  if (error) {
    return (
      <APIError 
        error={error}
        onRetry={loadData}
        title="Unable to load data"
      />
    );
  }

  return <div>{/* Display data */}</div>;
}
```

## Best Practices

### 1. Always Use Try-Catch in Event Handlers

```javascript
// ✓ GOOD
const handleClick = async () => {
  try {
    await someAsyncOperation();
  } catch (error) {
    addError(error);
  }
};

// ✗ BAD - Error will not be caught by ErrorBoundary
const handleClick = async () => {
  await someAsyncOperation(); // Unhandled error!
};
```

### 2. Use Appropriate Error Severity

```javascript
// ✓ GOOD - Validation error is a warning
addError(error, { severity: ERROR_SEVERITY.WARNING });

// ✓ GOOD - Network error is critical
addError(error, { severity: ERROR_SEVERITY.CRITICAL });

// ✗ BAD - All errors treated equally
addError(error);
```

### 3. Provide Context in Error Messages

```javascript
// ✓ GOOD - Clear what failed
addError(new Error('Failed to save profile'), {
  type: ERROR_TYPES.SERVER,
  metadata: { userId: user.id }
});

// ✗ BAD - Vague error message
addError(new Error('Error'));
```

### 4. Separate UI-Level from API-Level Errors

```javascript
// ✓ GOOD - Use both for comprehensive coverage
function Component() {
  const { addError } = useError(); // App-level
  const [error, setError] = useState(null); // Component-level

  const handleLoad = async () => {
    try {
      const data = await fetch('/api/data');
      setError(null);
    } catch (err) {
      // Critical errors go to global context
      if (err.status >= 500) {
        addError(err);
      } else {
        // Non-critical errors stay component-level
        setError(err);
      }
    }
  };
}
```

### 5. Implement Proper Cleanup

```javascript
// ✓ GOOD - Clean up errors after navigation
function Page() {
  const { clearErrors } = useError();

  useEffect(() => {
    return () => clearErrors(); // Cleanup on unmount
  }, [clearErrors]);
}
```

### 6. Log Errors Appropriately

```javascript
// ✓ GOOD - Log all critical errors
const addError = (error) => {
  if (error.severity === ERROR_SEVERITY.CRITICAL) {
    console.error('Critical error:', error);
    // Also send to error tracking service
    errorTracker.capture(error);
  }
};
```

### 7. Use ErrorPage for Route-Level Errors

```javascript
// ✓ GOOD - Use ErrorPage for HTTP status codes
<Route path="/error/404" element={<ErrorPage status={404} />} />
<Route path="/error/500" element={<ErrorPage status={500} />} />

// ✗ BAD - Showing bare HTTP errors
<div>{error.status}: {error.message}</div>
```

## Testing Errors

### Testing ErrorBoundary

```javascript
import { render, screen } from '@testing-library/react';
import ErrorBoundary from './ErrorBoundary';

describe('ErrorBoundary', () => {
  // Suppress console.error for this test
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    console.error.mockRestore();
  });

  it('displays error message when child component throws', () => {
    const BrokenComponent = () => {
      throw new Error('Test error');
    };

    render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
  });

  it('displays error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    const BrokenComponent = () => {
      throw new Error('Test error');
    };

    render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Error Details/i)).toBeInTheDocument();
    expect(screen.getByText(/Test error/i)).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });
});
```

### Testing Error Context

```javascript
import { renderHook, act } from '@testing-library/react';
import { ErrorProvider, useError, ERROR_SEVERITY } from './ErrorContext';

describe('ErrorContext', () => {
  it('adds and removes errors', () => {
    const { result } = renderHook(() => useError(), {
      wrapper: ErrorProvider
    });

    act(() => {
      result.current.addError(new Error('Test error'));
    });

    expect(result.current.errors).toHaveLength(1);

    act(() => {
      result.current.removeError(result.current.errors[0].id);
    });

    expect(result.current.errors).toHaveLength(0);
  });

  it('categorizes errors correctly', async () => {
    const { result } = renderHook(() => useError(), {
      wrapper: ErrorProvider
    });

    const networkError = new Error('Network error');
    networkError.type = 'NETWORK_ERROR';

    act(() => {
      result.current.addError(networkError);
    });

    expect(result.current.errors[0].type).toBe('NETWORK');
  });
});
```

### Simulating Errors During Development

Add this utility to help simulate different error types:

```javascript
// utils/errorSimulator.js
export const simulateError = (type) => {
  const errors = {
    NETWORK: () => {
      const error = new Error('Network error');
      error.type = 'NETWORK_ERROR';
      throw error;
    },
    TIMEOUT: () => {
      const error = new Error('Request timeout');
      error.code = 'ECONNABORTED';
      throw error;
    },
    AUTH: () => {
      const error = new Error('Unauthorized');
      error.status = 401;
      throw error;
    },
    SERVER: () => {
      const error = new Error('Internal Server Error');
      error.status = 500;
      throw error;
    }
  };

  if (errors[type]) {
    errors[type]();
  }
};

// Usage in component
import { simulateError } from './utils/errorSimulator';

function DevTools() {
  return (
    <div>
      <button onClick={() => simulateError('NETWORK')}>Simulate Network Error</button>
      <button onClick={() => simulateError('TIMEOUT')}>Simulate Timeout</button>
      <button onClick={() => simulateError('AUTH')}>Simulate Auth Error</button>
      <button onClick={() => simulateError('SERVER')}>Simulate Server Error</button>
    </div>
  );
}
```

## Summary

The AgriSight error handling system provides:

1. **ErrorBoundary** for catching unhandled React errors
2. **ErrorContext** for managing application-level errors
3. **Error UI Components** for displaying errors appropriately
4. **Error Categorization** for intelligent error handling
5. **Retry Logic** with exponential backoff
6. **Development Tools** for debugging and testing

By following the best practices and examples in this guide, you can build a robust, user-friendly application that gracefully handles all types of errors.
