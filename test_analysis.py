"""
Test script to demonstrate rating analysis functionality.
"""

import numpy as np
from datetime import datetime, timedelta
from massey_formulas import MasseyFormulas, GameResult
from rating_analysis import RatingAnalyzer
from pprint import pprint

def main():
    # Initialize formulas and analyzer
    formulas = MasseyFormulas()
    analyzer = RatingAnalyzer(formulas)
    
    # Create sample data
    teams = [
        "Beast Squares",
        "Gaussian Eliminators",
        "Likelihood Loggers",
        "Linear Aggressors"
    ]
    
    # Sample games from the paper's example
    base_date = datetime(2024, 1, 1)
    games = [
        GameResult(
            team_a="Beast Squares",
            team_b="Gaussian Eliminators",
            score_a=10, score_b=6,
            date=(base_date + timedelta(days=0)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Likelihood Loggers",
            team_b="Linear Aggressors",
            score_a=4, score_b=4,
            date=(base_date + timedelta(days=7)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Linear Aggressors",
            team_b="Gaussian Eliminators",
            score_a=9, score_b=2,
            date=(base_date + timedelta(days=14)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Beast Squares",
            team_b="Linear Aggressors",
            score_a=8, score_b=6,
            date=(base_date + timedelta(days=21)).timestamp(),
            is_home_a=True,
            weight=1.0
        ),
        GameResult(
            team_a="Gaussian Eliminators",
            team_b="Likelihood Loggers",
            score_a=3, score_b=2,
            date=(base_date + timedelta(days=28)).timestamp(),
            is_home_a=True,
            weight=1.0
        )
    ]
    
    # Sample ratings (could be calculated from games)
    ratings = {
        "Beast Squares": 1.316,
        "Gaussian Eliminators": 0.923,
        "Likelihood Loggers": 0.864,
        "Linear Aggressors": 1.104
    }
    
    print("1. Single Team Analysis")
    print("----------------------")
    team_analysis = analyzer.analyze_team(
        "Beast Squares",
        ratings,
        games,
        datetime.now().timestamp()
    )
    pprint(vars(team_analysis))
    print()
    
    print("2. Matchup Analysis")
    print("------------------")
    matchup = analyzer.analyze_matchup(
        "Beast Squares",
        "Gaussian Eliminators",
        ratings,
        games
    )
    pprint(vars(matchup))
    print()
    
    print("3. Decision Factors")
    print("------------------")
    factors = analyzer.get_decision_factors(
        "Beast Squares",
        "Gaussian Eliminators",
        ratings,
        games
    )
    pprint(factors)
    print()
    
    print("4. Comparative Analysis")
    print("----------------------")
    print("Team Ratings:")
    for team in teams:
        analysis = analyzer.analyze_team(
            team,
            ratings,
            games,
            datetime.now().timestamp()
        )
        print(f"\n{team}:")
        print(f"  Rating: {analysis.rating:.3f}")
        print(f"  Power: {analysis.power:.3f}")
        print(f"  Offense: {analysis.offense:.1f}")
        print(f"  Defense: {analysis.defense:.1f}")
        print(f"  Trend: {analysis.trend:+.1f}")
        print(f"  Win Prob vs Avg: {analysis.win_probability:.3f}")
    
    print("\n5. Matchup Matrix")
    print("----------------")
    print("Win Probabilities (row vs column):")
    print("            ", end="")
    for t in teams:
        print(f"{t[:10]:>10}", end="")
    print()
    
    for team_a in teams:
        print(f"{team_a[:12]:<12}", end="")
        for team_b in teams:
            if team_a == team_b:
                prob = 0.5
            else:
                matchup = analyzer.analyze_matchup(team_a, team_b, ratings, games)
                prob = matchup.win_probability
            print(f"{prob:>10.3f}", end="")
        print()

if __name__ == "__main__":
    main() 