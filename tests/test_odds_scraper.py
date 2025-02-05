"""Test the odds scraper functionality."""
import pytest
from utils.odds_scraper import OddsScraper
from datetime import datetime
import json

@pytest.fixture
def scraper():
    """Create scraper instance for testing."""
    return OddsScraper()

def test_draftkings_scraper(scraper):
    """Test DraftKings odds scraping."""
    odds = scraper.get_draftkings_odds('nba')
    assert isinstance(odds, dict)
    if odds:  # Only check structure if we got data
        for game_id, game_odds in odds.items():
            assert 'home_team' in game_odds
            assert 'away_team' in game_odds
            assert 'home_odds' in game_odds
            assert 'away_odds' in game_odds
            assert 'timestamp' in game_odds

def test_betmgm_scraper(scraper):
    """Test BetMGM odds scraping."""
    odds = scraper.get_betmgm_odds('nba')
    assert isinstance(odds, dict)
    if odds:
        for game_id, game_odds in odds.items():
            assert 'home_team' in game_odds
            assert 'away_team' in game_odds
            assert 'home_odds' in game_odds
            assert 'away_odds' in game_odds
            assert 'timestamp' in game_odds

def test_fanduel_scraper(scraper):
    """Test FanDuel odds scraping."""
    odds = scraper.get_fanduel_odds('nba')
    assert isinstance(odds, dict)
    if odds:
        for game_id, game_odds in odds.items():
            assert 'home_team' in game_odds
            assert 'away_team' in game_odds
            assert 'home_odds' in game_odds
            assert 'away_odds' in game_odds
            assert 'timestamp' in game_odds

def test_caesars_scraper(scraper):
    """Test Caesars odds scraping."""
    odds = scraper.get_caesars_odds('nba')
    assert isinstance(odds, dict)
    if odds:
        for game_id, game_odds in odds.items():
            assert 'home_team' in game_odds
            assert 'away_team' in game_odds
            assert 'home_odds' in game_odds
            assert 'away_odds' in game_odds
            assert 'timestamp' in game_odds

def test_all_odds(scraper):
    """Test getting odds from all sources."""
    all_odds = scraper.get_all_odds('nba')
    assert isinstance(all_odds, dict)
    assert 'metadata' in all_odds
    assert all_odds['metadata']['sport'] == 'nba'
    assert isinstance(all_odds['metadata']['success_count'], int)
    
    # Save example output
    with open('tests/example_odds.json', 'w') as f:
        json.dump(all_odds, f, indent=2)

def test_error_handling(scraper):
    """Test error handling for invalid sport."""
    odds = scraper.get_all_odds('invalid_sport')
    assert odds['metadata']['success_count'] == 0

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 