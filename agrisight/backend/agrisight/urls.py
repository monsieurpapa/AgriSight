"""
URL configuration for AgriSight project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core endpoints
    path('api/', include('apps.core.urls')),
    
    # Authentication endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),  # For social auth callbacks
    
    # API endpoints
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/geospatial/', include('apps.geospatial.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/reports-alerts/', include('apps.reports_alerts.urls')),
    path('api/v1/api-keys/', include('apps.api_keys_logs.urls')),
    path('api/v1/satellite-processing/', include('apps.satellite_processing.urls')),
    path('api/v1/ml-models/', include('apps.ml_models.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = "AgriSight Administration"
admin.site.site_title = "AgriSight Admin"
admin.site.index_title = "Welcome to AgriSight Administration"