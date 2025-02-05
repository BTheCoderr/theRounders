import json
import requests
from datetime import datetime

class ResultsUpdater:
    def __init__(self):
        self.api_key = 'YOUR_API_KEY'  # If needed for sports data API
        self.picks_file = 'picks_history.json'

    def load_picks(self):
        try:
            with open(self.picks_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"No picks file found at {self.picks_file}")
            return []

    def save_picks(self, picks):
        with open(self.picks_file, 'w') as f:
            json.dump(picks, f, indent=4)

    def update_pending_results(self):
        picks = self.load_picks()
        updated_count = 0

        for pick in picks:
            if pick['result'] == 'Pending':
                # For now, we'll simulate results
                # In production, you'd fetch real results from an API
                pick['result'] = self.get_game_result(pick)
                pick['odds'] = 1.91  # Default odds
                pick['bet_amount'] = 100  # Default bet amount
                updated_count += 1

        self.save_picks(picks)
        print(f"Updated {updated_count} pending results")
        return picks

    def get_game_result(self, pick):
        """
        Fetch actual game result from The Odds API
        """
        try:
            # Construct the API endpoint
            url = f"https://api.the-odds-api.com/v4/sports/{pick['sport'].lower()}/scores"
            params = {
                'apiKey': self.api_key,
                'date': pick['date']
            }
            
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse the response
            games = response.json()
            for game in games:
                if pick['game'] in game['teams']:
                    # Determine the result based on the score
                    if game['scores']['home'] > game['scores']['away']:
                        return 'Won' if pick['pick'] == game['home_team'] else 'Lost'
                    else:
                        return 'Won' if pick['pick'] == game['away_team'] else 'Lost'
            
            return 'Pending'  # If no result found, keep it pending
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game result: {e}")
            return 'Pending'

    def fetch_new_results(self):
        """
        Fetch new results from sports data API
        """
        picks = self.load_picks()
        pending_picks = [pick for pick in picks if pick['result'] == 'Pending']
        
        for pick in pending_picks:
            result = self.get_game_result(pick)
            if result != 'Pending':
                pick['result'] = result
                pick['odds'] = 1.91  # Default odds
                pick['bet_amount'] = 100  # Default bet amount
                print(f"Updated result for {pick['game']}: {result}")

        self.save_picks(picks)
        return picks

def main():
    updater = ResultsUpdater()
    print("Updating existing pending results...")
    updater.update_pending_results()
    print("\nFetching new results...")
    updater.fetch_new_results()

if __name__ == "__main__":
    main() 