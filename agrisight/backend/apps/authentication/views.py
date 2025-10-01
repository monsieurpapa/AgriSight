from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
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
    """
    pass


@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class CustomRegisterView(BaseRegisterView):
    """
    Custom registration view with rate limiting and custom serializer.
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
        'email_verification_required': False,  # Updated to match settings
        'password_requirements': {
            'min_length': 8,
            'require_uppercase': False,
            'require_lowercase': False,
            'require_numbers': False,
            'require_symbols': False
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



