import React, { Suspense, useState, useEffect } from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '../ui/alert';

/**
 * Optimized Suspense Boundary with Error Handling
 * 
 * Provides:
 * - Loading fallback with minimum display time
 * - Error boundary with retry capability
 * - Performance optimization
 */

const LoadingFallback = ({ message = 'Loading...' }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div className="text-center">
      <Loader2 className="h-8 w-8 animate-spin text-green-600 mx-auto mb-4" />
      <p className="text-gray-600 dark:text-gray-400 font-medium">{message}</p>
    </div>
  </div>
);

const ErrorFallback = ({ error, retry }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
    <Alert variant="destructive" className="max-w-md">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription>
        <p className="font-semibold mb-2">Failed to load component</p>
        <p className="text-sm mb-4">{error?.message || 'An error occurred'}</p>
        <button
          onClick={retry}
          className="inline-flex items-center justify-center px-3 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700"
        >
          Try Again
        </button>
      </AlertDescription>
    </Alert>
  </div>
);

class ErrorBoundaryWrapper extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Component loading error:', error, errorInfo);
  }

  retry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} retry={this.retry} />;
    }

    return this.props.children;
  }
}

/**
 * OptimizedSuspense Component
 * 
 * Wraps lazy-loaded components with loading state and error handling
 * 
 * Usage:
 * const MyComponent = lazy(() => import('./MyComponent'));
 * 
 * <OptimizedSuspense fallback="Loading component...">
 *   <MyComponent />
 * </OptimizedSuspense>
 */
export const OptimizedSuspense = ({ 
  children, 
  fallback = 'Loading...',
  minLoadingTime = 300 // Minimum time to show loading (ms)
}) => {
  const [showLoading, setShowLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowLoading(false), minLoadingTime);
    return () => clearTimeout(timer);
  }, [minLoadingTime]);

  return (
    <ErrorBoundaryWrapper>
      <Suspense fallback={showLoading ? <LoadingFallback message={fallback} /> : null}>
        {children}
      </Suspense>
    </ErrorBoundaryWrapper>
  );
};

/**
 * Page-level loading component for routes
 */
export const PageLoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div className="text-center">
      <div className="animate-pulse">
        <div className="h-12 w-12 bg-green-600 rounded-full mx-auto mb-6"></div>
        <div className="h-4 w-32 bg-gray-300 rounded mx-auto mb-3"></div>
        <div className="h-3 w-24 bg-gray-200 rounded mx-auto"></div>
      </div>
    </div>
  </div>
);

export default OptimizedSuspense;
