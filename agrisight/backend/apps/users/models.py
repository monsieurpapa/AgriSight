from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, SoftDeleteModel):
    """
    Custom user model extending Django's AbstractUser.
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('humanitarian', 'Humanitarian Organization'),
        ('cooperative', 'Agricultural Cooperative'),
        ('government', 'Government Agency'),
        ('researcher', 'Researcher'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')