"""
Serializers for machine learning models.
"""

from rest_framework import serializers
from .models import MLModel, ModelTrainingJob, ModelPrediction, ModelPerformanceMetrics, FeatureImportance


class FeatureImportanceSerializer(serializers.ModelSerializer):
    """Serializer for feature importance."""
    
    class Meta:
        model = FeatureImportance
        fields = ['feature_name', 'importance_score', 'rank']


class ModelPerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer for model performance metrics."""
    
    class Meta:
        model = ModelPerformanceMetrics
        fields = [
            'id', 'accuracy', 'precision', 'recall', 'f1_score', 'auc_score',
            'evaluation_dataset', 'evaluation_date', 'sample_size'
        ]


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer for ML models."""
    
    feature_importances = FeatureImportanceSerializer(many=True, read_only=True)
    performance_summary = serializers.ReadOnlyField()
    is_deployed = serializers.ReadOnlyField()
    
    class Meta:
        model = MLModel
        fields = [
            'id', 'name', 'model_type', 'algorithm', 'version', 'status',
            'training_data_size', 'training_date', 'training_duration_minutes',
            'accuracy', 'precision', 'recall', 'f1_score', 'validation_accuracy',
            'hyperparameters', 'feature_names', 'target_classes',
            'prediction_count', 'last_used', 'created_by', 'applicable_regions',
            'description', 'notes', 'created_at', 'updated_at',
            'feature_importances', 'performance_summary', 'is_deployed'
        ]
        read_only_fields = [
            'training_data_size', 'training_date', 'training_duration_minutes',
            'accuracy', 'precision', 'recall', 'f1_score', 'validation_accuracy',
            'prediction_count', 'last_used', 'created_at', 'updated_at'
        ]


class ModelTrainingJobSerializer(serializers.ModelSerializer):
    """Serializer for model training jobs."""
    
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_type = serializers.CharField(source='model.model_type', read_only=True)
    is_completed = serializers.ReadOnlyField()
    is_running = serializers.ReadOnlyField()
    
    class Meta:
        model = ModelTrainingJob
        fields = [
            'id', 'model', 'model_name', 'model_type', 'status',
            'training_config', 'data_sources', 'progress_percentage',
            'current_epoch', 'total_epochs', 'training_loss', 'validation_loss',
            'training_metrics', 'started_at', 'completed_at', 'duration_minutes',
            'error_message', 'celery_task_id', 'created_at',
            'is_completed', 'is_running'
        ]
        read_only_fields = [
            'status', 'progress_percentage', 'current_epoch', 'total_epochs',
            'training_loss', 'validation_loss', 'training_metrics',
            'started_at', 'completed_at', 'duration_minutes',
            'error_message', 'celery_task_id', 'created_at'
        ]


class ModelPredictionSerializer(serializers.ModelSerializer):
    """Serializer for model predictions."""
    
    model_name = serializers.CharField(source='model.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = ModelPrediction
        fields = [
            'id', 'model', 'model_name', 'region', 'region_name',
            'input_features', 'prediction_result', 'prediction_confidence',
            'prediction_probabilities', 'processing_time_ms', 'model_version',
            'ground_truth', 'is_validated', 'validation_accuracy', 'created_at'
        ]
        read_only_fields = [
            'prediction_result', 'prediction_confidence', 'prediction_probabilities',
            'processing_time_ms', 'created_at'
        ]


class CreateModelSerializer(serializers.ModelSerializer):
    """Serializer for creating new ML models."""
    
    class Meta:
        model = MLModel
        fields = [
            'name', 'model_type', 'algorithm', 'version', 'description',
            'notes', 'applicable_regions', 'hyperparameters'
        ]


class UpdateModelSerializer(serializers.ModelSerializer):
    """Serializer for updating ML models."""
    
    class Meta:
        model = MLModel
        fields = [
            'name', 'description', 'notes', 'applicable_regions',
            'hyperparameters'
        ]


class StartTrainingSerializer(serializers.Serializer):
    """Serializer for starting model training."""
    
    training_config = serializers.JSONField(default=dict)
    data_sources = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )


class MakePredictionSerializer(serializers.Serializer):
    """Serializer for making model predictions."""
    
    input_features = serializers.JSONField()
    region_id = serializers.UUIDField(required=False, allow_null=True)


class CompareModelsSerializer(serializers.Serializer):
    """Serializer for comparing multiple models."""
    
    model_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=2
    )
