import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sports_betting.data_collection.nhl import NHLDataCollector
from datetime import datetime

class NHLPlayoffSimulator:
    def __init__(self):
        self.nhl_collector = NHLDataCollector()
        self.eastern_teams = [
            'Boston', 'Buffalo', 'Carolina', 'Columbus', 'Detroit',
            'Florida', 'Montreal', 'New Jersey', 'NY Islanders',
            'NY Rangers', 'Ottawa', 'Philadelphia', 'Pittsburgh',
            'Tampa Bay', 'Toronto', 'Washington'
        ]
        
    def _format_team_row(self, rank, team):
        """Format a team's row for display in standings"""
        return (f"{rank:<4}"
                f"{team['TEAM']:<25}"
                f"{team['GP']:<5}"
                f"{team['W']:<6}"
                f"{team['L']:<6}"
                f"{team['OT']:<5}"
                f"{team['PTS']:<7}"
                f"{team['P%']:<8}"
                f"{team['GF']:<5}"
                f"{team['GA']:<5}"
                f"{team['DIFF']:<7}"
                f"{team['L10']:<8}"
                f"{team['STRK']:<6}")
    
    def display_current_standings(self):
        """Display current NHL standings by conference"""
        team_stats = self.nhl_collector.get_team_stats()
        if team_stats is None:
            return
            
        print("\n=== NHL SEASON STANDINGS ===")
        print(f"Updated as of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for conference in ['East', 'West']:
            print(f"{conference}ern Conference:")
            print("=" * 100)
            print(f"{'Rank':<4}{'Team':<25}{'GP':<5}{'W':<6}{'L':<6}{'OT':<5}{'PTS':<7}{'P%':<8}"
                  f"{'GF':<5}{'GA':<5}{'DIFF':<7}{'L10':<8}{'STRK':<6}")
            print("-" * 100)
            
            conf_teams = team_stats[team_stats['CONFERENCE'] == conference].sort_values('PTS', ascending=False)
            for idx, team in conf_teams.iterrows():
                rank = conf_teams.index.get_loc(idx) + 1
                print(self._format_team_row(rank, team))
            print()
    
    def display_playoff_picture(self):
        """Display current playoff picture and magic numbers"""
        team_stats = self.nhl_collector.get_team_stats()
        
        def get_conference(team_name):
            return 'East' if any(team in team_name for team in self.eastern_teams) else 'West'
        
        if team_stats is not None:
            team_stats['CONFERENCE'] = team_stats['TEAM'].map(get_conference)
            
            print("\n=== PLAYOFF PICTURE ===")
            print(f"Updated as of: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("2024-25 NHL Season\n")
            
            for conference in ['East', 'West']:
                print(f"\n{conference}ern Conference Playoff Race:")
                print("=" * 85)
                
                conf_teams = team_stats[team_stats['CONFERENCE'] == conference].sort_values('PTS', ascending=False)
                
                # Calculate games remaining and points pace
                conf_teams['GAMES_REMAINING'] = 82 - conf_teams['GP']
                conf_teams['POINTS_PACE'] = (conf_teams['PTS'] / conf_teams['GP'] * 82).round()
                
                print(f"{'Pos':<4}{'Team':<25}{'PTS':<6}{'GP':<5}{'REM':<5}{'PACE':<6}{'Last 10':<8}{'Status':<15}")
                print("-" * 85)
                
                for idx, team in conf_teams.iterrows():
                    pos = conf_teams.index.get_loc(idx) + 1
                    points_behind = team['PTS'] - conf_teams.iloc[7]['PTS'] if pos > 8 else None
                    
                    if pos <= 8:
                        status = "Playoff Position"
                    else:
                        status = f"{abs(points_behind)} pts back"
                    
                    print(f"{pos:<4}{team['TEAM']:<25}{team['PTS']:<6}{team['GP']:<5}"
                          f"{team['GAMES_REMAINING']:<5}{team['POINTS_PACE']:<6}"
                          f"{team.get('L10', '-'):<8}{status:<15}")
                    
                    if pos == 8:  # Playoff cutoff line
                        print("-" * 85)
        else:
            print("Error: Unable to fetch team stats")
    
    def simulate_and_display_playoffs(self):
        """Display comprehensive playoff predictions"""
        results = self.simulate_playoffs()
        
        print("\n=== 2024-25 NHL PLAYOFF PREDICTIONS ===")
        print(f"Updated as of: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display First Round Matchups
        print("\nPredicted First Round Matchups:")
        for conf in ['east', 'west']:
            print(f"\n{conf.upper()} Conference:")
            print("-" * 50)
            for matchup in results['first_round'][conf]:
                print(f"{matchup['matchup'][0]} vs {matchup['matchup'][1]}")
                print(f"Predicted Winner: {matchup['winner']} ({matchup['score']})")
        
        # Display Championship Probabilities
        print("\nChampionship Probabilities:")
        print("-" * 50)
        sorted_probs = sorted(results['probabilities'].items(), 
                            key=lambda x: x[1]['championship'], 
                            reverse=True)
        
        for team, probs in sorted_probs[:10]:  # Top 10 teams
            print(f"{team:<25} Cup: {probs['championship']:>5.1f}%  Conf Finals: {probs['conf_finals']:>5.1f}%")
    
    def run_multiple_simulations(self, num_sims=1000):
        """Run multiple playoff simulations to get probabilities"""
        team_stats = self.nhl_collector.get_team_stats()
        championship_counts = {}
        
        for _ in range(num_sims):
            results = self.simulate_playoffs()
            if results['finals']:
                winner = results['finals']['winner']
                championship_counts[winner] = championship_counts.get(winner, 0) + 1
        
        # Display Championship Probabilities
        print(f"\n=== CHAMPIONSHIP PROBABILITIES (Based on {num_sims} simulations) ===")
        print("-" * 50)
        
        # Sort by probability
        sorted_probs = sorted(championship_counts.items(), key=lambda x: x[1], reverse=True)
        for team, count in sorted_probs:
            prob = (count / num_sims) * 100
            print(f"{team:<25} {prob:.1f}%")
    
    def simulate_playoffs(self):
        """Simulate NHL playoff outcomes"""
        team_stats = self.nhl_collector.get_team_stats()
        
        # Add conference information
        team_stats['CONFERENCE'] = team_stats['TEAM_NAME'].apply(
            lambda x: 'East' if any(team in x for team in self.eastern_teams) else 'West'
        )
        
        results = {
            'first_round': {'east': [], 'west': []},
            'conf_finals': {'east': None, 'west': None},
            'finals': None,
            'probabilities': {}
        }
        
        # Run simulation
        for conf in ['East', 'West']:
            conf_teams = team_stats[team_stats['CONFERENCE'] == conf].sort_values('PTS', ascending=False).head(8)
            conf_key = conf.lower()
            
            # First round matchups (1v8, 2v7, 3v6, 4v5)
            matchups = [(0,7), (1,6), (2,5), (3,4)]
            
            for seed1, seed2 in matchups:
                team1 = conf_teams.iloc[seed1]
                team2 = conf_teams.iloc[seed2]
                winner = self._simulate_series(team1, team2)
                results['first_round'][conf_key].append({
                    'matchup': (team1['TEAM_NAME'], team2['TEAM_NAME']),
                    'winner': winner['TEAM_NAME'],
                    'score': self._generate_series_score()
                })
        
        return results

    def _simulate_series(self, team1, team2):
        """Simulate a playoff series between two teams"""
        team1_strength = team1['PTS'] + (team1['GF'] - team1['GA']) * 2
        team2_strength = team2['PTS'] + (team2['GF'] - team2['GA']) * 2
        win_prob = team1_strength / (team1_strength + team2_strength)
        return team1 if np.random.random() < win_prob else team2

    def _generate_series_score(self):
        """Generate a realistic playoff series score"""
        scores = ['4-0', '4-1', '4-2', '4-3']
        weights = [0.15, 0.25, 0.35, 0.25]
        return np.random.choice(scores, p=weights)

    def predict_season_outcomes(self):
        """Comprehensive predictions for regular season and playoffs"""
        team_stats = self.nhl_collector.get_team_stats()
        
        # Add conference information - Changed TEAM_NAME to TEAM
        team_stats['CONFERENCE'] = team_stats['TEAM'].apply(
            lambda x: 'East' if any(team in x for team in self.eastern_teams) else 'West'
        )
        
        # Project final records
        team_stats['GAMES_REMAINING'] = 82 - team_stats['GP']
        team_stats['POINTS_PCT'] = team_stats['PTS'] / (team_stats['GP'] * 2)
        team_stats['PROJECTED_PTS'] = team_stats['PTS'] + (team_stats['POINTS_PCT'] * 2 * team_stats['GAMES_REMAINING'])
        team_stats['PROJECTED_WINS'] = team_stats['W'] + (team_stats['W'] / team_stats['GP'] * team_stats['GAMES_REMAINING'])
        
        print("\n=== 2024-25 SEASON PREDICTIONS ===")
        print(f"Updated as of: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display projected standings
        for conference in ['East', 'West']:
            print(f"\n{conference}ern Conference Projected Final Standings:")
            print("=" * 90)
            print(f"{'Rank':<6}{'Team':<25}{'Current':<12}{'Projected':<12}{'Playoff Odds':<12}")
            print(f"{'':6}{'':25}{'PTS-GP':<12}{'PTS-W':<12}{'%':<12}")
            print("-" * 90)
            
            conf_teams = team_stats[team_stats['CONFERENCE'] == conference].sort_values('PROJECTED_PTS', ascending=False)
            
            for idx, team in conf_teams.iterrows():
                rank = conf_teams.index.get_loc(idx) + 1
                playoff_odds = "100%" if rank <= 8 else f"{max(0, 100 - (rank-8)*12):.1f}%"
                
                # Format each component separately
                current = f"{int(team['PTS'])}-{int(team['GP'])}"
                projected = f"{int(team['PROJECTED_PTS'])}-{int(team['PROJECTED_WINS'])}"
                
                # Changed TEAM_NAME to TEAM here
                print(f"{rank:<6}"
                      f"{team['TEAM']:<25}"
                      f"{current:<12}"
                      f"{projected:<12}"
                      f"{playoff_odds:<12}")
                
                if rank == 8:
                    print("-" * 90)
    
    def predict_team_points(self):
        """Predict final point totals and scoring for each team"""
        team_stats = self.nhl_collector.get_team_stats()
        
        # Calculate per-game metrics
        team_stats['GF_PER_GAME'] = team_stats['GF'] / team_stats['GP']
        team_stats['GA_PER_GAME'] = team_stats['GA'] / team_stats['GP']
        team_stats['POINTS_PER_GAME'] = team_stats['PTS'] / team_stats['GP']
        team_stats['GAMES_REMAINING'] = 82 - team_stats['GP']
        
        # Project rest of season
        team_stats['PROJECTED_GF'] = team_stats['GF'] + (team_stats['GF_PER_GAME'] * team_stats['GAMES_REMAINING'])
        team_stats['PROJECTED_GA'] = team_stats['GA'] + (team_stats['GA_PER_GAME'] * team_stats['GAMES_REMAINING'])
        team_stats['PROJECTED_PTS'] = team_stats['PTS'] + (team_stats['POINTS_PER_GAME'] * team_stats['GAMES_REMAINING'])
        
        print("\n=== TEAM POINTS PREDICTIONS ===")
        print(f"Updated as of: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nProjected Season Totals:")
        print("=" * 100)
        print(f"{'Team':<25}{'Current':<20}{'Projected':<25}{'Pace':<15}{'Over/Under':<15}")
        print(f"{'':25}{'PTS-GF-GA':<20}{'PTS-GF-GA':<25}{'Per Game':<15}{'82 Games':<15}")
        print("-" * 100)
        
        # Sort by projected points
        sorted_teams = team_stats.sort_values('PROJECTED_PTS', ascending=False)
        
        for _, team in sorted_teams.iterrows():
            current = f"{int(team['PTS'])}-{int(team['GF'])}-{int(team['GA'])}"
            projected = f"{int(team['PROJECTED_PTS'])}-{int(team['PROJECTED_GF'])}-{int(team['PROJECTED_GA'])}"
            pace = f"{team['POINTS_PER_GAME']:.2f}"
            
            # Calculate if team is on pace for over/under their current total
            trend = "↑" if team['POINTS_PER_GAME'] > (team['PTS'] / team['GP']) else "↓"
            
            print(f"{team['TEAM']:<25}{current:<20}{projected:<25}{pace:<15}{trend:<15}")
        
        # Add detailed scoring predictions
        print("\n=== SCORING PREDICTIONS ===")
        print("Top 5 Highest Scoring Teams (Projected GF):")
        print("-" * 50)
        top_scoring = sorted_teams.nlargest(5, 'PROJECTED_GF')
        for _, team in top_scoring.iterrows():
            print(f"{team['TEAM']:<25}{int(team['PROJECTED_GF'])} goals")
        
        print("\nTop 5 Best Defensive Teams (Projected GA):")
        print("-" * 50)
        top_defense = sorted_teams.nsmallest(5, 'PROJECTED_GA')
        for _, team in top_defense.iterrows():
            print(f"{team['TEAM']:<25}{int(team['PROJECTED_GA'])} goals against")
        
        # Add point total analysis
        print("\n=== POINT TOTAL ANALYSIS ===")
        print("Teams Most Likely to Exceed Current Pace:")
        print("-" * 50)
        
        # Calculate momentum (last 10 games vs season average)
        team_stats['RECENT_PPG'] = team_stats['PTS'] / team_stats['GP']  # Simplified for example
        team_stats['MOMENTUM'] = team_stats['RECENT_PPG'] - team_stats['POINTS_PER_GAME']
        
        momentum_teams = team_stats.nlargest(5, 'MOMENTUM')
        for _, team in momentum_teams.iterrows():
            print(f"{team['TEAM']:<25}Current: {int(team['PTS'])} pts, Projected: {int(team['PROJECTED_PTS'])} pts")
        
        return team_stats

def main():
    print("Starting Complete NHL Season Analysis...")
    simulator = NHLPlayoffSimulator()
    
    # Get current data
    team_stats = simulator.nhl_collector.get_team_stats()
    if team_stats is None:
        print("Error: Could not fetch NHL data. Please check your internet connection and try again.")
        return
    
    if len(team_stats) == 0:
        print("Error: No team data available")
        return
        
    print(f"Data last updated: {simulator.nhl_collector.last_updated}")
    
    # Only run the working methods
    simulator.display_current_standings()
    simulator.display_playoff_picture()
    simulator.predict_team_points()

if __name__ == "__main__":
    main()
