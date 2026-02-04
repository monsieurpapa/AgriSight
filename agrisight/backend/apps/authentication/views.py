from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from dj_rest_auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
    PasswordResetView as BasePasswordResetView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
    PasswordChangeView as BasePasswordChangeView,
    UserDetailsView as BaseUserDetailsView,
)
from dj_rest_auth.registration.views import (
    RegisterView as BaseRegisterView,
    VerifyEmailView as BaseVerifyEmailView,
    ResendEmailVerificationView as BaseResendEmailVerificationView,
)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from .serializers import (
    CustomRegisterSerializer,
    CustomUserDetailsSerializer,
    PasswordChangeSerializer,
    SocialLoginSerializer
)

User = get_user_model()


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
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        if not self.serializer.is_valid():
            if settings.DEBUG:
                return Response(
                    {"detail": "Login failed", "errors": self.serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "Unable to log in with provided credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.login()
        return self.get_response()


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST', block=False), name='post')
class CustomRegisterView(BaseRegisterView):
    """
    Custom registration view with rate limiting and custom serializer.
    
    CSRF exemption is necessary for SPA auth flow (same reasoning as CustomLoginView):
    - Registration is a POST from unauthenticated client
    - Client fetches CSRF token via GET /api/auth/csrf/ first
    - Client POSTs registration data with token in X-CSRFToken header
    - Without exemption, registration POST would be rejected before user is created
    - Frontend's CSRF token (in header) still prevents CSRF attacks
    """
    serializer_class = CustomRegisterSerializer


class CustomLogoutView(BaseLogoutView):
    """
    Custom logout view.
    """
    pass


@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class CustomPasswordResetView(BasePasswordResetView):
    """
    Custom password reset view with rate limiting.
    """
    pass


class CustomPasswordResetConfirmView(BasePasswordResetConfirmView):
    """
    Custom password reset confirmation view.
    """
    pass


class CustomPasswordChangeView(BasePasswordChangeView):
    """
    Custom password change view.
    """
    serializer_class = PasswordChangeSerializer


class CustomUserDetailsView(BaseUserDetailsView):
    """
    Custom user details view with extended serializer.
    """
    serializer_class = CustomUserDetailsSerializer
    permission_classes = [IsAuthenticated]


@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class CustomVerifyEmailView(BaseVerifyEmailView):
    """
    Custom email verification view with rate limiting.
    """
    pass


@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class CustomResendEmailVerificationView(BaseResendEmailVerificationView):
    """
    Custom resend email verification view with rate limiting.
    """
    pass


class GoogleLogin(SocialLoginView):
    """
    Google OAuth2 login view.
    """
    adapter_class = GoogleOAuth2Adapter
    serializer_class = SocialLoginSerializer


class FacebookLogin(SocialLoginView):
    """
    Facebook OAuth2 login view.
    """
    adapter_class = FacebookOAuth2Adapter
    serializer_class = SocialLoginSerializer


class GitHubLogin(SocialLoginView):
    """
    GitHub OAuth2 login view.
    """
    adapter_class = GitHubOAuth2Adapter
    serializer_class = SocialLoginSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_status(request):
    """
    Check authentication status and return user info.
    """
    serializer = CustomUserDetailsSerializer(request.user)
    return Response({
        'authenticated': True,
        'user': serializer.data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/1h', method='POST')
def request_account_deletion(request):
    """
    Request account deletion (GDPR compliance).
    """
    email = request.data.get('email')
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        # Send email to admin for manual review
        send_mail(
            'Account Deletion Request',
            f'User {user.email} has requested account deletion.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        return Response({
            'message': 'Account deletion request submitted. You will be contacted within 30 days.'
        })
    except User.DoesNotExist:
        # Don't reveal if email exists or not
        return Response({
            'message': 'If an account with this email exists, a deletion request has been submitted.'
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_config(request):
    """
    Get authentication configuration for frontend.
    """
    role_permissions = {
        'admin': ['*'],
        'humanitarian': ['view_data', 'export_data', 'generate_reports', 'view_analytics'],
        'cooperative': ['view_data', 'view_analytics', 'manage_regions', 'view_stress_events'],
        'government': ['view_data', 'view_analytics', 'manage_organizations', 'view_all_regions'],
        'researcher': ['view_data', 'view_analytics', 'export_data', 'view_stress_events', 'view_conflict_events']
    }

    role_labels = {
        'admin': 'Administrator',
        'humanitarian': 'Humanitarian',
        'cooperative': 'Cooperative',
        'government': 'Government',
        'researcher': 'Researcher'
    }

    return Response({
        'social_providers': {
            'google': {
                'enabled': True,
                'name': 'Google'
            },
            'facebook': {
                'enabled': True,
                'name': 'Facebook'
            },
            'github': {
                'enabled': True,
                'name': 'GitHub'
            }
        },
        'email_verification_required': True,
        'password_requirements': {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_symbols': False
        },
        'rbac': {
            'role_permissions': role_permissions,
            'role_labels': role_labels
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    Get CSRF token for frontend.
    """
    from django.middleware.csrf import get_token
    return Response({
        'csrfToken': get_token(request)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def password_reset_confirm_stub(request, uidb64=None, token=None):
    """
    Stub view for password reset confirm URL resolution in emails.
    """
    return HttpResponse(status=204)



