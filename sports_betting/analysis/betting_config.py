BETTING_CONFIG = {
    'NFL': {
        'key_numbers': {
            'spread': [3, 7, 10, 14, 17, 21],
            'total': [37, 41, 44, 47, 51, 54]
        },
        'margin_ranges': [0.5, 3, 7, 10, 14, 17],
        'scoring_pace': 'quarters',
        'situational_patterns': {
            'west_coast_east': {'weight': 1.15, 'description': 'West coast team traveling east for early game'},
            'short_week': {'weight': 0.9, 'description': 'Team on short rest (Thursday games)'},
            'london_games': {'weight': 0.85, 'description': 'International games adjustment'},
            'weather_threshold': {
                'wind': {'speed': 20, 'weight': 0.9, 'total_adjustment': -3},
                'snow': {'weight': 0.85, 'total_adjustment': -4},
                'rain': {'weight': 0.92, 'total_adjustment': -2}
            }
        }
    },
    'NBA': {
        'key_numbers': {
            'spread': [4, 5, 6, 7, 8, 9, 11],
            'total': [200, 210, 220, 230, 240]
        },
        'margin_ranges': [1, 3, 5, 7, 10, 15],
        'scoring_pace': 'continuous',
        'situational_patterns': {
            'back_to_back_road': {'weight': 0.82, 'description': 'Second game of road back-to-back'},
            'third_in_four': {'weight': 0.88, 'description': 'Third game in four nights'},
            'altitude_games': {'weight': 0.9, 'description': 'Games in Denver/Utah for visiting teams'},
            'rest_advantage': {'days': 3, 'weight': 1.12}
        }
    },
    'NCAAB': {
        'key_numbers': {
            'spread': [3, 4, 5, 7, 8, 10],
            'total': [120, 130, 140, 150, 160]
        },
        'margin_ranges': [1, 3, 5, 7, 10, 15],
        'scoring_pace': 'halves',
        'situational_patterns': {
            'conference_tournament': {'weight': 1.15, 'description': 'Conference tournament games'},
            'rivalry_games': {'weight': 1.1, 'description': 'Traditional rivalry matchups'},
            'post_exam_break': {'weight': 0.9, 'description': 'First game after exam break'},
            'home_court_advantage': {
                'duke': 1.2,
                'kansas': 1.15,
                'kentucky': 1.15,
                # Add more prominent home courts
            }
        }
    }
}

# Enhanced Weighting System
WEIGHTING_SYSTEM = {
    'book_weights': {
        'sharp': {
            'pinnacle': {'weight': 1.0, 'description': 'Market setter, accepts sharp action'},
            'circa': {'weight': 0.95, 'description': 'Sharp Vegas book'},
            'cris': {'weight': 0.9, 'description': 'Early market indicator'},
            'bookmaker': {'weight': 0.85, 'description': 'Sharp offshore book'}
        },
        'public': {
            'draftkings': {'weight': 0.75, 'description': 'High public volume'},
            'fanduel': {'weight': 0.75, 'description': 'High public volume'},
            'betmgm': {'weight': 0.7, 'description': 'Public-heavy book'},
            'caesars': {'weight': 0.7, 'description': 'Public-heavy book'}
        }
    },
    'line_movement': {
        'steam': {'threshold': 1.5, 'time_window': 300, 'min_books': 3},
        'reverse_line': {'threshold': 2.0, 'public_threshold': 70},
        'key_number': {'multiplier': 1.2, 'window': 0.5}
    },
    'timing_weights': {
        'opening_line': 1.0,
        'early_sharp': 0.95,
        'midday': 0.9,
        'pregame': 0.85
    }
}

# Historical Pattern Analysis
HISTORICAL_PATTERNS = {
    'NFL': {
        'home_dog_prime_time': {
            'threshold': 3,
            'weight': 1.2,
            'sample_size': 500,
            'win_rate': 0.56
        },
        'division_dog': {
            'threshold': 7,
            'weight': 1.1,
            'sample_size': 800,
            'win_rate': 0.54
        },
        'weather_impact': {
            'threshold': 20,
            'weight': 1.3,
            'conditions': ['wind', 'snow', 'extreme_cold']
        },
        'rest_advantage': {
            'days': 7,
            'weight': 1.15,
            'sample_size': 300,
            'win_rate': 0.53
        },
        'playoff_experience': {
            'weight': 1.1,
            'description': 'Teams with playoff experience in key games'
        }
    },
    'NBA': {
        'patterns': {
            'back_to_back': {
                'weight': 0.85,
                'road_weight': 0.8,
                'sample_size': 1000,
                'win_rate': 0.45
            },
            'rest_advantage': {
                'days': 2,
                'weight': 1.1,
                'sample_size': 500,
                'win_rate': 0.52
            },
            'home_stand': {
                'games': 3,
                'weight': 1.05,
                'momentum_factor': 1.02
            },
            'road_trip': {
                'games': 3,
                'weight': 0.95,
                'fatigue_factor': 0.98
            }
        },
        'season_timing': {
            'early_season': {'weight': 0.9, 'months': [10, 11]},
            'mid_season': {'weight': 1.0, 'months': [12, 1, 2]},
            'late_season': {'weight': 1.1, 'months': [3, 4]},
            'playoffs': {'weight': 1.2, 'round_multiplier': 1.05}
        }
    }
}

# Betting configuration settings
BETTING_CONFIG = {
    'min_confidence': 65,
    'max_units_per_bet': 5,
    'default_unit_size': 100,
    'max_daily_exposure': 2000,
    'required_edge': 2.5,
    'min_odds': -200,
    'max_odds': 200
}

# List of respected sportsbooks for line shopping
RESPECTED_BOOKS = [
    'Pinnacle',
    'Circa',
    'Westgate',
    'BetMGM',
    'DraftKings',
    'FanDuel',
    'Caesars',
    'PointsBet'
]

# Historical betting patterns and trends
HISTORICAL_PATTERNS = {
    'home_favorite_cover_rate': 0.52,
    'away_dog_cover_rate': 0.48,
    'over_rate': 0.51,
    'under_rate': 0.49,
    'home_ml_win_rate': 0.59,
    'favorite_ml_win_rate': 0.65,
    'reverse_line_movement_rate': 0.56
}

# Sport-specific configurations
SPORT_CONFIGS = {
    'NCAAF': {
        'home_field_advantage': 3,
        'key_numbers': [3, 7, 10, 14],
        'max_spread': 28
    },
    'NBA': {
        'home_field_advantage': 2.5,
        'key_numbers': [4, 5, 6],
        'max_spread': 16
    },
    'NFL': {
        'home_field_advantage': 2.5,
        'key_numbers': [3, 7, 10, 14],
        'max_spread': 14
    },
    'NCAAB': {
        'home_field_advantage': 3.5,
        'key_numbers': [3, 4, 7],
        'max_spread': 20
    },
    'NHL': {
        'home_field_advantage': 0.25,
        'key_numbers': [1, 1.5, 2],
        'max_spread': 2
    }
}

# Model weights for different factors
MODEL_WEIGHTS = {
    'power_ratings': 0.3,
    'recent_form': 0.2,
    'head_to_head': 0.15,
    'injuries': 0.15,
    'situational': 0.1,
    'weather': 0.05,
    'public_betting': 0.05
} 