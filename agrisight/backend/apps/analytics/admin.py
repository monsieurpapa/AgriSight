from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import AgriculturalStressEvent, ConflictEvent


@admin.register(AgriculturalStressEvent)
class AgriculturalStressEventAdmin(OSMGeoAdmin):
    """Admin configuration for AgriculturalStressEvent model."""
    
    list_display = ['stress_type', 'region', 'detection_date', 'severity', 'affected_area_hectares', 'is_verified']
    list_filter = ['stress_type', 'severity', 'is_verified', 'detection_date', 'region__country']
    search_fields = ['region__name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'detection_date'
    filter_horizontal = ['evidence_indices']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('id', 'region', 'crop_mapping', 'detection_date')
        }),
        ('Stress Details', {
            'fields': ('stress_type', 'severity', 'affected_area_hectares', 'description')
        }),
        ('Evidence', {
            'fields': ('evidence_indices',)
        }),
        ('Spatial Data', {
            'fields': ('geometry',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConflictEvent)
class ConflictEventAdmin(OSMGeoAdmin):
    """Admin configuration for ConflictEvent model."""
    
    list_display = ['event_type', 'region', 'event_date', 'intensity', 'affected_radius_km', 'source']
    list_filter = ['event_type', 'intensity', 'event_date', 'region__country']
    search_fields = ['region__name', 'event_type', 'description', 'source']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'event_date'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('region', 'event_date', 'event_type')
        }),
        ('Event Details', {
            'fields': ('description', 'source', 'intensity')
        }),
        ('Spatial Data', {
            'fields': ('location', 'affected_radius_km')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

