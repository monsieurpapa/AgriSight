"""
Custom middleware for error handling, logging, and security.
"""

import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import connection
from django.core.cache import cache
from django.db import DatabaseError
from rest_framework import status
from celery import current_app
from rest_framework.response import Response
import traceback

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Comprehensive error handling middleware that catches and logs all exceptions.
    """
    
    def process_exception(self, request, exception):
        """Process exceptions and return appropriate error responses."""
        # Log the exception
        self._log_exception(request, exception)
        
        # Determine error type and response
        if isinstance(exception, ValidationError):
            return self._handle_validation_error(request, exception)
        elif isinstance(exception, DatabaseError):
            return self._handle_database_error(request, exception)
        elif isinstance(exception, (PermissionDenied, PermissionError)):
            return self._handle_permission_error(request, exception)
        else:
            return self._handle_generic_error(request, exception)
    
    def _log_exception(self, request, exception):
        """Log exception details."""
        # Safely get user information
        user_info = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = getattr(request.user, 'username', 'authenticated_user')
        elif hasattr(request, 'user'):
            user_info = 'anonymous'
        
        logger.error(
            f"Exception in {request.method} {request.path}: {str(exception)}",
            extra={
                'request_method': request.method,
                'request_path': request.path,
                'request_user': user_info,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': traceback.format_exc()
            }
        )
    
    def _handle_validation_error(self, request, exception):
        """Handle validation errors."""
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Validation Error',
                'message': str(exception),
                'details': getattr(exception, 'message_dict', None)
            }, status=status.HTTP_400_BAD_REQUEST)
        return None
    
    def _handle_database_error(self, request, exception):
        """Handle database errors."""
        if request.path.startswith('/api/'):
            if settings.DEBUG:
                return JsonResponse({
                    'error': 'Database Error',
                    'message': str(exception)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({
                    'error': 'Database Error',
                    'message': 'An internal error occurred. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return None
    
    def _handle_permission_error(self, request, exception):
        """Handle permission errors."""
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Permission Denied',
                'message': 'You do not have permission to perform this action.'
            }, status=status.HTTP_403_FORBIDDEN)
        return None
    
    def _handle_generic_error(self, request, exception):
        """Handle generic errors."""
        if request.path.startswith('/api/'):
            if settings.DEBUG:
                return JsonResponse({
                    'error': 'Internal Server Error',
                    'message': str(exception),
                    'type': type(exception).__name__
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses for monitoring and debugging.
    """
    
    def process_request(self, request):
        """Log incoming request."""
        request._start_time = time.time()
        
        # Safely get user information
        user_info = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = getattr(request.user, 'username', 'authenticated_user')
        elif hasattr(request, 'user'):
            user_info = 'anonymous'
        
        # Log request details
        logger.info(
            f"Incoming request: {request.method} {request.path}",
            extra={
                'request_method': request.method,
                'request_path': request.path,
                'request_user': user_info,
                'request_ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'request_size': len(request.body) if hasattr(request, 'body') else 0
            }
        )
    
    def process_response(self, request, response):
        """Log outgoing response."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Safely get user information
            user_info = 'anonymous'
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = getattr(request.user, 'username', 'authenticated_user')
            elif hasattr(request, 'user'):
                user_info = 'anonymous'
            
            logger.info(
                f"Response: {request.method} {request.path} - {response.status_code} ({duration:.3f}s)",
                extra={
                    'request_method': request.method,
                    'request_path': request.path,
                    'request_user': user_info,
                    'response_status': response.status_code,
                    'response_duration': duration,
                    'response_size': len(response.content) if hasattr(response, 'content') else 0
                }
            )
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=(), "
            "vibrate=(), "
            "fullscreen=(self)"
        )
        
        # Strict Transport Security (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Fixed-window API rate limiting backed by the shared Django cache (Redis).

    Previously this kept counters in a per-process dict with a hard 100
    requests/hour/IP budget. A single dashboard load uses ~60 API calls, so
    users were throttled within a couple of page views; the resulting 429 on
    /api/auth/user/ made the SPA treat them as logged out. Counters were also
    per gunicorn worker and reset on restart, and the client IP was taken from
    a spoofable X-Forwarded-For header.

    Settings (all optional):
      API_RATE_LIMIT_REQUESTS          requests allowed per window (default 1000)
      API_RATE_LIMIT_WINDOW_SECONDS    window length (default 3600)
      API_RATE_LIMIT_EXEMPT_PATHS      path prefixes never counted
      API_RATE_LIMIT_TRUSTED_PROXIES   number of reverse proxies in front of
                                       Django; X-Forwarded-For is only used
                                       when this is > 0 (default 0)
    """

    CACHE_KEY_PREFIX = 'ratelimit:api'
    DEFAULT_EXEMPT_PATHS = (
        # Cheap session-bootstrap reads the SPA makes on every full page load.
        '/api/auth/csrf/',
        '/api/auth/config/',
        '/api/auth/user/',
    )

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    @property
    def limit(self):
        return int(getattr(settings, 'API_RATE_LIMIT_REQUESTS', 1000))

    @property
    def window(self):
        return int(getattr(settings, 'API_RATE_LIMIT_WINDOW_SECONDS', 3600))

    @property
    def exempt_paths(self):
        return tuple(getattr(settings, 'API_RATE_LIMIT_EXEMPT_PATHS', self.DEFAULT_EXEMPT_PATHS))

    def process_request(self, request):
        """Check rate limits."""
        if not request.path.startswith('/api/'):
            return None
        if request.method == 'OPTIONS' or request.path.startswith(self.exempt_paths):
            return None

        client_ip = self._get_client_ip(request)
        window_start = int(time.time() // self.window)
        key = f'{self.CACHE_KEY_PREFIX}:{client_ip}:{window_start}'

        try:
            # add() is a no-op if the key exists; incr() is atomic in Redis.
            cache.add(key, 0, timeout=self.window + 60)
            request_count = cache.incr(key)
        except Exception as exc:  # cache unavailable -> fail open, never block users
            logger.warning('Rate limit cache unavailable, allowing request: %s', exc)
            return None

        if request_count > self.limit:
            retry_after = self.window - int(time.time() % self.window)
            response = JsonResponse({
                'error': 'Rate Limit Exceeded',
                'message': 'Too many requests. Please try again later.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            response['Retry-After'] = str(max(retry_after, 1))
            return response
        return None

    def _get_client_ip(self, request):
        """
        Get the client IP. X-Forwarded-For is client-controlled, so it is only
        consulted when API_RATE_LIMIT_TRUSTED_PROXIES is set, and then we take
        the entry appended by the outermost trusted proxy (counting from the
        right), not the spoofable left-most entry.
        """
        trusted = int(getattr(settings, 'API_RATE_LIMIT_TRUSTED_PROXIES', 0))
        remote_addr = request.META.get('REMOTE_ADDR', 'unknown')
        if trusted <= 0:
            return remote_addr
        forwarded = [ip.strip() for ip in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',') if ip.strip()]
        if not forwarded:
            return remote_addr
        return forwarded[-trusted] if len(forwarded) >= trusted else forwarded[0]


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning.
    """
    
    def process_request(self, request):
        """Add API version to request."""
        if request.path.startswith('/api/'):
            # Extract version from Accept header or URL
            accept_header = request.META.get('HTTP_ACCEPT', '')
            if 'application/vnd.agrisight.v1+json' in accept_header:
                request.api_version = 'v1'
            elif '/api/v1/' in request.path:
                request.api_version = 'v1'
            else:
                request.api_version = 'v1'  # Default version
        
        return None


class HealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware to handle health check endpoints.
    """
    
    def process_request(self, request):
        """Handle health check requests."""
        if request.path == '/health/':
            return JsonResponse({
                'status': 'healthy',
                'timestamp': time.time(),
                'version': '1.0.0'
            })
        elif request.path == '/health/detailed/':
            # Detailed health check
            health_status = {
                'status': 'healthy',
                'timestamp': time.time(),
                'version': '1.0.0',
                'services': {
                    'database': self._check_database(),
                    'redis': self._check_redis(),
                    'celery': self._check_celery()
                }
            }
            
            # Check if any service is unhealthy
            for service, status in health_status['services'].items():
                if status != 'healthy':
                    health_status['status'] = 'unhealthy'
                    break
            
            return JsonResponse(health_status)
    
    def _check_database(self):
        """Check database connectivity."""
        try:
            connection.ensure_connection()
            return 'healthy'
        except Exception:
            return 'unhealthy'
    
    def _check_redis(self):
        """Check Redis connectivity."""
        try:
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            return 'healthy' if result == 'ok' else 'unhealthy'
        except Exception:
            return 'unhealthy'
    
    def _check_celery(self):
        """Check Celery connectivity."""
        try:
            # stats() returns None/{} when no worker replies; only a reply
            # from at least one worker means Celery can process tasks.
            stats = current_app.control.inspect(timeout=1.0).stats()
            return 'healthy' if stats else 'unhealthy'
        except Exception:
            return 'unhealthy'
