import requests
from datetime import datetime
from .stadium_data import NFL_STADIUMS, COLLEGE_STADIUMS
import logging

logger = logging.getLogger(__name__)

class WeatherAnalysis:
    def __init__(self):
        self.weather_api_key = "2Sa999LZ1SSJQvcMxFYMUAcMMfJ8QaDT"
        self.base_url = "https://api.tomorrow.io/v4/weather/forecast"
        
    def get_stadium_info(self, team_name, league='NFL'):
        """Get stadium information for a team"""
        stadiums = NFL_STADIUMS if league == 'NFL' else COLLEGE_STADIUMS
        return stadiums.get(team_name)
        
    def get_game_weather(self, home_team, game_time, league='NFL'):
        """Fetch weather data for outdoor games"""
        try:
            stadium = self.get_stadium_info(home_team, league)
            
            if not stadium:
                print(f"Stadium not found for {home_team}")
                return None
                
            if stadium['type'] == 'indoor':
                return {
                    'indoor': True,
                    'temperature': 72,
                    'wind_mph': 0,
                    'precipitation_mm': 0,
                    'humidity': 50
                }
                
            params = {
                'location': stadium['location'],
                'apikey': self.weather_api_key,
                'units': 'imperial'
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'timelines' in data:
                daily = data['timelines']['daily'][0]['values']
                temp_f = daily.get('temperatureMax', 0)
                
                if temp_f < 10:
                    temp_f = (temp_f * 9/5) + 32
                    
                return {
                    'indoor': False,
                    'temperature': round(temp_f, 1),
                    'wind_mph': daily.get('windSpeedAvg', 0),
                    'precipitation_mm': daily.get('precipitationIntensityAvg', 0),
                    'humidity': daily.get('humidityAvg', 0)
                }
                
            return None
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            logger.debug(f"Weather data received: {data}")
            return None
            
    def analyze_weather_impact(self, weather_data, sport):
        """Analyze weather impact on game"""
        if not weather_data or weather_data.get('indoor', False):
            return 0
            
        impact_score = 0
        
        if sport in ['NFL', 'NCAAF']:
            # Temperature impact
            if weather_data['temperature'] < 32:
                impact_score -= 10  # Cold weather
            elif weather_data['temperature'] > 85:
                impact_score -= 5   # Hot weather
                
            # Wind impact (affects passing game)
            if weather_data['wind_mph'] > 15:
                impact_score -= 15
            elif weather_data['wind_mph'] > 20:
                impact_score -= 25
                
            # Rain/Snow impact
            if weather_data['precipitation_mm'] > 5:
                impact_score -= 20
                
        return impact_score