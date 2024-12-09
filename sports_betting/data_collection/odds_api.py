import requests
import pandas as pd
from sports_betting.utils.logging_config import logger

class OddsAPICollector:
    def __init__(self):
        self.api_key = "f4b284d121161d41abae2044e2f93ab1"
        
    def get_odds(self, sport='basketball_nba') -> pd.DataFrame:
        """Get odds from the Odds API"""
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'spreads,totals,h2h',
                'oddsFormat': 'american'
            }
            
            logger.info(f"Fetching odds for {sport}...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Received odds data for {len(data)} games")
            
            return self._parse_odds_response(data)
            
        except Exception as e:
            logger.error(f"Error fetching odds: {str(e)}")
            return pd.DataFrame()

    def _parse_odds_response(self, response_data) -> pd.DataFrame:
        """Parse the odds API response into a DataFrame"""
        if not response_data:
            return pd.DataFrame()
            
        try:
            rows = []
            for game in response_data:
                for bookmaker in game['bookmakers']:
                    for market in bookmaker['markets']:
                        if market['key'] in ['h2h', 'spreads', 'totals']:
                            for outcome in market['outcomes']:
                                rows.append({
                                    'game_id': game['id'],
                                    'sport': game['sport_title'],
                                    'commence_time': game['commence_time'],
                                    'home_team': game['home_team'],
                                    'away_team': game['away_team'],
                                    'bookmaker': bookmaker['title'],
                                    'market': market['key'],
                                    'team': outcome['name'],
                                    'price': outcome['price'],
                                    'point': outcome.get('point', None)
                                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.error(f"Error parsing odds response: {str(e)}")
            return pd.DataFrame()