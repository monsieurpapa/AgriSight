from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


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
