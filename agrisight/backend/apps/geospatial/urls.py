from django.urls import path
from . import views

app_name = 'geospatial'

urlpatterns = [
    # Regions
    path('regions/', views.RegionListCreateView.as_view(), name='region-list-create'),
    path('regions/<int:pk>/', views.RegionDetailView.as_view(), name='region-detail'),
    path('regions/near/', views.regions_near_point, name='regions-near-point'),
    
    # Region Access
    path('region-access/', views.RegionAccessListCreateView.as_view(), name='region-access-list-create'),
    
    # Satellite Images
    path('satellite-images/', views.SatelliteImageListCreateView.as_view(), name='satellite-image-list-create'),
    path('satellite-images/<uuid:pk>/', views.SatelliteImageDetailView.as_view(), name='satellite-image-detail'),
    
    # Vegetation Indices
    path('vegetation-indices/', views.VegetationIndexListCreateView.as_view(), name='vegetation-index-list-create'),
    path('vegetation-indices/<int:pk>/', views.VegetationIndexDetailView.as_view(), name='vegetation-index-detail'),
    
    # Crops
    path('crops/', views.CropListCreateView.as_view(), name='crop-list-create'),
    path('crops/<int:pk>/', views.CropDetailView.as_view(), name='crop-detail'),
    
    # Crop Mappings
    path('crop-mappings/', views.CropMappingListCreateView.as_view(), name='crop-mapping-list-create'),
    path('crop-mappings/<int:pk>/', views.CropMappingDetailView.as_view(), name='crop-mapping-detail'),

    # Data Quality
    path('data-quality/', views.data_quality_summary, name='data-quality-summary'),
]
