from django.db import models
from apps.users.models import TimeStampedModel
from apps.core.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class Organization(TimeStampedModel, SoftDeleteModel):
    """
    Represents B2B client organizations using the platform.
    """
    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=50)
    subscription_plan = models.ForeignKey('SubscriptionPlan', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name


class SubscriptionPlan(TimeStampedModel, SoftDeleteModel):
    """
    Different subscription tiers for B2B clients.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    max_users = models.PositiveIntegerField()
    max_regions = models.PositiveIntegerField()
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name

