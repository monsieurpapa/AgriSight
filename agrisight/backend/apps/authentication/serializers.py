from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration serializer that includes user_type and organization fields.
    """
    user_type = serializers.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        help_text="Type of user account"
    )
    first_name = serializers.CharField(
        max_length=30,
        required=True,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        max_length=30,
        required=True,
        help_text="User's last name"
    )
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="User's phone number"
    )

    def get_cleaned_data(self):
        """
        Return cleaned data for user creation.
        """
        data = super().get_cleaned_data()
        data.update({
            'user_type': self.validated_data.get('user_type', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
        })
        return data

    def save(self, request):
        """
        Create and save the user with custom fields.
        """
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        
        # Set custom fields
        user.user_type = self.cleaned_data.get('user_type')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone_number = self.cleaned_data.get('phone_number', '')
        
        user.save()
        setup_user_email(request, user, [])
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """
    Custom user details serializer that includes additional fields.
    """
    user_type = serializers.CharField(source='get_user_type_display', read_only=True)
    user_type_code = serializers.CharField(source='user_type', read_only=True)
    organization = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'pk', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'user_type_code', 'organization', 'phone_number',
            'date_joined', 'last_login', 'is_active', 'permissions'
        )
        read_only_fields = ('pk', 'email', 'date_joined', 'last_login', 'is_active')

    def get_organization(self, obj):
        """
        Get organization details if user belongs to one.
        """
        if obj.organization:
            return {
                'id': obj.organization.id,
                'name': obj.organization.name,
                'type': obj.organization.organization_type
            }
        return None

    def get_full_name(self, obj):
        """
        Get user's full name.
        """
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_permissions(self, obj):
        """
        Get user permissions based on user type.
        """
        # Define role-based permissions
        role_permissions = {
            'admin': ['*'],  # All permissions
            'humanitarian': ['view_data', 'export_data', 'generate_reports', 'view_analytics'],
            'cooperative': ['view_data', 'view_analytics', 'manage_regions', 'view_stress_events'],
            'government': ['view_data', 'view_analytics', 'manage_organizations', 'view_all_regions'],
            'researcher': ['view_data', 'view_analytics', 'export_data', 'view_stress_events', 'view_conflict_events']
        }
        
        user_type = obj.user_type
        return role_permissions.get(user_type, ['view_data'])


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(
        max_length=128,
        required=True,
        help_text="Current password"
    )
    new_password1 = serializers.CharField(
        max_length=128,
        required=True,
        help_text="New password"
    )
    new_password2 = serializers.CharField(
        max_length=128,
        required=True,
        help_text="New password confirmation"
    )

    def validate(self, attrs):
        """
        Validate password change data.
        """
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return attrs

    def validate_old_password(self, value):
        """
        Validate old password.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your old password was entered incorrectly.")
        return value

    def save(self):
        """
        Save the new password.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class SocialLoginSerializer(serializers.Serializer):
    """
    Serializer for social login endpoints.
    """
    access_token = serializers.CharField(
        required=True,
        help_text="Access token from social provider"
    )
    code = serializers.CharField(
        required=False,
        help_text="Authorization code from social provider"
    )


class CustomLoginSerializer(serializers.Serializer):
    """
    Login serializer that accepts email or username and returns a clear error on failure.
    """
    email = serializers.EmailField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get('request')
        email = (attrs.get('email') or '').strip()
        username = (attrs.get('username') or '').strip()
        password = attrs.get('password')

        if not email and not username:
            raise serializers.ValidationError({'non_field_errors': ['Email or username is required.']})

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
            if user and not user.check_password(password):
                user = None

        if not user and username:
            user = User.objects.filter(username__iexact=username).first()
            if user and not user.check_password(password):
                user = None

        if not user and email and not username:
            # Fallback for legacy setups where email is stored in username
            user = User.objects.filter(username__iexact=email).first()
            if user and not user.check_password(password):
                user = None

        if not user:
            raise serializers.ValidationError({'non_field_errors': ['Unable to log in with provided credentials.']})

        if not user.is_active:
            raise serializers.ValidationError({'non_field_errors': ['User account is disabled.']})

        if getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', 'optional') == 'mandatory':
            email_qs = EmailAddress.objects.filter(user=user)
            if settings.DEBUG or user.is_staff or user.is_superuser:
                if not email_qs.exists():
                    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
                else:
                    email_qs.filter(verified=False).update(verified=True)
            else:
                if not email_qs.exists():
                    EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
                    raise serializers.ValidationError({'non_field_errors': ['E-mail is not verified.']})
                elif not email_qs.filter(verified=True).exists():
                    raise serializers.ValidationError({'non_field_errors': ['E-mail is not verified.']})

        attrs['user'] = user
        return attrs



