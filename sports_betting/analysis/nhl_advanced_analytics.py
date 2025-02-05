from datetime import datetime
import pandas as pd
from sports_betting.data_collection.nhl import NHLDataCollector
from sports_betting.utils.logging_config import logger

def get_predictions(game: pd.Series, team_stats: pd.DataFrame) -> dict:
    """Calculate predictions for a game"""
    try:
        home_stats = team_stats[team_stats['team_name'] == game.home_team].iloc[0]
        away_stats = team_stats[team_stats['team_name'] == game.away_team].iloc[0]
        
        # Basic predictions based on team stats
        predicted_spread = home_stats.point_diff - away_stats.point_diff + 1.5  # Home ice advantage
        predicted_total = home_stats.goals_per_game + away_stats.goals_against_per_game
        
        # Win probability calculation
        rating_diff = home_stats.rating - away_stats.rating + 1.5
        win_prob = 1 / (1 + 10 ** (-rating_diff/10))
        
        return {
            'predicted_spread': predicted_spread,
            'predicted_total': predicted_total,
            'home_win_prob': win_prob,
            'away_win_prob': 1 - win_prob,
            'home_rating': home_stats.rating,
            'away_rating': away_stats.rating
        }
        
    except Exception as e:
        logger.error(f"Error calculating predictions: {str(e)}")
        return {}

def main():
    collector = NHLDataCollector()
    odds_df = collector.get_odds()
    team_stats = collector.get_team_stats()
    
    print("\n=== TODAY'S NHL GAMES & PREDICTIONS ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    if odds_df.empty:
        print("\nNo games found for today.")
        return

    for _, game in odds_df.iterrows():
        print(f"\n{game.away_team} @ {game.home_team}")
        print("-" * 40)
        
        predictions = get_predictions(game, team_stats)
        if predictions:
            print("TEAM RATINGS:")
            print(f"{game.home_team}: {predictions['home_rating']:.1f}")
            print(f"{game.away_team}: {predictions['away_rating']:.1f}\n")
            
            print("ODDS:")
            if game.spread:
                print(f"Spread: {game.away_team} {game.spread:+.1f}")
            if game.total:
                print(f"Over/Under: {game.total:.1f}")
            if game.home_ml and game.away_ml:
                print(f"Moneyline: {game.away_team} ({game.away_ml:+.0f}) / {game.home_team} ({game.home_ml:+.0f})")
            
            print("\nPREDICTIONS:")
            print(f"Spread: {game.home_team} {predictions['predicted_spread']:+.1f}")
            print(f"Total: {predictions['predicted_total']:.1f}")
            print(f"Win Probability: {game.home_team} {predictions['home_win_prob']:.1%} / {game.away_team} {predictions['away_win_prob']:.1%}")
        else:
            print("Unable to generate predictions")

if __name__ == "__main__":
    main()
