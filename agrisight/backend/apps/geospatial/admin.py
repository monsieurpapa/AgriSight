from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Region, RegionAccess, SatelliteImage, VegetationIndex, Crop, CropMapping


@admin.register(Region)
class RegionAdmin(OSMGeoAdmin):
    """Admin configuration for Region model with map widget."""
    
    list_display = ['name', 'code', 'country', 'province', 'area_hectares', 'created_at']
    list_filter = ['country', 'province', 'created_at']
    search_fields = ['name', 'code', 'country', 'province']
    readonly_fields = ['area_hectares', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'country', 'province')
        }),
        ('Spatial Data', {
            'fields': ('geometry', 'area_hectares')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RegionAccess)
class RegionAccessAdmin(admin.ModelAdmin):
    """Admin configuration for RegionAccess model."""
    
    list_display = ['organization', 'region', 'access_level', 'start_date', 'end_date']
    list_filter = ['access_level', 'start_date', 'end_date']
    search_fields = ['organization__name', 'region__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Access Details', {
            'fields': ('organization', 'region', 'access_level')
        }),
        ('Validity Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    """Admin configuration for SatelliteImage model."""
    
    list_display = ['satellite_name', 'region', 'acquisition_date', 'cloud_cover_percentage', 'is_processed']
    list_filter = ['satellite_name', 'is_processed', 'acquisition_date', 'region__country']
    search_fields = ['satellite_name', 'region__name', 'image_path']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'acquisition_date'
    
    fieldsets = (
        ('Image Metadata', {
            'fields': ('id', 'satellite_name', 'region', 'acquisition_date')
        }),
        ('Technical Details', {
            'fields': ('cloud_cover_percentage', 'resolution_meters', 'bands_available')
        }),
        ('Storage', {
            'fields': ('image_path', 'is_processed', 'processing_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VegetationIndex)
class VegetationIndexAdmin(admin.ModelAdmin):
    """Admin configuration for VegetationIndex model."""
    
    list_display = ['index_type', 'satellite_image', 'mean_value', 'min_value', 'max_value']
    list_filter = ['index_type', 'satellite_image__satellite_name', 'satellite_image__region__country']
    search_fields = ['satellite_image__region__name', 'raster_path']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Index Information', {
            'fields': ('satellite_image', 'index_type')
        }),
        ('Statistical Values', {
            'fields': ('mean_value', 'min_value', 'max_value', 'std_deviation')
        }),
        ('Storage', {
            'fields': ('raster_path',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    """Admin configuration for Crop model."""
    
    list_display = ['name', 'scientific_name', 'created_at']
    search_fields = ['name', 'scientific_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name')
        }),
        ('Agricultural Details', {
            'fields': ('typical_growing_season', 'optimal_ndvi_range', 'water_requirements')
        }),
        ('Local Context', {
            'fields': ('local_importance',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropMapping)
class CropMappingAdmin(OSMGeoAdmin):
    """Admin configuration for CropMapping model with map widget."""
    
    list_display = ['crop', 'region', 'mapping_date', 'area_hectares', 'confidence_level']
    list_filter = ['crop', 'region__country', 'mapping_date']
    search_fields = ['crop__name', 'region__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'mapping_date'
    
    fieldsets = (
        ('Mapping Information', {
            'fields': ('region', 'crop', 'mapping_date')
        }),
        ('Area Details', {
            'fields': ('area_hectares', 'confidence_level')
        }),
        ('Spatial Data', {
            'fields': ('geometry',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

