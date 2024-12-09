from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
import xgboost as xgb
import numpy as np

class AdvancedMLModels:
    def __init__(self):
        self.models = {
            'rf': RandomForestClassifier(n_estimators=100, random_state=42),
            'gb': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'nn': MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42),
            'xgb': xgb.XGBClassifier(n_estimators=100, random_state=42)
        }
        self.best_model = None
        
    def train_models(self, X, y):
        """Train multiple models and select the best one"""
        best_score = 0
        
        for name, model in self.models.items():
            # Perform cross-validation
            scores = cross_val_score(model, X, y, cv=5)
            avg_score = np.mean(scores)
            
            if avg_score > best_score:
                best_score = avg_score
                self.best_model = model
                
        # Train best model on full dataset
        self.best_model.fit(X, y)
        return best_score
        
    def predict_proba(self, X):
        """Get probability predictions from best model"""
        if self.best_model is None:
            return 0.5
        return self.best_model.predict_proba(X)[0][1] 

class AdvancedMLFeatures:
    def __init__(self):
        self.features = [
            # Basic stats
            'win_rate', 'points_avg', 'defense_rating',
            
            # Advanced metrics
            'elo_rating', 'power_ranking', 'strength_of_schedule',
            
            # Recent performance
            'last_5_wins', 'last_10_performance', 'momentum_score',
            
            # Team composition
            'starter_impact', 'bench_strength', 'injury_impact',
            
            # Matchup specific
            'h2h_advantage', 'style_matchup', 'pace_differential',
            
            # Situational
            'rest_advantage', 'travel_distance', 'schedule_fatigue',
            
            # External factors
            'weather_impact', 'venue_advantage', 'referee_tendency'
        ]
        
    def calculate_elo_rating(self, team, historical_games):
        """Calculate team's ELO rating"""
        team_elo = 1500  # Starting ELO
        k_factor = 32
        
        for game in historical_games:
            opponent_elo = game.get('opponent_elo', 1500)  # Default opponent ELO
            expected_score = 1 / (1 + 10 ** ((opponent_elo - team_elo) / 400))
            actual_score = 1 if game['result'] == 'Won' else 0
            team_elo = team_elo + k_factor * (actual_score - expected_score)
            
        return team_elo
        
    def calculate_momentum_score(self, recent_games):
        """Calculate team's momentum based on recent performance"""
        momentum = 0
        weights = [1.0, 0.9, 0.8, 0.7, 0.6]  # More recent games have higher weight
        
        for game, weight in zip(recent_games, weights):
            if game['result'] == 'Won':
                momentum += weight * (1 + game['margin'] / 100)
            else:
                momentum -= weight * (1 + game['margin'] / 100)
                
        return momentum
        
    def calculate_style_matchup(self, team1_stats, team2_stats):
        """Analyze how team styles match up"""
        factors = {
            'pace': abs(team1_stats['pace'] - team2_stats['pace']),
            'three_point_rate': abs(team1_stats['three_rate'] - team2_stats['three_rate']),
            'paint_points': abs(team1_stats['paint_points'] - team2_stats['paint_points'])
        }
        
        return sum(factors.values()) / len(factors)
        
    def get_referee_tendency(self, referee, game_type):
        """Analyze referee tendencies"""
        # TODO: Implement referee analysis
        return 0