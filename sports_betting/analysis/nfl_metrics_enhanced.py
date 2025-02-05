import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from loguru import logger
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

class NFLMetricsEnhanced:
    def __init__(self):
        logger.info("Initializing Enhanced NFL Metrics System")
        self.feature_importance_history = {}
        self.quality_thresholds = {
            'missing_data': 0.05,  # 5% threshold
            'outlier': 2.5,        # std deviations
            'correlation': 0.8      # correlation threshold
        }
        self.scaler = StandardScaler()
        
    def calculate_all_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate all advanced metrics with quality checks"""
        try:
            metrics = {}
            
            # 1. Advanced Passing Metrics
            metrics.update(self._passing_metrics(data))
            
            # 2. Advanced Rushing Metrics
            metrics.update(self._rushing_metrics(data))
            
            # 3. Advanced Situational Metrics
            metrics.update(self._situational_metrics(data))
            
            # 4. Quality Checks
            quality_report = self._check_data_quality(pd.DataFrame(metrics))
            
            # 5. Feature Importance
            importance_report = self._track_feature_importance(pd.DataFrame(metrics))
            
            # 6. Correlation Analysis
            correlation_report = self._analyze_correlations(pd.DataFrame(metrics))
            
            return {
                'metrics': metrics,
                'quality_report': quality_report,
                'importance_report': importance_report,
                'correlation_report': correlation_report
            }
            
        except Exception as e:
            logger.error(f"Error in calculate_all_metrics: {str(e)}")
            raise
            
    def _passing_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate advanced passing metrics"""
        metrics = {}
        
        # CPOE (Completion Percentage Over Expected)
        metrics['cpoe'] = self._calculate_cpoe(
            data['completions'],
            data['attempts'],
            data['air_yards'],
            data.get('pressure', None)
        )
        
        # Air Yards Metrics
        metrics['avg_air_yards'] = data['air_yards'] / data['attempts']
        metrics['deep_pass_rate'] = (data['air_yards'] > 20).mean()
        metrics['completed_air_yards'] = data['completed_air_yards'] / data['completions']
        
        # Pressure and Protection Metrics
        if 'pressure' in data.columns:
            metrics['pressure_rate'] = data['pressure'] / data['dropbacks']
            metrics['clean_pocket_rating'] = self._calculate_clean_pocket_rating(data)
            
        # Advanced Efficiency
        metrics['pass_success_rate'] = self._calculate_success_rate(data, 'pass')
        metrics['explosive_pass_rate'] = (data['pass_yards'] > 20).mean()
        
        return metrics
        
    def _rushing_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate advanced rushing metrics"""
        metrics = {}
        
        # Efficiency Metrics
        metrics['yards_after_contact_per_rush'] = data['yards_after_contact'] / data['rush_attempts']
        metrics['broken_tackles_per_rush'] = data['broken_tackles'] / data['rush_attempts']
        metrics['stuff_rate'] = (data['rush_yards'] <= 0).mean()
        
        # Directional Success
        directions = ['left', 'middle', 'right']
        for direction in directions:
            metrics[f'{direction}_success_rate'] = self._calculate_directional_success(data, direction)
            
        # Situational Success
        metrics['power_success'] = self._calculate_power_success(data)
        metrics['open_field_yards'] = self._calculate_open_field_yards(data)
        
        return metrics
        
    def _situational_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate situational metrics"""
        metrics = {}
        
        # Down-specific Success Rates
        for down in [1, 2, 3, 4]:
            down_data = data[data['down'] == down]
            metrics[f'success_rate_down_{down}'] = self._calculate_success_rate(down_data)
            
        # Red Zone Efficiency
        metrics['red_zone_success'] = self._calculate_red_zone_efficiency(data)
        
        # Game Script Metrics
        metrics['early_down_pass_rate'] = self._calculate_early_down_pass_rate(data)
        metrics['play_action_rate'] = data['play_action'].mean()
        
        return metrics
        
    def _check_data_quality(self, metrics_df: pd.DataFrame) -> Dict:
        """Comprehensive data quality checks"""
        quality_report = {
            'missing_data': {},
            'outliers': {},
            'data_types': {},
            'value_ranges': {},
            'recommendations': []
        }
        
        for column in metrics_df.columns:
            # Missing Data Check
            missing_pct = metrics_df[column].isnull().mean()
            quality_report['missing_data'][column] = missing_pct
            
            if missing_pct > self.quality_thresholds['missing_data']:
                quality_report['recommendations'].append(
                    f"High missing data in {column}: {missing_pct:.2%}"
                )
                
            # Outlier Check
            z_scores = np.abs(stats.zscore(metrics_df[column].dropna()))
            outliers_pct = (z_scores > self.quality_thresholds['outlier']).mean()
            quality_report['outliers'][column] = outliers_pct
            
            if outliers_pct > 0.05:  # More than 5% outliers
                quality_report['recommendations'].append(
                    f"High outlier rate in {column}: {outliers_pct:.2%}"
                )
                
        return quality_report
        
    def _track_feature_importance(self, metrics_df: pd.DataFrame) -> Dict:
        """Track feature importance over time"""
        if 'target' not in metrics_df.columns:
            logger.warning("No target variable found for feature importance")
            return {}
            
        # Random Forest for feature importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        X = metrics_df.drop('target', axis=1)
        y = metrics_df['target']
        
        rf.fit(X, y)
        
        # Update importance history
        importance_dict = dict(zip(X.columns, rf.feature_importances_))
        for feature, importance in importance_dict.items():
            if feature not in self.feature_importance_history:
                self.feature_importance_history[feature] = []
            self.feature_importance_history[feature].append(importance)
            
        return {
            'current_importance': importance_dict,
            'importance_history': self.feature_importance_history
        }
        
    def _analyze_correlations(self, metrics_df: pd.DataFrame) -> Dict:
        """Analyze feature correlations"""
        corr_matrix = metrics_df.corr()
        
        # Find highly correlated features
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) > self.quality_thresholds['correlation']:
                    high_corr_pairs.append({
                        'features': (corr_matrix.columns[i], corr_matrix.columns[j]),
                        'correlation': corr_matrix.iloc[i, j]
                    })
                    
        return {
            'correlation_matrix': corr_matrix,
            'high_correlations': high_corr_pairs,
            'recommendations': [
                f"Consider removing one of {pair['features']} (correlation: {pair['correlation']:.2f})"
                for pair in high_corr_pairs
            ]
        }