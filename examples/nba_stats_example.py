import pandas as pd
import streamlit as st
from data_scrapers.nba_advanced_scraper import NBAAdvancedScraper
from data_integration.sports_data_aggregator import SportsDataAggregator

def display_team_stats(stats: pd.DataFrame, title: str, columns: list, sort_by: str):
    """Helper function to display team statistics"""
    st.header(title)
    if not stats.empty and all(col in stats.columns for col in columns):
        st.dataframe(
            stats.sort_values(sort_by, ascending=False)[columns]
        )
    else:
        st.warning("No data available for this section")

def display_player_stats(stats: pd.DataFrame, min_minutes: int, sort_metric: str):
    """Helper function to display player statistics"""
    st.header("Player Advanced Statistics")
    if not stats.empty:
        # Filter for minimum minutes played
        filtered_players = stats[stats['MIN'] >= min_minutes] if 'MIN' in stats.columns else stats
        
        # Get available metrics for sorting
        available_metrics = [col for col in ['PER', 'USG_PCT', 'TS_PCT', 'AST_PCT', 'REB_PCT', 'NET_RATING'] 
                           if col in stats.columns]
        
        if available_metrics:
            # Let user select from available metrics
            sort_metric = st.selectbox(
                "Sort By",
                available_metrics
            )
            
            # Display columns that exist in the DataFrame
            display_columns = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'PTS']
            display_columns = [col for col in display_columns if col in stats.columns]
            if sort_metric not in display_columns:
                display_columns.append(sort_metric)
            
            st.dataframe(
                filtered_players.sort_values(sort_metric, ascending=False)[display_columns].head(20)
            )
        else:
            st.warning("No advanced metrics available")
    else:
        st.warning("No player data available")

def display_mlb_stats(aggregator: SportsDataAggregator):
    """Display MLB statistics"""
    st.header("MLB Analysis")
    try:
        mlb_stats = aggregator.get_mlb_historical_analysis(2024)
        if not mlb_stats.empty:
            st.dataframe(mlb_stats)
        else:
            st.warning("No MLB data available")
    except Exception as e:
        st.error(f"Error loading MLB data: {str(e)}")

def display_tennis_stats(aggregator: SportsDataAggregator):
    """Display tennis statistics"""
    st.header("Tennis Player Analysis")
    try:
        tennis_stats = aggregator.get_tennis_player_analysis(2024)
        if not tennis_stats.empty:
            st.dataframe(tennis_stats)
        else:
            st.warning("No tennis data available")
    except Exception as e:
        st.error(f"Error loading tennis data: {str(e)}")

def main():
    # Initialize the scrapers
    nba_scraper = NBAAdvancedScraper()
    sports_aggregator = SportsDataAggregator()
    
    # Set up the Streamlit interface
    st.title("Sports Analytics Dashboard")
    
    # Sport selection
    sport = st.sidebar.selectbox(
        "Select Sport",
        ["NBA", "MLB", "Tennis"]
    )
    
    if sport == "NBA":
        # Season selection
        season = st.selectbox(
            "Select Season",
            ["2023-24", "2022-23", "2021-22", "2020-21", "2019-20"]
        )
        
        # Get all stats for the selected season
        with st.spinner("Fetching NBA statistics..."):
            stats = nba_scraper.get_all_stats(season)
        
        # Display team advanced stats
        display_team_stats(
            stats['team_advanced'],
            "Team Advanced Statistics",
            ['TEAM_NAME', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE'],
            'NET_RATING'
        )
        
        # Display clutch performance
        display_team_stats(
            stats['clutch'],
            "Team Clutch Performance",
            ['TEAM_NAME', 'W', 'L', 'CLUTCH_WIN_PCT', 'CLUTCH_NET_RATING'],
            'CLUTCH_WIN_PCT'
        )
        
        # Display shooting stats
        display_team_stats(
            stats['shooting'],
            "Team Shooting Statistics",
            ['TEAM_NAME', 'FG_PCT', 'FG3_PCT', 'EFG_PCT', 'TS_PCT'],
            'EFG_PCT'
        )
        
        # Display top lineups
        st.header("Most Effective 5-Man Lineups")
        lineup_stats = stats['lineups']
        if not lineup_stats.empty and all(col in lineup_stats.columns for col in ['GROUP_NAME', 'MIN', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'MIN_PER_GAME']):
            filtered_lineups = lineup_stats[lineup_stats['MIN'] >= 100]
            st.dataframe(
                filtered_lineups.sort_values('NET_RATING', ascending=False)
                [['GROUP_NAME', 'MIN', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'MIN_PER_GAME']]
                .head(10)
            )
        else:
            st.warning("No lineup data available")
        
        # Display player advanced stats
        player_stats = stats['player_advanced']
        min_minutes = st.slider("Minimum Minutes Played", 0, 2000, 500)
        display_player_stats(player_stats, min_minutes, 'PER')
        
    elif sport == "MLB":
        display_mlb_stats(sports_aggregator)
        
    elif sport == "Tennis":
        display_tennis_stats(sports_aggregator)

if __name__ == "__main__":
    main() 