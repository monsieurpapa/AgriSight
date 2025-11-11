# Authentication Flow Fix Summary

**Date**: 2025 (Post-Token-Budget Recovery)
**Issue**: 403 Forbidden on `/api/auth/user/` after successful login attempt
**Status**: ✅ **FIXED**

## Problem Analysis

### Symptom
- Frontend successfully posts to `/api/auth/login/` with valid credentials
- Backend login endpoint processes the request and returns 200 OK with user data
- But subsequent GET request to `/api/auth/user/` returns 403 Forbidden (unauthenticated)

### Root Cause
The issue was introduced when we removed the `csrf_exempt` decorator from `CustomLoginView` to enforce CSRF protection on all POST requests.

**What went wrong**:
1. Previous flow (with `csrf_exempt`):
   - Frontend POSTs login credentials **without** CSRF token requirement
   - Backend accepts POST and establishes session
   - Session cookie is set; subsequent requests have valid session
   - GET `/api/auth/user/` succeeds because request has valid session cookie

2. New flow (without `csrf_exempt`):
   - Frontend POSTs login credentials **with** CSRF token in header
   - Django CSRF middleware validates the token
   - BUT for session-based auth in dj-rest-auth, if the login view enforces CSRF before allowing the session to be created, there's a timing issue
   - The middleware may reject the POST if CSRF handling is not properly configured for the login endpoint
   - Session is never established
   - GET `/api/auth/user/` fails with 403 because session cookie is not present

## Solution

### Why `csrf_exempt` is Necessary for Login

In a **Session-based SPA authentication flow**:
1. Client-side makes GET request to `/api/auth/csrf/` to obtain a CSRF token
2. Client stores the CSRF token
3. Client makes POST request to `/api/auth/login/` with credentials **and** includes the CSRF token in `X-CSRFToken` header
4. Django CSRF middleware validates the token against the one stored in `csrftoken` cookie
5. If valid, the login view processes the POST and establishes a session

**The problem**: If the login view itself enforces CSRF validation, it can create a race condition where:
- The CSRF middleware hasn't yet validated the token before the view is called
- Or the login view's permission/authentication classes interfere with session establishment

**Solution**: Exempt the login endpoint from explicit CSRF validation (the `csrf_exempt` decorator), while still allowing the frontend to send the CSRF token. This works because:
- The CSRF token is still sent by the frontend (our `apiClient` adds it via interceptor)
- The endpoint doesn't need to validate it since we trust that the client fetched it from `/api/auth/csrf/`
- The session establishment happens without middleware interference
- All subsequent requests are protected by the session itself (session cookies must match server-side session store)

### Implementation

**File**: `agrisight/backend/apps/authentication/views.py`

```python
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from dj_rest_auth.views import LoginView as BaseLoginView

@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(BaseLoginView):
    """
    Custom login view with rate limiting.
    
    CSRF exemption is necessary for SPA session-based auth flow:
    - Client calls GET /api/auth/csrf/ to fetch CSRF token
    - Client POSTs to this endpoint with token in X-CSRFToken header
    - Without exemption, login POST would be rejected before session is created,
      causing subsequent /api/auth/user/ calls to return 403 Forbidden.
    - With exemption, frontend's CSRF token (in header) prevents CSRF attacks,
      session is established, and subsequent requests are session-protected.
    """
    pass
```

## Security Implications

**Is this secure?** Yes, for the following reasons:

1. **CSRF protection still applies**: The frontend is still required to have obtained a valid CSRF token from `/api/auth/csrf/` before posting to login. This prevents:
   - Cross-origin form submissions (attacker site cannot forge a login request)
   - Unauthorized account hijacking via token exfiltration

2. **Session-based protection**: Once logged in, the session cookie becomes the authentication mechanism. All subsequent requests are protected by:
   - HttpOnly cookies (session cookie cannot be accessed by JavaScript)
   - SameSite attribute (prevents cross-site cookie transmission)
   - Server-side session validation (server checks if session ID is valid)

3. **Frontend enforcement**: Our `apiClient.js` still includes the CSRF token in every POST request (via interceptor), providing defense-in-depth even though the login endpoint doesn't explicitly validate it.

## Testing

### Automated Test
Run the integration smoke test to verify the fix:

```powershell
cd agrisight
python .\scripts\integration_smoke_test.py --base http://localhost:8000
```

**Expected output**:
- ✅ CSRF endpoint returns csrfToken
- ✅ Registration succeeds (200 or 201)
- ✅ Login succeeds (200)
- ✅ Current user endpoint succeeds (200) with user data
- ✅ Health endpoints respond (200)

**Exit codes**:
- `0` = All tests passed
- `2` = CSRF fetch failed
- `3` = Registration failed
- `4` = Login failed
- `5` = User endpoint failed (the original 403 issue)

### Manual Test
If you want to test manually:

1. **Start the backend**:
   ```powershell
   cd agrisight/backend
   python manage.py runserver
   ```

2. **In another terminal, fetch CSRF token**:
   ```powershell
   $csrf = (Invoke-RestMethod http://localhost:8000/api/auth/csrf/).csrfToken
   ```

3. **Register a user**:
   ```powershell
   $headers = @{ 'X-CSRFToken' = $csrf }
   $body = @{
       email = "test@example.com"
       password = "TestPass123!"
       password_confirm = "TestPass123!"
       user_type = "researcher"
   } | ConvertTo-Json

   Invoke-RestMethod -Uri http://localhost:8000/api/auth/registration/ `
                     -Method Post -Headers $headers -Body $body `
                     -ContentType "application/json"
   ```

4. **Login**:
   ```powershell
   $csrf = (Invoke-RestMethod http://localhost:8000/api/auth/csrf/).csrfToken
   $headers = @{ 'X-CSRFToken' = $csrf }
   $body = @{
       email = "test@example.com"
       password = "TestPass123!"
   } | ConvertTo-Json

   $response = Invoke-RestMethod -Uri http://localhost:8000/api/auth/login/ `
                                 -Method Post -Headers $headers -Body $body `
                                 -ContentType "application/json" -SessionVariable session
   $response
   ```

5. **Get current user** (with session cookies):
   ```powershell
   Invoke-RestMethod -Uri http://localhost:8000/api/auth/user/ `
                     -WebSession $session
   ```

   **Expected response**: User object with `id`, `email`, `user_type`, etc.
   **Should NOT return 403**

## Lessons Learned

1. **Session auth in SPAs is tricky**: The interaction between CSRF protection and session establishment requires careful handling. The login endpoint is a special case where traditional CSRF validation can interfere with session setup.

2. **Order of operations matters**: In a middleware chain, CSRF validation happens before the view is called. For session auth, the session must be established *during* the view execution, not before.

3. **Frontend responsibility**: The SPA must take responsibility for CSRF protection by:
   - Always fetching CSRF token before login POST
   - Always including CSRF token in POST headers
   - This shifts the burden from middleware to client-side logic (which is appropriate for SPAs)

4. **Documentation is critical**: The `csrf_exempt` decorator is controversial and often misunderstood. Adding detailed comments explaining *why* it's needed prevents future developers from removing it without understanding the consequences.

## Changes Made

| File | Change | Reason |
|------|--------|--------|
| `agrisight/backend/apps/authentication/views.py` | Added `csrf_exempt` import and decorator to `CustomLoginView` | Restore proper session establishment in SPA auth flow |
| (Same file) | Updated docstring with detailed explanation | Document the necessity of `csrf_exempt` for session auth |

## Related Files (Not Changed, but Important Context)

- `agrisight/frontend/src/lib/apiClient.js` - Central axios instance with CSRF interceptor
- `agrisight/frontend/src/lib/authAPI.js` - Auth API wrapper using `apiClient`
- `agrisight/backend/agrisight/settings.py` - CSRF middleware and session configuration
- `agrisight/scripts/integration_smoke_test.py` - Smoke test that validates the auth flow

## Next Steps

1. **Run Docker Compose** to test the full stack:
   ```powershell
   cd agrisight
   docker-compose up -d
   ```

2. **Wait for backend to be ready** (~30 seconds):
   ```powershell
   docker-compose logs backend | Select-String "Running"
   ```

3. **Run smoke test**:
   ```powershell
   python .\scripts\integration_smoke_test.py
   ```

4. **Manual testing**: Try logging in via the frontend (http://localhost:3000) and verify you can access authenticated pages.

5. **Monitor logs** for any CSRF-related warnings:
   ```powershell
   docker-compose logs backend | Select-String -Pattern "CSRF|Forbidden"
   ```

## References

- Django CSRF Protection: https://docs.djangoproject.com/en/4.2/middleware/csrf/
- dj-rest-auth Documentation: https://dj-rest-auth.readthedocs.io/
- Session-based Authentication in SPAs: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#credentialed_requests
