from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.text import slugify

User = get_user_model()

USERNAME_MAX_LENGTH = User._meta.get_field('username').max_length


def generate_unique_username(email):
    """
    Build a unique username from the e-mail local part.

    Login is e-mail based (ACCOUNT_USER_MODEL_USERNAME_FIELD = None), so allauth
    never fills ``username`` — but ``User.username`` is still a unique column.
    Leaving it blank saved the first sign-up as username='' and every later
    sign-up failed with an IntegrityError (500).
    """
    local_part = (email or '').split('@')[0]
    base = slugify(local_part).replace('-', '_')[: USERNAME_MAX_LENGTH - 7] or 'user'
    # all_objects includes soft-deleted users, which still hold their username.
    manager = getattr(User, 'all_objects', User._default_manager)
    candidate = base
    while manager.filter(username__iexact=candidate).exists():
        candidate = f"{base}_{get_random_string(6, 'abcdefghijklmnopqrstuvwxyz0123456789')}"
    return candidate


def ensure_username(user):
    if not getattr(user, 'username', None):
        user.username = generate_unique_username(user.email)
    return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for allauth.
    """
    
    def is_open_for_signup(self, request):
        """
        Allow signup for all users.
        """
        return True
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user with custom fields from registration form.
        """
        user = super().save_user(request, user, form, commit=False)
        ensure_username(user)
        
        # Get custom fields from form if available
        if hasattr(form, 'cleaned_data'):
            user.user_type = form.cleaned_data.get('user_type', '')
            user.phone_number = form.cleaned_data.get('phone_number', '')
        
        if commit:
            user.save()
        return user
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send email confirmation with custom template.
        """
        # Use the default implementation for now
        # Can be customized later with custom email templates
        super().send_confirmation_mail(request, emailconfirmation, signup)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter for allauth.
    """
    
    def is_open_for_signup(self, request, sociallogin):
        """
        Allow social signup for all providers.
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user fields from social account data.
        """
        user = super().populate_user(request, sociallogin, data)
        ensure_username(user)
        
        # Set default user type for social signups
        if not hasattr(user, 'user_type') or not user.user_type:
            user.user_type = 'researcher'  # Default type for social signups
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user from social login.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Ensure user has a user_type
        if not user.user_type:
            user.user_type = 'researcher'
            user.save()
        
        return user
