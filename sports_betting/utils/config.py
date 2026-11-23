import os
# API Keys and Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")  # Your Odds API key
MYSPORTSFEEDS_API_KEY = os.getenv("MYSPORTSFEEDS_API_KEY", "")  # Add your complete key here
ACTION_NETWORK_KEY = ''  # We can leave this empty for now
WEATHER_API_KEY = ''     # We can leave this empty for now
SPORTS_RADAR_KEY = 'your_sports_radar_key'  # Replace with your Sports Radar key

# API Endpoints
ODDS_API_ENDPOINT = 'https://api.the-odds-api.com/v4/sports'
MYSPORTSFEEDS_API_ENDPOINT = 'https://api.mysportsfeeds.com/v2.1/pull'
ACTION_NETWORK_ENDPOINT = 'https://api.actionnetwork.com/web/v1'
WEATHER_API_ENDPOINT = 'http://api.openweathermap.org/data/2.5/weather'

# Sport IDs
SPORT_IDS = {
    'NBA': 'basketball_nba',
    'NFL': 'americanfootball_nfl',
    'NHL': 'icehockey_nhl',
    'MLB': 'baseball_mlb'
}

# Bookmaker IDs
BOOKMAKERS = [
    'fanduel',
    'draftkings',
    'betmgm',
    'caesars',
    'pointsbet'
]