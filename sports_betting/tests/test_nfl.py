import pytest
from sports_betting.data_collection.nfl import NFLDataCollector
import nfl_data_py as nfl

class TestNFLDataCollector:
    def setup_method(self):
        """Setup test collector"""
        self.nfl_collector = NFLDataCollector()

    def test_get_player_stats(self):
        """Test player statistics collection"""
        stats = self.nfl_collector.get_player_stats()
        
        # Test for required columns
        required_columns = [
            'player_name', 'team', 'position',
            'passing_yards', 'completion_percentage',
            'touchdowns', 'interceptions'
        ]
        
        for col in required_columns:
            assert col in stats.columns, f"Missing required column: {col}"
        
        assert len(stats) > 0, "No player data found"

    def test_get_team_stats(self):
        team_stats = self.nfl_collector.get_team_stats()
        
        expected_team_stats = [
            'team_name', 'points_per_game', 'points_allowed',
            'yards_per_game', 'rushing_yards_per_game',
            'passing_yards_per_game', 'third_down_conversion'
        ]
        
        for stat in expected_team_stats:
            assert stat in team_stats.columns, f"Missing column: {stat}"

    def test_get_advanced_metrics(self):
        metrics = self.nfl_collector.get_advanced_metrics()
        
        expected_metrics = ['dvoa_offense', 'dvoa_defense']
        for metric in expected_metrics:
            assert metric in metrics.columns, f"Missing metric: {metric}"

    def test_get_betting_trends(self):
        trends = self.nfl_collector.get_betting_trends()
        
        expected_trends = ['team', 'spread', 'total']
        for trend in expected_trends:
            assert trend in trends.columns, f"Missing trend: {trend}"

    def test_get_injury_impact(self):
        injury_data = self.nfl_collector.get_injury_impact()
        
        expected_fields = ['player_name', 'team', 'injury_status']
        for field in expected_fields:
            assert field in injury_data.columns, f"Missing field: {field}"

    def test_get_weather_conditions(self):
        weather = self.nfl_collector.get_weather_conditions()
        
        expected_conditions = ['game_id', 'temperature', 'wind_speed']
        for condition in expected_conditions:
            assert condition in weather.columns, f"Missing condition: {condition}"

if __name__ == '__main__':
    pytest.main()