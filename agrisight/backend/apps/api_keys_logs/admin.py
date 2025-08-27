from django.contrib import admin
from .models import APIKey, AnalyticsLog


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin configuration for APIKey model."""
    
    list_display = ['key_name', 'organization', 'key_prefix', 'is_active', 'expires_at', 'last_used_at']
    list_filter = ['is_active', 'organization', 'expires_at', 'last_used_at']
    search_fields = ['key_name', 'organization__name', 'key_prefix']
    readonly_fields = ['created_at', 'updated_at', 'last_used_at']
    
    fieldsets = (
        ('Key Information', {
            'fields': ('organization', 'key_name', 'key_prefix')
        }),
        ('Security', {
            'fields': ('key_hash', 'is_active', 'expires_at')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        }),
        ('Usage', {
            'fields': ('last_used_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalyticsLog)
class AnalyticsLogAdmin(admin.ModelAdmin):
    """Admin configuration for AnalyticsLog model."""
    
    list_display = ['organization', 'user', 'action_type', 'resource_type', 'status_code', 'response_time_ms', 'created_at']
    list_filter = ['action_type', 'resource_type', 'status_code', 'organization', 'created_at']
    search_fields = ['organization__name', 'user__username', 'request_path', 'ip_address']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('organization', 'user', 'action_type', 'resource_type', 'resource_id')
        }),
        ('Request Details', {
            'fields': ('request_path', 'ip_address', 'user_agent')
        }),
        ('Response Details', {
            'fields': ('status_code', 'response_time_ms')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

