from django.contrib import admin
from .models import Report, Alert


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin configuration for Report model."""
    
    list_display = ['title', 'organization', 'report_type', 'time_period_start', 'time_period_end', 'is_published']
    list_filter = ['report_type', 'is_published', 'organization', 'time_period_start']
    search_fields = ['title', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['regions']
    date_hierarchy = 'time_period_start'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'title', 'organization', 'report_type')
        }),
        ('Time Period', {
            'fields': ('time_period_start', 'time_period_end')
        }),
        ('Content', {
            'fields': ('regions', 'content', 'file_path')
        }),
        ('Publication', {
            'fields': ('is_published',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin configuration for Alert model."""
    
    list_display = ['title', 'organization', 'alert_type', 'severity', 'is_read', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_read', 'organization', 'created_at']
    search_fields = ['title', 'message', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['regions']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('id', 'organization', 'alert_type', 'severity')
        }),
        ('Content', {
            'fields': ('title', 'message', 'regions')
        }),
        ('Related Events', {
            'fields': ('related_stress_event', 'related_conflict_event')
        }),
        ('Read Status', {
            'fields': ('is_read', 'read_by', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

