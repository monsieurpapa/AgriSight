import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  AlertTriangle, 
  Home, 
  ArrowLeft, 
  RefreshCw, 
  Wifi, 
  WifiOff,
  Server,
  Shield,
  FileX,
  Clock
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { useAuth } from '../../contexts/AuthContext';

const ErrorPage = ({ 
  status = 500, 
  title, 
  description, 
  showRetry = true,
  showBack = true 
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, getDefaultPath } = useAuth();

  const getErrorConfig = (status) => {
    switch (status) {
      case 400:
        return {
          icon: <AlertTriangle className="h-16 w-16 text-yellow-600" />,
          title: "Bad Request",
          description: "The request was invalid or cannot be processed.",
          bgColor: "bg-yellow-50 dark:bg-yellow-900/10",
          borderColor: "border-yellow-200 dark:border-yellow-800"
        };
      case 401:
        return {
          icon: <Shield className="h-16 w-16 text-blue-600" />,
          title: "Authentication Required",
          description: "Please log in to access this page.",
          bgColor: "bg-blue-50 dark:bg-blue-900/10",
          borderColor: "border-blue-200 dark:border-blue-800"
        };
      case 403:
        return {
          icon: <Shield className="h-16 w-16 text-red-600" />,
          title: "Access Denied",
          description: "You don't have permission to access this resource.",
          bgColor: "bg-red-50 dark:bg-red-900/10",
          borderColor: "border-red-200 dark:border-red-800"
        };
      case 404:
        return {
          icon: <FileX className="h-16 w-16 text-gray-600" />,
          title: "Page Not Found",
          description: "The page you're looking for doesn't exist or has been moved.",
          bgColor: "bg-gray-50 dark:bg-gray-900/10",
          borderColor: "border-gray-200 dark:border-gray-800"
        };
      case 500:
        return {
          icon: <Server className="h-16 w-16 text-red-600" />,
          title: "Server Error",
          description: "Something went wrong on our end. Please try again later.",
          bgColor: "bg-red-50 dark:bg-red-900/10",
          borderColor: "border-red-200 dark:border-red-800"
        };
      case 502:
        return {
          icon: <Server className="h-16 w-16 text-orange-600" />,
          title: "Bad Gateway",
          description: "The server is temporarily unavailable. Please try again.",
          bgColor: "bg-orange-50 dark:bg-orange-900/10",
          borderColor: "border-orange-200 dark:border-orange-800"
        };
      case 503:
        return {
          icon: <Server className="h-16 w-16 text-yellow-600" />,
          title: "Service Unavailable",
          description: "The service is temporarily down for maintenance.",
          bgColor: "bg-yellow-50 dark:bg-yellow-900/10",
          borderColor: "border-yellow-200 dark:border-yellow-800"
        };
      case 504:
        return {
          icon: <Clock className="h-16 w-16 text-purple-600" />,
          title: "Gateway Timeout",
          description: "The request took too long to process. Please try again.",
          bgColor: "bg-purple-50 dark:bg-purple-900/10",
          borderColor: "border-purple-200 dark:border-purple-800"
        };
      case 'NETWORK_ERROR':
        return {
          icon: <WifiOff className="h-16 w-16 text-red-600" />,
          title: "Connection Error",
          description: "Unable to connect to the server. Please check your internet connection.",
          bgColor: "bg-red-50 dark:bg-red-900/10",
          borderColor: "border-red-200 dark:border-red-800"
        };
      default:
        return {
          icon: <AlertTriangle className="h-16 w-16 text-gray-600" />,
          title: "Something went wrong",
          description: "An unexpected error occurred. Please try again.",
          bgColor: "bg-gray-50 dark:bg-gray-900/10",
          borderColor: "border-gray-200 dark:border-gray-800"
        };
    }
  };

  const errorConfig = getErrorConfig(status);
  const finalTitle = title || errorConfig.title;
  const finalDescription = description || errorConfig.description;

  const handleRetry = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    const homePath = isAuthenticated ? getDefaultPath() : '/landing';
    navigate(homePath);
  };

  const handleGoBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      const homePath = isAuthenticated ? getDefaultPath() : '/landing';
      navigate(homePath);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <Card className={`w-full max-w-2xl ${errorConfig.bgColor} ${errorConfig.borderColor}`}>
        <CardHeader className="text-center">
          <div className="mx-auto mb-6">
            {errorConfig.icon}
          </div>
          <CardTitle className="text-3xl text-gray-900 dark:text-white">
            {finalTitle}
          </CardTitle>
          <CardDescription className="text-lg text-gray-600 dark:text-gray-400 mt-2">
            {finalDescription}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {showRetry && (
              <Button onClick={handleRetry} className="flex items-center">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            )}
            {showBack && (
              <Button 
                variant="outline" 
                onClick={handleGoBack}
                className="flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Go Back
              </Button>
            )}
            <Button 
              variant="outline" 
              onClick={handleGoHome}
              className="flex items-center"
            >
              <Home className="h-4 w-4 mr-2" />
              Go Home
            </Button>
          </div>
          
          {import.meta.env.DEV && (
            <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Debug Information:
              </h4>
              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <div>Status: {status}</div>
                <div>Path: {location.pathname}</div>
                <div>Timestamp: {new Date().toISOString()}</div>
                <div>User Agent: {navigator.userAgent}</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ErrorPage;
