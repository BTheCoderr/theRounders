from sports_betting.utils.bet_tracker import WaltersBetTracker, BetDetails
from datetime import datetime
import json

def main():
    # Initialize the tracker
    tracker = WaltersBetTracker()
    
    # Example of adding a new bet with Bill Walters-style detailed tracking
    new_bet = BetDetails(
        date=datetime.now().strftime("%Y-%m-%d"),
        sport="NBA",
        game="Lakers vs Warriors",
        pick_type="Spread",
        pick="Lakers",
        confidence=85,  # High confidence based on analysis
        line=-4.5,
        odds=1.91,
        bet_amount=100,
        book="DraftKings",
        bet_time=datetime.now().strftime("%H:%M:%S"),
        notes="Strong reverse line movement, key players available",
        edge=3.2,  # Calculated edge percentage
        category="Main",
        units=1.0,
        steam_move=True,
        injury_notes="All key players available"
    )
    
    # Add the bet to the tracker
    tracker.add_bet(new_bet)
    
    # Later, update the result with closing line value
    tracker.update_result(
        date=new_bet.date,
        game=new_bet.game,
        pick_type=new_bet.pick_type,
        result="Won",
        closing_line=-5.5  # The line moved in our favor
    )
    
    # Get comprehensive analytics
    analytics = tracker.get_analytics()
    
    # Print analytics in a readable format
    print("\n=== Betting Performance Analytics ===")
    print(json.dumps(analytics, indent=2))
    
    # Print specific insights
    if analytics.get("closing_line_value"):
        print("\n=== Closing Line Value Analysis ===")
        print(f"Average CLV: {analytics['closing_line_value']['average_clv']:.2f}")
        print(f"Win rate when getting CLV: {analytics['closing_line_value']['clv_win_rate']*100:.1f}%")
    
    if analytics.get("steam_move_performance"):
        print("\n=== Steam Move Performance ===")
        print(f"Steam move win rate: {analytics['steam_move_performance']['steam_win_rate']*100:.1f}%")
        print(f"Steam move ROI: {analytics['steam_move_performance']['steam_roi']*100:.1f}%")

if __name__ == "__main__":
    main() 