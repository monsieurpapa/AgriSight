from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.users.models import TimeStampedModel
from apps.organizations.models import Organization
import uuid


class Region(TimeStampedModel):
    """
    Geographical regions being monitored.
    Uses GeoDjango for spatial data.
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True)
    geometry = gis_models.MultiPolygonField(srid=4326)  # EPSG:4326 is WGS84
    area_hectares = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    organizations = models.ManyToManyField(Organization, through='RegionAccess')
    
    def __str__(self):
        return f"{self.name}, {self.province}, {self.country}"
    
    def save(self, *args, **kwargs):
        # Calculate area in hectares if not provided
        if not self.area_hectares and self.geometry:
            # Convert square meters to hectares (1 hectare = 10,000 sq meters)
            self.area_hectares = self.geometry.area / 10000
        super().save(*args, **kwargs)


class RegionAccess(TimeStampedModel):
    """
    Many-to-many relationship between Organizations and Regions with metadata.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=20, choices=(
        ('view', 'View Only'),
        ('analyze', 'Analysis Access'),
        ('full', 'Full Access'),
    ), default='view')
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ('organization', 'region')


class SatelliteImage(TimeStampedModel):
    """
    Stores metadata about satellite imagery.
    Actual image data would typically be stored in cloud storage with path references.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='satellite_images')
    acquisition_date = models.DateTimeField()
    satellite_name = models.CharField(max_length=100)  # e.g., "Sentinel-2", "Landsat 8"
    cloud_cover_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    resolution_meters = models.FloatField(help_text="Spatial resolution in meters")
    bands_available = models.JSONField(help_text="List of available spectral bands")
    image_path = models.CharField(max_length=500, help_text="Path to image file in storage")
    is_processed = models.BooleanField(default=False)
    processing_notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['region', 'acquisition_date']),
            models.Index(fields=['satellite_name']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        return f"{self.satellite_name} image of {self.region.name} on {self.acquisition_date.date()}"


class VegetationIndex(TimeStampedModel):
    """
    Stores calculated vegetation indices from satellite imagery.
    """
    satellite_image = models.ForeignKey(SatelliteImage, on_delete=models.CASCADE, related_name='vegetation_indices')
    index_type = models.CharField(max_length=20, choices=(
        ('NDVI', 'Normalized Difference Vegetation Index'),
        ('EVI', 'Enhanced Vegetation Index'),
        ('NDWI', 'Normalized Difference Water Index'),
        ('SAVI', 'Soil Adjusted Vegetation Index'),
    ))
    mean_value = models.FloatField()
    min_value = models.FloatField()
    max_value = models.FloatField()
    std_deviation = models.FloatField()
    raster_path = models.CharField(max_length=500, help_text="Path to processed raster file")
    
    class Meta:
        unique_together = ('satellite_image', 'index_type')
        indexes = [
            models.Index(fields=['index_type']),
        ]
    
    def __str__(self):
        return f"{self.index_type} for {self.satellite_image}"


class Crop(TimeStampedModel):
    """
    Information about crop types being monitored.
    """
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=200, blank=True)
    typical_growing_season = models.JSONField(help_text="Start and end months for growing seasons")
    optimal_ndvi_range = models.JSONField(help_text="Min and max NDVI values for healthy crop")
    water_requirements = models.TextField(blank=True)
    local_importance = models.TextField(blank=True, help_text="Description of importance to local food security")
    
    def __str__(self):
        return self.name


class CropMapping(TimeStampedModel):
    """
    Maps crops to specific regions with additional metadata.
    """
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    area_hectares = models.FloatField(null=True, blank=True)
    confidence_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence level of crop classification (0-100%)"
    )
    mapping_date = models.DateField()
    geometry = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    
    class Meta:
        unique_together = ('region', 'crop', 'mapping_date')
    
    def __str__(self):
        return f"{self.crop.name} in {self.region.name} ({self.mapping_date})"
