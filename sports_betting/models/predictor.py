import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import logging
from ..config.settings import MODEL_CONFIG

logger = logging.getLogger(__name__)

class BettingPredictor:
    def __init__(self):
        self.power_rankings = {}
        self.player_models = {}
        self.game_models = {}
        self.scalers = {}
        
    def update_power_rankings(self, sport: str, team_stats: pd.DataFrame):
        """Update power rankings for a specific sport."""
        if not MODEL_CONFIG['power_rankings']['enabled']:
            return
            
        try:
            # Calculate basic power ranking components
            rankings = pd.DataFrame()
            rankings['team'] = team_stats['team']
            
            # Win percentage
            rankings['win_pct'] = team_stats['wins'] / (team_stats['wins'] + team_stats['losses'])
            
            # Point differential
            rankings['point_diff'] = team_stats['points_for'] - team_stats['points_against']
            
            # Strength of schedule (simplified version)
            rankings['sos'] = team_stats['opponent_win_pct']
            
            # Recent form (last N games)
            rankings['recent_form'] = team_stats['last_10_wins'] / 10
            
            # Calculate composite score
            rankings['power_score'] = (
                rankings['win_pct'] * 0.3 +
                rankings['point_diff'].rank(pct=True) * 0.3 +
                rankings['sos'] * 0.2 +
                rankings['recent_form'] * 0.2
            )
            
            # Store rankings
            self.power_rankings[sport] = rankings.sort_values('power_score', ascending=False)
            
        except Exception as e:
            logger.error(f"Error updating power rankings for {sport}: {str(e)}")
    
    def train_player_props_model(self, sport: str, player_stats: pd.DataFrame):
        """Train LSTM model for player props predictions."""
        if not MODEL_CONFIG['player_props']['enabled']:
            return
            
        try:
            # Prepare sequences for LSTM
            sequence_length = MODEL_CONFIG['player_props']['lookback_periods']
            
            # Create sequences of player stats
            sequences = []
            labels = []
            
            for player in player_stats['player_id'].unique():
                player_data = player_stats[player_stats['player_id'] == player]
                if len(player_data) < sequence_length + 1:
                    continue
                    
                for i in range(len(player_data) - sequence_length):
                    sequences.append(player_data.iloc[i:i+sequence_length][['points', 'minutes', 'usage_rate']].values)
                    labels.append(player_data.iloc[i+sequence_length]['points'])
            
            X = np.array(sequences)
            y = np.array(labels)
            
            # Create and train LSTM model
            model = Sequential([
                LSTM(64, input_shape=(sequence_length, 3), return_sequences=True),
                Dropout(0.2),
                LSTM(32),
                Dense(16, activation='relu'),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse')
            model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
            
            self.player_models[sport] = model
            
        except Exception as e:
            logger.error(f"Error training player props model for {sport}: {str(e)}")
    
    def train_game_prediction_model(self, sport: str, historical_games: pd.DataFrame):
        """Train ensemble model for game predictions."""
        if not MODEL_CONFIG['game_predictions']['enabled']:
            return
            
        try:
            # Prepare features
            features = [
                'home_power_ranking', 'away_power_ranking',
                'home_recent_form', 'away_recent_form',
                'home_rest_days', 'away_rest_days',
                'home_injuries_impact', 'away_injuries_impact'
            ]
            
            X = historical_games[features]
            y = historical_games['home_team_won']
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train Random Forest model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_scaled, y)
            
            # Store model and scaler
            self.game_models[sport] = model
            self.scalers[sport] = scaler
            
        except Exception as e:
            logger.error(f"Error training game prediction model for {sport}: {str(e)}")
    
    def predict_game(self, sport: str, game_data: Dict) -> Dict:
        """Make predictions for a specific game."""
        try:
            if sport not in self.game_models:
                return {"error": "No model available for this sport"}
                
            # Prepare features
            features = pd.DataFrame([{
                'home_power_ranking': self.power_rankings[sport].loc[game_data['home_team'], 'power_score'],
                'away_power_ranking': self.power_rankings[sport].loc[game_data['away_team'], 'power_score'],
                'home_recent_form': game_data['home_recent_form'],
                'away_recent_form': game_data['away_recent_form'],
                'home_rest_days': game_data['home_rest_days'],
                'away_rest_days': game_data['away_rest_days'],
                'home_injuries_impact': game_data['home_injuries_impact'],
                'away_injuries_impact': game_data['away_injuries_impact']
            }])
            
            # Scale features
            X_scaled = self.scalers[sport].transform(features)
            
            # Make prediction
            win_prob = self.game_models[sport].predict_proba(X_scaled)[0][1]
            
            return {
                'home_win_probability': win_prob,
                'away_win_probability': 1 - win_prob,
                'confidence': abs(win_prob - 0.5) * 2  # Scale confidence based on probability distance from 0.5
            }
            
        except Exception as e:
            logger.error(f"Error making game prediction: {str(e)}")
            return {"error": str(e)}
    
    def predict_player_props(self, sport: str, player_data: Dict) -> Dict:
        """Predict player props for a specific player."""
        try:
            if sport not in self.player_models:
                return {"error": "No model available for this sport"}
                
            # Prepare sequence
            sequence = np.array([player_data['recent_stats']])  # Should be last N games' stats
            
            # Make prediction
            predicted_value = self.player_models[sport].predict(sequence)[0][0]
            
            return {
                'predicted_value': predicted_value,
                'confidence': self._calculate_props_confidence(predicted_value, player_data['prop_line'])
            }
            
        except Exception as e:
            logger.error(f"Error predicting player props: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_props_confidence(self, predicted_value: float, line: float) -> float:
        """Calculate confidence in player props prediction."""
        # Simple confidence calculation based on difference from line
        diff_percentage = abs(predicted_value - line) / line
        return min(diff_percentage * 100, 100)  # Cap confidence at 100% 