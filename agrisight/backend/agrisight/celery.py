import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrisight.settings')


app = Celery('agrisight')

# Load Celery config from Django settings with the CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    return f'Request: {self.request!r}'


