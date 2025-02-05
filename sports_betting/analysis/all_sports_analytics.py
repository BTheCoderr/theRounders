from sports_betting.analysis.nfl_advanced_analytics import main as nfl_main
from sports_betting.analysis.ncaab_advanced_analytics import main as ncaab_main
from sports_betting.analysis.ncaaf_advanced_analytics import main as ncaaf_main
from sports_betting.analysis.nba_advanced_analytics import main as nba_main
from sports_betting.analysis.nhl_advanced_analytics import main as nhl_main
from datetime import datetime

def main():
    print("\n=== ALL SPORTS GAMES & PREDICTIONS ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    print("\n=== NFL ===")
    nfl_main()
    print("\n=== NCAAB ===")
    ncaab_main()
    print("\n=== NCAAF ===")
    ncaaf_main()
    print("\n=== NBA ===")
    nba_main()
    print("\n=== NHL ===")
    nhl_main()

if __name__ == "__main__":
    main()
