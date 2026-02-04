"""
URL configuration for the core app.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('health/detailed/', views.health_check_detailed, name='health_check_detailed'),
    path('info/', views.api_info, name='api_info'),
    path('logs/errors/', views.log_frontend_error, name='log_frontend_error'),
]
