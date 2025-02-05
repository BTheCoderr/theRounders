import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sports_betting.analysis.nba_advanced_analytics import NBAAdvancedAnalytics
from sports_betting.analysis.nhl_advanced_analytics import NHLAdvancedAnalytics
from sports_betting.analysis.nfl_advanced_analytics import NFLAdvancedAnalytics
import pandas as pd

def run_advanced_analysis():
    # NBA Analysis
    nba_analyzer = NBAAdvancedAnalytics()
    
    # Load historical data
    nba_historical = pd.read_csv('data/historical/nba_games.csv')
    nba_current = pd.read_csv('data/current/nba_games.csv')
    
    # Run comprehensive analysis
    nba_analysis = nba_analyzer.integrate_historical_analysis(
        nba_current,
        nba_historical
    )
    
    # Create visualizations
    nba_visuals = nba_analyzer.visualize_team_performance(nba_current)
    
    # NHL Analysis
    nhl_analyzer = NHLAdvancedAnalytics()
    
    # Load NHL data
    nhl_historical = pd.read_csv('data/historical/nhl_games.csv')
    nhl_current = pd.read_csv('data/current/nhl_games.csv')
    
    # Run NHL analysis
    nhl_analysis = nhl_analyzer.integrate_historical_analysis(
        nhl_current,
        nhl_historical
    )
    
    # Create NHL visualizations
    nhl_visuals = nhl_analyzer.visualize_team_performance(nhl_current)
    
    # NFL Analysis
    nfl_analyzer = NFLAdvancedAnalytics()
    
    # Load NFL data
    nfl_historical = pd.read_csv('data/historical/nfl_games.csv')
    nfl_current = pd.read_csv('data/current/nfl_games.csv')
    
    # Run NFL analysis
    nfl_analysis = nfl_analyzer.integrate_historical_analysis(
        nfl_current,
        nfl_historical
    )
    
    # Create NFL visualizations
    nfl_visuals = nfl_analyzer.visualize_team_performance(nfl_current)
    
    # Save visualizations
    nba_visuals['off_rtg_plot'].savefig('reports/nba_offensive_rating.png')
    nhl_visuals['metrics_heatmap'].savefig('reports/nhl_metrics_heatmap.png')
    nfl_visuals['metrics_heatmap'].savefig('reports/nfl_metrics_heatmap.png')

if __name__ == "__main__":
    run_advanced_analysis()
