from .api_clients import OddsAPIClient
from nba import NBADataCollector
from nfl import NFLDataCollector
from nhl import NHLDataCollector

class DataCollector:
    def __init__(self):
        self.odds_client = OddsAPIClient()
        self.nba_collector = NBADataCollector()
        self.nfl_collector = NFLDataCollector()
        self.nhl_collector = NHLDataCollector()
        
    def collect_all_data(self, sport='NBA'):
        """Collect all necessary data for analysis"""
        
        # Get odds data
        odds_data = self.odds_client.get_odds(sport=sport)
        
        # Get public betting data
        public_betting = self.action_client.get_public_betting(sport=sport)
        
        # For outdoor sports, get weather data
        weather_data = None
        if sport in ['NFL', 'MLB']:
            weather_data = self._collect_weather_for_games(odds_data)
            
        return {
            'odds_data': odds_data,
            'public_betting': public_betting,
            'weather_data': weather_data
        }
        
    def _collect_weather_for_games(self, odds_data):
        """Collect weather data for each game location"""
        weather_data = {}
        
        for _, game in odds_data.iterrows():
            city = self._get_city_for_team(game['home_team'])
            if city:
                weather_data[game['game_id']] = self.weather_client.get_weather(city)
                
        return weather_data
        
    def _get_city_for_team(self, team_name):
        """Get city name for a team"""
        # This would be implemented with a mapping of team names to cities
        # Example: return TEAM_CITIES.get(team_name)
        return None