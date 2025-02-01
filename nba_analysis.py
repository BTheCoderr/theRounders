"""
NBA Analysis using Massey Ratings and Sauceda Rating systems.
Uses 2023-24 NBA season data.
"""

import numpy as np
from datetime import datetime, timedelta
from massey_formulas import MasseyFormulas, GameResult
from rating_analysis import RatingAnalyzer
from massey_schedule import MasseySchedule
from sauceda_ratings import SaucedaRatings
from pprint import pprint

def main():
    # Initialize rating systems
    formulas = MasseyFormulas()
    analyzer = RatingAnalyzer(formulas)
    schedule_calculator = MasseySchedule()
    sauceda = SaucedaRatings()
    
    # NBA Teams (focusing on key teams)
    teams = [
        "Boston Celtics",
        "Denver Nuggets",
        "LA Clippers",
        "Milwaukee Bucks",
        "Minnesota Timberwolves",
        "Philadelphia 76ers",
        "Phoenix Suns",
        "Golden State Warriors",
        "Oklahoma City Thunder",
        "New York Knicks",
        "Cleveland Cavaliers",
        "Sacramento Kings"
    ]
    
    # Recent NBA games (2024 season)
    base_date = datetime(2024, 1, 1)
    games = [
        # January 2024 games
        GameResult(
            team_a="Boston Celtics",
            team_b="Milwaukee Bucks",
            score_a=122,
            score_b=119,
            date=(base_date + timedelta(days=0)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Denver Nuggets",
            team_b="Golden State Warriors",
            score_a=130,
            score_b=127,
            date=(base_date + timedelta(days=0)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Phoenix Suns",
            team_b="LA Clippers",
            score_a=112,
            score_b=119,
            date=(base_date + timedelta(days=1)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Minnesota Timberwolves",
            team_b="Philadelphia 76ers",
            score_a=112,
            score_b=109,
            date=(base_date + timedelta(days=2)).timestamp(),
            is_home_a=False,
            weight=1.0
        ),
        GameResult(
            team_a="LA Clippers",
            team_b="Phoenix Suns",
            score_a=138,
            score_b=111,
            date=(base_date + timedelta(days=3)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Golden State Warriors",
            team_b="Denver Nuggets",
            score_a=111,
            score_b=130,
            date=(base_date + timedelta(days=4)).timestamp(),
            is_home_a=False,
            weight=1.0
        ),
        GameResult(
            team_a="Milwaukee Bucks",
            team_b="Boston Celtics",
            score_a=135,
            score_b=102,
            date=(base_date + timedelta(days=5)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Philadelphia 76ers",
            team_b="Minnesota Timberwolves",
            score_a=121,
            score_b=127,
            date=(base_date + timedelta(days=6)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        # Additional recent games
        GameResult(
            team_a="Oklahoma City Thunder",
            team_b="Boston Celtics",
            score_a=127,
            score_b=123,
            date=(base_date + timedelta(days=7)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="New York Knicks",
            team_b="Philadelphia 76ers",
            score_a=128,
            score_b=92,
            date=(base_date + timedelta(days=7)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Cleveland Cavaliers",
            team_b="Milwaukee Bucks",
            score_a=112,
            score_b=111,
            date=(base_date + timedelta(days=8)).timestamp(),
            is_home_a=False,
            weight=1.0
        ),
        GameResult(
            team_a="Sacramento Kings",
            team_b="Phoenix Suns",
            score_a=120,
            score_b=105,
            date=(base_date + timedelta(days=8)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="LA Clippers",
            team_b="Denver Nuggets",
            score_a=111,
            score_b=102,
            date=(base_date + timedelta(days=9)).timestamp(),
            is_home_a=True,
            weight=1.0
        )
    ]
    
    # Process all games through Sauceda system
    for game in games:
        sauceda.update_ratings(game)
    
    print("NBA TEAM ANALYSIS")
    print("=================")
    
    print("\n1. Sauceda Rating Analysis")
    print("-------------------------")
    sauceda_distribution = sauceda.analyze_rating_distribution()
    for tier in ["ELITE", "STRONG", "AVERAGE", "WEAK", "POOR"]:
        if sauceda_distribution[tier]:
            print(f"\n{tier} Teams:")
            for team in sauceda_distribution[tier]:
                rating = sauceda.ratings[team]
                print(f"  {team}: {rating:.1f}")
    
    print("\n2. Key Matchup Predictions")
    print("-------------------------")
    key_matchups = [
        ("Boston Celtics", "Denver Nuggets", True),
        ("LA Clippers", "Milwaukee Bucks", True),
        ("Minnesota Timberwolves", "Oklahoma City Thunder", True)
    ]
    
    for team_a, team_b, is_home in key_matchups:
        print(f"\n{team_a} vs {team_b} {'(Home)' if is_home else '(Away)'}:")
        # Sauceda prediction
        prediction = sauceda.predict_game(team_a, team_b, is_home)
        print(f"  Win Probability: {prediction.win_probability:.3f} for {team_a}")
        print(f"  Game Points: {prediction.winner_points:.3f} - {prediction.loser_points:.3f}")
        
        # Massey analysis
        matchup = analyzer.analyze_matchup(team_a, team_b, sauceda.ratings, games)
        print(f"  Expected Margin: {abs(matchup.expected_margin):.1f} points")
        print("  Key Factors:")
        for factor in matchup.key_factors:
            print(f"    - {factor}")
    
    print("\n3. Team Performance Metrics")
    print("--------------------------")
    for team in teams:
        analysis = analyzer.analyze_team(team, sauceda.ratings, games, datetime.now().timestamp())
        print(f"\n{team}:")
        print(f"  Current Rating: {analysis.rating:.3f}")
        print(f"  Offensive Rating: {analysis.offense:.1f} PPG")
        print(f"  Defensive Rating: {-analysis.defense:.1f} PPG Allowed")
        print(f"  Recent Trend: {analysis.trend:+.1f}")
        print(f"  Schedule Strength: {analysis.schedule_strength:.3f}")
        ci_low, ci_high = analysis.confidence_interval
        print(f"  Rating Range: [{ci_low:.2f}, {ci_high:.2f}]")
    
    print("\n4. Head-to-Head Matrix")
    print("---------------------")
    print("Win Probabilities (row vs column):")
    print("           ", end="")
    for t in teams:
        print(f"{t[:8]:>9}", end="")
    print()
    
    for team_a in teams:
        print(f"{team_a[:11]:<11}", end="")
        for team_b in teams:
            if team_a == team_b:
                prob = 0.500
            else:
                matchup = analyzer.analyze_matchup(team_a, team_b, sauceda.ratings, games)
                prob = matchup.win_probability
            print(f"{prob:>9.3f}", end="")
        print()
    
    print("\n5. Detailed Team Reports")
    print("----------------------")
    # Generate detailed report for top teams
    top_teams = ["Boston Celtics", "Denver Nuggets"]
    for team in top_teams:
        print(f"\nDetailed Report: {team}")
        print("-" * (len(team) + 16))
        
        analysis = analyzer.analyze_team(team, sauceda.ratings, games, datetime.now().timestamp())
        team_games = [g for g in games if team in (g.team_a, g.team_b)]
        
        print("Recent Games:")
        for game in sorted(team_games, key=lambda g: g.date, reverse=True):
            is_team_a = game.team_a == team
            team_score = game.score_a if is_team_a else game.score_b
            opp_score = game.score_b if is_team_a else game.score_a
            opp = game.team_b if is_team_a else game.team_a
            result = "W" if (is_team_a and game.score_a > game.score_b) or (not is_team_a and game.score_b > game.score_a) else "L"
            print(f"  {datetime.fromtimestamp(game.date).strftime('%Y-%m-%d')}: {result} vs {opp} ({team_score}-{opp_score})")
        
        print("\nPerformance Metrics:")
        print(f"  Overall Rating: {analysis.rating:.3f}")
        print(f"  Power Rating: {analysis.power:.3f}")
        print(f"  Offensive Efficiency: {analysis.offense:.1f}")
        print(f"  Defensive Efficiency: {-analysis.defense:.1f}")
        print(f"  Performance Variance: {analysis.variance:.3f}")
        print(f"  Schedule Strength: {analysis.schedule_strength:.3f}")
        
        print("\nProjected Matchups:")
        for opp in teams:
            if opp != team:
                matchup = analyzer.analyze_matchup(team, opp, sauceda.ratings, games)
                print(f"  vs {opp}: {matchup.win_probability:.3f} win probability")

    print("\n6. Massey Schedule Analysis")
    print("-------------------------")
    for team in teams:
        # Get opponent ratings from games
        opponent_ratings = []
        for game in games:
            if game.team_a == team:
                opponent_ratings.append(sauceda.ratings[game.team_b])
            elif game.team_b == team:
                opponent_ratings.append(sauceda.ratings[game.team_a])
        
        # Calculate Massey schedule metrics
        schedule_strength = schedule_calculator.calculate_schedule_strength(opponent_ratings)
        expected_wins = schedule_calculator.calculate_expected_wins(opponent_ratings, sauceda.ratings[team])
        distribution = schedule_calculator.analyze_schedule_distribution(opponent_ratings)
        insight = schedule_calculator.get_schedule_insight(opponent_ratings, sauceda.ratings[team])
        
        print(f"\n{team}:")
        print(f"  Massey Schedule Strength: {schedule_strength:.3f}")
        print(f"  Expected Wins: {expected_wins:.2f}")
        print("  Opponent Distribution:")
        for quality, count in distribution.items():
            if count > 0:
                print(f"    {quality}: {count}")
        print("  Schedule Insight:")
        print(f"    {insight}")

if __name__ == "__main__":
    main() 