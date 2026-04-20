import uuid
from django.db import models
from django.conf import settings
from apps.users.models import TimeStampedModel


class ConflictReport(TimeStampedModel):
    """A generated conflict-aware food security report for a set of DRC districts."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETE = 'COMPLETE', 'Complete'
        FAILED = 'FAILED', 'Failed'

    class EmailStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SENT = 'SENT', 'Sent'
        FAILED = 'FAILED', 'Failed'
        NOT_REQUESTED = 'NOT_REQUESTED', 'Not Requested'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conflict_reports',
    )
    district_ids = models.JSONField(help_text="List of Region PKs included in this report")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    celery_task_id = models.CharField(max_length=255, blank=True)
    pdf_file = models.FileField(upload_to='conflict_reports/', blank=True, null=True)
    recipient_email = models.EmailField(blank=True)
    email_status = models.CharField(
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.NOT_REQUESTED,
    )
    error_message = models.TextField(blank=True)
    feedback_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='cr_user_status_idx'),
            models.Index(fields=['feedback_token'], name='cr_feedback_token_idx'),
        ]

    def __str__(self):
        return f"ConflictReport {self.id} ({self.status}) {self.start_date}–{self.end_date}"


class NDVIBaseline(models.Model):
    """3-year NDVI baseline for a district, pre-cached via Celery beat."""

    region = models.OneToOneField(
        'geospatial.Region',
        on_delete=models.CASCADE,
        related_name='ndvi_baseline',
    )
    mean_ndvi = models.FloatField()
    std_ndvi = models.FloatField()
    baseline_years = models.PositiveSmallIntegerField(default=3)
    computed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"NDVIBaseline for {self.region.name} (mean={self.mean_ndvi:.3f})"


class ReportDataSnapshot(models.Model):
    """Per-district data snapshot for a report — one row per district per report."""

    report = models.ForeignKey(
        ConflictReport,
        on_delete=models.CASCADE,
        related_name='snapshots',
    )
    region = models.ForeignKey(
        'geospatial.Region',
        on_delete=models.PROTECT,
        related_name='report_snapshots',
    )
    ndvi_current = models.FloatField(null=True, blank=True)
    ndvi_baseline_mean = models.FloatField(null=True, blank=True)
    ndvi_anomaly = models.FloatField(null=True, blank=True, help_text="(current - baseline) / baseline * 100")
    conflict_event_count = models.PositiveIntegerField(null=True, blank=True)
    conflict_density_score = models.FloatField(null=True, blank=True, help_text="Normalised 0-100")
    idp_count = models.PositiveIntegerField(null=True, blank=True)
    displacement_score = models.FloatField(null=True, blank=True, help_text="Normalised 0-100")
    rainfall_mm = models.FloatField(null=True, blank=True)
    rainfall_deviation_pct = models.FloatField(null=True, blank=True)
    rainfall_score = models.FloatField(null=True, blank=True, help_text="Normalised 0-100")
    composite_score = models.FloatField(null=True, blank=True, help_text="Weighted 0-100 composite risk score")
    ipc_phase_proxy = models.CharField(max_length=30, blank=True)
    data_warnings = models.JSONField(default=list, help_text="List of data-quality warning strings")
    signals_detail = models.JSONField(default=dict, help_text="Raw API response snippets for audit")

    class Meta:
        unique_together = ('report', 'region')

    def __str__(self):
        return f"Snapshot {self.region.name} for {self.report_id}"


class RainfallBaseline(models.Model):
    """Per-district per-calendar-month rainfall baseline (mm), precomputed from CHIRPS historical data."""

    region = models.ForeignKey(
        'geospatial.Region',
        on_delete=models.CASCADE,
        related_name='rainfall_baselines',
    )
    month = models.PositiveSmallIntegerField(help_text="Calendar month 1-12")
    mean_mm = models.FloatField()
    std_mm = models.FloatField(default=0.0)
    baseline_years = models.PositiveSmallIntegerField(default=10)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('region', 'month')

    def __str__(self):
        return f"RainfallBaseline {self.region.name} month={self.month} (mean={self.mean_mm:.1f}mm)"


class ReportFeedback(models.Model):
    """Analyst feedback submitted via the UUID link in the PDF email."""

    report = models.OneToOneField(
        ConflictReport,
        on_delete=models.CASCADE,
        related_name='feedback',
    )
    accuracy_rating = models.PositiveSmallIntegerField(
        help_text="1 (poor) to 5 (excellent)",
        null=True,
        blank=True,
    )
    missing_data = models.TextField(blank=True)
    would_use_again = models.BooleanField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback for report {self.report_id} (rating={self.accuracy_rating})"
