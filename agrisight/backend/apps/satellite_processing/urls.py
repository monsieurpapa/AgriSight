from django.urls import path
from . import views

app_name = 'satellite_processing'

urlpatterns = [
    # Satellite data processing endpoints
    path('process/', views.trigger_satellite_processing, name='trigger_processing'),
    path('status/<str:task_id>/', views.get_processing_status, name='processing_status'),
    path('ingest/', views.manual_data_ingestion, name='manual_ingestion'),
    
    # Vegetation data endpoints
    path('vegetation/<uuid:region_id>/', views.get_region_vegetation_data, name='vegetation_data'),
    path('trend-analysis/', views.generate_trend_analysis, name='trend_analysis'),
    
    # Statistics and monitoring
    path('statistics/', views.get_processing_statistics, name='processing_statistics'),
    path('image/<uuid:image_id>/', views.get_satellite_image_details, name='image_details'),

    # Batch V2 endpoints
    path('batch/process/', views.trigger_batch_processing_view, name='trigger_batch_processing'),
    path('batch/region/<uuid:region_id>/', views.get_region_batch_jobs, name='region_batch_jobs'),
    path('batch/status/<str:job_id>/', views.get_batch_job_status, name='batch_job_status'),
]
