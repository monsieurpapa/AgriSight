import React, { createContext, useContext, useCallback, useReducer } from 'react';

/**
 * ErrorContext: Centralized error handling for the entire application
 * 
 * Manages:
 * - Error state and history
 * - Error notifications
 * - Retry logic
 * - Error categorization and severity levels
 */

// Error types and severities
export const ERROR_TYPES = {
  NETWORK: 'NETWORK',
  TIMEOUT: 'TIMEOUT',
  AUTH: 'AUTH',
  VALIDATION: 'VALIDATION',
  SERVER: 'SERVER',
  CLIENT: 'CLIENT',
  UNKNOWN: 'UNKNOWN',
};

export const ERROR_SEVERITY = {
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL',
};

// Initial state
const initialState = {
  errors: [],
  activeError: null,
  isRetrying: false,
  retryCount: 0,
  maxRetries: 3,
};

// Action types
const ERROR_ACTIONS = {
  ADD_ERROR: 'ADD_ERROR',
  REMOVE_ERROR: 'REMOVE_ERROR',
  CLEAR_ERRORS: 'CLEAR_ERRORS',
  SET_ACTIVE_ERROR: 'SET_ACTIVE_ERROR',
  RETRY_START: 'RETRY_START',
  RETRY_END: 'RETRY_END',
  RETRY_RESET: 'RETRY_RESET',
};

/**
 * Error reducer
 */
const errorReducer = (state, action) => {
  switch (action.type) {
    case ERROR_ACTIONS.ADD_ERROR: {
      const newError = {
        id: `${Date.now()}-${Math.random()}`,
        timestamp: new Date().toISOString(),
        ...action.payload,
      };
      return {
        ...state,
        errors: [...state.errors, newError],
        activeError: newError,
      };
    }

    case ERROR_ACTIONS.REMOVE_ERROR:
      return {
        ...state,
        errors: state.errors.filter((e) => e.id !== action.payload),
        activeError:
          state.activeError?.id === action.payload ? null : state.activeError,
      };

    case ERROR_ACTIONS.CLEAR_ERRORS:
      return {
        ...state,
        errors: [],
        activeError: null,
      };

    case ERROR_ACTIONS.SET_ACTIVE_ERROR:
      return {
        ...state,
        activeError: state.errors.find((e) => e.id === action.payload) || null,
      };

    case ERROR_ACTIONS.RETRY_START:
      return {
        ...state,
        isRetrying: true,
        retryCount: state.retryCount + 1,
      };

    case ERROR_ACTIONS.RETRY_END:
      return {
        ...state,
        isRetrying: false,
      };

    case ERROR_ACTIONS.RETRY_RESET:
      return {
        ...state,
        retryCount: 0,
        isRetrying: false,
      };

    default:
      return state;
  }
};

/**
 * ErrorContext
 */
const ErrorContext = createContext();

/**
 * ErrorProvider component
 */
export const ErrorProvider = ({ children }) => {
  const [state, dispatch] = useReducer(errorReducer, initialState);

  /**
   * Categorize and add error
   */
  const addError = useCallback((error, metadata = {}) => {
    const categorizedError = categorizeError(error);

    dispatch({
      type: ERROR_ACTIONS.ADD_ERROR,
      payload: {
        ...categorizedError,
        ...metadata,
      },
    });
  }, []);

  /**
   * Remove error by ID
   */
  const removeError = useCallback((errorId) => {
    dispatch({
      type: ERROR_ACTIONS.REMOVE_ERROR,
      payload: errorId,
    });
  }, []);

  /**
   * Clear all errors
   */
  const clearErrors = useCallback(() => {
    dispatch({
      type: ERROR_ACTIONS.CLEAR_ERRORS,
    });
  }, []);

  /**
   * Set active error
   */
  const setActiveError = useCallback((errorId) => {
    dispatch({
      type: ERROR_ACTIONS.SET_ACTIVE_ERROR,
      payload: errorId,
    });
  }, []);

  /**
   * Handle retry attempt
   */
  const handleRetry = useCallback(async (retryFn) => {
    if (state.retryCount >= state.maxRetries) {
      addError(
        new Error('Maximum retry attempts reached'),
        { severity: ERROR_SEVERITY.CRITICAL }
      );
      return false;
    }

    dispatch({ type: ERROR_ACTIONS.RETRY_START });

    try {
      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, state.retryCount - 1) * 1000;
      await new Promise((resolve) => setTimeout(resolve, delay));

      await retryFn();

      dispatch({ type: ERROR_ACTIONS.RETRY_RESET });
      clearErrors();
      return true;
    } catch (error) {
      dispatch({ type: ERROR_ACTIONS.RETRY_END });
      addError(error);
      return false;
    }
  }, [state.retryCount, state.maxRetries, addError, clearErrors]);

  /**
   * Reset retry state
   */
  const resetRetry = useCallback(() => {
    dispatch({ type: ERROR_ACTIONS.RETRY_RESET });
  }, []);

  const value = {
    ...state,
    addError,
    removeError,
    clearErrors,
    setActiveError,
    handleRetry,
    resetRetry,
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};

/**
 * Hook to use error context
 */
export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within ErrorProvider');
  }
  return context;
};

/**
 * Categorize error based on type and status
 */
export const categorizeError = (error) => {
  if (!error) {
    return {
      type: ERROR_TYPES.UNKNOWN,
      message: 'An unknown error occurred',
      severity: ERROR_SEVERITY.ERROR,
      status: null,
    };
  }

  // Network error
  if (error.type === 'NETWORK_ERROR' || error.message?.includes('connect')) {
    return {
      type: ERROR_TYPES.NETWORK,
      message:
        'Network connection failed. Please check your internet connection.',
      severity: ERROR_SEVERITY.ERROR,
      status: 0,
    };
  }

  // Timeout error
  if (error.type === 'TIMEOUT' || error.code === 'ECONNABORTED') {
    return {
      type: ERROR_TYPES.TIMEOUT,
      message: 'Request timed out. Please try again.',
      severity: ERROR_SEVERITY.WARNING,
      status: null,
    };
  }

  // Authentication errors (401)
  if (error.status === 401) {
    return {
      type: ERROR_TYPES.AUTH,
      message: 'Your session has expired. Please log in again.',
      severity: ERROR_SEVERITY.ERROR,
      status: 401,
    };
  }

  // Authorization errors (403)
  if (error.status === 403) {
    return {
      type: ERROR_TYPES.AUTH,
      message: 'You do not have permission to perform this action.',
      severity: ERROR_SEVERITY.WARNING,
      status: 403,
    };
  }

  // Validation errors (400)
  if (error.status === 400) {
    return {
      type: ERROR_TYPES.VALIDATION,
      message:
        error.message || 'The request contains invalid data. Please check and try again.',
      severity: ERROR_SEVERITY.WARNING,
      status: 400,
      details: error.data,
    };
  }

  // Server errors (5xx)
  if (error.status >= 500) {
    return {
      type: ERROR_TYPES.SERVER,
      message: 'Server error. Please try again later.',
      severity: ERROR_SEVERITY.CRITICAL,
      status: error.status,
    };
  }

  // Client errors (4xx)
  if (error.status >= 400) {
    return {
      type: ERROR_TYPES.CLIENT,
      message: error.message || 'An error occurred. Please try again.',
      severity: ERROR_SEVERITY.WARNING,
      status: error.status,
    };
  }

  // Default error
  return {
    type: ERROR_TYPES.UNKNOWN,
    message: error.message || 'An unexpected error occurred',
    severity: ERROR_SEVERITY.ERROR,
    status: null,
  };
};

export default ErrorContext;
