import React from 'react';
import { AlertTriangle, RefreshCcw, Home } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    // You would typically log this to an error reporting service like Sentry
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[400px] flex items-center justify-center p-6 text-center">
          <Card className="max-w-md w-full shadow-lg border-red-100">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-red-100 rounded-full">
                  <AlertTriangle className="h-10 w-10 text-red-600" />
                </div>
              </div>
              <CardTitle className="text-2xl font-bold text-gray-900">Something went wrong</CardTitle>
              <CardDescription className="text-gray-600">
                An unexpected error occurred in this part of the application.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col space-y-2">
                <Button
                  onClick={() => window.location.reload()}
                  className="w-full flex items-center justify-center gap-2"
                >
                  <RefreshCcw className="h-4 w-4" />
                  Reload Page
                </Button>
                <Button
                  variant="outline"
                  onClick={() => window.location.href = '/'}
                  className="w-full flex items-center justify-center gap-2"
                >
                  <Home className="h-4 w-4" />
                  Return to Dashboard
                </Button>
              </div>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="text-left mt-4 text-xs font-mono bg-gray-50 p-3 rounded overflow-auto max-h-40">
                  <summary className="cursor-pointer text-gray-700 font-semibold mb-2">Error Details</summary>
                  <pre className="text-red-600">{this.state.error.toString()}</pre>
                  <pre className="text-gray-500">{this.state.errorInfo.componentStack}</pre>
                </details>
              )}
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
