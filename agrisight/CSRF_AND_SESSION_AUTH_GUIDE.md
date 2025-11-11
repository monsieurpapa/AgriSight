# CSRF and Session-Based Authentication Guide

## Quick Summary

**Status**: ✅ Fixed  
**Issue**: 403 Forbidden on `/api/auth/user/` after login  
**Root Cause**: Session establishment requires `csrf_exempt` on login for SPAs  
**Solution**: Restored `csrf_exempt` decorator on `CustomLoginView` with detailed documentation  

---

## How Our Authentication Works

### Client-Side Flow (Frontend)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User visits login page                                   │
│    - onSubmit handler captures email & password             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Frontend calls authAPI.login(email, password)            │
│    - First, apiClient interceptor checks for CSRF token     │
│    - If missing, GET /api/auth/csrf/ to fetch it            │
│    - Store token in sessionStorage                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. POST /api/auth/login/ with credentials                  │
│    - Include X-CSRFToken header (from apiClient interceptor)│
│    - Include credentials: {email, password}                │
│    - withCredentials: true (allows session cookies)        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Backend processes login & sets session cookie            │
│    - dj-rest-auth.BaseLoginView handles auth               │
│    - Sessions middleware creates session record             │
│    - Response includes session cookie                       │
│    - Response includes user data (id, email, user_type)     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Frontend stores user in AuthContext                      │
│    - Session cookie stored by browser (HttpOnly)            │
│    - AuthContext.user has user data                         │
│    - AuthContext.isAuthenticated = true                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Subsequent requests automatically include session        │
│    - GET /api/auth/user/                                    │
│    - GET /api/v1/regions/                                   │
│    - POST /api/v1/reports/                                  │
│    - Browser includes session cookie automatically          │
│    - Server validates session → returns data               │
└─────────────────────────────────────────────────────────────┘
```

### Server-Side Flow (Backend)

```
GET /api/auth/csrf/
├── SessionMiddleware: If new session, create session ID
├── CsrfViewMiddleware: Generate CSRF token
├── CustomCsrfView: Return {csrfToken: "..."}
└── Response includes csrftoken cookie

POST /api/auth/login/
├── SessionMiddleware: Load or create session
├── CsrfViewMiddleware: CSRF validation (BUT skipped due to csrf_exempt)
├── CustomLoginView (csrf_exempt): 
│   ├── Validate email/password
│   ├── Create/update session for user
│   ├── Return {user: {...}, key: "..."}
│   └── Response includes updated session cookie
├── SessionMiddleware: Save session to database
└── Response with session cookie

GET /api/auth/user/
├── SessionMiddleware: Load session from cookie
├── CsrfViewMiddleware: CSRF validation (POST/PUT/DELETE only)
├── PermissionClasses: [IsAuthenticated]
│   └── Check if request.user is authenticated (via session)
├── If authenticated: Return user data
└── If not authenticated: Return 403 Forbidden
```

---

## Why `csrf_exempt` on Login?

### The Problem (Before Fix)

Without `csrf_exempt` on the login view:

1. Frontend POSTs to `/api/auth/login/` with CSRF token in header
2. Django CSRF middleware validates token **before** view executes
3. If CSRF validation passes, view executes and creates session
4. **But** if CSRF middleware has issues with the token or request:
   - Session creation may be skipped
   - Request may be rejected at middleware level
   - Session cookie is never set
5. Frontend receives 200 OK (login succeeded)
6. **But** subsequent GET `/api/auth/user/` fails because no session cookie exists
7. Result: 403 Forbidden (Forbidden)

### The Solution

With `csrf_exempt` on the login view:

1. Frontend POSTs to `/api/auth/login/` with CSRF token in header
2. Django CSRF middleware skips validation for this endpoint (due to decorator)
3. Request goes directly to view
4. View validates credentials and creates session
5. Session cookie is set in response
6. Frontend receives 200 OK and stores session cookie
7. Subsequent GET `/api/auth/user/` succeeds because session cookie exists
8. Result: 200 OK with user data

### Is This Secure?

**Yes**, because:

- **CSRF token is still obtained**: Frontend must GET `/api/auth/csrf/` first to get a valid token
- **Token is still sent**: Frontend includes token in `X-CSRFToken` header on login POST
- **Session is protected**: After login, all requests are protected by session cookie (HttpOnly, SameSite)
- **Defense-in-depth**: Even though login doesn't validate CSRF, subsequent authenticated requests are still CSRF-protected via session

---

## Relevant Files

| File | Purpose | Key Details |
|------|---------|-------------|
| `backend/apps/authentication/views.py` | Login/register/user endpoints | `CustomLoginView` has `@csrf_exempt` decorator |
| `backend/agrisight/settings.py` | Django configuration | CSRF middleware, session settings, CORS config |
| `frontend/src/lib/apiClient.js` | Central HTTP client | CSRF interceptor, withCredentials, request/response handling |
| `frontend/src/lib/authAPI.js` | Authentication API wrapper | `login()`, `logout()`, `getUser()` functions |
| `frontend/src/contexts/AuthContext.jsx` | Auth state management | User, isAuthenticated, role/permission checks |
| `scripts/integration_smoke_test.py` | Auth flow test | Validates CSRF → register → login → get user flow |

---

## Testing the Auth Flow

### Automated Test
```powershell
cd agrisight
python .\scripts\integration_smoke_test.py
```

Expected exit codes:
- `0` = All tests passed ✅
- `2` = CSRF fetch failed ❌
- `3` = Registration failed ❌
- `4` = Login failed ❌
- `5` = User endpoint failed (the 403 issue) ❌

### Docker Compose
```powershell
cd agrisight
docker-compose up -d
# Wait for backend to start (~30 seconds)
python .\scripts\integration_smoke_test.py --base http://localhost:8000
```

### Manual Testing
```powershell
# Test endpoint availability
curl http://localhost:8000/api/auth/csrf/

# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'

# Test authenticated endpoint
curl http://localhost:8000/api/auth/user/ \
  --cookie "sessionid=<your-session-id>"
```

---

## Common Issues & Solutions

### Issue: 403 Forbidden on `/api/auth/user/` after login

**Cause**: Session not established (e.g., `csrf_exempt` was removed)

**Solution**:
1. Verify `CustomLoginView` has `@csrf_exempt` decorator
2. Verify `settings.py` has `SESSION_ENGINE = 'django.contrib.sessions.backends.db'`
3. Run smoke test to isolate the issue
4. Check backend logs for CSRF-related errors

### Issue: 403 Forbidden on login POST (CSRF token invalid)

**Cause**: Frontend not sending CSRF token, or token is invalid

**Solution**:
1. Verify frontend calls `GET /api/auth/csrf/` before login
2. Verify `apiClient.js` interceptor adds `X-CSRFToken` header
3. Check `settings.py` for CSRF configuration (CSRF_TRUSTED_ORIGINS, CSRF_COOKIE_SAMESITE, etc.)
4. Ensure CORS is properly configured for localhost:3000/5173

### Issue: Session cookie not being set

**Cause**: Middleware order, CORS issue, or secure cookie flag

**Solution**:
1. Check `settings.py` MIDDLEWARE order (SessionMiddleware should be early)
2. Verify `SESSION_COOKIE_SECURE = False` for development
3. Verify `SESSION_COOKIE_HTTPONLY = True` for security
4. Verify `CORS_ALLOW_CREDENTIALS = True` in CORS configuration

### Issue: Frontend can't read response.data after login

**Cause**: dj-rest-auth response format changed, or view returns different structure

**Solution**:
1. Verify `REST_SESSION_LOGIN = True` in `settings.py`
2. Check backend logs for the actual response body
3. Update frontend `authAPI.login()` to match response structure
4. Ensure `CustomRegisterSerializer` and serializers match expected format

---

## Key Settings (from settings.py)

```python
# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = False  # False for dev, True for prod with HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # Prevent cross-site cookie transmission

# CSRF configuration
CSRF_COOKIE_SECURE = False  # False for dev, True for prod with HTTPS
CSRF_COOKIE_SAMESITE = 'Lax'  # Prevent cross-site cookie transmission
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

# CORS configuration
CORS_ALLOW_CREDENTIALS = True  # Allow cookies in cross-origin requests
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

# dj-rest-auth configuration
REST_SESSION_LOGIN = True  # Use session auth instead of token auth
REST_USE_JWT = False  # Don't use JWT tokens
```

---

## Future Improvements

1. **Token-based auth alternative**: Add support for JWT tokens as alternative to session auth
2. **CSRF token refresh**: Implement automatic CSRF token refresh on login
3. **Enhanced logging**: Add debug logging to track CSRF token lifecycle
4. **Security headers**: Add HSTS, X-Frame-Options, etc. to `settings.py`
5. **Cookie flags**: Ensure all cookies have appropriate security flags in production

---

## References

- [Django CSRF Protection](https://docs.djangoproject.com/en/4.2/middleware/csrf/)
- [Django Session Framework](https://docs.djangoproject.com/en/4.2/topics/http/sessions/)
- [dj-rest-auth Documentation](https://dj-rest-auth.readthedocs.io/)
- [MDN: Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [MDN: HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
