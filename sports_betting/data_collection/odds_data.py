import requests
import pandas as pd
from utils.config import ODDS_API_KEY

class OddsCollector:
    def __init__(self):
        self.odds_api_key = ODDS_API_KEY
    
    def get_current_odds(self, sport='basketball_nba'):
        """Get current odds from The Odds API"""
        url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds'
        params = {
            'apiKey': self.odds_api_key,
            'regions': 'us',
            'markets': 'spreads,totals,h2h'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return None