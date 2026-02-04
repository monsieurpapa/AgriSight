"""
Core views for the AgriSight application.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from celery import current_app
import redis
import logging

logger = logging.getLogger(__name__)


def require_admin(user):
    return user.is_authenticated and getattr(user, 'user_type', None) == 'admin'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    """
    if not require_admin(request.user):
        return Response({'detail': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check Redis connection
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"
    
    # Overall health status
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"
    
    return Response({
        'status': overall_status,
        'database': db_status,
        'cache': redis_status,
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def health_check_detailed(request):
    """
    Detailed health check endpoint for admins.
    """
    if not require_admin(request.user):
        return Response({'detail': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    services = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            services['database'] = 'healthy'
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        services['database'] = 'unhealthy'

    try:
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check')
        services['redis'] = 'healthy' if result == 'ok' else 'unhealthy'
    except Exception as exc:
        logger.error(f"Redis health check failed: {exc}")
        services['redis'] = 'unhealthy'

    try:
        current_app.control.inspect().stats()
        services['celery'] = 'healthy'
    except Exception as exc:
        logger.error(f"Celery health check failed: {exc}")
        services['celery'] = 'unhealthy'

    overall = 'healthy' if all(value == 'healthy' for value in services.values()) else 'unhealthy'
    return Response({
        'status': overall,
        'services': services,
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK if overall == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_info(request):
    """
    API information endpoint.
    """
    return Response({
        'name': 'AgriSight API',
        'version': '1.0.0',
        'description': 'Satellite-based agricultural monitoring platform API',
        'documentation': '/api/schema/',
        'endpoints': {
            'health': '/api/health/',
            'auth': '/api/auth/',
            'users': '/api/v1/users/',
            'organizations': '/api/v1/organizations/',
            'regions': '/api/v1/regions/',
            'analytics': '/api/v1/analytics/',
            'reports': '/api/v1/reports-alerts/',
            'satellite': '/api/v1/satellite-processing/',
            'ml_models': '/api/v1/ml-models/',
            'api_keys': '/api/v1/api-keys/'
        }
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def log_frontend_error(request):
    """
    Receive frontend error logs and write them to server logs.
    """
    try:
        payload = request.data if isinstance(request.data, dict) else {}
        logger.error(
            "Frontend error log received",
            extra={
                'frontend_error': payload,
                'request_ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        return Response({'status': 'logged'}, status=status.HTTP_202_ACCEPTED)
    except Exception as exc:
        logger.exception(f"Failed to log frontend error: {exc}")
        return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
