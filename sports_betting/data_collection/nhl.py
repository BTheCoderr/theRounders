from .base_collector import BaseDataCollector
import pandas as pd
import requests
from loguru import logger
from ..utils.season_utils import get_current_season
from sports_betting.data_collection.odds_api import OddsAPICollector
from sports_betting.utils.logging_config import logger

class NHLDataCollector(BaseDataCollector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.nhle.com/stats/rest/en"
        self.current_season = get_current_season('NHL')
        self.odds_collector = OddsAPICollector()

    def _fetch_team_stats(self) -> pd.DataFrame:
        """Fetch team statistics"""
        try:
            response = requests.get(f"{self.base_url}/team")
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}")
                
            data = response.json()
            teams_data = []
            for team in data.get('data', []):
                teams_data.append({
                    'team_name': team.get('name', ''),
                    'team_id': team.get('id', 0),
                    'division': team.get('divisionName', ''),
                    'conference': team.get('conferenceName', ''),
                    'games_played': team.get('gamesPlayed', 0),
                    'wins': team.get('wins', 0),
                    'losses': team.get('losses', 0),
                    'goals_per_game': team.get('goalsForPerGame', 0.0),
                    'goals_against_per_game': team.get('goalsAgainstPerGame', 0.0)
                })
            
            return pd.DataFrame(teams_data)
            
        except Exception as e:
            logger.error(f"Error fetching NHL team stats: {str(e)}")
            return pd.DataFrame(columns=[
                'team_name', 'team_id', 'division', 'conference',
                'games_played', 'wins', 'losses',
                'goals_per_game', 'goals_against_per_game'
            ])

    def _fetch_player_stats(self) -> pd.DataFrame:
        """Fetch player statistics"""
        try:
            # Use the NHL stats API with correct endpoint
            url = "https://api-web.nhle.com/v1/skater-stats-leaders/current"
            
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://www.nhl.com',
                'Referer': 'https://www.nhl.com/stats/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Debug logging
            logger.debug(f"API Response Status: {response.status_code}")
            logger.debug(f"API Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                logger.error(f"NHL API returned status code {response.status_code}")
                logger.error(f"Response content: {response.text[:200]}")
                raise Exception(f"API returned status code {response.status_code}")
            
            data = response.json()
            player_stats = []
            
            # Parse the points leaders
            for player in data.get('points', []):
                player_stats.append({
                    'player_name': player.get('fullName', ''),
                    'team': player.get('teamAbbrev', ''),
                    'position': player.get('positionCode', ''),
                    'games_played': int(player.get('gamesPlayed', 0)),
                    'goals': int(player.get('goals', 0)),
                    'assists': int(player.get('assists', 0)),
                    'points': int(player.get('points', 0))
                })
            
            df = pd.DataFrame(player_stats)
            if len(df) == 0:
                logger.warning("No player data returned from NHL API")
                logger.debug(f"Raw API response: {data}")
            else:
                logger.info(f"Successfully fetched {len(df)} player records")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching NHL player stats: {str(e)}")
            logger.exception("Full traceback:")
            return pd.DataFrame(columns=[
                'player_name', 'team', 'position',
                'games_played', 'goals', 'assists', 'points'
            ])

    def _fetch_game_data(self) -> pd.DataFrame:
        """Fetch real game data"""
        try:
            # Use the official NHL API
            url = "https://api-web.nhle.com/v1/schedule/now"
            response = requests.get(url)
            
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}")
            
            data = response.json()
            games_data = []
            
            for game in data.get('gameWeek', [{}])[0].get('games', []):
                games_data.append({
                    'game_id': game.get('id', ''),
                    'home_team': game.get('homeTeam', {}).get('abbrev', ''),
                    'away_team': game.get('awayTeam', {}).get('abbrev', ''),
                    'home_score': game.get('homeTeam', {}).get('score', 0),
                    'away_score': game.get('awayTeam', {}).get('score', 0),
                    'date': game.get('gameDate', '')
                })
            
            return pd.DataFrame(games_data)
            
        except Exception as e:
            logger.error(f"Error fetching NHL game data: {str(e)}")
            return pd.DataFrame(columns=[
                'game_id', 'home_team', 'away_team',
                'home_score', 'away_score', 'date'
            ])

    def _fetch_betting_odds(self) -> pd.DataFrame:
        """Fetch betting odds from external source"""
        try:
            # TODO: Implement with actual odds API
            # For now, return empty DataFrame with expected structure
            return pd.DataFrame(columns=[
                'game_id', 'home_team', 'away_team',
                'home_moneyline', 'away_moneyline',
                'over_under', 'home_spread', 'away_spread'
            ])
            
        except Exception as e:
            logger.error(f"Error fetching NHL betting odds: {str(e)}")
            return pd.DataFrame()

    def _fetch_weather_data(self) -> pd.DataFrame:
        """Fetch weather data (not applicable for NHL - indoor sport)"""
        # NHL games are indoor, so weather isn't relevant
        return pd.DataFrame(columns=['game_id', 'temperature', 'conditions'])

    def _calculate_advanced_metrics(self) -> pd.DataFrame:
        """Calculate advanced metrics for NHL teams"""
        try:
            team_stats = self._fetch_team_stats()
            
            # Calculate advanced metrics
            metrics = pd.DataFrame({
                'team_name': team_stats['team_name'],
                'goals_differential': team_stats['goals_per_game'] - team_stats['goals_against_per_game'],
                'win_percentage': team_stats['wins'] / (team_stats['wins'] + team_stats['losses'])
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating NHL advanced metrics: {str(e)}")
            return pd.DataFrame(columns=['team_name', 'goals_differential', 'win_percentage'])

    def _fetch_betting_trends(self) -> pd.DataFrame:
        """Fetch betting trends for NHL games"""
        try:
            # Mock data for betting trends
            return pd.DataFrame(columns=['team', 'spread', 'over_under', 'moneyline'])
            
        except Exception as e:
            logger.error(f"Error fetching NHL betting trends: {str(e)}")
            return pd.DataFrame(columns=['team', 'spread', 'over_under', 'moneyline'])

    def _fetch_injury_data(self) -> pd.DataFrame:
        """Fetch NHL injury data"""
        try:
            # Mock injury data until we have a reliable source
            return pd.DataFrame(columns=['player_name', 'team', 'injury_status', 'expected_return'])
            
        except Exception as e:
            logger.error(f"Error fetching NHL injury data: {str(e)}")
            return pd.DataFrame(columns=['player_name', 'team', 'injury_status', 'expected_return'])

    def get_game_data(self) -> pd.DataFrame:
        """Get game data"""
        return self._fetch_game_data()

    def get_betting_odds(self) -> pd.DataFrame:
        """Get betting odds"""
        return self._fetch_betting_odds()

    def get_odds(self) -> pd.DataFrame:
        """Get NHL odds data"""
        try:
            odds_df = self.odds_collector.get_odds(sport='icehockey_nhl')
            
            if odds_df.empty:
                logger.warning("No NHL odds data found")
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
            logger.error(f"Error processing NHL odds data: {str(e)}")
            return pd.DataFrame()

    def get_team_stats(self) -> pd.DataFrame:
        """Get NHL team statistics"""
        # Placeholder for team stats - implement real data collection
        return pd.DataFrame({
            'team_name': ['Sample Team 1', 'Sample Team 2'],
            'rating': [100.0, 95.0],
            'point_diff': [1.5, -1.5],
            'goals_per_game': [3.2, 2.8],
            'goals_against_per_game': [2.5, 3.0]
        })