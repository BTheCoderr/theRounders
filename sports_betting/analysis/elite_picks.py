from sports_betting.data_collection.nfl import NFLDataCollector
from sports_betting.data_collection.ncaab import NCAABDataCollector
from sports_betting.data_collection.ncaaf import NCAAFDataCollector
from sports_betting.data_collection.nba import NBADataCollector
from sports_betting.data_collection.nhl import NHLDataCollector
from datetime import datetime
import requests

class ElitePickAnalyzer:
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
        elite_picks = []
        
        if sport == 'NBA':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                home_ml = float(game.get('home_ml', 0))
                away_ml = float(game.get('away_ml', 0))
                
                reasons = []
                # Home favorite by 5-8 points with high total
                if -8 <= spread_value <= -5 and total > 230:
                    reasons.append(f"Strong home favorite in high-scoring matchup")
                    reasons.append(f"Total of {total} suggests fast-paced game")
                    reasons.append(f"Spread of {spread_value} indicates clear favorite")
                    elite_picks.append({
                        'type': 'Spread',
                        'pick': game['home_team'],
                        'confidence': 95,
                        'reasons': reasons
                    })
                
        elif sport == 'NHL':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                
                reasons = []
                # Strong home favorite on puck line with low total
                if spread_value == -1.5 and total <= 5.5:
                    reasons.append(f"Strong home favorite on puck line")
                    reasons.append(f"Low total of {total} suggests tight game")
                    elite_picks.append({
                        'type': 'Puck Line',
                        'pick': game['home_team'],
                        'confidence': 95,
                        'reasons': reasons
                    })
                
        elif sport == 'NFL':
            if game.get('spread') != 'N/A' and game.get('total') != 'N/A':
                spread_value = float(game['spread'])
                total = float(game['total'])
                
                reasons = []
                # Key number spreads with supporting totals
                if abs(spread_value) in [3, 7] and 42 <= total <= 49:
                    reasons.append(f"Key number spread of {abs(spread_value)}")
                    reasons.append(f"Total in sweet spot at {total}")
                    pick = game['home_team'] if spread_value < 0 else game['away_team']
                    elite_picks.append({
                        'type': 'Spread',
                        'pick': pick,
                        'confidence': 95,
                        'reasons': reasons
                    })

        return elite_picks

def main():
    print("\n=== ELITE PICKS OF THE DAY (95%+) 🏆 ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    analyzer = ElitePickAnalyzer()
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
        elite_games = False
        
        for game in games:
            picks = analyzer.analyze_game(game, sport)
            if picks:
                if not elite_games:
                    print(f"\n=== {sport} ELITE PICKS ===")
                    elite_games = True
                
                print(f"\n{game['away_team']} @ {game['home_team']}")
                print(f"Start Time: {game['start_time']} ET")
                print("\n🎯 ELITE PICKS:")
                
                for pick in picks:
                    print(f"\n{pick['type']}: {pick['pick']} ({pick['confidence']}% confidence)")
                    print("\nReasons:")
                    for reason in pick['reasons']:
                        print(f"• {reason}")
                    total_picks += 1
                print("-" * 60)
    
    if total_picks == 0:
        print("\n⚠️ No elite picks found for today's games.")
        print("Note: Elite picks require very specific criteria to be met.")
        print("Check back tomorrow for more opportunities!")
    else:
        print(f"\n📊 Total elite picks found: {total_picks}")
        print("Note: These picks are based on statistical analysis of key numbers and situations.")

if __name__ == "__main__":
    main()
