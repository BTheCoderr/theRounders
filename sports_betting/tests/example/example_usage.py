import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sports_betting.analysis.nfl_advanced_analytics import NFLAdvancedAnalytics
from sports_betting.analysis.nba_advanced_analytics import NBAAdvancedAnalytics
from sports_betting.analysis.nhl_advanced_analytics import NHLAdvancedAnalytics
from sports_betting.data_collection.nba import NBADataCollector
from sports_betting.data_collection.nhl import NHLDataCollector

def analyze_games():
    # NFL Analysis
    nfl_analyzer = NFLAdvancedAnalytics()
    nfl_report = nfl_analyzer.generate_comprehensive_report(
        team_id="NE",
        opponent_id="BUF",
        game_date="2024-01-01"
    )

    # NBA Analysis
    nba_collector = NBADataCollector()
    nba_analysis = nba_collector.get_comprehensive_game_analysis("GAME_ID")
    
    # NHL Analysis
    nhl_collector = NHLDataCollector()
    nhl_analysis = nhl_collector.get_comprehensive_game_analysis("GAME_ID")

    print("NBA Analysis:", nba_analysis)
    print("NHL Analysis:", nhl_analysis)

if __name__ == "__main__":
    analyze_games()
