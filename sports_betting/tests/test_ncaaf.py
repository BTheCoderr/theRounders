import os
import sys
import pandas as pd
import pytest
import warnings
from sports_betting.data_collection.ncaaf import NCAAFDataCollector
from sports_betting.data_collection.base_collector import BaseDataCollector

# Suppress pandas deprecation warning
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pandas.core.algorithms')

def test_ncaaf_data():
    """Test NCAAF data collection and processing"""
    collector = NCAAFDataCollector()
    
    # Get basic team data
    team_data = collector.get_team_stats()
    assert len(team_data) > 0, "No team data found"
    assert len(team_data) >= 130, "Should have at least 130 FBS teams"
    
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

def test_ncaaf_advanced_metrics():
    """Test NCAAF advanced analytics calculations"""
    collector = NCAAFDataCollector()
    metrics = collector.get_advanced_metrics()
    
    # Check if we got data
    assert len(metrics) > 0, "No advanced metrics data found"
    
    # Check required metrics columns
    required_metrics = [
        'offensive_rating', 'defensive_rating',
        'net_rating', 'pace', 'turnover_margin'
    ]
    
    for metric in required_metrics:
        assert metric in metrics.columns, f"Missing required metric: {metric}"
    
    # Check data types
    assert metrics['offensive_rating'].dtype in ['float64', 'int64'], "Offensive rating should be numeric"
    assert metrics['defensive_rating'].dtype in ['float64', 'int64'], "Defensive rating should be numeric"
    assert metrics['turnover_margin'].dtype in ['float64', 'int64'], "Turnover margin should be numeric"

def test_ncaaf_player_details():
    """Test NCAAF player statistics details"""
    collector = NCAAFDataCollector()
    player_data = collector.get_player_stats()
    
    # Check for reasonable number of players (FBS teams have ~85 scholarship players each)
    assert len(player_data) >= 11000, "Should have at least 11000 players"
    assert len(player_data) <= 15000, "Should not have more than 15000 players"
    
    # Check for duplicate players
    assert len(player_data) == len(player_data.drop_duplicates()), "Found duplicate player entries"
    
    # Check team_id validity
    team_data = collector.get_team_stats()
    valid_team_ids = team_data['team_id'].unique()
    assert player_data['team_id'].isin(valid_team_ids).all(), "Found players with invalid team IDs"
    
    # Check for missing values
    assert not player_data['player_name'].isna().any(), "Found players with missing names"
    assert not player_data['team_id'].isna().any(), "Found players with missing team IDs"

def test_ncaaf_conference_data():
    """Test conference data validity"""
    collector = NCAAFDataCollector()
    team_data = collector.get_team_stats()
    
    # Check if conferences are populated
    assert not team_data['conference'].isna().any(), "Found teams with missing conferences"
    
    # Check Power 5 conferences exist
    power5_conferences = ['ACC', 'Big 12', 'Big Ten', 'Pac-12', 'SEC']
    for conf in power5_conferences:
        assert team_data['conference'].str.contains(conf).any(), f"Missing Power 5 conference: {conf}"

def test_ncaaf_data_consistency():
    """Test data consistency across different methods"""
    collector = NCAAFDataCollector()
    team_data = collector.get_team_stats()
    player_data = collector.get_player_stats()
    metrics = collector.get_advanced_metrics()
    
    # Check if metrics exist for all teams
    assert len(metrics) == len(team_data), "Metrics count doesn't match team count"
    
    # Check if all teams have players
    team_ids_with_players = player_data['team_id'].unique()
    assert len(team_ids_with_players) == len(team_data), "Some teams are missing players"

def test_ncaaf_division_validity():
    """Test FBS division validity"""
    collector = NCAAFDataCollector()
    team_data = collector.get_team_stats()
    
    # Check total number of FBS teams (should be around 130-132)
    assert 130 <= len(team_data) <= 132, "Unexpected number of FBS teams"
    
    # Check for independent teams
    assert team_data[team_data['conference'] == 'Independent'].shape[0] > 0, "Missing independent teams"

def test_ncaaf_collector_init():
    """Test NCAAF collector initialization"""
    collector = NCAAFDataCollector()
    assert hasattr(collector, 'logger'), "NCAAF collector missing logger"
    assert isinstance(collector, BaseDataCollector), "NCAAF collector not inheriting from base"

if __name__ == "__main__":
    pytest.main([__file__]) 