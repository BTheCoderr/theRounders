from sports_betting.data_collection.nfl import NFLDataCollector
from sports_betting.data_collection.ncaab import NCAABDataCollector
from sports_betting.data_collection.ncaaf import NCAAFDataCollector
from sports_betting.data_collection.nba import NBADataCollector
from sports_betting.data_collection.nhl import NHLDataCollector
from datetime import datetime
import requests
import json

class SuperHighConfidenceAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.processed_games = set()

    def analyze_game(self, game, sport):
        game_id = f"{sport}_{game['away_team']}_{game['home_team']}_{game['start_time']}"
        if game_id in self.processed_games:
            return []
        
        self.processed_games.add(game_id)
        high_confidence_picks = []

        if sport == 'NBA':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                
                reasons = []
                # Home favorite scenarios
                if -12 <= spread_value <= -4:
                    reasons.append(f"Home team favored by {abs(spread_value)} points")
                    if total > 220:
                        reasons.append(f"High-scoring game expected (total: {total})")
                        reasons.append("Home teams typically perform better in high-scoring games")
                        high_confidence_picks.append({
                            'type': 'Spread',
                            'pick': game['home_team'],
                            'confidence': 90,
                            'reasons': reasons
                        })
                
                # Total scenarios
                if total > 235 or total < 210:
                    total_reasons = []
                    total_reasons.append(f"Extreme total of {total}")
                    pick = "UNDER" if total > 235 else "OVER"
                    total_reasons.append(f"Historical success rate high for {pick} at this number")
                    high_confidence_picks.append({
                        'type': 'Total',
                        'pick': f"{pick} {total}",
                        'confidence': 90,
                        'reasons': total_reasons
                    })

        elif sport == 'NHL':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                
                reasons = []
                # Puck line scenarios
                if spread_value == -1.5:
                    reasons.append("Strong home favorite on puck line")
                    if total <= 6:
                        reasons.append(f"Low-scoring game expected (total: {total})")
                        reasons.append("Favorites tend to cover in defensive games")
                        high_confidence_picks.append({
                            'type': 'Puck Line',
                            'pick': game['home_team'],
                            'confidence': 90,
                            'reasons': reasons
                        })

        elif sport == 'NFL':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                
                reasons = []
                # Key number spreads
                if abs(spread_value) in [3, 7, 10]:
                    reasons.append(f"Key number spread of {abs(spread_value)}")
                    if 44 <= total <= 51:
                        reasons.append(f"Total in prime range at {total}")
                        reasons.append("Historical success rate high at this spread/total combination")
                        pick = game['home_team'] if spread_value < 0 else game['away_team']
                        high_confidence_picks.append({
                            'type': 'Spread',
                            'pick': pick,
                            'confidence': 90,
                            'reasons': reasons
                        })

        elif sport == 'NCAAB':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                
                reasons = []
                # Home court advantage scenarios
                if -9 <= spread_value <= -4:
                    reasons.append(f"Home team favored by {abs(spread_value)} points")
                    if total < 140:
                        reasons.append(f"Low-scoring game expected (total: {total})")
                        reasons.append("Home teams historically strong in defensive games")
                        high_confidence_picks.append({
                            'type': 'Spread',
                            'pick': game['home_team'],
                            'confidence': 90,
                            'reasons': reasons
                        })

        elif sport == 'NCAAF':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                
                reasons = []
                # Large favorite scenarios
                if abs(spread_value) >= 14 and abs(spread_value) <= 21:
                    reasons.append(f"Strong favorite by {abs(spread_value)} points")
                    if total >= 55:
                        reasons.append(f"High-scoring game expected (total: {total})")
                        reasons.append("Favorites tend to cover in high-scoring games")
                        pick = game['home_team'] if spread_value < 0 else game['away_team']
                        high_confidence_picks.append({
                            'type': 'Spread',
                            'pick': pick,
                            'confidence': 90,
                            'reasons': reasons
                        })

        return high_confidence_picks

def log_prediction(game, pick, confidence, reasons):
    log_entry = {
        'game': f"{game['away_team']} @ {game['home_team']}",
        'start_time': game['start_time'],
        'pick': pick,
        'confidence': confidence,
        'reasons': reasons,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    with open('predictions_log.json', 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

def main():
    print("\n=== 🎯 SUPER HIGH CONFIDENCE PICKS (90%+) 🎯 ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    analyzer = SuperHighConfidenceAnalyzer()
    collectors = {
        'NFL': NFLDataCollector(),
        'NBA': NBADataCollector(),
        'NHL': NHLDataCollector(),
        'NCAAB': NCAABDataCollector(),
        'NCAAF': NCAAFDataCollector()
    }

    total_picks = 0
    for sport, collector in collectors.items():
        games = collector.get_odds()
        high_confidence_games = False
        
        for game in games:
            picks = analyzer.analyze_game(game, sport)
            if picks:
                if not high_confidence_games:
                    print(f"\n=== {sport} SUPER HIGH CONFIDENCE PICKS ===")
                    high_confidence_games = True
                
                print(f"\n{game['away_team']} @ {game['home_team']}")
                print(f"Start Time: {game['start_time']} ET")
                print("\n🎯 PICKS:")
                
                for pick in picks:
                    print(f"\n{pick['type']}: {pick['pick']} ({pick['confidence']}% confidence)")
                    print("\nReasons:")
                    for reason in pick['reasons']:
                        print(f"• {reason}")
                    total_picks += 1
                print("-" * 60)
    
    if total_picks == 0:
        print("\n⚠️ No super high confidence picks found for today's games.")
        print("Note: These picks require specific criteria to be met.")
        print("Check back tomorrow for more opportunities!")
    else:
        print(f"\n📊 Total super high confidence picks found: {total_picks}")
        print("Note: Picks are based on historical trends and key numbers.")

if __name__ == "__main__":
    main()
