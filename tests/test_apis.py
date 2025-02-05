import pytest
import asyncio
from datetime import datetime, timedelta
from odds_api import OddsAPI
from data_scraper import DataScraper
from api_config import APIConfig

@pytest.fixture
def odds_api():
    return OddsAPI()

@pytest.fixture
def data_scraper():
    return DataScraper()

@pytest.fixture
def api_config():
    return APIConfig()

def test_api_config_initialization(api_config):
    """Test API configuration initialization."""
    assert api_config.ODDS_API_KEY is not None, "Odds API key not found"
    assert isinstance(api_config.SUPPORTED_SPORTS, dict), "Supported sports not configured"
    assert len(api_config.SUPPORTED_SPORTS) > 0, "No sports configured"

def test_odds_api_sports(odds_api):
    """Test getting available sports."""
    sports = odds_api.get_sports()
    assert isinstance(sports, list), "Sports should be a list"
    assert len(sports) > 0, "No sports returned"
    assert all('key' in sport for sport in sports), "Sport missing key field"

def test_odds_api_odds(odds_api):
    """Test getting odds for a sport."""
    odds = odds_api.get_odds('nba')  # Test with NBA
    assert isinstance(odds, dict), "Odds should be a dictionary"
    if odds:  # Only if games are available
        game = next(iter(odds.values()))
        assert 'bookmakers' in game, "No bookmakers in odds data"
        assert 'commence_time' in game, "No commence time in odds data"

def test_odds_api_scores(odds_api):
    """Test getting scores."""
    scores = odds_api.get_scores('nba', daysFrom=1)
    assert isinstance(scores, dict), "Scores should be a dictionary"
    if scores:  # Only if games are available
        game = next(iter(scores.values()))
        assert 'completed' in game, "No completion status in scores"
        assert 'scores' in game, "No scores data"

@pytest.mark.asyncio
async def test_ufc_scraper(data_scraper):
    """Test UFC stats scraping."""
    # Test with a known UFC fighter ID
    fighter_stats = await data_scraper.scrape_ufc_stats("abc123")  # Replace with real ID
    if fighter_stats:  # Some requests might fail due to rate limiting
        assert 'name' in fighter_stats, "No fighter name found"
        assert 'record' in fighter_stats, "No fighter record found"
        assert 'striking' in fighter_stats, "No striking stats found"

@pytest.mark.asyncio
async def test_understat_scraper(data_scraper):
    """Test Understat soccer stats scraping."""
    # Test with a known match ID
    match_stats = await data_scraper.scrape_understat_match("12345")  # Replace with real ID
    if match_stats:  # Some requests might fail due to rate limiting
        assert 'teams' in match_stats, "No teams data found"
        assert 'score' in match_stats, "No score data found"
        assert 'xg' in match_stats, "No xG data found"

def test_rate_limiting(odds_api):
    """Test rate limiting functionality."""
    start_time = datetime.now()
    
    # Make multiple requests
    for _ in range(3):
        odds_api.get_sports()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Should take at least 10 seconds due to rate limiting
    assert duration >= 10, "Rate limiting not working as expected"

@pytest.mark.asyncio
async def test_batch_scraping(data_scraper):
    """Test batch scraping functionality."""
    # Test UFC card scraping
    card_stats = await data_scraper.scrape_ufc_card("ufc123")  # Replace with real event ID
    assert isinstance(card_stats, dict), "Card stats should be a dictionary"
    
    # Test multiple soccer matches
    match_ids = ["1", "2", "3"]  # Replace with real match IDs
    match_stats = await data_scraper.scrape_understat_matches(match_ids)
    assert isinstance(match_stats, dict), "Match stats should be a dictionary"

def test_error_handling(odds_api):
    """Test error handling."""
    # Test with invalid sport
    invalid_odds = odds_api.get_odds("invalid_sport")
    assert invalid_odds is None, "Should handle invalid sport gracefully"
    
    # Test with invalid parameters
    invalid_scores = odds_api.get_scores("nba", daysFrom=-1)
    assert invalid_scores is None, "Should handle invalid parameters gracefully" 