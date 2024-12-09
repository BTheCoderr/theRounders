from sports_betting.data_collection.ncaab import NCAABDataCollector
from datetime import datetime

def main():
    print("\n=== TODAY'S NCAAB GAMES & PREDICTIONS ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    collector = NCAABDataCollector()
    games = collector.get_odds()

    for game in games:
        print(f"\n{game['away_team']} @ {game['home_team']}")
        print(f"Start Time: {game['start_time']} ET")
        print(f"Venue: {game['venue']}")
        
        print("\nODDS:")
        print(f"Spread: {game['spread']}")
        print(f"Total: {game['total']}")
        print(f"Moneyline: {game['away_team']} {game['away_ml']} | {game['home_team']} {game['home_ml']}")
        
        print("\nPREDICTIONS:")
        # Spread prediction with confidence (adjusted for NCAAB)
        if game['spread'] != 'N/A':
            spread_value = float(game['spread'])
            # Higher confidence in home teams due to court advantage
            spread_confidence = 75 if abs(spread_value) <= 4 else (65 if abs(spread_value) <= 8 else 55)
            if spread_value < 0:  # Home team favored
                spread_confidence += 5
            pick = game['home_team'] if spread_value < 0 else game['away_team']
            print(f"Spread Pick: {pick} ({spread_confidence}% confidence)")
        
        # Total prediction with confidence (adjusted for NCAAB scoring)
        if game['total'] != 'N/A':
            total = float(game['total'])
            if total > 155:  # High scoring for NCAAB
                print(f"Total Pick: UNDER {game['total']} (65% confidence)")
            elif total < 130:  # Low scoring for NCAAB
                print(f"Total Pick: OVER {game['total']} (65% confidence)")
            else:
                print(f"Total Pick: {'OVER' if total < 142.5 else 'UNDER'} {game['total']} (55% confidence)")
        
        # Moneyline prediction with confidence based on spread
        if game['home_ml'] != 'N/A' and game['away_ml'] != 'N/A':
            home_ml = float(game['home_ml'])
            away_ml = float(game['away_ml'])
            spread_value = abs(float(game['spread']))
            
            # Calculate confidence based on spread and home court
            if spread_value <= 4:
                ml_confidence = 70
            elif spread_value <= 8:
                ml_confidence = 60
            else:
                ml_confidence = 50
            
            # Add home court advantage to confidence
            if home_ml > away_ml:
                ml_confidence += 5
            
            pick = game['home_team'] if home_ml > away_ml else game['away_team']
            print(f"Moneyline Pick: {pick} ({ml_confidence}% confidence)")
        
        print("-" * 60)

if __name__ == "__main__":
    main()
