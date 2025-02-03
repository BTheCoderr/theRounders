"""Secure API configuration handler."""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import logging
from functools import wraps
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class APIKeyError(Exception):
    """Custom exception for API key errors."""
    pass

class RateLimitError(Exception):
    """Custom exception for rate limiting."""
    pass

class APIConfig:
    """Secure API configuration handler."""
    
    def __init__(self):
        self._validate_environment()
        # All APIs have 1000 calls quota and 1 QPS limit
        self.rate_limits = {
            'table_tennis': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'nba': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'ncaamb': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'nfl': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'nhl': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'mma': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'tennis': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'mlb': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'ncaafb': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'odds_prematch': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'odds_regular': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'odds_props': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000},
            'odds_futures': {'calls': 0, 'last_reset': time.time(), 'limit': 1000, 'window': 2592000}
        }
        
        # QPS tracking
        self.last_call_time = {}
        self.QPS_LIMIT = 1
        
    def _validate_environment(self):
        """Validate all required API keys are present."""
        required_keys = [
            'SPORTRADAR_API_KEY',
            'ODDS_API_KEY',
            'STREAMLIT_API_KEY'
        ]
        
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        if missing_keys:
            raise APIKeyError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """Check if we're within rate limits for the specified API."""
        now = time.time()
        
        # Check QPS limit
        if api_name in self.last_call_time:
            time_since_last_call = now - self.last_call_time[api_name]
            if time_since_last_call < 1/self.QPS_LIMIT:
                return False
        
        # Update last call time
        self.last_call_time[api_name] = now
        
        rate_info = self.rate_limits[api_name]
        
        # Reset counter if we're in a new window
        if now - rate_info['last_reset'] > rate_info['window']:
            rate_info['calls'] = 0
            rate_info['last_reset'] = now
        
        # Check if we're at the limit
        if rate_info['calls'] >= rate_info['limit']:
            return False
        
        rate_info['calls'] += 1
        return True
    
    def get_api_key(self, api_name: str) -> str:
        """Securely retrieve API key."""
        # Most APIs use SportRadar key
        sportradar_apis = [
            'table_tennis', 'nba', 'ncaamb', 'nfl', 'nhl',
            'mma', 'tennis', 'mlb', 'ncaafb'
        ]
        
        odds_apis = [
            'odds_prematch', 'odds_regular', 'odds_props', 'odds_futures'
        ]
        
        if api_name in sportradar_apis:
            key = os.getenv('SPORTRADAR_API_KEY')
        elif api_name in odds_apis:
            key = os.getenv('ODDS_API_KEY')
        else:
            raise APIKeyError(f"Unknown API: {api_name}")
            
        if not key:
            raise APIKeyError(f"API key not found for {api_name}")
            
        return key
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def make_api_call(self, api_name: str, endpoint: str, method: str = 'GET', **kwargs):
        """Make an API call with retry logic and rate limiting."""
        import requests
        
        if not self._check_rate_limit(api_name):
            raise RateLimitError(f"Rate limit exceeded for {api_name}")
        
        # SportRadar uses api_key parameter, Odds API uses different auth
        if api_name.startswith('odds_'):
            if 'params' not in kwargs:
                kwargs['params'] = {}
            kwargs['params']['apiKey'] = self.get_api_key(api_name)
        else:
            if 'params' not in kwargs:
                kwargs['params'] = {}
            kwargs['params']['api_key'] = self.get_api_key(api_name)
        
        try:
            response = requests.request(
                method=method,
                url=endpoint,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed: {str(e)}")
            raise 