# AgriSight Security Documentation

## Overview

This document outlines the comprehensive security measures implemented in the AgriSight platform to protect user data, ensure system integrity, and maintain compliance with security best practices.

## Security Architecture

### Defense in Depth Strategy

AgriSight implements multiple layers of security controls:

1. **Network Security**: HTTPS, WSS, CORS, Rate Limiting
2. **Application Security**: Authentication, Authorization, Input Validation
3. **Data Security**: Encryption, Access Controls, Audit Logging
4. **Infrastructure Security**: Container Security, Network Isolation
5. **Operational Security**: Monitoring, Incident Response, Updates

## Authentication & Authorization

### Session-Based Authentication

AgriSight uses secure session-based authentication instead of JWT tokens for enhanced security:

```python
# Session configuration
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour timeout
```

### CSRF Protection

All state-changing requests are protected with CSRF tokens:

```python
# CSRF middleware configuration
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]

# CSRF settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://agrisight.com']
```

### Password Security

Strong password requirements and secure storage:

```python
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

### Role-Based Access Control (RBAC)

```python
# User roles and permissions
class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('analyst', 'Agricultural Analyst'),
        ('manager', 'Field Operations Manager'),
        ('coordinator', 'Regional Coordinator'),
        ('viewer', 'Read-only User'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
```

## Network Security

### HTTPS/WSS Enforcement

All communication is encrypted in transit:

```python
# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### CORS Configuration

Controlled cross-origin resource sharing:

```python
CORS_ALLOWED_ORIGINS = [
    "https://agrisight.com",
    "https://www.agrisight.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### Rate Limiting

Protection against abuse and DoS attacks:

```python
# Rate limiting middleware
class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limits = {
            'default': 100,  # requests per hour
            'auth': 10,      # login attempts per hour
            'api': 1000,     # API calls per hour
        }
```

## Data Security

### Database Security

```python
# Database connection security
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

### Data Encryption

- **At Rest**: Database encryption, file system encryption
- **In Transit**: TLS 1.3 for all communications
- **Application Level**: Sensitive data encryption before storage

### Access Controls

```python
# Model-level permissions
class Region(models.Model):
    organizations = models.ManyToManyField('Organization')
    
    def has_access(self, user):
        if user.user_type == 'admin':
            return True
        return self.organizations.filter(id=user.organization.id).exists()
```

## Input Validation & Sanitization

### API Input Validation

```python
# DRF serializers with validation
class StressEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgriculturalStressEvent
        fields = ['stress_type', 'severity', 'region', 'description']
    
    def validate_stress_type(self, value):
        allowed_types = ['drought', 'flood', 'pest', 'disease']
        if value not in allowed_types:
            raise serializers.ValidationError("Invalid stress type")
        return value
```

### SQL Injection Prevention

Django ORM provides automatic SQL injection protection:

```python
# Safe database queries
regions = Region.objects.filter(
    organizations=user.organization,
    is_active=True
).select_related('geometry')
```

### XSS Prevention

```python
# Template auto-escaping
{{ user_input|escape }}  # Automatic HTML escaping

# JSON responses
return JsonResponse(data, safe=False)  # Proper JSON encoding
```

## Security Headers

### Comprehensive Security Headers

```python
# Security headers middleware
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss:; "
            "frame-ancestors 'none';"
        )
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
```

## Audit Logging

### Comprehensive Audit Trail

```python
# Audit logging middleware
class AuditLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.path}", extra={
            'user_id': getattr(request.user, 'id', None),
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'timestamp': timezone.now().isoformat(),
        })
        
        response = self.get_response(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(f"Response: {response.status_code}", extra={
            'duration': duration,
            'response_size': len(response.content),
        })
        
        return response
```

### Security Event Logging

```python
# Security event logging
def log_security_event(event_type, user, details):
    logger.warning(f"Security Event: {event_type}", extra={
        'event_type': event_type,
        'user_id': user.id if user.is_authenticated else None,
        'ip_address': get_client_ip(request),
        'details': details,
        'timestamp': timezone.now().isoformat(),
    })
```

## WebSocket Security

### WebSocket Authentication

```python
# WebSocket consumer with authentication
class AgriSightConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authenticate user via session
        user = await self.authenticate_user(self.scope['session'])
        if not user:
            await self.close(code=4001)  # Unauthorized
            return
        
        self.user = user
        await self.accept()
```

### WebSocket Rate Limiting

```python
# WebSocket rate limiting
class WebSocketRateLimit:
    def __init__(self):
        self.connections = {}
        self.max_connections_per_ip = 5
    
    async def check_rate_limit(self, client_ip):
        if client_ip not in self.connections:
            self.connections[client_ip] = 0
        
        if self.connections[client_ip] >= self.max_connections_per_ip:
            return False
        
        self.connections[client_ip] += 1
        return True
```

## Container Security

### Docker Security

```dockerfile
# Secure Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r agrisight && useradd -r -g agrisight agrisight

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership
RUN chown -R agrisight:agrisight /app
USER agrisight

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1
```

### Docker Compose Security

```yaml
# docker-compose.yml security
version: '3.8'
services:
  backend:
    build: ./backend
    user: "1000:1000"  # Non-root user
    read_only: true    # Read-only filesystem
    tmpfs:
      - /tmp
      - /var/tmp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    networks:
      - agrisight-network
```

## Vulnerability Management

### Dependency Scanning

```bash
# Security scanning tools
pip install safety bandit

# Check for known vulnerabilities
safety check

# Static security analysis
bandit -r backend/

# Docker image scanning
docker scout cves agrisight/backend:latest
```

### Security Updates

```python
# Automated security updates
# requirements.txt with pinned versions
Django==4.2.7
djangorestframework==3.14.0
psycopg2-binary==2.9.7
redis==4.6.0
```

## Incident Response

### Security Incident Response Plan

1. **Detection**: Automated monitoring and alerting
2. **Assessment**: Severity classification and impact analysis
3. **Containment**: Immediate threat isolation
4. **Eradication**: Remove threat and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Post-incident review and improvements

### Security Monitoring

```python
# Security monitoring alerts
def monitor_security_metrics():
    # Failed login attempts
    failed_logins = AuditLog.objects.filter(
        event_type='login_failed',
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).count()
    
    if failed_logins > 50:
        send_security_alert('High number of failed login attempts')
    
    # Unusual API usage
    api_calls = AuditLog.objects.filter(
        event_type='api_call',
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    if api_calls > 1000:
        send_security_alert('Unusual API usage pattern')
```

## Compliance & Standards

### Security Standards Compliance

- **OWASP Top 10**: Protection against common web vulnerabilities
- **ISO 27001**: Information security management
- **SOC 2**: Security, availability, and confidentiality
- **GDPR**: Data protection and privacy (if applicable)

### Data Privacy

```python
# Data privacy controls
class DataPrivacyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log data access
        if request.user.is_authenticated:
            logger.info(f"Data access by user {request.user.id}", extra={
                'user_id': request.user.id,
                'endpoint': request.path,
                'timestamp': timezone.now().isoformat(),
            })
        
        return self.get_response(request)
```

## Security Testing

### Automated Security Testing

```python
# Security test cases
class SecurityTestCase(TestCase):
    def test_sql_injection_protection(self):
        response = self.client.get('/api/regions/?name=<script>alert("xss")</script>')
        self.assertNotContains(response, '<script>')
    
    def test_csrf_protection(self):
        response = self.client.post('/api/stress-events/', {
            'stress_type': 'drought',
            'severity': 'high'
        })
        self.assertEqual(response.status_code, 403)
    
    def test_authentication_required(self):
        response = self.client.get('/api/regions/')
        self.assertEqual(response.status_code, 401)
```

### Penetration Testing

Regular penetration testing schedule:
- **Quarterly**: Automated vulnerability scanning
- **Annually**: Professional penetration testing
- **Ad-hoc**: Security assessment for major releases

## Security Configuration

### Environment-Specific Security

```python
# Development security
if DEBUG:
    # Relaxed security for development
    CORS_ALLOW_ALL_ORIGINS = True
    CSRF_COOKIE_SECURE = False
else:
    # Production security
    CORS_ALLOW_ALL_ORIGINS = False
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
```

### Security Headers Configuration

```python
# Production security headers
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

## Security Best Practices

### Development Security

1. **Secure Coding**: Follow OWASP secure coding practices
2. **Code Review**: Security-focused code reviews
3. **Dependency Management**: Regular updates and vulnerability scanning
4. **Secret Management**: Use environment variables for secrets
5. **Error Handling**: Avoid information disclosure in error messages

### Operational Security

1. **Access Control**: Principle of least privilege
2. **Monitoring**: Continuous security monitoring
3. **Backup Security**: Encrypted backups with access controls
4. **Incident Response**: Documented procedures and team training
5. **Security Awareness**: Regular security training for team members

## Security Checklist

### Pre-Deployment Security Checklist

- [ ] All dependencies updated and vulnerability-free
- [ ] Security headers configured
- [ ] Authentication and authorization tested
- [ ] Input validation implemented
- [ ] Error handling secure
- [ ] Logging and monitoring configured
- [ ] SSL/TLS certificates valid
- [ ] Database security configured
- [ ] Container security hardened
- [ ] Security tests passing

### Ongoing Security Maintenance

- [ ] Regular security updates
- [ ] Vulnerability scanning
- [ ] Security monitoring
- [ ] Access review
- [ ] Backup verification
- [ ] Incident response testing
- [ ] Security training updates
- [ ] Compliance audits

---

*This security documentation is regularly updated to reflect current security measures and best practices.*
