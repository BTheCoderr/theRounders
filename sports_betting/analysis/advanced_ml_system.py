# Standard libraries
import numpy as np
import pandas as pd
from datetime import datetime
import os

# ML libraries
import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Visualization
import plotly.graph_objects as go

# Model persistence
import joblib

# Type hints
from typing import Dict, List, Optional

class AdvancedBettingML:
    def __init__(self, sport: str):
        self.sport = sport
        self.models = {
            'random_forest': self._build_random_forest(),
            'gradient_boost': self._build_gradient_boost(),
            'xgboost': self._build_xgboost(),
            'lightgbm': self._build_lightgbm()
        }
        
        # Sport-specific models
        self.sport_models = {
            'NFL': {
                'spread': self._build_nfl_spread_model(),
                'totals': self._build_nfl_totals_model(),
                'props': self._build_nfl_props_model()
            },
            'NBA': {
                'spread': self._build_nba_spread_model(),
                'totals': self._build_nba_totals_model(),
                'player_props': self._build_nba_props_model()
            }
        }
        
        self.scaler = StandardScaler()
        self.feature_engineering = FeatureEngineering()
        self.risk_manager = RiskManager()
        
    def _build_random_forest(self):
        """Build a Random Forest model"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            class_weight='balanced'
        )
        
    def _build_gradient_boost(self):
        """Build Gradient Boosting model"""
        return GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            min_samples_split=2
        )
        
    def _build_xgboost(self):
        """Build XGBoost model"""
        return xgb.XGBClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            min_child_weight=1,
            gamma=0,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='binary:logistic',
            random_state=42
        )
        
    def _build_lightgbm(self):
        """Build LightGBM model"""
        return lgb.LGBMClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            num_leaves=31,
            feature_fraction=0.8,
            bagging_fraction=0.8,
            random_state=42
        )
        
    def _build_nfl_spread_model(self):
        """Build NFL spread model"""
        # Implement the model building logic here
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            class_weight='balanced'
        )
        
    def _build_nfl_totals_model(self):
        """Build NFL totals model"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            class_weight='balanced'
        )
        
    def _build_nfl_props_model(self):
        """Build NFL props model"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            class_weight='balanced'
        )
        
    def _build_nba_spread_model(self):
        """Build NBA spread model"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            class_weight='balanced'
        )
        
    def _build_nba_totals_model(self):
        """Build NBA totals model"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            class_weight='balanced'
        )
        
    def _build_nba_props_model(self):
        """Build NBA props model"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            class_weight='balanced'
        )
        
    def save_models(self, path: str = 'models/'):
        """Save all trained models"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = os.path.join(path, self.sport, timestamp)
        os.makedirs(save_path, exist_ok=True)
        
        for name, model in self.models.items():
            model_path = os.path.join(save_path, f'{name}.joblib')
            joblib.dump(model, model_path)
            
        # Save scaler
        scaler_path = os.path.join(save_path, 'scaler.joblib')
        joblib.dump(self.scaler, scaler_path)
        
        return save_path
        
    def load_models(self, path: str):
        """Load saved models"""
        for name in self.models.keys():
            model_path = os.path.join(path, f'{name}.joblib')
            if os.path.exists(model_path):
                self.models[name] = joblib.load(model_path)
                
        # Load scaler
        scaler_path = os.path.join(path, 'scaler.joblib')
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
            
    def monitor_performance(self, predictions: Dict, actual_results: Dict):
        """Monitor model performance in real-time"""
        performance_metrics = {
            'accuracy': {},
            'roi': {},
            'kelly_fraction': {}
        }
        
        for model_name in self.models:
            model_preds = predictions[model_name]
            
            # Calculate accuracy
            accuracy = accuracy_score(
                actual_results['outcomes'],
                model_preds['predictions']
            )
            
            # Calculate ROI
            roi = self._calculate_roi(
                model_preds['bets'],
                actual_results['outcomes'],
                actual_results['odds']
            )
            
            # Update Kelly fraction based on performance
            kelly = self.risk_manager.update_kelly_fraction(
                accuracy,
                roi,
                model_name
            )
            
            performance_metrics['accuracy'][model_name] = accuracy
            performance_metrics['roi'][model_name] = roi
            performance_metrics['kelly_fraction'][model_name] = kelly
            
        return performance_metrics

class FeatureEngineering:
    def __init__(self):
        self.feature_sets = {
            'NFL': self._nfl_features,
            'NBA': self._nba_features,
            'NHL': self._nhl_features
        }
        
    def create_features(self, data: pd.DataFrame, sport: str) -> pd.DataFrame:
        """Create sport-specific features"""
        if sport not in self.feature_sets:
            raise ValueError(f"Sport {sport} not supported")
            
        return self.feature_sets[sport](data)
        
    def _nfl_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create NFL-specific features"""
        features = pd.DataFrame()
        
        # Basic stats
        features['yards_per_play'] = data['total_yards'] / data['total_plays']
        features['turnover_diff'] = data['takeaways'] - data['giveaways']
        
        # Advanced metrics
        features['pass_success_rate'] = self._calculate_success_rate(data, 'pass')
        features['rush_success_rate'] = self._calculate_success_rate(data, 'rush')
        
        # Situational features
        features['red_zone_efficiency'] = data['red_zone_scores'] / data['red_zone_attempts']
        features['third_down_conv'] = data['third_down_conv'] / data['third_down_attempts']
        
        return features
        
    def _nba_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create NBA-specific features"""
        features = pd.DataFrame()
        
        # Example features
        features['true_shooting'] = data['points'] / (2 * (data['field_goal_attempts'] + 0.44 * data['free_throw_attempts']))
        features['pace'] = data['possessions'] / data['minutes_played']
        
        return features
        
    def _nhl_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create NHL-specific features"""
        features = pd.DataFrame()
        
        # Example features
        features['goals_per_game'] = data['goals'] / data['games']
        features['shots_per_game'] = data['shots'] / data['games']
        
        return features
        
    def _calculate_success_rate(self, data: pd.DataFrame, play_type: str) -> float:
        """Calculate success rate for a given play type"""
        # Implement the logic to calculate success rate for the given play type
        pass

class RiskManager:
    def __init__(self):
        self.kelly_fractions = {
            'random_forest': 0.25,
            'gradient_boost': 0.25,
            'xgboost': 0.25,
            'lightgbm': 0.25
        }
        
        self.position_limits = {
            'max_per_bet': 0.05,    # 5% of bankroll
            'max_per_day': 0.20,    # 20% of bankroll
            'max_per_sport': 0.30   # 30% of bankroll
        }
        
    def calculate_position_size(self, confidence: float, odds: float, 
                              model_name: str, current_exposure: Dict) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        # Get base Kelly fraction for model
        kelly_fraction = self.kelly_fractions[model_name]
        
        # Calculate Kelly bet size
        decimal_odds = self._american_to_decimal(odds)
        p = confidence
        q = 1 - p
        b = decimal_odds - 1
        kelly = (b * p - q) / b
        
        # Apply fraction and limits
        position = kelly * kelly_fraction
        
        # Apply position limits
        position = min(
            position,
            self.position_limits['max_per_bet'],
            self.position_limits['max_per_day'] - current_exposure['daily'],
            self.position_limits['max_per_sport'] - current_exposure['sport']
        )
        
        return max(0, position)
        
    def update_kelly_fraction(self, accuracy: float, roi: float, 
                            model_name: str) -> float:
        """Update Kelly fraction based on performance"""
        base_fraction = self.kelly_fractions[model_name]
        
        # Adjust based on accuracy
        if accuracy < 0.52:  # Below breakeven
            base_fraction *= 0.8
        elif accuracy > 0.58:  # Strong performance
            base_fraction *= 1.2
            
        # Adjust based on ROI
        if roi < -0.05:  # Poor ROI
            base_fraction *= 0.8
        elif roi > 0.10:  # Strong ROI
            base_fraction *= 1.2
            
        # Apply limits
        base_fraction = max(0.1, min(0.5, base_fraction))
        
        # Update stored fraction
        self.kelly_fractions[model_name] = base_fraction
        
        return base_fraction 