import pytest
from sports_betting.data_collection.nhl import NHLDataCollector

class TestNHLDataCollector:
    def setup_method(self):
        self.nhl_collector = NHLDataCollector()

    def test_team_stats(self):
        """Test team statistics collection"""
        stats = self.nhl_collector.get_team_stats()
        
        required_columns = [
            'team_name', 'team_id', 'division', 'conference',
            'games_played', 'wins', 'losses',
            'goals_per_game', 'goals_against_per_game'
        ]
        
        for col in required_columns:
            assert col in stats.columns, f"Missing required column: {col}"
        assert len(stats) > 0, "No team data found"

    def test_player_stats(self):
        """Test player statistics collection"""
        stats = self.nhl_collector.get_player_stats()
        
        required_columns = [
            'player_name', 'team', 'position',
            'games_played', 'goals', 'assists', 'points'
        ]
        
        for col in required_columns:
            assert col in stats.columns, f"Missing required column: {col}"
        assert len(stats) > 0, "No player data found"

    def test_game_data(self):
        """Test game data collection"""
        games = self.nhl_collector.get_game_data()
        
        required_columns = [
            'game_id', 'home_team', 'away_team',
            'home_score', 'away_score', 'date'
        ]
        
        for col in required_columns:
            assert col in games.columns, f"Missing required column: {col}"
        assert len(games) > 0, "No game data found"

    def test_betting_odds(self):
        """Test betting odds collection"""
        odds = self.nhl_collector.get_betting_odds()
        
        required_columns = [
            'game_id', 'home_team', 'away_team',
            'home_moneyline', 'away_moneyline',
            'over_under', 'home_spread', 'away_spread'
        ]
        
        for col in required_columns:
            assert col in odds.columns, f"Missing required column: {col}"
        # Note: Not asserting length since betting data might not be available