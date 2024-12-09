import requests
import pandas as pd
from datetime import datetime, timedelta
from sports_betting.utils.config import *

class OddsAPIClient:
    def __init__(self):
        self.api_key = ODDS_API_KEY
        self.base_url = ODDS_API_ENDPOINT
        
    def get_odds(self, sport='NBA', market='spreads'):
        """Get current odds for a sport"""
        sport_id = SPORT_IDS.get(sport.upper())
        if not sport_id:
            raise ValueError(f"Sport {sport} not supported")
            
        url = f"{self.base_url}/{sport_id}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': market,
            'bookmakers': ','.join(BOOKMAKERS)
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return self._parse_odds_response(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error fetching odds: {e}")
            return None
            
    def _parse_odds_response(self, data):
        """Parse odds API response into DataFrame"""
        odds_list = []
        
        for game in data:
            game_id = game['id']
            home_team = game['home_team']
            away_team = game['away_team']
            commence_time = game['commence_time']
            
            for bookmaker in game['bookmakers']:
                for market in bookmaker['markets']:
                    if market['key'] == 'spreads':
                        for outcome in market['outcomes']:
                            odds_list.append({
                                'game_id': game_id,
                                'timestamp': datetime.now(),
                                'home_team': home_team,
                                'away_team': away_team,
                                'commence_time': commence_time,
                                'bookmaker': bookmaker['key'],
                                'team': outcome['name'],
                                'spread': float(outcome['point']),
                                'price': outcome['price']
                            })
        
        return pd.DataFrame(odds_list)

class ActionNetworkClient:
    def __init__(self):
        self.api_key = ACTION_NETWORK_KEY
        self.base_url = ACTION_NETWORK_ENDPOINT
        
    def get_public_betting(self, sport='NBA'):
        """Get public betting percentages"""
        url = f"{self.base_url}/games"
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        params = {
            'sport': sport.lower(),
            'include': 'betting_percentages'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return self._parse_betting_response(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error fetching public betting data: {e}")
            return None
            
    def _parse_betting_response(self, data):
        """Parse public betting data into DataFrame"""
        betting_list = []
        
        for game in data['games']:
            betting_list.append({
                'game_id': game['id'],
                'timestamp': datetime.now(),
                'home_team': game['home_team']['name'],
                'away_team': game['away_team']['name'],
                'spread_bet_home': game.get('betting_percentages', {}).get('spread_home', 50),
                'spread_bet_away': game.get('betting_percentages', {}).get('spread_away', 50),
                'money_bet_home': game.get('betting_percentages', {}).get('money_home', 50),
                'money_bet_away': game.get('betting_percentages', {}).get('money_away', 50)
            })
            
        return pd.DataFrame(betting_list)

class WeatherAPIClient:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.base_url = WEATHER_API_ENDPOINT
        
    def get_weather(self, city):
        """Get weather data for a city"""
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'imperial'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return self._parse_weather_response(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
            
    def _parse_weather_response(self, data):
        """Parse weather data into DataFrame"""
        return {
            'temperature': data['main']['temp'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind']['deg'],
            'precipitation': data.get('rain', {}).get('1h', 0),
            'humidity': data['main']['humidity']
        }