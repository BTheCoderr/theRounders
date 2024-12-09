from sports_betting.data_collection.nfl import NFLDataCollector
from sports_betting.data_collection.ncaab import NCAABDataCollector
from sports_betting.data_collection.ncaaf import NCAAFDataCollector
from sports_betting.data_collection.nba import NBADataCollector
from sports_betting.data_collection.nhl import NHLDataCollector
from datetime import datetime
import json
import requests

class ResultsTracker:
    def __init__(self):
        self.picks_file = 'picks_history.json'
        self.results_file = 'picks_results.json'
        self.odds_api_key = 'f4b284d121161d41abae2044e2f93ab1'
        self.collectors = {
            'NFL': NFLDataCollector(),
            'NBA': NBADataCollector(),
            'NHL': NHLDataCollector(),
            'NCAAB': NCAABDataCollector(),
            'NCAAF': NCAAFDataCollector()
        }
        
    def fetch_scores(self, sport):
        """Fetch scores using existing sport collectors"""
        try:
            if sport == 'NBA':
                url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
            elif sport == 'NHL':
                url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
            elif sport == 'NFL':
                url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            elif sport == 'NCAAB':
                url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
            elif sport == 'NCAAF':
                url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
            
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Error fetching {sport} scores: {str(e)}")
            return None

    def check_pick_result(self, pick, scores):
        """Check if our pick won based on actual scores"""
        try:
            if not scores:
                return 'Pending'
                
            for event in scores.get('events', []):
                competition = event['competitions'][0]
                home_team = competition['competitors'][0]['team']['name']
                away_team = competition['competitors'][1]['team']['name']
                
                # Match the game
                if f"{away_team} @ {home_team}" == pick['game']:
                    if competition['status']['type']['completed']:
                        home_score = int(competition['competitors'][0]['score'])
                        away_score = int(competition['competitors'][1]['score'])
                        
                        # Handle different pick types
                        if pick['pick_type'] == 'Spread':
                            spread = float(pick.get('spread', 0))
                            if pick['pick'] == home_team:
                                return 'Win' if (home_score + spread) > away_score else 'Loss'
                            else:
                                return 'Win' if (away_score + spread) > home_score else 'Loss'
                                
                        elif pick['pick_type'] == 'Total':
                            total = float(pick.get('total', 0))
                            actual_total = home_score + away_score
                            if 'OVER' in pick['pick']:
                                return 'Win' if actual_total > total else 'Loss'
                            else:
                                return 'Win' if actual_total < total else 'Loss'
                                
                        elif pick['pick_type'] == 'Moneyline':
                            winner = home_team if home_score > away_score else away_team
                            return 'Win' if pick['pick'] == winner else 'Loss'
                    
                    return 'Pending'  # Game not completed
            
            return 'Pending'  # Game not found
            
        except Exception as e:
            print(f"Error checking pick result: {str(e)}")
            return 'Error'

    def update_results(self):
        print("\n=== CHECKING RESULTS FOR PREVIOUS PICKS ===")
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
        print("=" * 60)
        
        try:
            with open(self.picks_file, 'r') as f:
                picks = [json.loads(line) for line in f]
            
            updated_picks = []
            for pick in picks:
                if pick['result'] == 'Pending':
                    scores = self.fetch_scores(pick['sport'])
                    pick['result'] = self.check_pick_result(pick, scores)
                updated_picks.append(pick)
            
            # Save updated results
            with open(self.results_file, 'w') as f:
                for pick in updated_picks:
                    json.dump(pick, f)
                    f.write('\n')
                    
            self.show_results_summary(updated_picks)
                    
        except Exception as e:
            print(f"Error updating results: {str(e)}")

    def show_results_summary(self, picks):
        print("\n=== PICKS RESULTS SUMMARY ===")
        
        # Overall results
        wins = sum(1 for pick in picks if pick['result'] == 'Win')
        losses = sum(1 for pick in picks if pick['result'] == 'Loss')
        pushes = sum(1 for pick in picks if pick['result'] == 'Push')
        pending = sum(1 for pick in picks if pick['result'] == 'Pending')
        
        if wins + losses > 0:
            win_pct = (wins / (wins + losses)) * 100
        else:
            win_pct = 0
            
        print(f"\nOverall Record: {wins}-{losses}-{pushes} ({win_pct:.1f}%)")
        print(f"Pending Picks: {pending}")
        
        # Results by sport
        sports = set(pick['sport'] for pick in picks)
        for sport in sports:
            sport_picks = [pick for pick in picks if pick['sport'] == sport]
            sport_wins = sum(1 for pick in sport_picks if pick['result'] == 'Win')
            sport_losses = sum(1 for pick in sport_picks if pick['result'] == 'Loss')
            sport_pushes = sum(1 for pick in sport_picks if pick['result'] == 'Push')
            
            if sport_wins + sport_losses > 0:
                sport_win_pct = (sport_wins / (sport_wins + sport_losses)) * 100
            else:
                sport_win_pct = 0
                
            print(f"\n{sport}: {sport_wins}-{sport_losses}-{sport_pushes} ({sport_win_pct:.1f}%)")
        
        print("\n" + "=" * 60)

def main():
    tracker = ResultsTracker()
    tracker.update_results()

if __name__ == "__main__":
    main() 