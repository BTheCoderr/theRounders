import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from typing import Dict, List
import asyncio
import aiohttp
from datetime import datetime
import logging
from loguru import logger

logger = logging.getLogger(__name__)

class ModernMLSystem:
    def __init__(self):
        self.model = MLPRegressor(
            hidden_layer_sizes=(100, 50),
            max_iter=1000,
            random_state=42
        )
        self.is_fitted = False
        self.default_features = None  # Store default feature values

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Fit the MLPRegressor model"""
        try:
            # Store feature names and their default values
            self.default_features = {col: X_train[col].mean() for col in X_train.columns}
            
            # Fit the model
            self.model.fit(X_train, y_train)
            self.is_fitted = True
            
        except Exception as e:
            logger.error(f"Error fitting model: {str(e)}")
            self.is_fitted = False

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using the MLPRegressor model"""
        try:
            if not self.is_fitted:
                logger.error("Model not fitted. Using default predictions.")
                return np.zeros(len(X))
                
            # Fill missing features with defaults if necessary
            if self.default_features:
                for col in self.default_features:
                    if col not in X.columns:
                        X[col] = self.default_features[col]
                        
            return self.model.predict(X)
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            return np.zeros(len(X))

    def predict_line_movement(self, features: Dict) -> Dict:
        """Predict line movement for each sport"""
        predictions = {}
        
        try:
            for sport, sport_features in features.items():
                if not isinstance(sport_features, pd.DataFrame) or sport_features.empty:
                    logger.warning(f"No features available for {sport}")
                    continue
                    
                # Process features and make predictions
                if not self.is_fitted:
                    logger.warning(f"Model not fitted for {sport}. Using default predictions.")
                    predictions[sport] = {
                        'predicted_movement': 0,
                        'confidence': 0,
                        'recommendation': 'PASS'
                    }
                else:
                    pred = self.predict(sport_features)
                    confidence = self._calculate_confidence(pred)
                    
                    predictions[sport] = {
                        'predicted_movement': float(pred.mean()),
                        'confidence': confidence,
                        'recommendation': self._get_recommendation(confidence)
                    }
                    
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting line movement: {str(e)}")
            return {}

    def _calculate_confidence(self, prediction: np.ndarray) -> float:
        """Calculate confidence score for prediction"""
        try:
            # Simple confidence calculation based on prediction variance
            confidence = 100 * (1 - np.std(prediction) / np.max(np.abs(prediction)))
            return max(min(confidence, 100), 0)  # Clamp between 0 and 100
        except:
            return 0.0

    def _get_recommendation(self, confidence: float) -> str:
        """Get recommendation based on confidence score"""
        if confidence >= 80:
            return 'STRONG BET'
        elif confidence >= 65:
            return 'CONSIDER'
        else:
            return 'PASS'