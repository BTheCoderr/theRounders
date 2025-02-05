import requests
import json
from datetime import datetime

def test_odds_api():
    API_KEY = 'f4b284d121161d41abae2044e2f93ab1'
    SPORT = 'basketball_nba'  # testing with NBA first
    
    print("\nTesting The Odds API")
    print("=" * 50)
    
    # 1. First test the sports endpoint
    base_url = 'https://api.the-odds-api.com/v4'
    
    try:
        # List all sports
        sports_url = f'{base_url}/sports'
        sports_response = requests.get(
            sports_url,
            params={'apiKey': API_KEY}
        )
        
        print(f"\n1. Sports List Request:")
        print(f"URL: {sports_url}")
        print(f"Status: {sports_response.status_code}")
        
        if sports_response.status_code == 200:
            sports = sports_response.json()
            print("\nAvailable Sports:")
            for sport in sports:
                if sport['active']:
                    print(f"- {sport['key']}: {sport['title']} (Active)")
                    
        # 2. Get odds for NBA
        odds_url = f'{base_url}/sports/{SPORT}/odds'
        odds_response = requests.get(
            odds_url,
            params={
                'apiKey': API_KEY,
                'regions': 'us',
                'markets': 'spreads,totals',
                'oddsFormat': 'american'
            }
        )
        
        print(f"\n2. Odds Request for {SPORT}:")
        print(f"URL: {odds_url}")
        print(f"Status: {odds_response.status_code}")
        
        if odds_response.status_code == 200:
            games = odds_response.json()
            print(f"\nFound {len(games)} games")
            
            if games:
                print("\nFirst Game Details:")
                game = games[0]
                print(f"Teams: {game['away_team']} @ {game['home_team']}")
                print(f"Start Time: {game['commence_time']}")
                if 'bookmakers' in game:
                    print(f"Number of bookmakers: {len(game['bookmakers'])}")
                    
        else:
            print(f"Error: {odds_response.text}")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_odds_api() 