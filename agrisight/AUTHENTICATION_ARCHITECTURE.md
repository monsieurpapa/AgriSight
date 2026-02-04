# AgriSight Authentication Architecture Design

## Executive Summary

This document outlines the authentication architecture for the AgriSight agricultural monitoring platform. The current implementation uses Django-allauth + dj-rest-auth with session-based authentication and CSRF protection to support user registration, login, password reset, email verification, and social authentication capabilities.

## Current System Analysis

### Existing Infrastructure

The AgriSight platform currently operates with the following technology stack:

**Backend Architecture:**
- Django 4.2.7 with Django REST Framework 3.14.0
- Custom User model extending AbstractUser with user types (admin, humanitarian, cooperative, government, researcher)
- PostgreSQL with PostGIS for geospatial data
- Redis for caching and Celery task queue
- Existing CORS configuration for frontend-backend communication

**Frontend Architecture:**
- React 19.1.0 with modern hooks and context API
- Vite build system with TypeScript support
- Tailwind CSS with Radix UI components
- React Router DOM for navigation
- Axios for HTTP requests with React Query for state management

**Current Authentication Setup:**
The system has a complete authentication flow with:
- Custom User model with organization relationships and user type classification
- Django REST Framework with SessionAuthentication configured
- CSRF protection for state-changing requests
- Email verification enforced for new registrations

### Identified Requirements

Based on the codebase analysis and user requirements, the authentication system must support:

1. **User Registration** - New user account creation with email verification
2. **User Login** - Secure credential-based authentication
3. **Password Reset** - Self-service password recovery via email
4. **Email Verification** - Account activation and email confirmation
5. **Social Logins** - Third-party authentication (Google, Facebook, GitHub)
6. **Multi-user Types** - Support for different user roles and organizations
7. **API Integration** - RESTful endpoints for frontend consumption
8. **Security** - Modern security practices and token management

## Authentication Strategy: Session Cookies vs API Tokens

### Analysis Framework

When choosing between session cookies and API tokens for authentication, several factors must be considered:

**Session Cookies Advantages:**
- Automatic handling by browsers
- Built-in CSRF protection with Django
- Simpler implementation for traditional web applications
- Automatic expiration and cleanup
- Secure by default with HttpOnly and Secure flags

**Session Cookies Disadvantages:**
- Limited cross-domain support
- Challenges with mobile applications
- CSRF token management complexity
- Less suitable for API-first architectures
- Scaling challenges with multiple server instances

**API Tokens (JWT) Advantages:**
- Stateless authentication suitable for microservices
- Cross-domain and mobile application support
- Self-contained with embedded user information
- Scalable across multiple server instances
- Industry standard for modern applications
- Better suited for API-first architectures

**API Tokens Disadvantages:**
- Token storage security considerations
- Manual token lifecycle management
- Potential for token bloat with excessive claims
- Revocation complexity without server-side storage

### Recommended Approach: Session-Based Authentication

For the AgriSight platform, we implement **session-based authentication** for the following reasons:

1. **API-First Architecture**: The platform follows a decoupled architecture with React frontend consuming Django REST API endpoints
2. **Security**: CSRF protection and HttpOnly cookies reduce token handling risk
3. **Operational Simplicity**: Fewer moving parts for SPA + Django deployments
4. **Modern Standards**: Aligns with secure session-based SPA patterns

### Implementation Strategy

We implement a session-based approach using Django-allauth:

- **Django-allauth** for comprehensive authentication features (registration, social auth, email verification)
- **Session cookies** managed by Django
- **CSRF protection** for all state-changing requests

## Django-allauth Integration Plan

### Core Components

**Django-allauth Configuration:**
Django-allauth will provide the foundation for authentication features:

```python
INSTALLED_APPS = [
    # ... existing apps
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]
```

**Authentication Settings:**
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
```

### API Endpoints Design

The authentication system will expose the following RESTful endpoints:

**User Management:**
- `POST /api/auth/registration/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user profile
- `PUT /api/auth/user/` - Update user profile

**Password Management:**
- `POST /api/auth/password/reset/` - Request password reset
- `POST /api/auth/password/reset/confirm/` - Confirm password reset
- `POST /api/auth/password/change/` - Change password (authenticated)

**Email Verification:**
- `POST /api/auth/registration/verify-email/` - Verify email address
- `POST /api/auth/registration/resend-email/` - Resend verification email

**Social Authentication:**
- `POST /api/auth/google/` - Google OAuth login
- `POST /api/auth/facebook/` - Facebook OAuth login
- `POST /api/auth/github/` - GitHub OAuth login

### Security Implementation

**Session Security:**
- Session cookies with HttpOnly and Secure flags (production)
- CSRF protection on all state-changing requests
- Secure transmission over HTTPS only

**Password Security:**
- Django's built-in password validation
- Minimum 8 characters with complexity requirements (upper/lower/number)
- Password hashing using Django's PBKDF2 algorithm
- Rate limiting on authentication attempts

**Email Security:**
- Email verification mandatory for account activation
- Secure email templates with proper token validation
- Email rate limiting to prevent spam

## Frontend Integration Architecture

### Authentication Context

The React frontend will implement a centralized authentication context:

```javascript
const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: () => {},
  logout: () => {},
  register: () => {},
});
```

### Session Management

**Axios Interceptors:**
- CSRF token retrieval for state-changing requests
- Redirect to login on 401 responses

**Route Protection:**
- Higher-order component for protected routes
- Automatic redirection to login for unauthenticated users
- Role-based access control for different user types

### User Interface Components

**Authentication Forms:**
- Login form with email/password fields
- Registration form with user type selection
- Password reset request and confirmation forms
- Email verification status and resend functionality

**Social Authentication:**
- OAuth buttons for Google, Facebook, GitHub
- Seamless integration with Django-allauth social providers
- Error handling for social authentication failures

## Database Schema Extensions

### User Model Enhancements

The existing User model will be extended to support authentication features:

```python
class User(AbstractUser):
    # Existing fields
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    organization = models.ForeignKey('organizations.Organization', ...)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # New authentication fields
    email_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
```

### Social Account Integration

Django-allauth will automatically create social account tables:
- `socialaccount_socialaccount` - Links users to social providers
- `socialaccount_socialtoken` - Stores OAuth tokens
- `socialaccount_socialapp` - Configures social applications

## Security Considerations

### OWASP Compliance

The authentication system will address OWASP Top 10 security risks:

1. **Broken Authentication**: Session cookies with proper expiration and CSRF protection
2. **Sensitive Data Exposure**: HTTPS enforcement and secure token storage
3. **XML External Entities**: Not applicable for JSON-based API
4. **Broken Access Control**: Role-based permissions and route protection
5. **Security Misconfiguration**: Proper Django security settings
6. **Cross-Site Scripting**: Input validation and output encoding
7. **Insecure Deserialization**: JSON-only data exchange
8. **Known Vulnerabilities**: Regular dependency updates
9. **Insufficient Logging**: Comprehensive authentication logging
10. **Insufficient Monitoring**: Failed login attempt tracking

### Rate Limiting

Implementation of rate limiting to prevent abuse:
- Login attempts: 5 attempts per IP per 15 minutes
- Registration: 3 registrations per IP per hour
- Password reset: 3 requests per email per hour
- Email verification: 3 resend requests per email per hour

### Data Protection

Compliance with data protection regulations:
- Minimal data collection principle
- User consent for data processing
- Right to data deletion (account deactivation)
- Data encryption in transit and at rest

## Implementation Phases

### Phase 1: Backend Authentication Setup
1. Install and configure Django-allauth
2. Configure session authentication and CSRF protection
3. Create authentication API endpoints
4. Set up email configuration for verification
5. Configure social authentication providers

### Phase 2: Frontend Authentication Integration
1. Create authentication context and providers
2. Implement authentication forms and components
3. Set up API client with token management
4. Create protected route components
5. Implement social login buttons

### Phase 3: Testing and Security Hardening
1. Comprehensive unit and integration testing
2. Security testing and vulnerability assessment
3. Performance testing for authentication flows
4. User acceptance testing
5. Documentation and deployment preparation

## Conclusion

The current session-based authentication system using Django-allauth provides a comprehensive, secure, and scalable solution for the AgriSight platform. This architecture supports all required authentication features while maintaining flexibility for future enhancements and mobile application development. The implementation follows modern security best practices and provides an excellent user experience across all supported authentication methods.

The next phase will involve the detailed implementation of the Django-allauth backend system with all specified authentication features.
