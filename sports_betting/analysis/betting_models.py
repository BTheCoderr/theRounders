import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

class BettingModels:
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100)
        self.gb_model = GradientBoostingRegressor()
        self.xgb_model = xgb.XGBClassifier()
        self.scaler = StandardScaler()

    def prepare_features(self, game_data):
        """Prepare features for betting models"""
        features = {
            'team_stats': self._process_team_stats(game_data),
            'player_stats': self._process_player_stats(game_data),
            'situational': self._process_situational_factors(game_data),
            'trends': self._process_betting_trends(game_data),
            'external': self._process_external_factors(game_data)
        }
        return pd.DataFrame(features)

    def predict_spread(self, features):
        """Predict against the spread outcome"""
        predictions = {
            'rf_prediction': self.rf_model.predict_proba(features),
            'gb_prediction': self.gb_model.predict(features),
            'xgb_prediction': self.xgb_model.predict_proba(features)
        }
        return self._ensemble_predictions(predictions)

    def predict_totals(self, features):
        """Predict over/under outcome"""
        return self.gb_model.predict(features)

    def analyze_value_opportunities(self, predictions, current_lines):
        """Identify value betting opportunities"""
        value_bets = []
        for game, pred in predictions.items():
            edge = self._calculate_betting_edge(pred, current_lines[game])
            if abs(edge) > 0.05:  # 5% edge threshold
                value_bets.append({
                    'game': game,
                    'edge': edge,
                    'confidence': self._calculate_confidence(pred)
                })
        return value_bets

    def _process_team_stats(self, data):
        """Process team-specific statistics"""
        return {
            'offensive_rating': data['off_rtg'],
            'defensive_rating': data['def_rtg'],
            'pace': data['pace'],
            'recent_form': self._calculate_recent_form(data),
            'rest_days': data['rest_days']
        }

    def _process_situational_factors(self, data):
        """Process situational betting factors"""
        return {
            'back_to_back': data['b2b'],
            'travel_distance': data['travel_dist'],
            'home_away': data['is_home'],
            'division_game': data['is_division'],
            'revenge_game': data['is_revenge']
        }
