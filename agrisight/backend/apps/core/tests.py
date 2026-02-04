"""
Comprehensive tests for core middleware and utilities.
"""

from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import DatabaseError
from unittest.mock import patch, MagicMock
import json

from .middleware import (
    ErrorHandlingMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    APIVersionMiddleware,
    HealthCheckMiddleware
)

User = get_user_model()


class ErrorHandlingMiddlewareTest(TestCase):
    """Test error handling middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = ErrorHandlingMiddleware(get_response=lambda req: HttpResponse())
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        exception = ValidationError('Test validation error')
        
        response = self.middleware.process_exception(request, exception)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Validation Error')
    
    def test_database_error_handling(self):
        """Test handling of database errors."""
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        exception = DatabaseError('Test database error')
        
        with self.settings(DEBUG=True):
            response = self.middleware.process_exception(request, exception)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.content)
            self.assertEqual(data['error'], 'Database Error')
    
    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        exception = PermissionDenied('Test permission error')
        
        response = self.middleware.process_exception(request, exception)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Permission Denied')
    
    def test_generic_error_handling(self):
        """Test handling of generic errors."""
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        exception = ValueError('Test generic error')
        
        with self.settings(DEBUG=True):
            response = self.middleware.process_exception(request, exception)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.content)
            self.assertEqual(data['error'], 'Internal Server Error')
    
    def test_non_api_error_handling(self):
        """Test that non-API errors are not handled by middleware."""
        request = self.factory.get('/non-api/test/')
        request.user = self.user
        
        exception = ValueError('Test error')
        
        response = self.middleware.process_exception(request, exception)
        
        self.assertIsNone(response)


class SecurityHeadersMiddlewareTest(TestCase):
    """Test security headers middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(get_response=lambda req: HttpResponse())
    
    def test_security_headers_added(self):
        """Test that security headers are added to responses."""
        request = self.factory.get('/')
        response = HttpResponse()
        
        processed_response = self.middleware.process_response(request, response)
        
        # Check security headers
        self.assertEqual(processed_response['X-Frame-Options'], 'DENY')
        self.assertEqual(processed_response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(processed_response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(processed_response['Referrer-Policy'], 'strict-origin-when-cross-origin')
        
        # Check CSP header exists
        self.assertIn('Content-Security-Policy', processed_response)
    
    def test_https_security_headers(self):
        """Test security headers for HTTPS requests."""
        request = self.factory.get('/', secure=True)
        response = HttpResponse()
        
        processed_response = self.middleware.process_response(request, response)
        
        # Check HSTS header for HTTPS
        self.assertIn('Strict-Transport-Security', processed_response)


class RateLimitMiddlewareTest(TestCase):
    """Test rate limiting middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(get_response=lambda req: HttpResponse())
    
    def test_rate_limit_normal_requests(self):
        """Test that normal requests pass through."""
        request = self.factory.get('/api/test/')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)  # No rate limiting
    
    def test_rate_limit_exceeded(self):
        """Test rate limiting when limit is exceeded."""
        request = self.factory.get('/api/test/')
        
        # Simulate many requests
        now = __import__('time').time()
        for _ in range(101):  # Exceed the limit of 100
            self.middleware.requests.setdefault('127.0.0.1', []).append(now)
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 429)


class HealthCheckMiddlewareTest(TestCase):
    """Test health check middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = HealthCheckMiddleware(get_response=lambda req: HttpResponse())
    
    def test_basic_health_check(self):
        """Test basic health check endpoint."""
        request = self.factory.get('/health/')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
    
    @patch('apps.core.middleware.cache')
    @patch('apps.core.middleware.connection')
    @patch('apps.core.middleware.current_app')
    def test_detailed_health_check(self, mock_celery, mock_db, mock_cache):
        """Test detailed health check endpoint."""
        # Mock all services as healthy
        mock_db.ensure_connection.return_value = None
        mock_cache.set.return_value = True
        mock_cache.get.return_value = 'ok'
        mock_celery.control.inspect.return_value.stats.return_value = {}
        
        request = self.factory.get('/health/detailed/')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('services', data)
        self.assertEqual(data['services']['database'], 'healthy')
        self.assertEqual(data['services']['redis'], 'healthy')
        self.assertEqual(data['services']['celery'], 'healthy')
    
    @patch('apps.core.middleware.cache')
    @patch('apps.core.middleware.connection')
    @patch('apps.core.middleware.current_app')
    def test_unhealthy_services(self, mock_celery, mock_db, mock_cache):
        """Test health check with unhealthy services."""
        # Mock database as unhealthy
        mock_db.ensure_connection.side_effect = Exception('Database error')
        mock_cache.set.return_value = True
        mock_cache.get.return_value = 'ok'
        mock_celery.control.inspect.return_value.stats.return_value = {}
        
        request = self.factory.get('/health/detailed/')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNotNone(response)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['services']['database'], 'unhealthy')


class HealthCheckViewTest(TestCase):
    """Test health check API views with admin gating."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
        self.user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='testpass123',
            user_type='humanitarian'
        )

    @patch('apps.core.views.cache')
    @patch('apps.core.views.connection')
    def test_health_check_admin_only(self, mock_connection, mock_cache):
        mock_connection.cursor.return_value.__enter__.return_value.execute.return_value = None
        mock_cache.set.return_value = True
        mock_cache.get.return_value = 'ok'

        self.client.force_login(self.user)
        forbidden = self.client.get('/api/health/')
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)

    @patch('apps.core.views.cache')
    @patch('apps.core.views.connection')
    @patch('apps.core.views.current_app')
    def test_health_check_detailed_admin_only(self, mock_celery, mock_connection, mock_cache):
        mock_connection.cursor.return_value.__enter__.return_value.execute.return_value = None
        mock_cache.set.return_value = True
        mock_cache.get.return_value = 'ok'
        mock_celery.control.inspect.return_value.stats.return_value = {}

        self.client.force_login(self.user)
        forbidden = self.client.get('/api/health/detailed/')
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.get('/api/health/detailed/')
        self.assertEqual(response.status_code, 200)


class APIVersionMiddlewareTest(TestCase):
    """Test API versioning middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = APIVersionMiddleware(get_response=lambda req: HttpResponse())
    
    def test_api_version_from_header(self):
        """Test API version extraction from Accept header."""
        request = self.factory.get('/api/test/')
        request.META['HTTP_ACCEPT'] = 'application/vnd.agrisight.v1+json'
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)  # Middleware doesn't return response
        self.assertEqual(request.api_version, 'v1')
    
    def test_api_version_from_url(self):
        """Test API version extraction from URL."""
        request = self.factory.get('/api/v1/test/')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertEqual(request.api_version, 'v1')
    
    def test_default_api_version(self):
        """Test default API version."""
        request = self.factory.get('/api/test/')
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)
        self.assertEqual(request.api_version, 'v1')


class RequestLoggingMiddlewareTest(TestCase):
    """Test request logging middleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestLoggingMiddleware(get_response=lambda req: HttpResponse())
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('apps.core.middleware.logger')
    def test_request_logging(self, mock_logger):
        """Test that requests are logged."""
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        # Process request
        self.middleware.process_request(request)
        
        # Verify logging was called
        mock_logger.info.assert_called()
        
        # Check that start time was set
        assertHasAttr(request, '_start_time')
    
    @patch('apps.core.middleware.logger')
    def test_response_logging(self, mock_logger):
        """Test that responses are logged."""
        request = self.factory.get('/api/test/')
        request.user = self.user
        request._start_time = 1234567890.0
        
        response = HttpResponse()
        
        # Process response
        processed_response = self.middleware.process_response(request, response)
        
        # Verify logging was called
        mock_logger.info.assert_called()
        
        # Response should be unchanged
        self.assertEqual(processed_response, response)
    
    def test_client_ip_extraction(self):
        """Test client IP extraction."""
        request = self.factory.get('/api/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
        
        # Test without forwarded header
        del request.META['HTTP_X_FORWARDED_FOR']
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')


class MiddlewareIntegrationTest(TestCase):
    """Integration tests for middleware stack."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_middleware_stack_order(self):
        """Test that middleware is applied in correct order."""
        # This test ensures middleware is properly ordered in settings
        from django.conf import settings
        
        expected_order = [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.security.SecurityMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
            'apps.core.middleware.HealthCheckMiddleware',
            'apps.core.middleware.RequestLoggingMiddleware',
            'apps.core.middleware.ErrorHandlingMiddleware',
            'apps.core.middleware.SecurityHeadersMiddleware',
            'apps.core.middleware.RateLimitMiddleware',
            'apps.core.middleware.APIVersionMiddleware',
        ]
        
        # Check that our custom middleware is in the expected positions
        middleware = settings.MIDDLEWARE
        for i, expected_middleware in enumerate(expected_order):
            if i < len(middleware):
                self.assertEqual(middleware[i], expected_middleware)
    
    @patch('apps.core.middleware.logger')
    def test_full_request_cycle(self, mock_logger):
        """Test a full request cycle through all middleware."""
        # Create a simple view that returns a response
        def test_view(request):
            return HttpResponse('OK')
        
        # Apply middleware stack
        from django.test import Client
        client = Client()
        
        # Make a request
        response = client.get('/api/test/')
        
        # The response should have security headers
        self.assertIn('X-Frame-Options', response)
        self.assertIn('X-Content-Type-Options', response)
        
        # Logging should have occurred
        mock_logger.info.assert_called()


# Utility test functions
def assertHasAttr(obj, attr):
    """Assert that an object has an attribute."""
    if not hasattr(obj, attr):
        raise AssertionError(f"Object {obj} does not have attribute {attr}")
