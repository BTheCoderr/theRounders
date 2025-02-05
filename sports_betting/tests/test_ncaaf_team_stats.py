import pytest
from sports_betting.data_collection.ncaaf import NCAAFDataCollector
import pandas as pd

def test_team_stats_structure():
    """Test basic team stats collection structure"""
    collector = NCAAFDataCollector()
    team_data = collector.get_team_stats()
    
    # Basic DataFrame checks
    assert isinstance(team_data, pd.DataFrame), "Should return DataFrame"
    assert not team_data.empty, "DataFrame should not be empty"
    
    # Required columns
    required_columns = ['team_id', 'team_name', 'conference']
    for col in required_columns:
        assert col in team_data.columns, f"Missing required column: {col}"
    
    # Data type checks
    assert team_data['team_id'].dtype in ['int64', 'object'], "team_id should be numeric or string"
    assert team_data['team_name'].dtype == 'object', "team_name should be string"
    
    # Basic data validation
    assert len(team_data) >= 130, "Should have at least 130 FBS teams"
    assert not team_data['team_name'].isna().any(), "No team names should be null" 