from datetime import datetime
from .analysis.main_betting_system import BettingSystem
from .analysis.performance_dashboard import plot_performance
from .analysis.advanced_strategy import analyze_historical_data
from .analysis.testing_framework import test_strategy

def run_complete_system():
    print("\n=== SPORTS BETTING SYSTEM ===")
    print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 40)

    try:
        # 1. Initialize the betting system
        print("\n1. Initializing betting system...")
        system = BettingSystem()

        # 2. Run historical analysis
        print("\n2. Running historical analysis...")
        test_strategy()

        # 3. Generate today's picks
        print("\n3. Generating today's picks...")
        system.run_daily_analysis()

        # 4. Display recommendations
        print("\n4. Today's betting recommendations:")
        system.display_recommendations()

        # 5. Save results
        print("\n5. Saving results...")
        system.save_results()

        # 6. Show performance dashboard
        print("\n6. Generating performance dashboard...")
        plot_performance()

        print("\nSystem run completed successfully!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("System run failed!")

if __name__ == "__main__":
    run_complete_system() 