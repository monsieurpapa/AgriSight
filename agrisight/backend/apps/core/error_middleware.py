"""
Error handling middleware for request/response processing.
"""

import uuid
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class TraceIDMiddleware(MiddlewareMixin):
    """
    Middleware to add trace IDs to all requests.
    
    Helps track errors and requests through the system.
    """
    
    def process_request(self, request):
        """Add trace ID to request."""
        # Get or generate trace ID
        trace_id = request.META.get('HTTP_X_TRACE_ID') or str(uuid.uuid4())
        request.trace_id = trace_id
        return None
    
    def process_response(self, response, request):
        """Add trace ID to response."""
        trace_id = getattr(request, 'trace_id', str(uuid.uuid4()))
        response['X-Trace-ID'] = trace_id
        return response


class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all errors with context.
    """
    
    # Paths to exclude from logging (e.g., health checks)
    EXCLUDE_PATHS = ['/health', '/api/health', '/__health__']
    
    def __init__(self, get_response):
        """Initialize middleware."""
        self.get_response = get_response
        super().__init__(get_response)
    
    def should_log_path(self, path):
        """Check if path should be logged."""
        return not any(path.startswith(exclude) for exclude in self.EXCLUDE_PATHS)
    
    def process_exception(self, request, exception):
        """Log exceptions with full context."""
        if not self.should_log_path(request.path):
            return None
        
        trace_id = getattr(request, 'trace_id', 'unknown')
        user_id = request.user.id if request.user and request.user.is_authenticated else None
        
        logger.error(
            f"Unhandled exception: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                'trace_id': trace_id,
                'path': request.path,
                'method': request.method,
                'user_id': user_id,
                'query_params': request.GET.dict() if request.GET else {},
            }
        )
        
        return None


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log request/response details for debugging.
    
    Only logs in development mode to avoid performance impact.
    """
    
    EXCLUDE_PATHS = ['/health', '/api/health', '/__health__', '/static/', '/media/']
    
    def should_log_path(self, path):
        """Check if path should be logged."""
        return not any(path.startswith(exclude) for exclude in self.EXCLUDE_PATHS)
    
    def process_request(self, request):
        """Log request details."""
        if not settings.DEBUG or not self.should_log_path(request.path):
            return None
        
        # Don't log request body for large uploads
        try:
            if request.content_length and request.content_length > 10000:
                request.body_logged = False
            else:
                request.body_logged = True
                # Store body for logging in process_response
                request._body_to_log = request.body
        except Exception:
            request.body_logged = False
        
        return None
    
    def process_response(self, response, request):
        """Log response details."""
        if not settings.DEBUG or not self.should_log_path(request.path):
            return response
        
        trace_id = getattr(request, 'trace_id', 'unknown')
        user_id = request.user.id if request.user and request.user.is_authenticated else None
        
        # Only log if successful (2xx, 3xx) or in debug mode
        should_log = (
            settings.DEBUG and 
            (response.status_code < 400 or getattr(request, 'path', '').startswith('/api/'))
        )
        
        if should_log:
            try:
                logger.debug(
                    f"{request.method} {request.path} - {response.status_code}",
                    extra={
                        'trace_id': trace_id,
                        'path': request.path,
                        'method': request.method,
                        'status_code': response.status_code,
                        'user_id': user_id,
                    }
                )
            except Exception:
                pass
        
        return response


class CORSErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to properly handle CORS errors.
    """
    
    def process_response(self, response, request):
        """Add CORS headers to error responses."""
        # Add CORS headers for proper error handling
        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            if origin in allowed_origins or getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False):
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken, X-Trace-ID'
                response['Access-Control-Allow-Credentials'] = 'true'
        
        return response
