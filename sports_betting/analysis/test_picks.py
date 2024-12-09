from datetime import datetime
from sports_betting.analysis.select_picks import get_todays_picks

def test_picks():
    print("\nTesting Betting Picks with Weather Analysis")
    print("=" * 50)
    
    # Sample games for testing
    sample_games = [
        {
            'home_team': 'Buffalo Bills',
            'away_team': 'New England Patriots',
            'game_time': datetime.now(),
            'odds': {'spread': -3.5, 'total': 44.5}
        },
        {
            'home_team': 'Green Bay Packers',
            'away_team': 'Chicago Bears',
            'game_time': datetime.now(),
            'odds': {'spread': -2.5, 'total': 42.5}
        }
    ]
    
    get_todays_picks()

if __name__ == "__main__":
    test_picks() 