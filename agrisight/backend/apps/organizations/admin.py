from django.contrib import admin
from .models import Organization, SubscriptionPlan


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin configuration for Organization model."""
    
    list_display = ['name', 'organization_type', 'subscription_plan', 'is_active', 'created_at']
    list_filter = ['organization_type', 'subscription_plan', 'is_active', 'created_at']
    search_fields = ['name', 'contact_email', 'organization_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'organization_type', 'is_active')
        }),
        ('Subscription', {
            'fields': ('subscription_plan',)
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Admin configuration for SubscriptionPlan model."""
    
    list_display = ['name', 'price_monthly', 'price_yearly', 'max_users', 'max_regions', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_regions')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

