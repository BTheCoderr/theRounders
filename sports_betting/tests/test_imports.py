def test_data_collection_imports():
    """Test that all data collection modules can be imported"""
    try:
        from sports_betting.data_collection import (
            base_collector,
            api_clients,
            data_collector,
            nfl,
            nba,
            nhl,
            ncaaf,
            ncaab,
            mlb,
            injury_data,
            odds_data,
            sports_data,
            weather_data
        )
        assert True
    except ImportError as e:
        assert False, f"Import failed: {str(e)}" 