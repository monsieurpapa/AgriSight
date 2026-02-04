from django.db import models
from apps.users.models import TimeStampedModel
from apps.geospatial.models import Region

class BatchJob(TimeStampedModel):
    """
    Tracks Sentinel Hub Batch V2 processing jobs.
    """
    STATUS_CHOICES = (
        ('CREATED', 'Created'),
        ('ANALYSING', 'Analysing'),
        ('ANALYSIS_DONE', 'Analysis Done'),
        ('PROCESSING', 'Processing'),
        ('DONE', 'Done'),
        ('FAILED', 'Failed'),
        ('PARTIAL', 'Partial'),
        ('CANCELED', 'Canceled'),
    )

    request_id = models.CharField(max_length=100, unique=True, help_text="Sentinel Hub Batch Request ID")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='batch_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED')
    description = models.TextField(blank=True)
    bbox = models.JSONField(help_text="Bounding box used [min_lon, min_lat, max_lon, max_lat]")
    time_range_start = models.DateTimeField()
    time_range_end = models.DateTimeField()
    s3_bucket = models.CharField(max_length=100)
    tile_count = models.IntegerField(default=0)
    value_estimation = models.FloatField(null=True, blank=True, help_text="Estimated cost in PU")
    
    def __str__(self):
        return f"BatchJob {self.request_id} ({self.status})"
