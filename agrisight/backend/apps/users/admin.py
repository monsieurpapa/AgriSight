from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Additional Info'), {
            'fields': ('user_type', 'organization', 'phone_number')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Additional Info'), {
            'fields': ('user_type', 'organization', 'phone_number')
        }),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'organization', 'is_staff')
    list_filter = BaseUserAdmin.list_filter + ('user_type', 'organization')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'organization__name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organization')

