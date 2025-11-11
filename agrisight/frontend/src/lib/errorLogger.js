/**
 * Error Logging Service
 * 
 * Provides centralized error logging for the frontend application.
 * Logs to:
 * - Browser console (development)
 * - Backend error tracking service
 * - Session storage (for user support)
 */

import apiClient from './apiClient';

// Log levels
export const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL',
};

// Maximum logs to store in session
const MAX_SESSION_LOGS = 100;

/**
 * ErrorLogger class for comprehensive error logging
 */
class ErrorLogger {
  constructor() {
    this.sessionLogs = [];
    this.enableRemoteLogging = true;
    this.enableConsoleLogging = true;
    this.logLevel = process.env.NODE_ENV === 'development' ? LOG_LEVELS.DEBUG : LOG_LEVELS.ERROR;
  }

  /**
   * Log an error with full context
   */
  logError(error, context = {}) {
    const errorLog = this._createErrorLog(error, context);
    this._writeLog(errorLog);
  }

  /**
   * Log a message
   */
  log(message, level = LOG_LEVELS.INFO, context = {}) {
    const log = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      url: window.location.href,
      userAgent: navigator.userAgent,
    };
    this._writeLog(log);
  }

  /**
   * Log warning
   */
  warn(message, context = {}) {
    this.log(message, LOG_LEVELS.WARN, context);
  }

  /**
   * Log debug message (only in development)
   */
  debug(message, context = {}) {
    if (process.env.NODE_ENV === 'development') {
      this.log(message, LOG_LEVELS.DEBUG, context);
    }
  }

  /**
   * Log critical error
   */
  critical(message, error = null, context = {}) {
    if (error) {
      this.logError(error, { level: LOG_LEVELS.CRITICAL, ...context });
    } else {
      this.log(message, LOG_LEVELS.CRITICAL, context);
    }
  }

  /**
   * Create structured error log
   */
  _createErrorLog(error, context = {}) {
    return {
      timestamp: new Date().toISOString(),
      level: context.level || LOG_LEVELS.ERROR,
      type: error.type || 'UNKNOWN_ERROR',
      message: error.message || String(error),
      status: error.status || null,
      code: error.code || null,
      stack: error.stack || '',
      url: window.location.href,
      userAgent: navigator.userAgent,
      context,
      // Include trace ID if available
      traceId: error.traceId || context.traceId || this._getTraceId(),
    };
  }

  /**
   * Write log to multiple destinations
   */
  _writeLog(log) {
    // Store in session
    this._storeInSession(log);

    // Log to console (development only)
    if (this.enableConsoleLogging) {
      this._logToConsole(log);
    }

    // Send to backend (errors and critical logs only)
    if (
      this.enableRemoteLogging &&
      (log.level === LOG_LEVELS.ERROR || log.level === LOG_LEVELS.CRITICAL)
    ) {
      this._sendToBackend(log);
    }
  }

  /**
   * Store log in session storage
   */
  _storeInSession(log) {
    try {
      if (!sessionStorage) return;

      const logs = this._getSessionLogs();
      logs.push(log);

      // Keep only last 100 logs
      if (logs.length > MAX_SESSION_LOGS) {
        logs.shift();
      }

      sessionStorage.setItem('errorLogs', JSON.stringify(logs));
    } catch (e) {
      // Silently fail if storage full
      console.warn('Failed to store log in session:', e);
    }
  }

  /**
   * Get all logs from session storage
   */
  _getSessionLogs() {
    try {
      if (!sessionStorage) return [];
      const logs = sessionStorage.getItem('errorLogs');
      return logs ? JSON.parse(logs) : [];
    } catch (e) {
      return [];
    }
  }

  /**
   * Log to console with appropriate styling
   */
  _logToConsole(log) {
    const timestamp = new Date(log.timestamp).toLocaleTimeString();
    const prefix = `[${timestamp}] ${log.level}`;

    switch (log.level) {
      case LOG_LEVELS.DEBUG:
        console.debug(`%c${prefix}`, 'color: gray', log.message, log.context);
        break;

      case LOG_LEVELS.INFO:
        console.info(`%c${prefix}`, 'color: blue', log.message, log.context);
        break;

      case LOG_LEVELS.WARN:
        console.warn(`%c${prefix}`, 'color: orange', log.message, log.context);
        if (log.stack) {
          console.warn('Stack:', log.stack);
        }
        break;

      case LOG_LEVELS.ERROR:
        console.error(`%c${prefix}`, 'color: red', log.message, log.context);
        if (log.stack) {
          console.error('Stack:', log.stack);
        }
        break;

      case LOG_LEVELS.CRITICAL:
        console.error(`%c${prefix}`, 'color: darkred; font-weight: bold', log.message, log.context);
        if (log.stack) {
          console.error('Stack:', log.stack);
        }
        break;

      default:
        console.log(`${prefix}:`, log.message, log.context);
    }
  }

  /**
   * Send error log to backend
   */
  async _sendToBackend(log) {
    try {
      await apiClient.post('/api/logs/errors/', {
        timestamp: log.timestamp,
        level: log.level,
        type: log.type,
        message: log.message,
        status: log.status,
        code: log.code,
        stack: log.stack,
        url: log.url,
        context: log.context,
        traceId: log.traceId,
      });
    } catch (error) {
      // Silently fail - don't create infinite loop of error logging
      console.warn('Failed to send error log to backend:', error);
    }
  }

  /**
   * Get or create trace ID
   */
  _getTraceId() {
    if (!sessionStorage) return null;

    let traceId = sessionStorage.getItem('traceId');
    if (!traceId) {
      traceId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('traceId', traceId);
    }
    return traceId;
  }

  /**
   * Get all session logs
   */
  getSessionLogs() {
    return this._getSessionLogs();
  }

  /**
   * Clear session logs
   */
  clearSessionLogs() {
    try {
      if (sessionStorage) {
        sessionStorage.removeItem('errorLogs');
      }
    } catch (e) {
      console.warn('Failed to clear session logs:', e);
    }
  }

  /**
   * Export logs for debugging
   */
  exportLogs() {
    const logs = this.getSessionLogs();
    const dataStr = JSON.stringify(logs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `error-logs-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Configure logger
   */
  configure(options = {}) {
    if (options.enableRemoteLogging !== undefined) {
      this.enableRemoteLogging = options.enableRemoteLogging;
    }
    if (options.enableConsoleLogging !== undefined) {
      this.enableConsoleLogging = options.enableConsoleLogging;
    }
    if (options.logLevel !== undefined) {
      this.logLevel = options.logLevel;
    }
  }
}

// Create singleton instance
const errorLogger = new ErrorLogger();

// Expose in development for debugging
if (process.env.NODE_ENV === 'development') {
  window.errorLogger = errorLogger;
}

export default errorLogger;

/**
 * Global error handler for uncaught errors
 */
export function setupGlobalErrorHandlers() {
  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    errorLogger.logError(event.error || new Error(event.message), {
      type: 'UNCAUGHT_ERROR',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    });
  });

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    errorLogger.logError(event.reason || new Error('Unhandled Promise rejection'), {
      type: 'UNHANDLED_REJECTION',
    });
  });

  // Log performance metrics
  if (window.performance && window.performance.timing) {
    window.addEventListener('load', () => {
      const timing = window.performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;

      if (loadTime > 5000) {
        // Warn if load time is excessive
        errorLogger.warn('Page load time excessive', {
          loadTime,
          type: 'PERFORMANCE',
          threshold: 5000,
        });
      }
    });
  }
}

/**
 * Create an error logger wrapper for React Error Boundary
 */
export function createErrorBoundaryLogger() {
  return {
    captureException: (error, context = {}) => {
      errorLogger.logError(error, {
        type: 'REACT_ERROR_BOUNDARY',
        componentStack: context.componentStack,
        ...context,
      });
    },

    captureMessage: (message, level = LOG_LEVELS.ERROR) => {
      errorLogger.log(message, level);
    },
  };
}

/**
 * Create API call logger
 */
export function createAPILogger() {
  return {
    logRequest: (config) => {
      errorLogger.debug('API Request', {
        method: config.method?.toUpperCase(),
        url: config.url,
        params: config.params,
      });
    },

    logResponse: (response) => {
      errorLogger.debug('API Response', {
        status: response.status,
        url: response.config.url,
        duration: response.duration,
      });
    },

    logError: (error) => {
      errorLogger.logError(error, {
        type: 'API_ERROR',
        status: error.status,
        url: error.url,
      });
    },
  };
}
