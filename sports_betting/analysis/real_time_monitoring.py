import pandas as pd
import numpy as np
from typing import Dict, List
import plotly.graph_objects as go
from datetime import datetime

class RealTimeMonitoring:
    def __init__(self):
        self.performance_history = {
            'accuracy': [],
            'roi': [],
            'kelly_fractions': [],
            'model_selections': []
        }
        
        self.alert_thresholds = {
            'accuracy_drop': 0.05,  # 5% drop in accuracy
            'roi_drop': 0.10,      # 10% drop in ROI
            'confidence_threshold': 0.60
        }
        
    def update_models(self, new_results: Dict):
        """Update models with new results"""
        # Calculate performance metrics
        metrics = self._calculate_metrics(new_results)
        
        # Update performance history
        self._update_history(metrics)
        
        # Check for alerts
        alerts = self._check_alerts(metrics)
        
        # Update model weights
        self._update_model_weights(metrics)
        
        return {
            'metrics': metrics,
            'alerts': alerts,
            'recommendations': self._generate_recommendations(metrics)
        }
        
    def visualize_performance(self):
        """Create performance visualization dashboard"""
        fig = go.Figure()
        
        # Add accuracy trace
        fig.add_trace(go.Scatter(
            x=self.performance_history['dates'],
            y=self.performance_history['accuracy'],
            name='Accuracy'
        ))
        
        # Add ROI trace
        fig.add_trace(go.Scatter(
            x=self.performance_history['dates'],
            y=self.performance_history['roi'],
            name='ROI'
        ))
        
        # Update layout
        fig.update_layout(
            title='Model Performance Over Time',
            xaxis_title='Date',
            yaxis_title='Performance Metrics'
        )
        
        return fig
        
    def _check_alerts(self, metrics: Dict) -> List[str]:
        """Check for performance alerts"""
        alerts = []
        
        # Check accuracy drop
        if metrics['accuracy_change'] < -self.alert_thresholds['accuracy_drop']:
            alerts.append(f"Accuracy drop of {abs(metrics['accuracy_change']):.2%}")
            
        # Check ROI drop
        if metrics['roi_change'] < -self.alert_thresholds['roi_drop']:
            alerts.append(f"ROI drop of {abs(metrics['roi_change']):.2%}")
            
        return alerts
        
    def _update_model_weights(self, metrics: Dict):
        """Update model weights based on performance"""
        for model in metrics['model_performance']:
            # Calculate new weight based on recent performance
            new_weight = self._calculate_model_weight(
                metrics['model_performance'][model]
            )
            
            # Update model weight
            self.model_weights[model] = new_weight
            
    def _generate_recommendations(self, metrics: Dict) -> Dict:
        """Generate recommendations based on performance"""
        recommendations = {
            'model_adjustments': [],
            'risk_adjustments': [],
            'feature_adjustments': []
        }
        
        # Check for model adjustments
        if metrics['accuracy'] < 0.52:
            recommendations['model_adjustments'].append(
                "Consider retraining models with recent data"
            )
            
        # Check for risk adjustments
        if metrics['roi'] < 0:
            recommendations['risk_adjustments'].append(
                "Reduce position sizes temporarily"
            )
            
        return recommendations