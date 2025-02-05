"""
Test script for MLB Rating System.
Uses sample data to demonstrate predictions and analysis.
"""

from mlb_ratings import MLBRatings

def main():
    # Initialize rating system
    mlb = MLBRatings()
    
    # Add some sample teams with ratings
    # Format: name, offense, defense, park effect, games played
    teams = [
        ("New York Yankees", 5.2, -0.8, 0.7, 82),  # Strong offense, good defense, hitter's park
        ("Los Angeles Dodgers", 4.8, -1.2, -0.3, 82),  # Good offense, great defense, pitcher's park
        ("Houston Astros", 4.5, -0.9, 0.2, 82),  # Good all-around team
        ("Boston Red Sox", 4.9, 0.5, 1.2, 82),  # Strong offense, weak defense, extreme hitter's park
        ("San Francisco Giants", 3.8, -1.1, -0.8, 82)  # Average offense, good defense, extreme pitcher's park
    ]
    
    for team in teams:
        mlb.add_team(*team)
    
    # Add some sample pitchers
    # Format: name, team, offense (run support), defense (prevention), home/away, team starts, total starts
    pitchers = [
        ("Gerrit Cole", "New York Yankees", 0.5, -1.8, -0.2, 18, 18),  # Ace with good run support
        ("Clayton Kershaw", "Los Angeles Dodgers", 0.3, -1.5, -0.5, 15, 15),  # Veteran ace, better on road
        ("Justin Verlander", "Houston Astros", 0.4, -1.2, 0.3, 16, 16),  # Solid ace, better at home
        ("Chris Sale", "Boston Red Sox", -0.2, -0.8, 0.8, 12, 12),  # Good pitcher, much better at home
        ("Logan Webb", "San Francisco Giants", -0.3, -1.1, -0.4, 17, 17)  # Good pitcher, better on road
    ]
    
    for pitcher in pitchers:
        mlb.add_pitcher(*pitcher)
    
    print("MLB RATING ANALYSIS")
    print("==================")
    
    # Analyze some matchups
    print("\n1. Key Matchup Predictions")
    print("-------------------------")
    matchups = [
        ("New York Yankees", "Boston Red Sox", "Gerrit Cole", "Chris Sale"),
        ("Los Angeles Dodgers", "San Francisco Giants", "Clayton Kershaw", "Logan Webb"),
        ("Houston Astros", "New York Yankees", "Justin Verlander", None)
    ]
    
    for home, away, home_p, away_p in matchups:
        print(f"\n{home} vs {away}")
        if home_p or away_p:
            print(f"Pitchers: {home_p or 'TBD'} vs {away_p or 'TBD'}")
        prediction = mlb.predict_game(home, away, home_p, away_p)
        print(f"Predicted Score: {home} {prediction.home_score:.1f}, {away} {prediction.away_score:.1f}")
        print(f"Win Probability: {prediction.home_win_prob:.3f} for {home}")
        print(f"Expected Total Runs: {prediction.total_runs:.1f}")
        print("Analysis:")
        for line in prediction.description.split("\n"):
            print(f"  {line}")
    
    print("\n2. Pitcher Analysis")
    print("-----------------")
    for pitcher in ["Gerrit Cole", "Clayton Kershaw", "Justin Verlander"]:
        print(f"\n{pitcher}:")
        analysis = mlb.analyze_pitcher_impact(pitcher)
        for line in analysis.split("\n"):
            print(f"  {line}")
    
    print("\n3. Ballpark Analysis")
    print("------------------")
    for team in ["Boston Red Sox", "San Francisco Giants", "Los Angeles Dodgers"]:
        print(f"\n{team} Ballpark:")
        analysis = mlb.analyze_ballpark_factors(team)
        for line in analysis.split("\n"):
            print(f"  {line}")

if __name__ == "__main__":
    main() 