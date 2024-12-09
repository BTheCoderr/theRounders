import requests
from datetime import datetime
from .weather_analysis import WeatherAnalysis
from .advanced_analytics import AdvancedAnalytics

def evaluate_factors(pick, required_factors):
    """
    Evaluate if a pick meets all required factors
    Returns True if all factors are met, False otherwise
    """
    factors_met = {
        "Home team advantage": check_home_advantage(pick),
        "Recent team performance": check_recent_performance(pick),
        "Key player availability": check_player_availability(pick),
        "Rest days between games": check_rest_days(pick),
    }
    
    return all(factors_met.get(factor, False) for factor in required_factors)

def select_high_confidence_picks(picks, factors):
    """
    Select picks that meet confidence criteria
    """
    selected_picks = []
    for pick in picks:
        sport = pick['sport']
        pick_type = pick['pick_type']
        confidence = pick.get('confidence', 0)
        
        if sport in factors and pick_type in factors[sport]:
            criteria = factors[sport][pick_type]
            if confidence >= criteria['min_confidence']:
                if evaluate_factors(pick, criteria['factors']):
                    selected_picks.append(pick)
    return selected_picks

# Helper functions
def check_home_advantage(pick):
    # Implement home advantage logic
    return True

def check_recent_performance(pick):
    # Implement recent performance logic
    return True

def check_player_availability(pick):
    # Implement player availability logic
    return True

def check_rest_days(pick):
    # Implement rest days logic
    return True

def get_todays_picks():
    weather = WeatherAnalysis()
    analyzer = AdvancedAnalytics()
    
    print("\nAnalyzing Today's Games...")
    print("=" * 50)
    
    for sport in ['NFL', 'NCAAF']:  # Focus on outdoor sports
        try:
            # Get games from API
            games = get_games(sport)
            
            for game in games:
                # Get weather impact
                weather_data = weather.get_game_weather(
                    home_team=game['home_team'],
                    game_time=game['game_time'],
                    league=sport
                )
                
                if weather_data:
                    weather_impact = weather.analyze_weather_impact(weather_data, sport)
                    
                    # Add weather data to analysis
                    game['weather'] = weather_data
                    game['weather_impact'] = weather_impact
                    
                    print(f"\nGame: {game['away_team']} @ {game['home_team']}")
                    print(f"Weather: {weather_data['temperature']}°F, Wind: {weather_data['wind_mph']} mph")
                    print(f"Weather Impact Score: {weather_impact}")
                    
                    # Get betting recommendation
                    analysis = analyzer.analyze_game(game)
                    if analysis:
                        print(f"Recommendation: {analysis['recommended_bet']}")
                        print(f"Confidence: {analysis['confidence']}%")
                
        except Exception as e:
            print(f"Error analyzing {sport} games: {e}")
            continue

def analyze_spread(outcomes):
    """Analyze spread odds and generate pick"""
    if len(outcomes) < 2:
        return None
        
    # Basic spread analysis
    spread = float(outcomes[0]['point'])
    if abs(spread) > 7:  # High spread
        confidence = 65
    else:
        confidence = 75
        
    return {
        'pick': f"{outcomes[0]['name']} {outcomes[0]['point']}",
        'odds': outcomes[0]['price'],
        'confidence': confidence
    }

def analyze_total(outcomes):
    """Analyze total odds and generate pick"""
    if len(outcomes) < 2:
        return None
        
    # Basic totals analysis
    total = float(outcomes[0]['point'])
    if total > 220:  # High total
        pick = 'UNDER'
        confidence = 70
    else:
        pick = 'OVER'
        confidence = 65
        
    return {
        'pick': f"{pick} {outcomes[0]['point']}",
        'odds': outcomes[0]['price'],
        'confidence': confidence
    }

def get_games(sport):
    """Get today's games for given sport"""
    try:
        from .api_integrations import OddsAPI
        api = OddsAPI()
        return api.get_todays_games()
    except Exception as e:
        print(f"Error getting {sport} games: {e}")
        return []

def display_game_analysis(game, weather_data=None, analysis=None):
    """Display detailed game analysis"""
    print(f"\n{'='*80}")
    print(f"Game Analysis: {game['away_team']} @ {game['home_team']}")
    print(f"Time: {game['game_time'].strftime('%I:%M %p ET')}")
    print(f"{'='*80}")
    
    # Odds Comparison
    print("\nOdds Comparison:")
    print("-" * 40)
    for book in game['odds']['spread']['range']:
        print(f"{book['book']:10} {book['spread']:>6} ({book['odds']:>6})")
    
    # Best Available Odds
    print("\nBest Available Odds:")
    print("-" * 40)
    best = game['best_odds']
    print(f"Spread: {best['spread']['spread']} ({best['spread']['odds']}) @ {best['spread']['book']}")
    print(f"Total: {best['total']['total']} ({best['total']['odds']}) @ {best['total']['book']}")
    print(f"ML: {best['moneyline']['odds']} @ {best['moneyline']['book']}")
    
    # Weather Impact (if applicable)
    if weather_data:
        print("\nWeather Conditions:")
        print("-" * 40)
        print(f"Temperature: {weather_data['temperature']}°F")
        print(f"Wind: {weather_data['wind_mph']} mph")
        print(f"Precipitation: {weather_data['precipitation_mm']}%")
        
    # Betting Analysis
    if analysis:
        print("\nBetting Analysis:")
        print("-" * 40)
        print(f"Win Probability: {analysis['win_probability']}%")
        print(f"Value Rating: {analysis['betting_value']}")
        print(f"Confidence: {analysis['confidence']}%")
        print(f"Recommendation: {analysis['recommended_bet']}")
        
        if 'key_metrics' in analysis:
            print("\nKey Metrics:")
            for metric, value in analysis['key_metrics'].items():
                print(f"{metric}: {value}")

if __name__ == "__main__":
    picks = get_todays_picks()  # Modify get_todays_picks() to return picks
    
    print("\n=== TODAY'S BETTING RECOMMENDATIONS ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 50)
    
    if picks:  # Check if we have any picks
        for pick in picks:
            print(f"\nSport: {pick['sport']}")
            print(f"Game: {pick['game']}")
            print(f"Time: {pick['game_time']}")
            print(f"Pick: {pick['pick']}")
            print(f"Odds: {pick['odds']}")
            print(f"Confidence: {pick['confidence']}%")
            print("-" * 30)
    else:
        print("\nNo picks available for today.")
    