from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomLoginView,
    CustomRegisterView,
    CustomLogoutView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    CustomPasswordChangeView,
    CustomUserDetailsView,
    CustomVerifyEmailView,
    CustomResendEmailVerificationView,
    GoogleLogin,
    FacebookLogin,
    GitHubLogin,
    auth_status,
    request_account_deletion,
    auth_config,
)

urlpatterns = [
    # Authentication status and config
    path('status/', auth_status, name='auth_status'),
    path('config/', auth_config, name='auth_config'),
    
    # Core authentication
    path('login/', CustomLoginView.as_view(), name='rest_login'),
    path('logout/', CustomLogoutView.as_view(), name='rest_logout'),
    path('user/', CustomUserDetailsView.as_view(), name='rest_user_details'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration
    path('registration/', CustomRegisterView.as_view(), name='rest_register'),
    path('registration/verify-email/', CustomVerifyEmailView.as_view(), name='rest_verify_email'),
    path('registration/resend-email/', CustomResendEmailVerificationView.as_view(), name='rest_resend_email'),
    
    # Password management
    path('password/reset/', CustomPasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/', CustomPasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='rest_password_change'),
    
    # Social authentication
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('facebook/', FacebookLogin.as_view(), name='facebook_login'),
    path('github/', GitHubLogin.as_view(), name='github_login'),
    
    # GDPR compliance
    path('delete-account/', request_account_deletion, name='request_account_deletion'),
    
    # Include default dj-rest-auth URLs for any missing endpoints
    path('', include('dj_rest_auth.urls')),
]
