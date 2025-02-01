import numpy as np
import pandas as pd
from datetime import datetime
import requests
from nba_api.stats.endpoints import leaguegamefinder
import logging

class BettingSystem:
    def __init__(self, massey_ratings, api_key=None):
        self.massey_ratings = massey_ratings
        self.api_key = api_key
        self.clv_analyzer = CLVAnalyzer()
        self.logger = logging.getLogger(__name__)
        
    def predict_spread(self, home_team, away_team, is_home=True):
        """Predict spread using Massey ratings."""
        try:
            home_rating = self.massey_ratings.get(home_team, 0)
            away_rating = self.massey_ratings.get(away_team, 0)
            spread = home_rating - away_rating + (3.5 if is_home else -3.5)  # Add home court advantage
            return spread
        except Exception as e:
            self.logger.error(f"Error predicting spread: {str(e)}")
            return None
            
    def hybrid_prediction(self, home_elo, away_elo, massey_spread):
        """Combine Massey and ELO predictions."""
        try:
            # ELO win probability
            elo_diff = home_elo - away_elo
            elo_win_prob = 1 / (1 + 10 ** (-elo_diff / 400))
            
            # Massey spread to win probability
            massey_win_prob = 1 / (1 + np.exp(-0.15 * massey_spread))
            
            # Weighted average
            return 0.6 * massey_win_prob + 0.4 * elo_win_prob
        except Exception as e:
            self.logger.error(f"Error calculating hybrid prediction: {str(e)}")
            return None
    
    def get_best_odds(self, team):
        """Get best available odds for a team."""
        if not self.api_key:
            return None, None
            
        try:
            response = requests.get(
                "https://api.the-odds-api.com/v4/sports/basketball_nba/odds",
                params={
                    "apiKey": self.api_key,
                    "regions": "us",
                    "markets": "spreads"
                }
            )
            all_odds = response.json()
            team_odds = [o for o in all_odds if team in o['home_team'] or team in o['away_team']]
            if team_odds:
                best = min(team_odds, key=lambda x: x['bookmakers'][0]['spread'])
                return best['bookmakers'][0]['spread'], best['bookmakers'][0]['price']
            return None, None
        except Exception as e:
            self.logger.error(f"Error fetching odds: {str(e)}")
            return None, None
    
    def should_bet(self, massey_edge, line_movement, sharp_percent):
        """Determine if bet meets Walters criteria."""
        return (
            massey_edge > 0.03 and      # 3% edge
            line_movement > 0.5 and     # Line moved 0.5 points in favor
            sharp_percent > 65          # Sharp money threshold
        )
    
    def backtest_massey(self, season='2023-24'):
        """Backtest Massey ratings against historical spreads."""
        try:
            # Fetch historical data
            gamefinder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                league_id_nullable='00'
            )
            games = gamefinder.get_data_frames()[0]
            
            # Process games for backtesting
            results = []
            for _, game in games.iterrows():
                pred_spread = self.predict_spread(game['TEAM_NAME_HOME'], game['TEAM_NAME_AWAY'])
                if pred_spread is not None:
                    results.append({
                        'date': game['GAME_DATE'],
                        'home_team': game['TEAM_NAME_HOME'],
                        'away_team': game['TEAM_NAME_AWAY'],
                        'pred_spread': pred_spread,
                        'actual_spread': game['PTS_HOME'] - game['PTS_AWAY']
                    })
            
            results_df = pd.DataFrame(results)
            accuracy = (
                (results_df['pred_spread'] > 0) == (results_df['actual_spread'] > 0)
            ).mean()
            
            return accuracy, results_df
        except Exception as e:
            self.logger.error(f"Error in backtest: {str(e)}")
            return None, None

class CLVAnalyzer:
    def __init__(self):
        self.bets = []
        
    def add_bet(self, pred_spread, closing_spread):
        """Add a bet to track CLV."""
        self.bets.append(pred_spread - closing_spread)
        
    def clv_score(self):
        """Calculate average CLV across all bets."""
        if not self.bets:
            return 0.0
        return np.mean(self.bets)
        
    def get_stats(self):
        """Get detailed CLV statistics."""
        if not self.bets:
            return {
                'avg_clv': 0.0,
                'positive_clv_rate': 0.0,
                'total_bets': 0
            }
            
        return {
            'avg_clv': np.mean(self.bets),
            'positive_clv_rate': (np.array(self.bets) > 0).mean(),
            'total_bets': len(self.bets)
        } 