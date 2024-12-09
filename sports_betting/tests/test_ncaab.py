import os
import sys
import pandas as pd
import pytest
import warnings
from sports_betting.data_collection.ncaab import NCAABDataCollector

# Suppress pandas deprecation warning
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pandas.core.algorithms')

def test_ncaab_data():
    """Test NCAAB data collection and processing"""
    collector = NCAABDataCollector()
    
    # Get basic team data
    team_data = collector.get_team_stats()
    assert len(team_data) > 0, "No team data found"
    assert len(team_data) >= 350, "Should have at least 350 D1 teams"
    
    # Get player data
    player_data = collector.get_player_stats()
    assert len(player_data) > 0, "No player data found"
    
    # Check required columns
    required_team_columns = ['team_id', 'team_name', 'conference']
    required_player_columns = ['player_id', 'player_name', 'team_id']
    
    for col in required_team_columns:
        assert col in team_data.columns, f"Missing required column: {col}"
    for col in required_player_columns:
        assert col in player_data.columns, f"Missing required column: {col}"

def test_ncaab_advanced_metrics():
    """Test NCAAB advanced analytics calculations"""
    collector = NCAABDataCollector()
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

def test_ncaab_player_details():
    """Test NCAAB player statistics details"""
    collector = NCAABDataCollector()
    player_data = collector.get_player_stats()
    
    # Check for reasonable number of players (D1 teams have ~15 players each, ~350 teams)
    assert len(player_data) >= 4000, "Should have at least 4000 players"
    assert len(player_data) <= 6000, "Should not have more than 6000 players"
    
    # Check for duplicate players
    assert len(player_data) == len(player_data.drop_duplicates()), "Found duplicate player entries"
    
    # Check team_id validity
    team_data = collector.get_team_stats()
    valid_team_ids = team_data['team_id'].unique()
    assert player_data['team_id'].isin(valid_team_ids).all(), "Found players with invalid team IDs"
    
    # Check for missing values
    assert not player_data['player_name'].isna().any(), "Found players with missing names"
    assert not player_data['team_id'].isna().any(), "Found players with missing team IDs"

def test_ncaab_conference_data():
    """Test conference data validity"""
    collector = NCAABDataCollector()
    team_data = collector.get_team_stats()
    
    # Check if conferences are populated
    assert not team_data['conference'].isna().any(), "Found teams with missing conferences"
    
    # Check major conferences exist
    major_conferences = ['ACC', 'Big 12', 'Big East', 'Big Ten', 'Pac-12', 'SEC']
    for conf in major_conferences:
        assert team_data['conference'].str.contains(conf).any(), f"Missing major conference: {conf}"

def test_ncaab_data_consistency():
    """Test data consistency across different methods"""
    collector = NCAABDataCollector()
    team_data = collector.get_team_stats()
    player_data = collector.get_player_stats()
    metrics = collector.get_advanced_metrics()
    
    # Check if metrics exist for all teams
    assert len(metrics) == len(team_data), "Metrics count doesn't match team count"
    
    # Check if all teams have players
    team_ids_with_players = player_data['team_id'].unique()
    assert len(team_ids_with_players) == len(team_data), "Some teams are missing players"

if __name__ == "__main__":
    pytest.main([__file__]) 