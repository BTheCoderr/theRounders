from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Keys and credentials
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
SPORTSDATA_API_KEY = os.getenv('SPORTSDATA_API_KEY')
BETFAIR_API_KEY = os.getenv('BETFAIR_API_KEY')

# Database settings
DATABASE = {
    'type': 'postgresql',  # or 'mongodb'
    'name': os.getenv('DB_NAME', 'sports_betting'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
}

# Sports coverage configuration
SUPPORTED_SPORTS = {
    'NBA': {
        'enabled': True,
        'api_endpoint': 'https://api.sportsdata.io/v3/nba',
        'metrics': ['spreads', 'moneylines', 'totals', 'player_props'],
        'update_interval': 300,  # seconds
    },
    'NFL': {
        'enabled': True,
        'api_endpoint': 'https://api.sportsdata.io/v3/nfl',
        'metrics': ['spreads', 'moneylines', 'totals', 'player_props'],
        'update_interval': 300,
    },
    'MLB': {
        'enabled': True,
        'api_endpoint': 'https://api.sportsdata.io/v3/mlb',
        'metrics': ['moneylines', 'totals', 'player_props'],
        'update_interval': 300,
    },
    'NHL': {
        'enabled': True,
        'api_endpoint': 'https://api.sportsdata.io/v3/nhl',
        'metrics': ['spreads', 'moneylines', 'totals'],
        'update_interval': 300,
    }
}

# Betting strategy settings
STRATEGY_CONFIG = {
    'kelly_criterion': {
        'enabled': True,
        'fraction': 0.25,  # Kelly fraction for conservative betting
    },
    'hedging': {
        'enabled': True,
        'min_guaranteed_profit': 0.02,  # 2% minimum profit for hedge suggestions
    },
    'arbitrage': {
        'enabled': True,
        'min_profit': 0.01,  # 1% minimum profit for arbitrage opportunities
    }
}

# Model settings
MODEL_CONFIG = {
    'power_rankings': {
        'enabled': True,
        'update_frequency': 'daily',
        'factors': ['wins', 'point_differential', 'strength_of_schedule', 'recent_form'],
    },
    'player_props': {
        'enabled': True,
        'model_type': 'lstm',
        'lookback_periods': 10,
        'confidence_threshold': 0.65,
    },
    'game_predictions': {
        'enabled': True,
        'model_type': 'ensemble',
        'components': ['elo', 'massey', 'neural_network'],
    }
}

# Sportsbook configuration
SPORTSBOOKS = {
    'draftkings': {
        'enabled': True,
        'api_endpoint': os.getenv('DRAFTKINGS_API_ENDPOINT'),
        'api_key': os.getenv('DRAFTKINGS_API_KEY'),
    },
    'fanduel': {
        'enabled': True,
        'api_endpoint': os.getenv('FANDUEL_API_ENDPOINT'),
        'api_key': os.getenv('FANDUEL_API_KEY'),
    },
    'betmgm': {
        'enabled': True,
        'api_endpoint': os.getenv('BETMGM_API_ENDPOINT'),
        'api_key': os.getenv('BETMGM_API_KEY'),
    }
}

# Web interface settings
WEB_CONFIG = {
    'host': os.getenv('WEB_HOST', 'localhost'),
    'port': int(os.getenv('WEB_PORT', 8000)),
    'debug': os.getenv('DEBUG', 'True').lower() == 'true',
    'refresh_interval': 30,  # seconds
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'betting.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
} 