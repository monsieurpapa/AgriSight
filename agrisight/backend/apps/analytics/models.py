from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import TimeStampedModel
from apps.geospatial.models import Region, VegetationIndex, CropMapping
import uuid


class AgriculturalStressEvent(TimeStampedModel):
    """
    Records detected stress events in agricultural areas.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    crop_mapping = models.ForeignKey(CropMapping, on_delete=models.SET_NULL, null=True, blank=True)
    detection_date = models.DateField()
    stress_type = models.CharField(max_length=50, choices=(
        ('water', 'Water Stress'),
        ('disease', 'Disease/Pest'),
        ('nutrient', 'Nutrient Deficiency'),
        ('conflict', 'Conflict-Related'),
        ('other', 'Other'),
    ))
    severity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Severity level from 1 (mild) to 5 (severe)"
    )
    affected_area_hectares = models.FloatField()
    description = models.TextField()
    evidence_indices = models.ManyToManyField(VegetationIndex, blank=True)
    geometry = gis_models.MultiPolygonField(srid=4326)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['region', 'detection_date']),
            models.Index(fields=['stress_type']),
            models.Index(fields=['severity']),
        ]
    
    def __str__(self):
        return f"{self.stress_type} stress in {self.region.name} on {self.detection_date}"


class ConflictEvent(TimeStampedModel):
    """
    Records conflict events that may impact agricultural activities.
    """
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    event_date = models.DateField()
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    source = models.CharField(max_length=255)
    intensity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Intensity level from 1 (minor) to 5 (major)"
    )
    location = gis_models.PointField(srid=4326)
    affected_radius_km = models.FloatField(help_text="Estimated radius of impact in kilometers")
    
    class Meta:
        indexes = [
            models.Index(fields=['region', 'event_date']),
            models.Index(fields=['intensity']),
        ]
    
    def __str__(self):
        return f"{self.event_type} in {self.region.name} on {self.event_date}"

