from typing import Dict, List, Optional
import requests
import time
from datetime import datetime
import logging
from api_config import APIConfig

class OddsAPI:
    def __init__(self):
        self.config = APIConfig()
        self.last_request_time = 0
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Validate API key
        if not self.config.ODDS_API_KEY:
            self.logger.warning("Odds API key not found. Some features will be limited.")
            # Don't raise an error, just log a warning
    
    def _handle_rate_limit(self):
        """Ensure we don't exceed API rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = self.config.get_rate_limit('odds_api')['min_interval']
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make a request to the Odds API."""
        try:
            self._handle_rate_limit()
            
            url = self.config.get_odds_url(endpoint, **kwargs)
            headers = self.config.get_headers('odds')
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to {endpoint}: {str(e)}")
            return None
    
    def get_sports(self) -> List[Dict]:
        """Get list of available sports."""
        response = self._make_request('sports')
        if response:
            return [
                {
                    'key': sport['key'],
                    'group': sport['group'],
                    'title': sport['title'],
                    'active': sport['active']
                }
                for sport in response
                if sport['key'] in self.config.SUPPORTED_SPORTS
            ]
        return []
    
    def get_odds(self, sport: str, regions: str = 'us', 
                markets: str = 'h2h,spreads,totals') -> Optional[Dict]:
        """Get odds for a specific sport."""
        params = {
            'sport': sport,
            'regions': regions,
            'markets': markets
        }
        
        response = self._make_request('odds', **params)
        if response:
            return self._process_odds_response(response)
        return None
    
    def _process_odds_response(self, response: List[Dict]) -> Dict:
        """Process and structure the odds response."""
        processed_odds = {}
        
        for game in response:
            game_key = f"{game['home_team']} vs {game['away_team']}"
            processed_odds[game_key] = {
                'id': game['id'],
                'sport_key': game['sport_key'],
                'commence_time': game['commence_time'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'bookmakers': self._process_bookmakers(game['bookmakers'])
            }
        
        return processed_odds
    
    def _process_bookmakers(self, bookmakers: List[Dict]) -> Dict:
        """Process bookmaker odds data."""
        processed_books = {}
        
        for book in bookmakers:
            processed_books[book['key']] = {
                'title': book['title'],
                'last_update': book['last_update'],
                'markets': self._process_markets(book['markets'])
            }
        
        return processed_books
    
    def _process_markets(self, markets: List[Dict]) -> Dict:
        """Process market odds data."""
        processed_markets = {}
        
        for market in markets:
            processed_markets[market['key']] = {
                'outcomes': {
                    outcome['name']: {
                        'price': outcome.get('price'),
                        'point': outcome.get('point')
                    }
                    for outcome in market['outcomes']
                }
            }
        
        return processed_markets
    
    def get_scores(self, sport: str, daysFrom: int = 1) -> Optional[Dict]:
        """Get scores and game results."""
        params = {
            'sport': sport,
            'daysFrom': daysFrom
        }
        
        response = self._make_request('scores', **params)
        if response:
            return self._process_scores_response(response)
        return None
    
    def _process_scores_response(self, response: List[Dict]) -> Dict:
        """Process and structure the scores response."""
        processed_scores = {}
        
        for game in response:
            game_key = f"{game['home_team']} vs {game['away_team']}"
            processed_scores[game_key] = {
                'id': game['id'],
                'sport_key': game['sport_key'],
                'commence_time': game['commence_time'],
                'completed': game['completed'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'scores': game.get('scores', {}),
                'last_update': game.get('last_update')
            }
        
        return processed_scores
    
    def get_historical_odds(self, sport: str, date: str) -> Optional[Dict]:
        """Get historical odds data for analysis."""
        params = {
            'sport': sport,
            'date': date
        }
        
        response = self._make_request('historical_odds', **params)
        if response:
            return self._process_odds_response(response)
        return None 