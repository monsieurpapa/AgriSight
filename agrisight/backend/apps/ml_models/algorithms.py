"""
Machine Learning algorithms implementation for agricultural monitoring.
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib
import logging

logger = logging.getLogger(__name__)


class AgriculturalStressDetector:
    """
    Machine learning model for detecting agricultural stress.
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for stress detection.
        
        Args:
            data: DataFrame with vegetation indices and metadata
            
        Returns:
            Prepared feature array
        """
        # Define feature columns
        feature_columns = [
            'NDVI_mean', 'NDVI_std', 'NDVI_min', 'NDVI_max',
            'EVI_mean', 'EVI_std', 'EVI_min', 'EVI_max',
            'NDWI_mean', 'NDWI_std', 'NDWI_min', 'NDWI_max',
            'SAVI_mean', 'SAVI_std', 'SAVI_min', 'SAVI_max',
            'cloud_cover', 'resolution', 'days_since_rainfall',
            'temperature_anomaly', 'precipitation_anomaly'
        ]
        
        # Select available features
        available_features = [col for col in feature_columns if col in data.columns]
        self.feature_names = available_features
        
        # Fill missing values
        features = data[available_features].fillna(0)
        
        # Add derived features
        if 'NDVI_mean' in features.columns and 'EVI_mean' in features.columns:
            features['NDVI_EVI_ratio'] = features['NDVI_mean'] / (features['EVI_mean'] + 1e-8)
        
        if 'NDVI_mean' in features.columns and 'NDWI_mean' in features.columns:
            features['NDVI_NDWI_diff'] = features['NDVI_mean'] - features['NDWI_mean']
        
        # Temporal features
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            features['month'] = data['date'].dt.month
            features['day_of_year'] = data['date'].dt.dayofyear
        
        # Update feature names
        self.feature_names = list(features.columns)
        
        return features.values
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, float]:
        """
        Train the stress detection model.
        
        Args:
            X: Feature matrix
            y: Target labels
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training metrics
        """
        try:
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            
            # Initialize and train model
            if self.model_type == 'random_forest':
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
            elif self.model_type == 'svm':
                self.model = SVC(
                    kernel='rbf',
                    C=1.0,
                    gamma='scale',
                    probability=True,
                    random_state=42
                )
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate on validation set
            y_pred = self.model.predict(X_val_scaled)
            y_pred_proba = self.model.predict_proba(X_val_scaled)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_val, y_pred),
                'precision': precision_score(y_val, y_pred, average='weighted'),
                'recall': recall_score(y_val, y_pred, average='weighted'),
                'f1_score': f1_score(y_val, y_pred, average='weighted'),
                'confusion_matrix': confusion_matrix(y_val, y_pred).tolist(),
                'classification_report': classification_report(y_val, y_pred, output_dict=True)
            }
            
            self.is_trained = True
            
            logger.info(f"Model trained successfully. Accuracy: {metrics['accuracy']:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new data.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_scores = self.model.feature_importances_
        return dict(zip(self.feature_names, importance_scores))
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.is_trained = True
        
        logger.info(f"Model loaded from {filepath}")


class CropClassificationModel:
    """
    Machine learning model for crop type classification.
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_trained = False
    
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for crop classification.
        
        Args:
            data: DataFrame with satellite data and crop labels
            
        Returns:
            Prepared feature array
        """
        # Define feature columns for crop classification
        feature_columns = [
            'B02_mean', 'B03_mean', 'B04_mean', 'B08_mean',
            'B11_mean', 'B12_mean',
            'NDVI_mean', 'EVI_mean', 'NDWI_mean', 'SAVI_mean',
            'NDVI_std', 'EVI_std', 'NDWI_std', 'SAVI_std',
            'NDVI_min', 'NDVI_max', 'EVI_min', 'EVI_max',
            'cloud_cover', 'resolution'
        ]
        
        # Select available features
        available_features = [col for col in feature_columns if col in data.columns]
        self.feature_names = available_features
        
        # Fill missing values
        features = data[available_features].fillna(0)
        
        # Add temporal features
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            features['month'] = data['date'].dt.month
            features['day_of_year'] = data['date'].dt.dayofyear
            features['season'] = data['date'].dt.month.map(self._get_season)
        
        # Add spatial features
        if 'latitude' in data.columns and 'longitude' in data.columns:
            features['lat'] = data['latitude']
            features['lon'] = data['longitude']
            features['elevation_estimate'] = self._estimate_elevation(
                data['latitude'], data['longitude']
            )
        
        # Update feature names
        self.feature_names = list(features.columns)
        
        return features.values
    
    def _get_season(self, month: int) -> int:
        """Get season from month (0=Winter, 1=Spring, 2=Summer, 3=Fall)."""
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Fall
    
    def _estimate_elevation(self, lat: pd.Series, lon: pd.Series) -> pd.Series:
        """Estimate elevation from coordinates (simplified)."""
        # This is a simplified elevation estimation
        # In practice, you'd use a digital elevation model
        return np.random.uniform(0, 2000, len(lat))
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, float]:
        """Train the crop classification model."""
        try:
            # Encode labels
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y_encoded, test_size=validation_split, random_state=42, stratify=y_encoded
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            
            # Initialize and train model
            if self.model_type == 'random_forest':
                self.model = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    class_weight='balanced'
                )
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate on validation set
            y_pred = self.model.predict(X_val_scaled)
            y_pred_proba = self.model.predict_proba(X_val_scaled)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_val, y_pred),
                'precision': precision_score(y_val, y_pred, average='weighted'),
                'recall': recall_score(y_val, y_pred, average='weighted'),
                'f1_score': f1_score(y_val, y_pred, average='weighted'),
                'confusion_matrix': confusion_matrix(y_val, y_pred).tolist(),
                'classification_report': classification_report(y_val, y_pred, output_dict=True),
                'class_names': self.label_encoder.classes_.tolist()
            }
            
            self.is_trained = True
            
            logger.info(f"Crop classification model trained. Accuracy: {metrics['accuracy']:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training crop classification model: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make crop classification predictions."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions_encoded = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Decode predictions
        predictions = self.label_encoder.inverse_transform(predictions_encoded)
        
        return predictions, probabilities


class AnomalyDetectionModel:
    """
    Anomaly detection model for identifying unusual agricultural patterns.
    """
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
    
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for anomaly detection.
        
        Args:
            data: DataFrame with time series vegetation data
            
        Returns:
            Prepared feature array
        """
        # Define feature columns
        feature_columns = [
            'NDVI_mean', 'NDVI_std', 'NDVI_trend',
            'EVI_mean', 'EVI_std', 'EVI_trend',
            'NDWI_mean', 'NDWI_std', 'NDWI_trend',
            'SAVI_mean', 'SAVI_std', 'SAVI_trend'
        ]
        
        # Select available features
        available_features = [col for col in feature_columns if col in data.columns]
        self.feature_names = available_features
        
        # Fill missing values
        features = data[available_features].fillna(0)
        
        # Add temporal features
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            features['month'] = data['date'].dt.month
            features['day_of_year'] = data['date'].dt.dayofyear
        
        # Add statistical features
        for col in ['NDVI_mean', 'EVI_mean', 'NDWI_mean', 'SAVI_mean']:
            if col in features.columns:
                features[f'{col}_zscore'] = (features[col] - features[col].mean()) / (features[col].std() + 1e-8)
        
        # Update feature names
        self.feature_names = list(features.columns)
        
        return features.values
    
    def train(self, X: np.ndarray) -> Dict[str, float]:
        """Train the anomaly detection model."""
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Initialize and train model
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100
            )
            
            # Train model
            self.model.fit(X_scaled)
            
            # Calculate training metrics
            anomaly_scores = self.model.decision_function(X_scaled)
            predictions = self.model.predict(X_scaled)
            
            n_anomalies = np.sum(predictions == -1)
            n_normal = np.sum(predictions == 1)
            
            metrics = {
                'total_samples': len(X),
                'anomalies_detected': int(n_anomalies),
                'normal_samples': int(n_normal),
                'contamination_rate': float(n_anomalies / len(X)),
                'mean_anomaly_score': float(np.mean(anomaly_scores)),
                'std_anomaly_score': float(np.std(anomaly_scores))
            }
            
            self.is_trained = True
            
            logger.info(f"Anomaly detection model trained. Contamination: {metrics['contamination_rate']:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training anomaly detection model: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make anomaly detection predictions.
        
        Returns:
            Tuple of (predictions, anomaly_scores)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.decision_function(X_scaled)
        
        return predictions, anomaly_scores
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'contamination': self.contamination
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Anomaly detection model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.contamination = model_data['contamination']
        self.is_trained = True
        
        logger.info(f"Anomaly detection model loaded from {filepath}")


class ModelEnsemble:
    """
    Ensemble model combining multiple algorithms for robust predictions.
    """
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.is_trained = False
    
    def add_model(self, name: str, model: Any, weight: float = 1.0):
        """Add a model to the ensemble."""
        self.models[name] = model
        self.weights[name] = weight
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train all models in the ensemble."""
        try:
            ensemble_metrics = {}
            
            for name, model in self.models.items():
                if hasattr(model, 'train'):
                    metrics = model.train(X, y)
                    ensemble_metrics[name] = metrics
                    logger.info(f"Model {name} trained with accuracy: {metrics.get('accuracy', 'N/A')}")
            
            self.is_trained = True
            return ensemble_metrics
            
        except Exception as e:
            logger.error(f"Error training ensemble: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make ensemble predictions."""
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before making predictions")
        
        predictions_list = []
        probabilities_list = []
        
        for name, model in self.models.items():
            if hasattr(model, 'predict'):
                pred, prob = model.predict(X)
                predictions_list.append(pred)
                probabilities_list.append(prob)
        
        # Simple voting for predictions
        if predictions_list:
            # For classification, use majority voting
            predictions_array = np.array(predictions_list)
            ensemble_predictions = []
            
            for i in range(predictions_array.shape[1]):
                unique, counts = np.unique(predictions_array[:, i], return_counts=True)
                ensemble_predictions.append(unique[np.argmax(counts)])
            
            ensemble_predictions = np.array(ensemble_predictions)
            
            # Average probabilities
            ensemble_probabilities = np.mean(probabilities_list, axis=0)
            
            return ensemble_predictions, ensemble_probabilities
        
        return np.array([]), np.array([])
