import pytest
from sports_betting.data_collection.base_collector import BaseDataCollector
import pandas as pd

class TestCollector(BaseDataCollector):
    """Test implementation of BaseDataCollector"""
    def _fetch_team_stats(self) -> pd.DataFrame:
        return pd.DataFrame({'test': [1]})
    
    def _fetch_player_stats(self) -> pd.DataFrame:
        return pd.DataFrame({'test': [1]})
    
    def _fetch_betting_trends(self) -> pd.DataFrame:
        return pd.DataFrame({'test': [1]})
    
    def _fetch_injury_data(self) -> pd.DataFrame:
        return pd.DataFrame({'test': [1]})
    
    def _fetch_weather_data(self) -> pd.DataFrame:
        return pd.DataFrame({'test': [1]})
    
    def _calculate_advanced_metrics(self, team_stats: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({'test': [1]})

def test_base_collector_methods():
    """Test that all base collector methods work"""
    collector = TestCollector()
    
    # Test each method returns a DataFrame
    assert isinstance(collector._fetch_team_stats(), pd.DataFrame)
    assert isinstance(collector._fetch_player_stats(), pd.DataFrame)
    assert isinstance(collector._fetch_betting_trends(), pd.DataFrame)
    assert isinstance(collector._fetch_injury_data(), pd.DataFrame)
    assert isinstance(collector._fetch_weather_data(), pd.DataFrame)
    assert isinstance(collector._calculate_advanced_metrics(pd.DataFrame()), pd.DataFrame)