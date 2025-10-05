from django.urls import path
from . import views

app_name = 'ml_models'

urlpatterns = [
    # ML model management endpoints
    path('models/', views.MLModelListCreateView.as_view(), name='model_list_create'),
    path('models/<uuid:pk>/', views.MLModelDetailView.as_view(), name='model_detail'),
    path('models/<uuid:pk>/train/', views.start_model_training, name='start_training'),
    path('models/<uuid:pk>/predict/', views.make_prediction, name='make_prediction'),
    path('models/<uuid:pk>/performance/', views.get_model_performance, name='model_performance'),
    
    # Training job endpoints
    path('training-jobs/', views.TrainingJobListView.as_view(), name='training_job_list'),
    path('training-jobs/<uuid:pk>/', views.TrainingJobDetailView.as_view(), name='training_job_detail'),
    path('training-jobs/<uuid:pk>/status/', views.get_training_status, name='training_status'),
    
    # Prediction endpoints
    path('predictions/', views.PredictionListView.as_view(), name='prediction_list'),
    path('predictions/<uuid:pk>/', views.PredictionDetailView.as_view(), name='prediction_detail'),
    
    # Model comparison and analytics
    path('compare-models/', views.compare_models, name='compare_models'),
    path('feature-importance/<uuid:model_id>/', views.get_feature_importance, name='feature_importance'),
]
