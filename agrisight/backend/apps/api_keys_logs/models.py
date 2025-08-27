from django.db import models
from django.contrib.auth import get_user_model
from apps.users.models import TimeStampedModel
from apps.organizations.models import Organization

User = get_user_model()


class APIKey(TimeStampedModel):
    """
    API keys for B2B clients to access the system programmatically.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    key_name = models.CharField(max_length=100)
    key_prefix = models.CharField(max_length=10)  # Visible prefix for identification
    key_hash = models.CharField(max_length=100)  # Hashed API key for security
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    permissions = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ('organization', 'key_name')
    
    def __str__(self):
        return f"{self.key_name} for {self.organization.name}"


class AnalyticsLog(TimeStampedModel):
    """
    Logs system usage for analytics and billing purposes.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100, blank=True)
    request_path = models.CharField(max_length=500)
    response_time_ms = models.IntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['organization', 'action_type']),
            models.Index(fields=['created_at']),
        ]

