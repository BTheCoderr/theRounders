"""Test API connections and rate limiting."""
import pytest
from utils.api_config import APIConfig, APIKeyError, RateLimitError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def api_config():
    """Create APIConfig instance for testing."""
    return APIConfig()

def test_api_key_validation(api_config):
    """Test API key validation."""
    # This should not raise an exception if .env is properly configured
    api_config._validate_environment()

def test_rate_limiting(api_config):
    """Test rate limiting functionality."""
    # Test odds API rate limiting
    for _ in range(api_config.rate_limits['odds_api']['limit']):
        assert api_config._check_rate_limit('odds_api') == True
    
    # Next call should return False
    assert api_config._check_rate_limit('odds_api') == False

def test_sportsdata_api_connection(api_config):
    """Test SportRadar API connection."""
    try:
        # Test endpoint for NBA games
        response = api_config.make_api_call(
            api_name='sportsdata',
            endpoint='http://api.sportradar.us/nba/trial/v7/en/games/2024/schedule.json',
            params={'api_key': api_config.get_api_key('sportsdata')}
        )
        assert response is not None
        assert 'games' in response or 'league' in response
    except Exception as e:
        pytest.fail(f"SportRadar API test failed: {str(e)}")

def test_odds_api_connection(api_config):
    """Test The Odds API connection."""
    try:
        response = api_config.make_api_call(
            api_name='odds_api',
            endpoint='https://api.the-odds-api.com/v4/sports/basketball_nba/odds',
            params={
                'apiKey': api_config.get_api_key('odds_api'),
                'regions': 'us',
                'markets': 'h2h,spreads'
            }
        )
        assert response is not None
        assert isinstance(response, list)
    except Exception as e:
        pytest.fail(f"Odds API test failed: {str(e)}")

def test_football_data_connection(api_config):
    """Test Football-Data API connection."""
    try:
        response = api_config.make_api_call(
            api_name='football_data',
            endpoint='http://api.football-data.org/v4/matches',
            headers={'X-Auth-Token': api_config.get_api_key('football_data')}
        )
        assert response is not None
        assert 'matches' in response or 'count' in response
    except Exception as e:
        pytest.fail(f"Football-Data API test failed: {str(e)}")

def test_error_handling(api_config):
    """Test error handling for API calls."""
    with pytest.raises(APIKeyError):
        api_config.get_api_key('invalid_api')
    
    # Test rate limit error
    api_config.rate_limits['odds_api']['calls'] = api_config.rate_limits['odds_api']['limit']
    with pytest.raises(RateLimitError):
        api_config.make_api_call('odds_api', 'https://api.example.com')

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 