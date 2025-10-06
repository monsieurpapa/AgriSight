from django.urls import path
from . import views

app_name = 'api_keys_logs'

urlpatterns = [
    # API Keys
    path('keys/', views.APIKeyListCreateView.as_view(), name='api-key-list-create'),
    path('keys/<int:pk>/', views.APIKeyDetailView.as_view(), name='api-key-detail'),
    path('keys/<int:pk>/regenerate/', views.regenerate_api_key, name='regenerate-api-key'),
    
    # Analytics Logs
    path('logs/', views.AnalyticsLogListView.as_view(), name='analytics-log-list'),
    path('usage-stats/', views.usage_statistics, name='usage-statistics'),
]

