"""
Celery Beat configuration for AgriSight platform.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrisight.settings')
django.setup()

from celery import Celery
from django.conf import settings

# Initialize Celery
app = Celery('agrisight')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()

