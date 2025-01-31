from typing import Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig:
    # API Keys
    ODDS_API_KEY = os.getenv('ODDS_API_KEY')
    SPORTSDATA_API_KEY = os.getenv('SPORTSDATA_API_KEY')
    FOOTBALL_DATA_KEY = os.getenv('FOOTBALL_DATA_KEY', '')  # Soccer data
    
    # Base URLs
    ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
    NBA_API_BASE_URL = "https://stats.nba.com/stats"
    FOOTBALL_DATA_URL = "https://api.football-data.org/v4"
    UFC_STATS_URL = "http://ufcstats.com/statistics"
    UNDERSTAT_BASE_URL = "https://understat.com"
    
    # Endpoints
    ODDS_ENDPOINTS = {
        'sports': '/sports',
        'odds': '/sports/{sport}/odds',
        'scores': '/sports/{sport}/scores',
        'historical_odds': '/sports/{sport}/odds-history'
    }
    
    NBA_ENDPOINTS = {
        'scoreboard': '/scoreboardv2',
        'player_stats': '/leaguedashplayerstats',
        'team_stats': '/leaguedashteamstats',
        'game_stats': '/boxscoretraditionalv2'
    }
    
    SOCCER_ENDPOINTS = {
        'matches': '/matches',
        'teams': '/teams',
        'standings': '/competitions/{competition_id}/standings'
    }
    
    # Rate Limiting Settings
    RATE_LIMITS = {
        'odds_api': {
            'requests_per_month': 500,
            'min_interval': 5  # seconds between requests
        },
        'nba_api': {
            'requests_per_minute': 20,
            'min_interval': 3
        },
        'football_data': {
            'requests_per_minute': 10,
            'min_interval': 6
        },
        'understat': {
            'requests_per_minute': 20,
            'min_interval': 3
        }
    }
    
    # Supported Sports
    SUPPORTED_SPORTS = {
        'NFL': {
            'api_key_required': True,
            'odds_api_key': True,
            'scraping_required': True,
            'endpoints': ['odds', 'scores', 'historical_odds']
        },
        'NBA': {
            'api_key_required': False,
            'odds_api_key': True,
            'scraping_required': False,
            'endpoints': ['odds', 'scores', 'historical_odds', 'player_stats']
        },
        'MLB': {
            'api_key_required': True,
            'odds_api_key': True,
            'scraping_required': True,
            'endpoints': ['odds', 'scores']
        },
        'NHL': {
            'api_key_required': True,
            'odds_api_key': True,
            'scraping_required': True,
            'endpoints': ['odds', 'scores']
        },
        'UFC': {
            'api_key_required': False,
            'odds_api_key': True,
            'scraping_required': True,
            'endpoints': ['odds', 'historical_odds']
        },
        'EPL': {
            'api_key_required': True,
            'odds_api_key': True,
            'scraping_required': True,
            'endpoints': ['odds', 'matches', 'standings']
        }
    }
    
    @classmethod
    def get_odds_url(cls, endpoint: str, **kwargs) -> str:
        """Get full URL for Odds API endpoint."""
        base_endpoint = cls.ODDS_ENDPOINTS[endpoint]
        formatted_endpoint = base_endpoint.format(**kwargs)
        return f"{cls.ODDS_API_BASE_URL}{formatted_endpoint}"
    
    @classmethod
    def get_nba_url(cls, endpoint: str) -> str:
        """Get full URL for NBA API endpoint."""
        return f"{cls.NBA_API_BASE_URL}{cls.NBA_ENDPOINTS[endpoint]}"
    
    @classmethod
    def get_soccer_url(cls, endpoint: str, **kwargs) -> str:
        """Get full URL for Football-Data API endpoint."""
        base_endpoint = cls.SOCCER_ENDPOINTS[endpoint]
        formatted_endpoint = base_endpoint.format(**kwargs)
        return f"{cls.FOOTBALL_DATA_URL}{formatted_endpoint}"
    
    @classmethod
    def get_headers(cls, api_type: str) -> Dict:
        """Get headers for API requests."""
        headers = {
            'User-Agent': 'TheRounders/1.0 (https://github.com/BTheCoderr/theRounders)'
        }
        
        if api_type == 'odds':
            headers['apikey'] = cls.ODDS_API_KEY
        elif api_type == 'football-data':
            headers['X-Auth-Token'] = cls.FOOTBALL_DATA_KEY
        elif api_type == 'nba':
            headers.update({
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            })
        
        return headers
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        return {
            'odds_api': bool(cls.ODDS_API_KEY),
            'sportsdata': bool(cls.SPORTSDATA_API_KEY),
            'football_data': bool(cls.FOOTBALL_DATA_KEY)
        }
    
    @classmethod
    def get_rate_limit(cls, api_type: str) -> Dict:
        """Get rate limit settings for an API."""
        return cls.RATE_LIMITS.get(api_type, {
            'requests_per_minute': 10,
            'min_interval': 6
        }) 