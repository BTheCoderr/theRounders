import os
import sys
import pandas as pd
import pytest
import warnings
from sports_betting.data_collection.nba import NBADataCollector

# Suppress the deprecation warning from pandas
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pandas.core.algorithms')

def test_nba_data():
    """Test NBA data collection and processing"""
    collector = NBADataCollector()
    
    # Get basic team data
    team_data = collector.get_team_stats()
    assert len(team_data) > 0
    
    # Get player data
    player_data = collector.get_player_stats()
    assert len(player_data) > 0
    
    # Check required columns
    required_team_columns = ['team_id', 'team_name', 'conference']
    required_player_columns = ['player_id', 'player_name', 'team_id']
    
    for col in required_team_columns:
        assert col in team_data.columns, f"Missing required column: {col}"
    for col in required_player_columns:
        assert col in player_data.columns, f"Missing required column: {col}"

def test_nba_advanced_metrics():
    """Test NBA advanced analytics calculations"""
    collector = NBADataCollector()
    metrics = collector.get_advanced_metrics()
    
    # Check if we got data
    assert len(metrics) > 0, "No advanced metrics data found"
    
    # Check required metrics columns
    required_metrics = [
        'offensive_rating', 'defensive_rating',
        'net_rating', 'pace', 'true_shooting_percentage'
    ]
    
    for metric in required_metrics:
        assert metric in metrics.columns, f"Missing required metric: {metric}"
    
    # Check data types and ranges
    assert metrics['offensive_rating'].dtype in ['float64', 'int64'], "Offensive rating should be numeric"
    assert metrics['defensive_rating'].dtype in ['float64', 'int64'], "Defensive rating should be numeric"
    assert metrics['true_shooting_percentage'].between(0, 1).all(), "True shooting percentage should be between 0 and 1"

def test_nba_player_details():
    """Test NBA player statistics details"""
    collector = NBADataCollector()
    player_data = collector.get_player_stats()
    
    # Check for reasonable number of players
    assert len(player_data) >= 350, "Should have at least 350 players"
    assert len(player_data) <= 600, "Should not have more than 600 players"
    
    # Check for duplicate players
    assert len(player_data) == len(player_data.drop_duplicates()), "Found duplicate player entries"
    
    # Check team_id validity
    team_data = collector.get_team_stats()
    valid_team_ids = team_data['team_id'].unique()
    assert player_data['team_id'].isin(valid_team_ids).all(), "Found players with invalid team IDs"
    
    # Check for missing values
    assert not player_data['player_name'].isna().any(), "Found players with missing names"
    assert not player_data['team_id'].isna().any(), "Found players with missing team IDs"

if __name__ == "__main__":
    pytest.main([__file__])