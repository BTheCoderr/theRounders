from sports_betting.data_collection.nfl import NFLDataCollector
from sports_betting.data_collection.ncaab import NCAABDataCollector
from sports_betting.data_collection.ncaaf import NCAAFDataCollector
from sports_betting.data_collection.nba import NBADataCollector
from sports_betting.data_collection.nhl import NHLDataCollector
from datetime import datetime

def analyze_game(game, sport):
    high_confidence_picks = []
    
    # Analyze spread
    if game.get('spread') != 'N/A':
        spread_value = float(game['spread'])
        confidence = 0
        
        # Sport-specific confidence calculations
        if sport == 'NFL':
            confidence = 85 if abs(spread_value) <= 3 else (75 if abs(spread_value) <= 7 else 65)
        elif sport == 'NCAAB':
            confidence = 85 if abs(spread_value) <= 4 else (75 if abs(spread_value) <= 8 else 65)
        elif sport == 'NCAAF':
            confidence = 85 if abs(spread_value) <= 7 else (75 if abs(spread_value) <= 14 else 65)
        elif sport == 'NBA':
            confidence = 85 if abs(spread_value) <= 5 else (75 if abs(spread_value) <= 10 else 65)
        elif sport == 'NHL':
            confidence = 85 if abs(spread_value) <= 1.5 else 70
        
        if confidence >= 80:
            pick = game['home_team'] if spread_value < 0 else game['away_team']
            high_confidence_picks.append(f"Spread: {pick} ({confidence}% confidence)")
    
    # Analyze total
    if game.get('total') != 'N/A':
        total = float(game['total'])
        confidence = 0
        pick = ""
        
        # Sport-specific total analysis
        if sport == 'NFL':
            if total > 50 or total < 40:
                confidence = 80
                pick = "UNDER" if total > 50 else "OVER"
        elif sport == 'NCAAB':
            if total > 155 or total < 130:
                confidence = 80
                pick = "UNDER" if total > 155 else "OVER"
        elif sport == 'NCAAF':
            if total > 65 or total < 45:
                confidence = 80
                pick = "UNDER" if total > 65 else "OVER"
        elif sport == 'NBA':
            if total > 230 or total < 210:
                confidence = 80
                pick = "UNDER" if total > 230 else "OVER"
        elif sport == 'NHL':
            if total > 6.5 or total < 5.0:
                confidence = 80
                pick = "UNDER" if total > 6.5 else "OVER"
        
        if confidence >= 80:
            high_confidence_picks.append(f"Total: {pick} {game['total']} ({confidence}% confidence)")
    
    # Analyze moneyline
    if game.get('home_ml') != 'N/A' and game.get('away_ml') != 'N/A':
        home_ml = float(game['home_ml'])
        away_ml = float(game['away_ml'])
        confidence = 0
        
        # Calculate moneyline confidence based on odds difference
        ml_diff = abs(home_ml - away_ml)
        if ml_diff > 150:  # Strong favorite
            confidence = 80
            pick = game['home_team'] if home_ml > away_ml else game['away_team']
            high_confidence_picks.append(f"Moneyline: {pick} ({confidence}% confidence)")
    
    return high_confidence_picks

def main():
    print("\n=== HIGH CONFIDENCE PICKS (80%+) ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    # Collect games for each sport
    collectors = {
        'NFL': NFLDataCollector(),
        'NCAAB': NCAABDataCollector(),
        'NCAAF': NCAAFDataCollector(),
        'NBA': NBADataCollector(),
        'NHL': NHLDataCollector()
    }

    for sport, collector in collectors.items():
        games = collector.get_odds()
        high_confidence_games = False
        
        for game in games:
            picks = analyze_game(game, sport)
            if picks:
                if not high_confidence_games:
                    print(f"\n=== {sport} HIGH CONFIDENCE PICKS ===")
                    high_confidence_games = True
                
                print(f"\n{game['away_team']} @ {game['home_team']}")
                print(f"Start Time: {game['start_time']} ET")
                print("\nHIGH CONFIDENCE PICKS:")
                for pick in picks:
                    print(pick)
                print("-" * 60)

if __name__ == "__main__":
    main()
