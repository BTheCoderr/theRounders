from sports_betting.data_collection.ncaaf import NCAAFDataCollector
from sports_betting.analysis.advanced_analytics import AdvancedAnalytics
from sports_betting.analysis.betting_models import BettingModels
from sports_betting.analysis.power_ratings import PowerRatings
from sports_betting.analysis.line_movement import LineMovement
from datetime import datetime
import pandas as pd
import pytz
from loguru import logger

def get_predictions(collector, game, power_ratings, betting_models):
    """Generate comprehensive predictions for a game"""
    try:
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Get team stats and metrics
        team_stats = collector.get_team_stats()
        advanced_metrics = collector.get_advanced_metrics()
        
        # Calculate power rating advantage
        power_advantage = power_ratings.get_rating_difference(home_team, away_team)
        
        # Get model predictions
        model_prediction = betting_models.predict_game(home_team, away_team)
        
        # Calculate projected score
        home_projected = model_prediction['home_score']
        away_projected = model_prediction['away_score']
        
        # Generate betting recommendations
        recommendations = []
        
        # Spread recommendation
        if pd.notna(game['spread']):
            spread_value = float(game['spread'])
            projected_diff = home_projected - away_projected
            if abs(projected_diff - spread_value) > 3:
                if projected_diff > spread_value:
                    recommendations.append(f"Take {home_team} {spread_value}")
                else:
                    recommendations.append(f"Take {away_team} +{abs(spread_value)}")
        
        # Over/Under recommendation
        if pd.notna(game['over_under']):
            total = float(game['over_under'])
            projected_total = home_projected + away_projected
            if abs(projected_total - total) > 4:
                recommendations.append(f"{'Over' if projected_total > total else 'Under'} {total}")
        
        return {
            'projected_score': f"{away_team} {away_projected:.1f} - {home_team} {home_projected:.1f}",
            'power_advantage': f"{home_team if power_advantage > 0 else away_team} by {abs(power_advantage):.1f}",
            'confidence': model_prediction['confidence'],
            'recommendations': recommendations,
            'key_factors': model_prediction['key_factors']
        }
        
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return None

def main():
    collector = NCAAFDataCollector()
    power_ratings = PowerRatings()
    betting_models = BettingModels()
    
    # Get today's games and odds
    games_df = collector.get_odds()
    
    # Print header
    et_time = datetime.now(pytz.timezone('US/Eastern'))
    print("\n=== TODAY'S NCAAF GAMES & PREDICTIONS ===")
    print(f"Generated: {et_time.strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    if games_df.empty:
        print("\nNo games found for today")
        return

    # Iterate through games
    for _, game in games_df.iterrows():
        try:
            print(f"\n{game['away_team']} @ {game['home_team']}")
            print("-" * 40)
            
            # Display odds
            print("ODDS:")
            if pd.notna(game['spread']):
                print(f"Spread: {game['spread']}")
            else:
                print("Spread: Not available")
            
            if pd.notna(game['over_under']):
                print(f"Over/Under: {game['over_under']}")
            else:
                print("Over/Under: Not available")
            
            if pd.notna(game['home_moneyline']) and pd.notna(game['away_moneyline']):
                print(f"Moneyline: {game['away_team']} ({game['away_moneyline']}) / {game['home_team']} ({game['home_moneyline']})")
            else:
                print("Moneyline: Not available")
            
            # Get and display predictions
            print("\nPREDICTIONS:")
            predictions = get_predictions(collector, game, power_ratings, betting_models)
            
            if predictions:
                print(f"Projected Score: {predictions['projected_score']}")
                print(f"Power Rating Edge: {predictions['power_advantage']}")
                print(f"Model Confidence: {predictions['confidence']}%")
                
                if predictions['recommendations']:
                    print("\nRECOMMENDATIONS:")
                    for rec in predictions['recommendations']:
                        print(f"- {rec}")
                
                if predictions['key_factors']:
                    print("\nKEY FACTORS:")
                    for factor in predictions['key_factors']:
                        print(f"- {factor}")
            
            print("-" * 40)
            
        except Exception as e:
            logger.error(f"Error processing game {_}: {str(e)}")
            continue

if __name__ == "__main__":
    main()