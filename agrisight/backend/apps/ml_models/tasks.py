"""
Celery tasks for machine learning model training and prediction.
"""

from celery import shared_task
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, Any, List
from django.utils import timezone

from .models import MLModel, ModelTrainingJob, ModelPrediction, ModelPerformanceMetrics, FeatureImportance
from .algorithms import AgriculturalStressDetector, CropClassificationModel, AnomalyDetectionModel

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def train_model_task(self, training_job_id: str) -> Dict[str, Any]:
    """
    Train a machine learning model.
    
    Args:
        training_job_id: ID of the training job
        
    Returns:
        Dict with training results
    """
    try:
        training_job = ModelTrainingJob.objects.get(id=training_job_id)
        model = training_job.model
        
        # Update job status
        training_job.status = 'running'
        training_job.started_at = timezone.now()
        training_job.save()
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Preparing training data...'}
        )
        
        # Prepare training data based on model type
        if model.model_type == 'stress_detection':
            X, y = _prepare_stress_detection_data(training_job.data_sources)
            ml_model = AgriculturalStressDetector(model_type=model.algorithm)
            
        elif model.model_type == 'crop_classification':
            X, y = _prepare_crop_classification_data(training_job.data_sources)
            ml_model = CropClassificationModel(model_type=model.algorithm)
            
        elif model.model_type == 'anomaly_detection':
            X = _prepare_anomaly_detection_data(training_job.data_sources)
            y = None
            ml_model = AnomalyDetectionModel()
            
        else:
            raise ValueError(f"Unsupported model type: {model.model_type}")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Training model...'}
        )
        
        # Train the model
        if model.model_type == 'anomaly_detection':
            metrics = ml_model.train(X)
        else:
            metrics = ml_model.train(X, y)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Saving model and calculating metrics...'}
        )
        
        # Save the trained model
        model_file_path = f"ml_models/{model.name}_v{model.version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        ml_model.save_model(model_file_path)
        
        # Update model with training results
        model.model_file = model_file_path
        model.status = 'trained'
        model.training_date = timezone.now()
        model.training_data_size = len(X)
        model.accuracy = metrics.get('accuracy')
        model.precision = metrics.get('precision')
        model.recall = metrics.get('recall')
        model.f1_score = metrics.get('f1_score')
        model.validation_accuracy = metrics.get('accuracy')
        model.feature_names = ml_model.feature_names
        model.save()
        
        # Save feature importance
        if hasattr(ml_model, 'get_feature_importance'):
            importance_scores = ml_model.get_feature_importance()
            for rank, (feature_name, score) in enumerate(importance_scores.items(), 1):
                FeatureImportance.objects.create(
                    model=model,
                    feature_name=feature_name,
                    importance_score=score,
                    rank=rank
                )
        
        # Create performance metrics record
        ModelPerformanceMetrics.objects.create(
            model=model,
            accuracy=metrics.get('accuracy', 0.0),
            precision=metrics.get('precision', 0.0),
            recall=metrics.get('recall', 0.0),
            f1_score=metrics.get('f1_score', 0.0),
            evaluation_dataset='training_set',
            evaluation_date=timezone.now().date(),
            sample_size=len(X),
            confusion_matrix=metrics.get('confusion_matrix', {}),
            classification_report=metrics.get('classification_report', {})
        )
        
        # Update training job
        training_job.status = 'completed'
        training_job.completed_at = timezone.now()
        training_job.duration_minutes = int((training_job.completed_at - training_job.started_at).total_seconds() / 60)
        training_job.training_metrics = metrics
        training_job.save()
        
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Training completed successfully'}
        )
        
        return {
            'training_job_id': training_job_id,
            'model_id': str(model.id),
            'metrics': metrics,
            'success': True
        }
        
    except Exception as exc:
        logger.error(f"Error training model: {str(exc)}")
        
        # Update training job with error
        if 'training_job' in locals():
            training_job.status = 'failed'
            training_job.error_message = str(exc)
            training_job.error_traceback = str(exc)
            training_job.completed_at = timezone.now()
            training_job.save()
        
        self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def make_prediction_task(self, model_id: str, input_features: Dict[str, Any], region_id: str = None) -> Dict[str, Any]:
    """
    Make predictions using a trained model.
    
    Args:
        model_id: ID of the trained model
        input_features: Input features for prediction
        region_id: Optional region ID
        
    Returns:
        Dict with prediction results
    """
    try:
        model = MLModel.objects.get(id=model_id)
        
        if not model.is_deployed:
            raise ValueError("Model is not deployed")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Loading model...'}
        )
        
        # Load the trained model
        ml_model = _load_model_by_type(model)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Processing input features...'}
        )
        
        # Convert input features to numpy array
        feature_names = model.feature_names
        if not feature_names:
            raise ValueError("Model has no feature names defined")
        
        # Create feature vector
        feature_vector = np.array([input_features.get(feature, 0.0) for feature in feature_names]).reshape(1, -1)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Making prediction...'}
        )
        
        # Make prediction
        start_time = timezone.now()
        predictions, probabilities = ml_model.predict(feature_vector)
        end_time = timezone.now()
        
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Calculate confidence
        prediction_confidence = float(np.max(probabilities)) if len(probabilities) > 0 else 0.0
        
        # Convert probabilities to dict
        if hasattr(ml_model, 'label_encoder') and ml_model.label_encoder:
            class_names = ml_model.label_encoder.classes_
            prediction_probabilities = {
                str(class_name): float(prob) 
                for class_name, prob in zip(class_names, probabilities[0])
            }
        else:
            prediction_probabilities = {
                f"class_{i}": float(prob) 
                for i, prob in enumerate(probabilities[0])
            }
        
        # Create prediction record
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        prediction = ModelPrediction.objects.create(
            model=model,
            input_features=input_features,
            input_data_hash=_hash_input_data(input_features),
            prediction_result={
                'prediction': predictions[0].tolist() if hasattr(predictions[0], 'tolist') else str(predictions[0]),
                'confidence': prediction_confidence
            },
            prediction_confidence=prediction_confidence,
            prediction_probabilities=prediction_probabilities,
            processing_time_ms=processing_time_ms,
            model_version=model.version
        )
        
        # Update model usage statistics
        model.increment_prediction_count()
        
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Prediction completed'}
        )
        
        return {
            'prediction_id': str(prediction.id),
            'model_id': model_id,
            'prediction': predictions[0].tolist() if hasattr(predictions[0], 'tolist') else str(predictions[0]),
            'confidence': prediction_confidence,
            'probabilities': prediction_probabilities,
            'processing_time_ms': processing_time_ms,
            'success': True
        }
        
    except Exception as exc:
        logger.error(f"Error making prediction: {str(exc)}")
        self.retry(countdown=30, exc=exc)


@shared_task
def evaluate_model_performance(model_id: str, test_dataset: str) -> Dict[str, Any]:
    """
    Evaluate model performance on a test dataset.
    
    Args:
        model_id: ID of the model to evaluate
        test_dataset: Name/identifier of the test dataset
        
    Returns:
        Dict with evaluation results
    """
    try:
        model = MLModel.objects.get(id=model_id)
        
        # Load the trained model
        ml_model = _load_model_by_type(model)
        
        # Prepare test data
        if model.model_type == 'stress_detection':
            X_test, y_test = _prepare_stress_detection_data([test_dataset])
        elif model.model_type == 'crop_classification':
            X_test, y_test = _prepare_crop_classification_data([test_dataset])
        elif model.model_type == 'anomaly_detection':
            X_test = _prepare_anomaly_detection_data([test_dataset])
            y_test = None
        else:
            raise ValueError(f"Unsupported model type: {model.model_type}")
        
        # Make predictions
        predictions, probabilities = ml_model.predict(X_test)
        
        # Calculate metrics
        if model.model_type == 'anomaly_detection':
            # For anomaly detection, calculate different metrics
            n_anomalies = np.sum(predictions == -1)
            n_normal = np.sum(predictions == 1)
            
            metrics = {
                'accuracy': float(n_normal / len(predictions)),
                'precision': float(n_normal / (n_normal + n_anomalies)) if (n_normal + n_anomalies) > 0 else 0.0,
                'recall': float(n_normal / len(predictions)),
                'f1_score': 0.0,  # Calculate if needed
                'anomalies_detected': int(n_anomalies),
                'normal_samples': int(n_normal)
            }
        else:
            # Calculate standard classification metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            metrics = {
                'accuracy': float(accuracy_score(y_test, predictions)),
                'precision': float(precision_score(y_test, predictions, average='weighted')),
                'recall': float(recall_score(y_test, predictions, average='weighted')),
                'f1_score': float(f1_score(y_test, predictions, average='weighted'))
            }
        
        # Save performance metrics
        ModelPerformanceMetrics.objects.create(
            model=model,
            accuracy=metrics['accuracy'],
            precision=metrics.get('precision', 0.0),
            recall=metrics.get('recall', 0.0),
            f1_score=metrics.get('f1_score', 0.0),
            evaluation_dataset=test_dataset,
            evaluation_date=timezone.now().date(),
            sample_size=len(X_test)
        )
        
        logger.info(f"Model {model.name} evaluated. Accuracy: {metrics['accuracy']:.4f}")
        
        return {
            'model_id': model_id,
            'evaluation_dataset': test_dataset,
            'metrics': metrics,
            'sample_size': len(X_test),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error evaluating model performance: {str(e)}")
        return {'error': str(e), 'success': False}


def _prepare_stress_detection_data(data_sources: List[str]) -> tuple:
    """Prepare data for stress detection model training."""
    # This would typically load data from databases, files, or APIs
    # For now, return mock data
    
    n_samples = 1000
    n_features = 15
    
    # Mock feature data (vegetation indices, weather, etc.)
    X = np.random.uniform(0, 1, (n_samples, n_features))
    
    # Mock stress labels (0: normal, 1: water stress, 2: nutrient stress, 3: disease)
    y = np.random.choice([0, 1, 2, 3], n_samples, p=[0.6, 0.2, 0.15, 0.05])
    
    return X, y


def _prepare_crop_classification_data(data_sources: List[str]) -> tuple:
    """Prepare data for crop classification model training."""
    # Mock data for crop classification
    
    n_samples = 2000
    n_features = 20
    
    # Mock feature data (satellite bands, vegetation indices, etc.)
    X = np.random.uniform(0, 1, (n_samples, n_features))
    
    # Mock crop labels
    crop_types = ['maize', 'rice', 'wheat', 'sorghum', 'beans', 'cassava']
    y = np.random.choice(crop_types, n_samples)
    
    return X, y


def _prepare_anomaly_detection_data(data_sources: List[str]) -> np.ndarray:
    """Prepare data for anomaly detection model training."""
    # Mock data for anomaly detection
    
    n_samples = 1500
    n_features = 12
    
    # Mock feature data (mostly normal with some anomalies)
    X_normal = np.random.normal(0.5, 0.1, (int(n_samples * 0.9), n_features))
    X_anomaly = np.random.normal(0.8, 0.2, (int(n_samples * 0.1), n_features))
    
    X = np.vstack([X_normal, X_anomaly])
    np.random.shuffle(X)
    
    return X


def _load_model_by_type(model: MLModel):
    """Load the appropriate model class based on model type."""
    if model.model_type == 'stress_detection':
        return AgriculturalStressDetector(model_type=model.algorithm)
    elif model.model_type == 'crop_classification':
        return CropClassificationModel(model_type=model.algorithm)
    elif model.model_type == 'anomaly_detection':
        return AnomalyDetectionModel()
    else:
        raise ValueError(f"Unsupported model type: {model.model_type}")


def _hash_input_data(input_features: Dict[str, Any]) -> str:
    """Create a hash of input data for deduplication."""
    import hashlib
    import json
    
    # Sort keys for consistent hashing
    sorted_features = json.dumps(input_features, sort_keys=True)
    return hashlib.sha256(sorted_features.encode()).hexdigest()
