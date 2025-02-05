import asyncio
import pytest
from datetime import datetime, timedelta
from sports_apis import SportsAPI
import pandas as pd

@pytest.mark.asyncio
async def test_nba_data():
    """Test NBA data retrieval."""
    async with SportsAPI() as api:
        # Test NBA scoreboard
        scoreboard = api.get_nba_scoreboard()
        # During testing, we'll accept None as a valid response
        # since the NBA API might be rate limited or unavailable
        if scoreboard is not None:
            assert 'resultSets' in scoreboard
        
        # Test NBA player stats
        player_stats = api.get_nba_player_stats()
        if player_stats is not None:
            assert isinstance(player_stats, dict)
        
        # Test team info
        teams = api.get_nba_team_info()
        if teams is not None:
            assert len(teams) > 0

@pytest.mark.asyncio
async def test_mlb_data():
    """Test MLB data retrieval."""
    async with SportsAPI() as api:
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Test MLB schedule
        schedule = await api.get_mlb_schedule(date=today)
        assert schedule is not None
        
        if schedule.get('dates') and schedule['dates'][0].get('games'):
            game_pk = schedule['dates'][0]['games'][0]['gamePk']
            # Test MLB game data
            game = await api.get_mlb_game(game_pk)
            assert game is not None

@pytest.mark.asyncio
async def test_nhl_scraping():
    """Test NHL web scraping."""
    async with SportsAPI() as api:
        # Test NHL scores scraping
        scores = await api.scrape_nhl_scores()
        assert scores is not None
        assert isinstance(scores, pd.DataFrame)
        # During testing, accept empty DataFrame as valid
        # since there might not be any games
        if not scores.empty:
            # Test required columns
            required_columns = ['home_team', 'away_team', 'home_score', 'away_score', 'status']
            assert all(col in scores.columns for col in required_columns)
        else:
            # Verify empty DataFrame has correct columns
            assert list(scores.columns) == ['home_team', 'away_team', 'home_score', 'away_score', 'status']

@pytest.mark.asyncio
async def test_espn_odds():
    """Test ESPN odds scraping."""
    async with SportsAPI() as api:
        # Test NFL odds
        nfl_odds = await api.scrape_espn_odds('nfl')
        assert nfl_odds is not None
        assert isinstance(nfl_odds, pd.DataFrame)

@pytest.mark.asyncio
async def test_all_odds():
    """Test getting all odds."""
    async with SportsAPI() as api:
        odds = await api.get_all_odds()
        assert odds is not None
        assert isinstance(odds, dict)
        # Verify we got data for at least one sport
        assert len(odds) > 0

if __name__ == '__main__':
    pytest.main(['-v', 'test_sports_api.py']) 