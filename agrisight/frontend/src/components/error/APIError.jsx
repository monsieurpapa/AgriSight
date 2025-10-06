import React from 'react';
import { AlertTriangle, RefreshCw, Wifi, WifiOff, Server, Clock, Shield, FileX } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';

const APIError = ({ 
  error, 
  onRetry, 
  title = "API Error", 
  description = "An error occurred while communicating with the server.",
  showRetry = true,
  className = ""
}) => {
  const getErrorIcon = (status) => {
    switch (status) {
      case 0:
      case 'NETWORK_ERROR':
        return <WifiOff className="h-6 w-6 text-red-600" />;
      case 401:
        return <Shield className="h-6 w-6 text-yellow-600" />;
      case 403:
        return <Shield className="h-6 w-6 text-red-600" />;
      case 404:
        return <FileX className="h-6 w-6 text-gray-600" />;
      case 500:
      case 502:
      case 503:
      case 504:
        return <Server className="h-6 w-6 text-red-600" />;
      case 'TIMEOUT':
        return <Clock className="h-6 w-6 text-yellow-600" />;
      default:
        return <AlertTriangle className="h-6 w-6 text-red-600" />;
    }
  };

  const getErrorTitle = (status) => {
    switch (status) {
      case 0:
      case 'NETWORK_ERROR':
        return "Connection Error";
      case 401:
        return "Authentication Required";
      case 403:
        return "Access Denied";
      case 404:
        return "Not Found";
      case 500:
        return "Server Error";
      case 502:
        return "Bad Gateway";
      case 503:
        return "Service Unavailable";
      case 504:
        return "Gateway Timeout";
      case 'TIMEOUT':
        return "Request Timeout";
      default:
        return title;
    }
  };

  const getErrorDescription = (status, message) => {
    switch (status) {
      case 0:
      case 'NETWORK_ERROR':
        return "Unable to connect to the server. Please check your internet connection and try again.";
      case 401:
        return "Your session has expired. Please log in again to continue.";
      case 403:
        return "You don't have permission to access this resource. Contact your administrator if you believe this is an error.";
      case 404:
        return "The requested resource was not found. It may have been moved or deleted.";
      case 500:
        return "The server encountered an internal error. Please try again later or contact support.";
      case 502:
        return "The server is temporarily unavailable. Please try again in a few moments.";
      case 503:
        return "The service is temporarily unavailable due to maintenance. Please try again later.";
      case 504:
        return "The request took too long to process. Please try again.";
      case 'TIMEOUT':
        return "The request timed out. Please check your connection and try again.";
      default:
        return message || description;
    }
  };

  const getErrorActions = (status) => {
    const actions = [];
    
    if (showRetry) {
      actions.push(
        <Button key="retry" onClick={onRetry} className="flex items-center">
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </Button>
      );
    }

    switch (status) {
      case 401:
        actions.push(
          <Button 
            key="login" 
            variant="outline" 
            onClick={() => window.location.href = '/login'}
            className="flex items-center"
          >
            Go to Login
          </Button>
        );
        break;
      case 0:
      case 'NETWORK_ERROR':
        actions.push(
          <Button 
            key="check-connection" 
            variant="outline" 
            onClick={() => window.location.reload()}
            className="flex items-center"
          >
            <Wifi className="h-4 w-4 mr-2" />
            Check Connection
          </Button>
        );
        break;
    }

    return actions;
  };

  const status = error?.response?.status || error?.status || error?.code || 0;
  const message = error?.response?.data?.message || error?.message || error?.response?.data?.detail;

  return (
    <Card className={`border-red-200 bg-red-50 dark:bg-red-900/10 ${className}`}>
      <CardContent className="p-6">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            {getErrorIcon(status)}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">
              {getErrorTitle(status)}
            </h3>
            <p className="text-red-600 dark:text-red-300 mt-1">
              {getErrorDescription(status, message)}
            </p>
            
            {process.env.NODE_ENV === 'development' && error && (
              <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/20 rounded-lg">
                <h4 className="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
                  Debug Information:
                </h4>
                <pre className="text-xs text-red-700 dark:text-red-300 overflow-auto">
                  {JSON.stringify({
                    status: status,
                    message: message,
                    url: error?.config?.url,
                    method: error?.config?.method,
                    timestamp: new Date().toISOString()
                  }, null, 2)}
                </pre>
              </div>
            )}
            
            <div className="flex flex-wrap gap-2 mt-4">
              {getErrorActions(status)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default APIError;
