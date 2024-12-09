from datetime import datetime
from analysis.main_betting_system import BettingSystem
from analysis.advanced_strategy import analyze_historical_data
from analysis.testing_framework import test_strategy

def main():
    # Initialize the system
    system = BettingSystem()
    
    print(f"\n=== DAILY BETTING ANALYSIS ===")
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 40)
    
    # 1. Run historical analysis
    print("\nRunning historical analysis...")
    test_strategy()
    
    # 2. Get today's picks
    print("\nGenerating today's picks...")
    system.run_daily_analysis()
    
    # 3. Display recommendations
    system.display_recommendations()
    
    # 4. Save results
    print("\nSaving results...")
    # TODO: Implement save_results()

if __name__ == "__main__":
    main() 