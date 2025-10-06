from django.urls import path
from . import views

app_name = 'reports_alerts'

urlpatterns = [
    # Reports
    path('reports/', views.ReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<uuid:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<uuid:pk>/download/', views.download_report, name='download-report'),
    
    # Alerts
    path('alerts/', views.AlertListCreateView.as_view(), name='alert-list-create'),
    path('alerts/<uuid:pk>/', views.AlertDetailView.as_view(), name='alert-detail'),
    path('alerts/<uuid:alert_id>/mark-read/', views.mark_alert_as_read, name='mark-alert-read'),
    path('alerts/mark-all-read/', views.mark_all_alerts_as_read, name='mark-all-alerts-read'),
    path('alerts/unread-count/', views.unread_alerts_count, name='unread-alerts-count'),
    path('alerts/recent/', views.recent_alerts, name='recent-alerts'),
]

