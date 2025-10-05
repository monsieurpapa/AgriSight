"""
Machine Learning models for agricultural monitoring.
"""

import os
import pickle
import numpy as np
from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.conf import settings
from apps.users.models import TimeStampedModel
from apps.geospatial.models import Region

User = get_user_model()


class MLModel(TimeStampedModel):
    """
    Store machine learning model metadata and files.
    """
    MODEL_TYPES = (
        ('stress_detection', 'Agricultural Stress Detection'),
        ('crop_classification', 'Crop Type Classification'),
        ('anomaly_detection', 'Anomaly Detection'),
        ('yield_prediction', 'Yield Prediction'),
        ('change_detection', 'Change Detection'),
    )
    
    MODEL_ALGORITHMS = (
        ('random_forest', 'Random Forest'),
        ('isolation_forest', 'Isolation Forest'),
        ('svm', 'Support Vector Machine'),
        ('cnn', 'Convolutional Neural Network'),
        ('transformer', 'Transformer (PSETAE)'),
        ('autoencoder', 'Autoencoder'),
        ('ensemble', 'Ensemble Model'),
    )
    
    STATUS_CHOICES = (
        ('training', 'Training'),
        ('trained', 'Trained'),
        ('deployed', 'Deployed'),
        ('failed', 'Training Failed'),
        ('deprecated', 'Deprecated'),
    )
    
    name = models.CharField(max_length=255, unique=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    algorithm = models.CharField(max_length=50, choices=MODEL_ALGORITHMS)
    version = models.CharField(max_length=20, default='1.0.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training')
    
    # Model files
    model_file = models.FileField(upload_to='ml_models/', blank=True, null=True)
    preprocessing_pipeline = models.FileField(upload_to='ml_models/preprocessing/', blank=True, null=True)
    feature_importance = models.FileField(upload_to='ml_models/features/', blank=True, null=True)
    
    # Training metadata
    training_data_size = models.PositiveIntegerField(default=0)
    training_date = models.DateTimeField(null=True, blank=True)
    training_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Performance metrics
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    validation_accuracy = models.FloatField(null=True, blank=True)
    
    # Model configuration
    hyperparameters = models.JSONField(default=dict, blank=True)
    feature_names = models.JSONField(default=list, blank=True)
    target_classes = models.JSONField(default=list, blank=True)
    
    # Usage tracking
    prediction_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    applicable_regions = models.ManyToManyField(Region, blank=True)
    
    # Model description
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_type', 'status']),
            models.Index(fields=['algorithm']),
            models.Index(fields=['training_date']),
        ]
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()})"
    
    @property
    def is_deployed(self):
        """Check if model is deployed and ready for use."""
        return self.status == 'deployed' and self.model_file
    
    @property
    def performance_summary(self):
        """Get performance metrics summary."""
        metrics = {}
        if self.accuracy is not None:
            metrics['accuracy'] = self.accuracy
        if self.precision is not None:
            metrics['precision'] = self.precision
        if self.recall is not None:
            metrics['recall'] = self.recall
        if self.f1_score is not None:
            metrics['f1_score'] = self.f1_score
        return metrics
    
    def load_model(self):
        """Load the trained model from file."""
        if not self.model_file:
            raise ValueError(f"Model {self.name} has no model file")
        
        model_path = default_storage.path(self.model_file.name)
        
        if self.algorithm in ['cnn', 'transformer', 'autoencoder']:
            # For deep learning models, we'd typically load using tensorflow/pytorch
            # This is a placeholder implementation
            import pickle
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            # For sklearn models
            import pickle
            with open(model_path, 'rb') as f:
                return pickle.load(f)
    
    def increment_prediction_count(self):
        """Increment the prediction count and update last used timestamp."""
        from django.utils import timezone
        self.prediction_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['prediction_count', 'last_used'])


class ModelTrainingJob(TimeStampedModel):
    """
    Track model training jobs and their progress.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Training configuration
    training_config = models.JSONField(default=dict)
    data_sources = models.JSONField(default=list)
    
    # Progress tracking
    progress_percentage = models.FloatField(default=0.0)
    current_epoch = models.PositiveIntegerField(default=0)
    total_epochs = models.PositiveIntegerField(default=0)
    
    # Results
    training_loss = models.FloatField(null=True, blank=True)
    validation_loss = models.FloatField(null=True, blank=True)
    training_metrics = models.JSONField(default=dict, blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)
    
    # Celery task tracking
    celery_task_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Training job for {self.model.name} - {self.get_status_display()}"
    
    @property
    def is_completed(self):
        return self.status in ['completed', 'failed', 'cancelled']
    
    @property
    def is_running(self):
        return self.status == 'running'


class ModelPrediction(TimeStampedModel):
    """
    Store model predictions for analysis and monitoring.
    """
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='predictions')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    
    # Input data
    input_features = models.JSONField()
    input_data_hash = models.CharField(max_length=64, help_text="Hash of input data for deduplication")
    
    # Predictions
    prediction_result = models.JSONField()
    prediction_confidence = models.FloatField(null=True, blank=True)
    prediction_probabilities = models.JSONField(default=dict, blank=True)
    
    # Metadata
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    model_version = models.CharField(max_length=20)
    
    # Ground truth (if available for validation)
    ground_truth = models.JSONField(null=True, blank=True)
    is_validated = models.BooleanField(default=False)
    validation_accuracy = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model', 'created_at']),
            models.Index(fields=['region', 'created_at']),
            models.Index(fields=['input_data_hash']),
        ]
    
    def __str__(self):
        return f"Prediction {self.id} by {self.model.name}"


class ModelPerformanceMetrics(TimeStampedModel):
    """
    Store model performance metrics over time.
    """
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Metrics
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    
    # Additional metrics
    auc_score = models.FloatField(null=True, blank=True)
    confusion_matrix = models.JSONField(default=dict, blank=True)
    classification_report = models.JSONField(default=dict, blank=True)
    
    # Evaluation context
    evaluation_dataset = models.CharField(max_length=255, blank=True)
    evaluation_date = models.DateField()
    sample_size = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['-evaluation_date']
        unique_together = ['model', 'evaluation_date', 'evaluation_dataset']
    
    def __str__(self):
        return f"Performance metrics for {self.model.name} on {self.evaluation_date}"


class FeatureImportance(TimeStampedModel):
    """
    Store feature importance scores for models.
    """
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='feature_importances')
    feature_name = models.CharField(max_length=255)
    importance_score = models.FloatField()
    rank = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['model', 'rank']
        unique_together = ['model', 'feature_name']
    
    def __str__(self):
        return f"{self.feature_name} importance for {self.model.name}: {self.importance_score:.4f}"
