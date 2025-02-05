from typing import Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig:
    def __init__(self):
        # Primary Odds APIs
        self.ODDS_API_KEY = os.getenv('ODDS_API_KEY')
        self.ODDSAPI_KEY = os.getenv('ODDSAPI_KEY')
        
        # Sport-Specific APIs
        self.FOOTBALL_DATA_KEY = os.getenv('FOOTBALL_DATA_KEY')
        
        # Base URLs
        self.ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
        self.ODDSAPI_BASE_URL = "https://api.oddsapi.io/v1"
        self.FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"
        
        # Sport-Specific Base URLs
        self.NBA_STATS_BASE_URL = "https://stats.nba.com/stats"
        self.MLB_STATS_BASE_URL = "https://statsapi.mlb.com/api/v1"
        self.NHL_STATS_BASE_URL = "https://statsapi.web.nhl.com/api/v1"
        
        # Supported sports with their API identifiers
        self.SUPPORTED_SPORTS = {
            "NFL": {
                "odds_api": "americanfootball_nfl",
                "oddsapi": "american-football/nfl",
                "espn": "nfl"
            },
            "NBA": {
                "odds_api": "basketball_nba",
                "oddsapi": "basketball/nba",
                "stats": {
                    "scoreboard": "scoreBoard/v2",
                    "player_stats": "leaguedashplayerstats",
                    "team_stats": "leaguedashteamstats",
                    "game_stats": "boxscoretraditionalv2"
                }
            },
            "MLB": {
                "odds_api": "baseball_mlb",
                "oddsapi": "baseball/mlb",
                "stats": {
                    "schedule": "schedule",
                    "game": "game",
                    "standings": "standings",
                    "stats": "stats"
                }
            },
            "NHL": {
                "odds_api": "icehockey_nhl",
                "oddsapi": "ice-hockey/nhl",
                "stats": {
                    "schedule": "schedule",
                    "game": "game",
                    "standings": "standings",
                    "stats": "stats"
                }
            },
            "UFC/MMA": {
                "odds_api": "mma_mixed_martial_arts",
                "oddsapi": "mma"
            },
            "EPL": {
                "odds_api": "soccer_epl",
                "oddsapi": "soccer/epl",
                "football_data": "PL"
            },
            "Champions League": {
                "odds_api": "soccer_uefa_champs_league",
                "oddsapi": "soccer/champions-league",
                "football_data": "CL"
            }
        }
        
        # Scraping endpoints
        self.SCRAPING_ENDPOINTS = {
            "UFC": "http://ufcstats.com/statistics",
            "Understat": "https://understat.com/match",
            "ESPN": {
                "NFL": "https://www.espn.com/nfl/scoreboard",
                "NBA": "https://www.espn.com/nba/scoreboard",
                "MLB": "https://www.espn.com/mlb/scoreboard",
                "NHL": "https://www.espn.com/nhl/scoreboard"
            }
        }
        
        # Sport-specific headers
        self.NBA_HEADERS = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "stats.nba.com",
            "Origin": "https://www.nba.com",
            "Referer": "https://www.nba.com/",
            "User-Agent": os.getenv('USER_AGENT')
        }
        
        # Rate limits
        self.RATE_LIMITS = {
            "odds_api": {
                "requests_per_minute": int(os.getenv('ODDS_API_REQUESTS_PER_MINUTE', 3)),
                "min_interval": 20,  # seconds
                "daily_limit": 500
            },
            "oddsapi": {
                "requests_per_minute": int(os.getenv('ODDSAPI_REQUESTS_PER_MINUTE', 100)),
                "min_interval": 1,  # seconds
                "daily_limit": 100
            },
            "football_data": {
                "requests_per_minute": int(os.getenv('FOOTBALL_DATA_REQUESTS_PER_MINUTE', 10)),
                "min_interval": 6  # seconds
            },
            "nba_stats": {
                "min_interval": int(os.getenv('NBA_STATS_DELAY', 3))
            },
            "mlb_stats": {
                "min_interval": int(os.getenv('MLB_STATS_DELAY', 2))
            },
            "nhl_stats": {
                "min_interval": int(os.getenv('NHL_STATS_DELAY', 2))
            },
            "espn": {
                "min_interval": 5  # seconds
            }
        }
        
        # Sport IDs for ESPN
        self.ESPN_SPORT_IDS = {
            'NFL': 'nfl',
            'NCAAF': 'college-football',
            'NCAAB': 'mens-college-basketball',
            'NBA': 'nba',
            'MLB': 'mlb',
            'NHL': 'nhl'
        }
    
    def get_api_headers(self, api_name: str) -> Dict:
        """Get headers for specific API requests."""
        headers = {
            "User-Agent": os.getenv('USER_AGENT')
        }
        
        if api_name == "odds_api":
            headers["apiKey"] = self.ODDS_API_KEY
        elif api_name == "oddsapi":
            headers["X-API-Key"] = self.ODDSAPI_KEY
        elif api_name == "football_data":
            headers["X-Auth-Token"] = self.FOOTBALL_DATA_KEY
        elif api_name == "nba_stats":
            headers.update(self.NBA_HEADERS)
        elif api_name == "espn":
            headers.update({
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            })
        
        return headers
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate all API keys are present and well-formed."""
        return {
            "The Odds API": bool(self.ODDS_API_KEY and len(self.ODDS_API_KEY) > 20),
            "OddsAPI": bool(self.ODDSAPI_KEY and len(self.ODDSAPI_KEY) > 20),
            "Football-Data.org": bool(self.FOOTBALL_DATA_KEY and len(self.FOOTBALL_DATA_KEY) > 20)
        }
    
    def get_sport_endpoints(self, sport: str, api: str = "odds_api") -> Dict:
        """Get endpoints for a specific sport from a specific API."""
        if sport not in self.SUPPORTED_SPORTS:
            return None
            
        sport_config = self.SUPPORTED_SPORTS[sport]
        if api not in sport_config:
            return None
            
        if api in ["odds_api", "oddsapi"]:
            base_url = getattr(self, f"{api.upper()}_BASE_URL")
            sport_id = sport_config[api]
            return {
                "odds": f"{base_url}/sports/{sport_id}/odds",
                "scores": f"{base_url}/sports/{sport_id}/scores"
            }
        elif api == "stats":
            if sport == "NBA":
                base_url = self.NBA_STATS_BASE_URL
            elif sport == "MLB":
                base_url = self.MLB_STATS_BASE_URL
            elif sport == "NHL":
                base_url = self.NHL_STATS_BASE_URL
            else:
                return None
                
            return {endpoint: f"{base_url}/{path}" 
                    for endpoint, path in sport_config["stats"].items()}
        elif api == "football_data":
            base_url = self.FOOTBALL_DATA_BASE_URL
            competition_id = sport_config[api]
            return {
                "matches": f"{base_url}/competitions/{competition_id}/matches",
                "standings": f"{base_url}/competitions/{competition_id}/standings"
            }
            
        return None

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
    def get_rate_limit(cls, api_type: str) -> Dict:
        """Get rate limit settings for an API."""
        return cls.RATE_LIMITS.get(api_type, {
            'requests_per_minute': 10,
            'min_interval': 6
        }) 