"""
API views for machine learning models management.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import MLModel, ModelTrainingJob, ModelPrediction, ModelPerformanceMetrics
from .algorithms import AgriculturalStressDetector, CropClassificationModel, AnomalyDetectionModel
from .tasks import train_model_task, make_prediction_task


class MLModelListCreateView(generics.ListCreateAPIView):
    """List and create ML models."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return MLModel.objects.all()
        elif user.organization:
            return MLModel.objects.filter(applicable_regions__organizations=user.organization).distinct()
        return MLModel.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MLModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific ML model."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = MLModel.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_model_training(request, pk):
    """Start training a new model."""
    model = get_object_or_404(MLModel, pk=pk)
    
    # Check permissions
    if request.user.user_type != 'admin' and model.created_by != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Start training job
    training_config = request.data.get('training_config', {})
    data_sources = request.data.get('data_sources', [])
    
    # Create training job
    training_job = ModelTrainingJob.objects.create(
        model=model,
        training_config=training_config,
        data_sources=data_sources,
        status='pending'
    )
    
    # Start Celery task
    task = train_model_task.delay(str(training_job.id))
    training_job.celery_task_id = task.id
    training_job.save()
    
    return Response({
        'training_job_id': str(training_job.id),
        'task_id': task.id,
        'status': 'Training started'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def make_prediction(request, pk):
    """Make predictions using a trained model."""
    model = get_object_or_404(MLModel, pk=pk)
    
    if not model.is_deployed:
        return Response(
            {'error': 'Model is not deployed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get input features
    input_features = request.data.get('input_features', {})
    region_id = request.data.get('region_id')
    
    if not input_features:
        return Response(
            {'error': 'input_features are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Start prediction task
    task = make_prediction_task.delay(str(model.id), input_features, region_id)
    
    return Response({
        'task_id': task.id,
        'status': 'Prediction started'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_model_performance(request, pk):
    """Get model performance metrics."""
    model = get_object_or_404(MLModel, pk=pk)
    
    # Get recent performance metrics
    metrics = ModelPerformanceMetrics.objects.filter(model=model).order_by('-evaluation_date')[:10]
    
    performance_data = []
    for metric in metrics:
        performance_data.append({
            'evaluation_date': metric.evaluation_date.isoformat(),
            'accuracy': metric.accuracy,
            'precision': metric.precision,
            'recall': metric.recall,
            'f1_score': metric.f1_score,
            'auc_score': metric.auc_score,
            'sample_size': metric.sample_size,
            'evaluation_dataset': metric.evaluation_dataset
        })
    
    return Response({
        'model_id': str(model.id),
        'model_name': model.name,
        'performance_history': performance_data,
        'current_metrics': model.performance_summary
    })


class TrainingJobListView(generics.ListAPIView):
    """List training jobs."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return ModelTrainingJob.objects.all()
        else:
            return ModelTrainingJob.objects.filter(model__created_by=user)


class TrainingJobDetailView(generics.RetrieveAPIView):
    """Get training job details."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = ModelTrainingJob.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_training_status(request, pk):
    """Get training job status."""
    training_job = get_object_or_404(ModelTrainingJob, pk=pk)
    
    # Check permissions
    if request.user.user_type != 'admin' and training_job.model.created_by != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    response_data = {
        'training_job_id': str(training_job.id),
        'model_name': training_job.model.name,
        'status': training_job.status,
        'progress_percentage': training_job.progress_percentage,
        'current_epoch': training_job.current_epoch,
        'total_epochs': training_job.total_epochs,
        'started_at': training_job.started_at.isoformat() if training_job.started_at else None,
        'completed_at': training_job.completed_at.isoformat() if training_job.completed_at else None,
        'duration_minutes': training_job.duration_minutes
    }
    
    if training_job.status == 'failed':
        response_data['error_message'] = training_job.error_message
    
    if training_job.status == 'completed':
        response_data['training_metrics'] = training_job.training_metrics
    
    return Response(response_data)


class PredictionListView(generics.ListAPIView):
    """List model predictions."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return ModelPrediction.objects.all()
        else:
            return ModelPrediction.objects.filter(
                model__created_by=user
            )


class PredictionDetailView(generics.RetrieveAPIView):
    """Get prediction details."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = ModelPrediction.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def compare_models(request):
    """Compare performance of multiple models."""
    model_ids = request.data.get('model_ids', [])
    
    if len(model_ids) < 2:
        return Response(
            {'error': 'At least 2 model IDs are required for comparison'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    comparison_data = []
    
    for model_id in model_ids:
        try:
            model = MLModel.objects.get(id=model_id)
            
            # Get recent performance metrics
            latest_metrics = ModelPerformanceMetrics.objects.filter(
                model=model
            ).order_by('-evaluation_date').first()
            
            comparison_data.append({
                'model_id': str(model.id),
                'model_name': model.name,
                'model_type': model.get_model_type_display(),
                'algorithm': model.get_algorithm_display(),
                'version': model.version,
                'status': model.status,
                'current_metrics': model.performance_summary,
                'latest_evaluation': {
                    'accuracy': latest_metrics.accuracy if latest_metrics else None,
                    'precision': latest_metrics.precision if latest_metrics else None,
                    'recall': latest_metrics.recall if latest_metrics else None,
                    'f1_score': latest_metrics.f1_score if latest_metrics else None,
                    'evaluation_date': latest_metrics.evaluation_date.isoformat() if latest_metrics else None
                } if latest_metrics else None
            })
            
        except MLModel.DoesNotExist:
            continue
    
    return Response({
        'comparison_data': comparison_data,
        'total_models': len(comparison_data)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_feature_importance(request, model_id):
    """Get feature importance for a specific model."""
    model = get_object_or_404(MLModel, id=model_id)
    
    # Check permissions
    if request.user.user_type != 'admin' and model.created_by != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get feature importance from database
    feature_importances = model.feature_importances.all().order_by('-importance_score')
    
    importance_data = []
    for feature in feature_importances:
        importance_data.append({
            'feature_name': feature.feature_name,
            'importance_score': feature.importance_score,
            'rank': feature.rank
        })
    
    return Response({
        'model_id': str(model.id),
        'model_name': model.name,
        'feature_importances': importance_data,
        'total_features': len(importance_data)
    })
