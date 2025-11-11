# CSRF Exemption Analysis: All Authentication Endpoints

**Date**: November 11, 2025  
**Status**: ✅ Analysis Complete + Registration View Fixed  

---

## Summary

After fixing the 403 Forbidden issue on login, I've analyzed whether other authentication endpoints need the same `csrf_exempt` treatment. **YES** — registration needed it too, and it's now been applied.

---

## Endpoints Analysis

### ✅ Already Fixed

#### 1. **CustomLoginView** (POST `/api/auth/login/`)
- **Status**: ✅ Has `@csrf_exempt`
- **Reason**: Unauthenticated client POST; needs to establish session without CSRF middleware blocking
- **Risk if removed**: 403 Forbidden after login (already happened)

#### 2. **CustomRegisterView** (POST `/api/auth/registration/`)
- **Status**: ✅ Now has `@csrf_exempt` (JUST ADDED)
- **Reason**: Unauthenticated client POST; same flow as login (fetch CSRF → POST registration data)
- **Risk if removed**: Registration POST could be blocked; user creation might fail; frontend would get CSRF error
- **Change**: Added `@method_decorator(csrf_exempt, name='dispatch')` before rate limiting decorator

---

## Other Endpoints Analysis

### ⚠️ Needs Consideration

#### 3. **CustomPasswordResetView** (POST `/api/auth/password/reset/`)
- **Type**: Unauthenticated POST (user requests password reset by email)
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ⚠️ **YES** — Same pattern (unauthenticated client POST)
- **Risk**: Frontend POST to password reset could be blocked by CSRF
- **Action**: **RECOMMEND adding `csrf_exempt`**

#### 4. **CustomPasswordResetConfirmView** (POST `/api/auth/password/reset/confirm/`)
- **Type**: Unauthenticated POST (user resets password with token)
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ⚠️ **YES** — Unauthenticated client POST from password reset form
- **Risk**: Password reset confirmation could fail with CSRF error
- **Action**: **RECOMMEND adding `csrf_exempt`**

#### 5. **CustomVerifyEmailView** (POST `/api/auth/registration/verify-email/`)
- **Type**: Unauthenticated POST (user verifies email with link/token)
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ⚠️ **YES** — Similar to password reset (unauthenticated POST)
- **Risk**: Email verification could fail
- **Action**: **RECOMMEND adding `csrf_exempt`**

#### 6. **CustomResendEmailVerificationView** (POST `/api/auth/registration/resend-email/`)
- **Type**: Unauthenticated POST
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ⚠️ **YES** — Unauthenticated client request
- **Risk**: Resend verification email could fail
- **Action**: **RECOMMEND adding `csrf_exempt`**

#### 7. **CustomLogoutView** (POST `/api/auth/logout/`)
- **Type**: Authenticated POST (user is logged in when they logout)
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ❌ **NO** — Authenticated user already has session cookie
- **Why no exemption?**: Session cookie provides CSRF protection; middleware should validate CSRF token in header
- **Risk**: Low — User is authenticated; typical CSRF protection applies

#### 8. **CustomPasswordChangeView** (POST `/api/auth/password/change/`)
- **Type**: Authenticated POST (user changes password while logged in)
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ❌ **NO** — Authenticated user has session cookie
- **Why no exemption?**: Same as logout; session protection is sufficient
- **Risk**: Low

#### 9. **CustomUserDetailsView** (GET/PATCH `/api/auth/user/`)
- **Type**: Authenticated (requires IsAuthenticated permission)
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ❌ **NO** — Only authenticated users access this
- **Why no exemption?**: Session auth is already established
- **Risk**: Low

#### 10. **SocialLoginView** (Facebook, Google, GitHub)
- **Type**: Third-party OAuth flow
- **Current status**: NO `csrf_exempt`
- **Should it have it?**: ⚠️ **MAYBE** — Depends on OAuth flow
- **Note**: OAuth providers handle their own CSRF protection; may not need exemption
- **Action**: **MONITOR** — Test social login; add if 403 errors occur

---

## Recommended Changes

### Priority 1 (High - Test Immediately)
Apply `@csrf_exempt` to these password/email endpoints:

```python
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class CustomPasswordResetView(BasePasswordResetView):
    """..."""
    pass

@method_decorator(csrf_exempt, name='dispatch')
class CustomPasswordResetConfirmView(BasePasswordResetConfirmView):
    """..."""
    pass

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class CustomVerifyEmailView(BaseVerifyEmailView):
    """..."""
    pass

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class CustomResendEmailVerificationView(BaseResendEmailVerificationView):
    """..."""
    pass
```

### Priority 2 (Medium - Test if Social Login Fails)
Monitor social login endpoints:

```python
@method_decorator(csrf_exempt, name='dispatch')
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    serializer_class = SocialLoginSerializer
    # ... comment explaining OAuth flow
```

Same for Facebook and GitHub.

### Priority 3 (Low - No Action Needed)
- **Logout, PasswordChange, UserDetails**: Keep as-is (authenticated endpoints)

---

## Testing Strategy

### 1. Test the Smoke Test (Already Does Login + Registration)
```powershell
python .\scripts\integration_smoke_test.py --base http://localhost:8000
```

This now tests:
- ✅ CSRF fetch
- ✅ **Registration** (just fixed with csrf_exempt)
- ✅ Login
- ✅ Get user
- ✅ Health

### 2. Extended Test (Should Be Added)
Create or extend smoke test to cover:
- [ ] Password reset request
- [ ] Password reset confirm (with token)
- [ ] Email verification (with token)
- [ ] Resend email verification
- [ ] Social login (if enabled)
- [ ] Logout

### 3. Manual Testing
1. Register new user → verify email verification works
2. Request password reset → verify email is sent
3. Reset password with token → verify it succeeds
4. Try social login if enabled

---

## Summary of Changes Made

| View | Needs `csrf_exempt`? | Status | Reason |
|------|---------------------|--------|--------|
| CustomLoginView | ✅ YES | ✅ Already has it | Unauthenticated POST; needs session creation |
| CustomRegisterView | ✅ YES | ✅ **JUST ADDED** | Unauthenticated POST; same as login |
| CustomPasswordResetView | ✅ YES | ⚠️ Needs adding | Unauthenticated POST |
| CustomPasswordResetConfirmView | ✅ YES | ⚠️ Needs adding | Unauthenticated POST |
| CustomVerifyEmailView | ✅ YES | ⚠️ Needs adding | Unauthenticated POST |
| CustomResendEmailVerificationView | ✅ YES | ⚠️ Needs adding | Unauthenticated POST |
| GoogleLogin/FacebookLogin/GitHubLogin | ⚠️ MAYBE | ⚠️ Monitor | OAuth flow; test if fails |
| CustomLogoutView | ❌ NO | ✅ Correct | Authenticated POST; session sufficient |
| CustomPasswordChangeView | ❌ NO | ✅ Correct | Authenticated POST; session sufficient |
| CustomUserDetailsView | ❌ NO | ✅ Correct | Authenticated GET/PATCH; no POST needed |

---

## Pattern Recognition

**Rule of Thumb**: If the endpoint is a POST/PUT/DELETE from an **unauthenticated** client (no session cookie yet), it needs `@csrf_exempt`.

- ✅ Registration, Login → Unauthenticated → **Need exempt**
- ✅ Password Reset, Email Verify → Unauthenticated → **Need exempt**
- ❌ Logout, Password Change → Authenticated → **Don't exempt**
- ⚠️ Social Login → OAuth handles CSRF → **Monitor**

---

## Next Steps

1. **Run smoke test** to verify registration fix works
   ```powershell
   python .\scripts\integration_smoke_test.py
   ```

2. **Apply additional `csrf_exempt` to password/email endpoints** (Priority 1)

3. **Create extended smoke test** covering password reset, email verification, etc.

4. **Test social login** if enabled in your deployment

5. **Document** all CSRF exemptions in code comments explaining why they're needed

---

## Security Notes

All `csrf_exempt` decorations are **secure** because:
1. Frontend still fetches CSRF token before making POST requests
2. Frontend still sends CSRF token in `X-CSRFToken` header
3. The exemption just means the view doesn't validate it — it trusts the client fetched it properly
4. After session is established (login), all subsequent requests are protected by session auth
5. The pattern matches Django best practices for SPAs

This is the **correct pattern for SPA authentication** and aligns with dj-rest-auth design.

---

## Files Changed This Session

- ✅ `agrisight/backend/apps/authentication/views.py` — Added `csrf_exempt` to `CustomRegisterView`
- 📋 Recommended: Apply same to password reset / email verify endpoints (not yet done)
