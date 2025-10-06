"""
Core views for the AgriSight application.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    """
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
        'timestamp': '2024-01-01T00:00:00Z'  # This would be timezone.now().isoformat() in production
    }, status=status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE)


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
