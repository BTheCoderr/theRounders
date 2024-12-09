from .base_collector import BaseDataCollector
from sports_betting.data_collection.odds_api import OddsAPICollector
import pandas as pd
import nfl_data_py as nfl
from loguru import logger
from ..utils.season_utils import get_current_season

class NFLDataCollector(BaseDataCollector):
    def __init__(self):
        super().__init__()
        self.current_season = get_current_season('NFL')
        self.odds_collector = OddsAPICollector()
        
    def get_odds(self) -> pd.DataFrame:
        """Get NFL odds data"""
        try:
            odds_df = self.odds_collector.get_odds(sport='americanfootball_nfl')
            
            if odds_df.empty:
                logger.warning("No NFL odds data found")
                return pd.DataFrame()
                
            # Process the odds data into a cleaner format
            games = []
            for game_id in odds_df['game_id'].unique():
                game_odds = odds_df[odds_df['game_id'] == game_id].iloc[0]
                
                game_data = {
                    'home_team': game_odds['home_team'],
                    'away_team': game_odds['away_team'],
                    'commence_time': game_odds['commence_time']
                }
                
                # Add market data if available
                spreads = odds_df[(odds_df['game_id'] == game_id) & (odds_df['market'] == 'spreads')]
                totals = odds_df[(odds_df['game_id'] == game_id) & (odds_df['market'] == 'totals')]
                moneyline = odds_df[(odds_df['game_id'] == game_id) & (odds_df['market'] == 'h2h')]
                
                if not spreads.empty:
                    game_data['spread'] = spreads[spreads['team'] == game_data['away_team']]['point'].iloc[0]
                    
                if not totals.empty:
                    game_data['total'] = totals[totals['team'] == 'Over']['point'].iloc[0]
                    
                if not moneyline.empty:
                    home_ml = moneyline[moneyline['team'] == game_data['home_team']]['price'].iloc[0]
                    away_ml = moneyline[moneyline['team'] == game_data['away_team']]['price'].iloc[0]
                    game_data['home_ml'] = home_ml
                    game_data['away_ml'] = away_ml
                
                games.append(game_data)
                
            return pd.DataFrame(games)
            
        except Exception as e:
            logger.error(f"Error processing NFL odds data: {str(e)}")
            return pd.DataFrame()

    def _fetch_player_stats(self) -> pd.DataFrame:
        """Fetch player statistics"""
        try:
            weekly = nfl.import_weekly_data([self.current_season])
            
            # Aggregate stats by player using correct column names
            stats = weekly.groupby('player_display_name').agg({
                'recent_team': 'first',
                'position': 'first',
                'passing_yards': 'sum',
                'completions': 'sum',
                'attempts': 'sum',
                'passing_tds': 'sum',
                'interceptions': 'sum'
            }).reset_index()
            
            # Rename columns to match test requirements
            stats = stats.rename(columns={
                'player_display_name': 'player_name',
                'recent_team': 'team',
                'passing_tds': 'touchdowns'
            })
            
            # Calculate completion percentage
            stats['completion_percentage'] = (stats['completions'] / stats['attempts'] * 100)
            
            # Select only required columns
            return stats[['player_name', 'team', 'position', 'passing_yards', 
                         'completion_percentage', 'touchdowns', 'interceptions']]
                         
        except Exception as e:
            logger.error(f"Error fetching player stats: {str(e)}")
            return pd.DataFrame(columns=[
                'player_name', 'team', 'position',
                'passing_yards', 'completion_percentage',
                'touchdowns', 'interceptions'
            ])

    def _fetch_team_stats(self) -> pd.DataFrame:
        """Fetch team statistics"""
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
            params = {
                'season': self.current_season
            }
            # ... rest of method
            
        except Exception as e:
            logger.error(f"Error fetching team stats: {str(e)}")
            return pd.DataFrame(columns=[
                'team_name', 'points_per_game', 'points_allowed',
                'yards_per_game', 'rushing_yards_per_game',
                'passing_yards_per_game', 'third_down_conversion'
            ])

    def _calculate_advanced_metrics(self) -> pd.DataFrame:
        """Calculate advanced metrics"""
        try:
            weekly = nfl.import_weekly_data([self.current_season])
            
            metrics = pd.DataFrame({
                'team': weekly['recent_team'].unique(),
                'dvoa_offense': weekly.groupby('recent_team')['total_yards'].mean(),
                'dvoa_defense': weekly.groupby('recent_team')['yards_allowed'].mean()
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return pd.DataFrame(columns=['dvoa_offense', 'dvoa_defense'])

    def _fetch_betting_trends(self) -> pd.DataFrame:
        """Fetch betting trends"""
        try:
            weekly = nfl.import_weekly_data([self.current_season])
            
            trends = weekly.groupby('recent_team').agg({
                'spread_line': 'mean',
                'total_line': 'mean'
            }).reset_index()
            
            return trends.rename(columns={
                'recent_team': 'team',
                'spread_line': 'spread',
                'total_line': 'total'
            })
            
        except Exception as e:
            logger.error(f"Error fetching betting trends: {str(e)}")
            return pd.DataFrame(columns=['team', 'spread', 'total'])

    def _fetch_injury_data(self) -> pd.DataFrame:
        """Fetch injury data"""
        try:
            weekly = nfl.import_weekly_data([self.current_season])
            
            injuries = weekly[weekly['injury_status'].notna()].groupby('player_display_name').agg({
                'recent_team': 'first',
                'injury_status': 'first'
            }).reset_index()
            
            return injuries.rename(columns={
                'player_display_name': 'player_name',
                'recent_team': 'team'
            })
            
        except Exception as e:
            logger.error(f"Error fetching injuries: {str(e)}")
            return pd.DataFrame(columns=['player_name', 'team', 'injury_status'])

    def _fetch_weather_data(self) -> pd.DataFrame:
        """Fetch weather data"""
        try:
            weekly = nfl.import_weekly_data([self.current_season])
            
            weather = weekly[['game_id', 'weather_temperature', 'weather_wind_mph']].copy()
            return weather.rename(columns={
                'weather_temperature': 'temperature',
                'weather_wind_mph': 'wind_speed'
            })
            
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            return pd.DataFrame(columns=['game_id', 'temperature', 'wind_speed'])

# The issue is we're not properly importing the nfl_data_py package
# Let's verify it's installed and working:

import nfl_data_py as nfl

# Test if we can get basic data
try:
    # Get current season data
    data = nfl.import_weekly_data([2023])
    print("Data retrieved successfully!")
    print("Sample columns:", data.columns.tolist()[:5])
except Exception as e:
    print(f"Error: {str(e)}")