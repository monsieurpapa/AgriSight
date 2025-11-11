import React, { useEffect } from 'react';
import { X, AlertCircle, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { useError, ERROR_SEVERITY } from '../../contexts/ErrorContext';
import { cn } from '../../lib/utils';

/**
 * ErrorNotification Component
 * 
 * Displays error notifications with:
 * - Auto-dismiss functionality
 * - Retry buttons for retryable errors
 * - Different severity levels
 * - Smooth animations
 */
const ErrorNotification = ({ error, onDismiss }) => {
  if (!error) return null;

  const { severity, message, type, status } = error;

  // Determine icon and colors based on severity
  const getStyles = () => {
    switch (severity) {
      case ERROR_SEVERITY.INFO:
        return {
          bgColor: 'bg-blue-50 dark:bg-blue-900/10',
          borderColor: 'border-blue-200 dark:border-blue-800',
          textColor: 'text-blue-800 dark:text-blue-200',
          icon: <Info className="h-5 w-5 text-blue-600" />,
          autoDismiss: 5000,
        };
      case ERROR_SEVERITY.WARNING:
        return {
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/10',
          borderColor: 'border-yellow-200 dark:border-yellow-800',
          textColor: 'text-yellow-800 dark:text-yellow-200',
          icon: <AlertTriangle className="h-5 w-5 text-yellow-600" />,
          autoDismiss: 7000,
        };
      case ERROR_SEVERITY.ERROR:
        return {
          bgColor: 'bg-red-50 dark:bg-red-900/10',
          borderColor: 'border-red-200 dark:border-red-800',
          textColor: 'text-red-800 dark:text-red-200',
          icon: <AlertCircle className="h-5 w-5 text-red-600" />,
          autoDismiss: 10000,
        };
      case ERROR_SEVERITY.CRITICAL:
        return {
          bgColor: 'bg-red-100 dark:bg-red-900/20',
          borderColor: 'border-red-300 dark:border-red-700',
          textColor: 'text-red-900 dark:text-red-100',
          icon: <AlertCircle className="h-5 w-5 text-red-700" />,
          autoDismiss: 0, // Don't auto-dismiss critical errors
        };
      default:
        return {
          bgColor: 'bg-gray-50 dark:bg-gray-900/10',
          borderColor: 'border-gray-200 dark:border-gray-800',
          textColor: 'text-gray-800 dark:text-gray-200',
          icon: <AlertCircle className="h-5 w-5 text-gray-600" />,
          autoDismiss: 5000,
        };
    }
  };

  const styles = getStyles();

  // Auto-dismiss after timeout
  useEffect(() => {
    if (styles.autoDismiss > 0) {
      const timeout = setTimeout(onDismiss, styles.autoDismiss);
      return () => clearTimeout(timeout);
    }
  }, [styles.autoDismiss, onDismiss]);

  return (
    <div
      className={cn(
        'rounded-lg border p-4 shadow-sm',
        'animate-in fade-in slide-in-from-top-4 duration-300',
        styles.bgColor,
        styles.borderColor,
        styles.textColor
      )}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">{styles.icon}</div>

        <div className="flex-1">
          <p className="font-medium">{message}</p>
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-2 text-xs opacity-70">
              <p>Type: {type}</p>
              {status && <p>Status: {status}</p>}
            </div>
          )}
        </div>

        <button
          onClick={onDismiss}
          className="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity"
          aria-label="Dismiss"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

/**
 * ErrorNotificationStack Component
 * 
 * Displays a stack of error notifications
 */
export const ErrorNotificationStack = () => {
  const { errors, removeError } = useError();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {errors.map((error) => (
        <ErrorNotification
          key={error.id}
          error={error}
          onDismiss={() => removeError(error.id)}
        />
      ))}
    </div>
  );
};

export default ErrorNotification;
