import requests
from utils.config import WEATHER_API_KEY

class WeatherDataCollector:
    def __init__(self):
        self.weather_api_key = WEATHER_API_KEY
    
    def get_weather(self, location):
        """Get current weather data for a location"""
        url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
