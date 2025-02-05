import json
from datetime import datetime
from .bill_walters_strategy import WaltersStrategy
from .api_integrations import OddsAPI
from .weather_analysis import WeatherAnalyzer

def show_picks():
    with open('picks_history.json', 'r') as f:
        picks = json.load(f)
        
    print("\n=== PICKS HISTORY ===")
    print(f"Total Picks: {len(picks)}")
    print("=" * 50)
    
    for pick in picks:
        print(f"\nDate: {pick['date']}")
        print(f"Game: {pick['game']}")
        print(f"Pick: {pick['pick']}")
        print(f"Result: {pick['result']}")
        print(f"Odds: {pick.get('odds', 'N/A')}")
        print(f"Bet Amount: ${pick.get('bet_amount', 'N/A')}")
        print("-" * 30)

def display_todays_picks():
    # Initialize strategy with $400 bankroll
    strategy = WaltersStrategy(bankroll=400.00)
    odds_api = OddsAPI()
    
    print(f"\n=== WALTERS STRATEGY BETTING RECOMMENDATIONS ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 50)

    # Get today's available games and odds
    available_games = odds_api.get_todays_games()
    
    # Apply strategy to get validated picks
    validated_picks = strategy.apply_strategy(available_games)
    
    if not validated_picks:
        print("\nNo picks meeting criteria for today.")
        return

    print("\nHIGH CONFIDENCE PICKS:")
    for i, pick in enumerate(validated_picks, 1):
        print(f"\n{i}. {pick['sport']}: {pick['game']}")
        print(f"   - Pick: {pick['pick_type']} {pick['pick']}")
        print(f"   - Confidence: {pick['confidence']}%")
        print(f"   - Recommended Bet: ${pick['recommended_bet']:,.2f}")
        print(f"   - Best Timing: {pick.get('bet_timing', 'As soon as possible')}")
        print(f"   - Edge: {pick.get('edge', 0)*100:.1f}%")
        print("   " + "-" * 40)

if __name__ == "__main__":
    show_picks()
    display_todays_picks()