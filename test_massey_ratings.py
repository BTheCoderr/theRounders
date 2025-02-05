import pytest
import numpy as np
import pandas as pd
from sports_apis import MasseyRatings

def test_massey_basic():
    """Test basic Massey ratings functionality."""
    # Create a simple system with 4 teams
    teams = ['TeamA', 'TeamB', 'TeamC', 'TeamD']
    massey = MasseyRatings(teams, min_games=1)  # Only require 1 game for testing
    
    # Add some game results
    massey.add_game('TeamA', 'TeamB', 100, 90)  # TeamA wins by 10
    massey.add_game('TeamB', 'TeamC', 95, 85)   # TeamB wins by 10
    massey.add_game('TeamC', 'TeamD', 80, 70)   # TeamC wins by 10
    massey.add_game('TeamD', 'TeamA', 85, 75)   # TeamD wins by 10
    
    # Calculate ratings
    ratings = massey.calculate_ratings()
    
    # Check that we have ratings for all teams
    assert len(ratings) == 4
    
    # Ratings should sum to zero (within floating point precision)
    assert abs(sum(ratings.values())) < 1e-10
    
    # Get rankings
    rankings = massey.get_rankings()
    assert len(rankings) == 4
    assert all(col in rankings.columns for col in ['team', 'rating', 'games_played'])

def test_massey_predictions():
    """Test game prediction functionality."""
    teams = ['Warriors', 'Lakers', 'Celtics', 'Nets']
    massey = MasseyRatings(teams, min_games=2)  # Require 2 games for testing
    
    # Add some games with clear dominance pattern
    massey.add_game('Warriors', 'Lakers', 120, 100)
    massey.add_game('Warriors', 'Celtics', 115, 100)
    massey.add_game('Warriors', 'Nets', 110, 90)
    massey.add_game('Lakers', 'Celtics', 105, 100)
    massey.add_game('Lakers', 'Nets', 108, 95)
    massey.add_game('Celtics', 'Nets', 100, 90)
    
    # Calculate ratings
    massey.calculate_ratings()
    
    # Predict a game
    win_prob, point_diff = massey.predict_game('Warriors', 'Nets')
    
    # Warriors should be heavily favored
    assert win_prob > 0.5
    assert point_diff > 0

def test_massey_invalid_teams():
    """Test handling of invalid team names."""
    teams = ['TeamA', 'TeamB']
    massey = MasseyRatings(teams, min_games=1)
    
    # Try to add game with invalid team
    with pytest.raises(ValueError):
        massey.add_game('TeamA', 'InvalidTeam', 100, 90)

def test_massey_weighted_games():
    """Test weighted game functionality."""
    teams = ['TeamA', 'TeamB']
    massey = MasseyRatings(teams, min_games=2)  # Require 2 games for testing
    
    # Add regular season game
    massey.add_game('TeamA', 'TeamB', 100, 90, weight=1.0)
    
    # Add playoff game with higher weight
    massey.add_game('TeamB', 'TeamA', 95, 85, weight=2.0)
    massey.add_game('TeamB', 'TeamA', 105, 95, weight=2.0)  # Add another game to meet min_games
    
    ratings = massey.calculate_ratings()
    
    # TeamB should be rated higher due to weighted playoff wins
    assert ratings['TeamB'] > ratings['TeamA']

def test_massey_insufficient_games():
    """Test handling of teams with insufficient games."""
    teams = ['TeamA', 'TeamB', 'TeamC']
    massey = MasseyRatings(teams, min_games=2)
    
    # Only add one game
    massey.add_game('TeamA', 'TeamB', 100, 90)
    
    ratings = massey.calculate_ratings()
    
    # Should have no ratings due to insufficient games
    assert len(ratings) == 0

def test_massey_rankings_format():
    """Test the format of rankings DataFrame."""
    teams = ['TeamA', 'TeamB']
    massey = MasseyRatings(teams, min_games=2)  # Require 2 games for testing
    
    # Add enough games to meet minimum requirement
    massey.add_game('TeamA', 'TeamB', 100, 90)
    massey.add_game('TeamB', 'TeamA', 95, 85)
    massey.add_game('TeamA', 'TeamB', 110, 100)
    
    rankings = massey.get_rankings()
    
    # Check DataFrame structure
    assert isinstance(rankings, pd.DataFrame)
    assert len(rankings) == 2
    assert all(col in rankings.columns for col in ['team', 'rating', 'games_played'])
    assert all(rankings['games_played'] >= 2)

if __name__ == '__main__':
    pytest.main(['-v', 'test_massey_ratings.py']) 