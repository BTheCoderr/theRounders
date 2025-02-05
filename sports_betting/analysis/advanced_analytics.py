import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta
from .api_integrations import SportsDataAPI
from .ml_models import AdvancedMLFeatures
from .weather_analysis import WeatherAnalysis

class AdvancedAnalytics:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.historical_data = None
        self.features = [
            'home_win_rate', 'away_win_rate',
            'home_points_avg', 'away_points_avg',
            'home_defense_rating', 'away_defense_rating',
            'home_rest_days', 'away_rest_days',
            'head_to_head_advantage'
        ]
        self.api = SportsDataAPI()
        self.ml_features = AdvancedMLFeatures()
        self.weather_analyzer = WeatherAnalysis()
        
    def analyze_game(self, game_data, historical_picks):
        """Enhanced game analysis with ML and advanced metrics"""
        try:
            # Get basic team metrics
            home_metrics = self.get_team_metrics(game_data['home_team'], game_data['sport'])
            away_metrics = self.get_team_metrics(game_data['away_team'], game_data['sport'])
            
            # Get head-to-head history
            h2h_stats = self.api.get_head_to_head(
                game_data['home_team'],
                game_data['away_team'],
                game_data['sport']
            )
            
            # Calculate advanced features
            features = {
                'home_win_rate': home_metrics['win_rate'],
                'away_win_rate': away_metrics['win_rate'],
                'home_points_avg': home_metrics['points_avg'],
                'away_points_avg': away_metrics['points_avg'],
                'home_defense_rating': home_metrics['defense_rating'],
                'away_defense_rating': away_metrics['defense_rating'],
                'home_rest_days': self.calculate_rest_days(game_data['home_team']),
                'away_rest_days': self.calculate_rest_days(game_data['away_team']),
                'h2h_advantage': self.calculate_h2h_advantage(h2h_stats),
                'recent_form': self.calculate_recent_form(
                    game_data['home_team'],
                    game_data['away_team']
                ),
                'injury_impact': self.calculate_injury_impact(
                    game_data['home_team'],
                    game_data['away_team']
                ),
                'schedule_fatigue': self.calculate_schedule_fatigue(
                    game_data['home_team'],
                    game_data['sport']
                )
            }
            
            # Add sport-specific features
            if game_data['sport'] == 'NHL':
                features.update({
                    'home_power_play': home_metrics['power_play'],
                    'away_power_play': away_metrics['power_play'],
                    'home_penalty_kill': home_metrics['penalty_kill'],
                    'away_penalty_kill': away_metrics['penalty_kill']
                })
            elif game_data['sport'] == 'NBA':
                features.update({
                    'home_rebounds': home_metrics['rebounds'],
                    'away_rebounds': away_metrics['rebounds'],
                    'home_assists': home_metrics['assists'],
                    'away_assists': away_metrics['assists']
                })
            elif game_data['sport'] == 'NFL':
                features.update({
                    'home_turnover_diff': home_metrics['turnover_diff'],
                    'away_turnover_diff': away_metrics['turnover_diff'],
                    'home_yards_per_game': home_metrics['yards_per_game'],
                    'away_yards_per_game': away_metrics['yards_per_game']
                })
                
            # Add new ML features
            features.update({
                'elo_rating_diff': self.ml_features.calculate_elo_rating(
                    game_data['home_team'],
                    historical_picks
                ) - self.ml_features.calculate_elo_rating(
                    game_data['away_team'],
                    historical_picks
                ),
                'momentum_score': self.ml_features.calculate_momentum_score(
                    self.get_recent_games(game_data['home_team'])
                ),
                'style_matchup': self.ml_features.calculate_style_matchup(
                    home_metrics,
                    away_metrics
                )
            })
            
            # Add weather impact for outdoor sports
            if game_data['sport'] in ['NFL']:
                weather_data = self.weather_analyzer.get_game_weather(
                    game_data['venue'],
                    game_data['game_time']
                )
                features['weather_impact'] = self.weather_analyzer.analyze_weather_impact(
                    weather_data,
                    game_data['sport']
                )
                
            # Calculate win probability using ML model
            win_prob = self.predict_win_probability(features)
            
            # Calculate betting value
            value = self.calculate_betting_value(win_prob, game_data['odds'])
            
            # Generate confidence score
            confidence = self.calculate_enhanced_confidence(
                win_prob,
                value,
                features,
                h2h_stats
            )
            
            return {
                'win_probability': win_prob,
                'betting_value': value,
                'confidence': confidence,
                'recommended_bet': self.get_recommended_bet(confidence, value),
                'analysis': {
                    'h2h_history': h2h_stats,
                    'key_metrics': features,
                    'value_rating': self.calculate_value_rating(value, win_prob)
                }
            }
            
        except Exception as e:
            print(f"Error in advanced analysis: {e}")
            return None
            
    def get_team_metrics(self, team, sport='NHL'):
        """Get real team metrics from API"""
        if sport == 'NHL':
            stats = self.api.get_nhl_team_stats(team)
            if stats:
                return {
                    'win_rate': stats['win_rate'],
                    'points_avg': stats['goals_per_game'],
                    'defense_rating': 100 - (stats['goals_against'] * 10),
                    'power_play': stats['power_play_pct'],
                    'penalty_kill': stats['penalty_kill_pct']
                }
        else:  # NBA
            stats = self.api.get_nba_team_stats(team)
            if stats:
                return {
                    'win_rate': stats['win_rate'],
                    'points_avg': stats['points_per_game'],
                    'defense_rating': 100 - (stats['points_allowed'] / 1.5),
                    'rebounds': stats['rebounds_per_game'],
                    'assists': stats['assists_per_game']
                }
                
        # Fallback to default values if API fails
        return super().get_team_metrics(team)
        
    def calculate_rest_days(self, team):
        """
        Calculate days since last game
        """
        # TODO: Implement real schedule checking
        return 2  # Example value
        
    def get_head_to_head_advantage(self, home_team, away_team):
        """
        Calculate head-to-head advantage based on historical matchups
        """
        # TODO: Implement real head-to-head analysis
        return 0.1  # Example value
        
    def predict_win_probability(self, features):
        """
        Use machine learning model to predict win probability
        """
        # Convert features to array
        X = np.array([[
            features[f] for f in self.features
        ]])
        
        # Make prediction
        try:
            prob = self.model.predict_proba(X)[0][1]
            return round(prob * 100, 2)
        except:
            return 50.0
            
    def calculate_betting_value(self, win_prob, odds):
        """
        Calculate betting value based on Kelly Criterion
        """
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
            
        edge = (win_prob/100 * decimal_odds) - 1
        return round(edge * 100, 2)
        
    def calculate_confidence(self, win_prob, value, features):
        """
        Calculate confidence score based on multiple factors
        """
        base_confidence = win_prob
        
        # Adjust for value
        if value > 10:
            base_confidence += 10
        elif value > 5:
            base_confidence += 5
            
        # Adjust for rest advantage
        rest_advantage = features['home_rest_days'] - features['away_rest_days']
        if abs(rest_advantage) >= 2:
            base_confidence += 5
            
        # Cap confidence at 95%
        return min(95, round(base_confidence))
        
    def get_recommended_bet(self, confidence, value):
        """
        Get recommended bet size based on confidence and value
        """
        if confidence >= 80 and value >= 5:
            return "Strong Bet"
        elif confidence >= 70 and value >= 3:
            return "Medium Bet"
        elif confidence >= 60 and value >= 1:
            return "Small Bet"
        else:
            return "No Bet"
        
    def calculate_schedule_fatigue(self, team, sport):
        """Calculate team's fatigue based on recent schedule"""
        try:
            # Get last 10 games
            games = self.api.get_recent_games(team, sport, limit=10)
            if not games:
                return 0
            
            fatigue_score = 0
            today = datetime.now()
            
            for game in games:
                game_date = datetime.strptime(game['date'], '%Y-%m-%d')
                days_ago = (today - game_date).days
                
                # Recent games have more impact
                if days_ago <= 3:
                    fatigue_score += 3
                elif days_ago <= 5:
                    fatigue_score += 2
                elif days_ago <= 7:
                    fatigue_score += 1
                    
                # Add travel impact
                if game.get('away_game'):
                    fatigue_score += 0.5
                    
                # Back-to-back games
                if days_ago <= 1:
                    fatigue_score += 4
                    
            # Normalize score (0-100)
            return min(100, fatigue_score * 5)
            
        except Exception as e:
            print(f"Error calculating schedule fatigue: {e}")
            return 0
        
    def calculate_enhanced_confidence(self, win_prob, value, features, h2h_stats):
        """Calculate confidence score with advanced metrics"""
        base_confidence = win_prob
        
        # Value adjustment
        if value > 10:
            base_confidence += 10
        elif value > 5:
            base_confidence += 5
            
        # Fatigue impact
        fatigue_diff = features.get('home_fatigue', 0) - features.get('away_fatigue', 0)
        if abs(fatigue_diff) > 20:
            base_confidence += (5 if fatigue_diff < 0 else -5)
            
        # Head-to-head history
        if h2h_stats:
            if h2h_stats['streak'] >= 3:
                base_confidence += 5
            elif h2h_stats['streak'] <= -3:
                base_confidence -= 5
                
        # Recent form
        if features.get('recent_form', 0) > 0.7:
            base_confidence += 5
        elif features.get('recent_form', 0) < 0.3:
            base_confidence -= 5
            
        # Cap confidence
        return min(95, max(5, round(base_confidence)))
 