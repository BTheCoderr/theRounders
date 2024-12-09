import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sports_betting.data_collection.nba import NBADataCollector

class NBAPlayoffSimulator:
    def __init__(self):
        self.nba_collector = NBADataCollector()
        self.eastern_teams = [
            'Celtics', 'Bucks', '76ers', 'Heat', 'Knicks', 'Cavaliers', 
            'Hawks', 'Nets', 'Bulls', 'Raptors', 'Pacers', 'Hornets', 
            'Wizards', 'Pistons', 'Magic'
        ]
        self.results = {
            'first_round': {'east': [], 'west': []},
            'semifinals': {'east': [], 'west': []},
            'conf_finals': {'east': None, 'west': None},
            'finals': None
        }
    
    def simulate_and_visualize(self):
        """Run complete playoff simulation and create visualization"""
        print("\n🏀 2024 NBA PLAYOFF SIMULATOR 🏀")
        team_stats = self.nba_collector.get_team_stats()
        
        if team_stats is None:
            print("Error: Could not retrieve team stats")
            return
        
        # Process team data
        team_stats['CONFERENCE'] = team_stats['TEAM_NAME'].apply(
            lambda x: 'East' if any(team in x for team in self.eastern_teams) else 'West'
        )
        team_stats['STRENGTH'] = (
            0.35 * team_stats['W_PCT'] +
            0.25 * (team_stats['PLUS_MINUS'] / team_stats['PLUS_MINUS'].max()) +
            0.20 * (team_stats['PTS'] / team_stats['PTS'].max()) +
            0.20 * team_stats['FG_PCT']
        )
        
        # Separate conferences
        self.east = team_stats[team_stats['CONFERENCE'] == 'East'].sort_values('STRENGTH', ascending=False).head(8)
        self.west = team_stats[team_stats['CONFERENCE'] == 'West'].sort_values('STRENGTH', ascending=False).head(8)
        
        # Simulate all rounds and store results
        print("\n=== FIRST ROUND ===")
        
        # Eastern Conference First Round
        print("\nEASTERN CONFERENCE - First Round:")
        east_winners = []
        for i in range(4):
            team1 = self.east.iloc[i]
            team2 = self.east.iloc[7-i]
            winner, games, score = self.predict_series(team1, team2)
            east_winners.append(winner)
            self.results['first_round']['east'].append({
                'matchup': (team1['TEAM_NAME'], team2['TEAM_NAME']),
                'winner': winner['TEAM_NAME'],
                'score': score,
                'games': games
            })
            
            print(f"\n{i+1}) {team1['TEAM_NAME']} vs ({8-i}) {team2['TEAM_NAME']}")
            print(f"Series Winner: {winner['TEAM_NAME']} ({score})")
            for game in games:
                print(f"Game {game['game']}: {game['team1_score']} - {game['team2_score']}")
        
        # Western Conference First Round
        print("\nWESTERN CONFERENCE - First Round:")
        west_winners = []
        for i in range(4):
            team1 = self.west.iloc[i]
            team2 = self.west.iloc[7-i]
            winner, games, score = self.predict_series(team1, team2)
            west_winners.append(winner)
            self.results['first_round']['west'].append({
                'matchup': (team1['TEAM_NAME'], team2['TEAM_NAME']),
                'winner': winner['TEAM_NAME'],
                'score': score,
                'games': games
            })
            
            print(f"\n{i+1}) {team1['TEAM_NAME']} vs ({8-i}) {team2['TEAM_NAME']}")
            print(f"Series Winner: {winner['TEAM_NAME']} ({score})")
            for game in games:
                print(f"Game {game['game']}: {game['team1_score']} - {game['team2_score']}")
        
        # Simulate Eastern Conference Semifinals
        print("\n=== EASTERN CONFERENCE - SEMIFINALS ===")
        east_semis = [east_winners[0], east_winners[1]]
        east_winner, games, score = self.predict_series(east_semis[0], east_semis[1])
        self.results['semifinals']['east'] = {
            'winner': east_winner['TEAM_NAME'],
            'score': score,
            'games': games
        }
        
        print(f"\nEASTERN CONFERENCE - Semifinals: {east_semis[0]['TEAM_NAME']} vs {east_semis[1]['TEAM_NAME']}")
        print(f"Series Winner: {east_winner['TEAM_NAME']} ({score})")
        for game in games:
            print(f"Game {game['game']}: {game['team1_score']} - {game['team2_score']}")
        
        # Simulate Western Conference Semifinals
        print("\n=== WESTERN CONFERENCE - SEMIFINALS ===")
        west_semis = [west_winners[0], west_winners[1]]
        west_winner, games, score = self.predict_series(west_semis[0], west_semis[1])
        self.results['semifinals']['west'] = {
            'winner': west_winner['TEAM_NAME'],
            'score': score,
            'games': games
        }
        
        print(f"\nWESTERN CONFERENCE - Semifinals: {west_semis[0]['TEAM_NAME']} vs {west_semis[1]['TEAM_NAME']}")
        print(f"Series Winner: {west_winner['TEAM_NAME']} ({score})")
        for game in games:
            print(f"Game {game['game']}: {game['team1_score']} - {game['team2_score']}")
        
        # Simulate Eastern Conference Finals
        print("\n=== EASTERN CONFERENCE - FINALS ===")
        east_finals = [east_winner, west_winner]
        east_winner, games, score = self.predict_series(east_finals[0], east_finals[1])
        self.results['conf_finals']['east'] = {
            'winner': east_winner['TEAM_NAME'],
            'score': score,
            'games': games
        }
        
        print(f"\nEASTERN CONFERENCE - Finals: {east_finals[0]['TEAM_NAME']} vs {east_finals[1]['TEAM_NAME']}")
        print(f"Series Winner: {east_winner['TEAM_NAME']} ({score})")
        for game in games:
            print(f"Game {game['game']}: {game['team1_score']} - {game['team2_score']}")
        
        # Simulate Western Conference Finals
        print("\n=== WESTERN CONFERENCE - FINALS ===")
        west_finals = [west_winner, east_winner]
        west_winner, games, score = self.predict_series(west_finals[0], west_finals[1])
        self.results['conf_finals']['west'] = {
            'winner': west_winner['TEAM_NAME'],
            'score': score,
            'games': games
        }
        
        print(f"\nWESTERN CONFERENCE - Finals: {west_finals[0]['TEAM_NAME']} vs {west_finals[1]['TEAM_NAME']}")
        print(f"Series Winner: {west_winner['TEAM_NAME']} ({score})")
        for game in games:
            print(f"Game {game['game']}: {game['team1_score']} - {game['team2_score']}")
        
        # Simulate NBA Finals
        print("\n=== NBA FINALS ===")
        champion, games, score = self.predict_series(east_winner, west_winner)
        self.results['finals'] = {
            'winner': champion['TEAM_NAME'],
            'score': score,
            'games': games
        }
        
        print(f"\nNBA Finals: {east_winner['TEAM_NAME']} vs {west_winner['TEAM_NAME']}")
        print(f"Series Winner: {champion['TEAM_NAME']} ({score})")
        for game in games:
            print(f"Game {game['game']}: {game['team1_score']} - {game['team2_score']}")
        
        # Visualize playoff bracket
        self.visualize_playoff_bracket()
    
    def visualize_playoff_bracket(self):
        """Create a simple, clear playoff bracket visualization"""
        plt.figure(figsize=(20, 12))
        
        def draw_matchup(ax, x, y, team1, team2, winner, score, round_num):
            # Draw box
            width = 0.25
            height = 0.1
            rect = plt.Rectangle((x, y), width, height, facecolor='white', edgecolor='black')
            ax.add_patch(rect)
            
            # Add team names and score
            ax.text(x + width/2, y + height/2, 
                   f"{team1} vs {team2}\n{winner} ({score})", 
                   ha='center', va='center', fontsize=8)
            
            return x + width, y + height/2  # Return connection point for next round
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))
        ax1.set_title('Eastern Conference', pad=20, color='#17408B')
        ax2.set_title('Western Conference', pad=20, color='#C9082A')
        
        # Set up axes
        for ax in [ax1, ax2]:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Draw brackets for each conference
        for conf, ax, results in [('east', ax1, self.results['first_round']['east']), 
                                ('west', ax2, self.results['first_round']['west'])]:
            # First round (4 matchups)
            y_positions = [0.8, 0.6, 0.4, 0.2]
            round1_endpoints = []
            for i, match in enumerate(results):
                end_point = draw_matchup(ax, 0.05, y_positions[i], 
                                      match['matchup'][0], match['matchup'][1],
                                      match['winner'], match['score'], 1)
                round1_endpoints.append(end_point)
            
            # Draw lines connecting to semifinals
            if self.results['semifinals'][conf]:
                semis = self.results['semifinals'][conf]
                # Draw connecting lines and semifinal matchups
                semi_y = (y_positions[0] + y_positions[1]) / 2
                end_point = draw_matchup(ax, 0.4, semi_y,
                                       round1_endpoints[0][0], round1_endpoints[1][0],
                                       semis['winner'], semis['score'], 2)
                
                # Draw lines to conference finals
                if self.results['conf_finals'][conf]:
                    conf_finals = self.results['conf_finals'][conf]
                    finals_y = 0.5
                    draw_matchup(ax, 0.7, finals_y,
                               semis['winner'], "Winner of other bracket",
                               conf_finals['winner'], conf_finals['score'], 3)
        
        # Add NBA Finals result at the bottom
        if self.results['finals']:
            plt.figtext(0.5, 0.05,
                       f"NBA FINALS CHAMPION: {self.results['finals']['winner']} ({self.results['finals']['score']})",
                       ha='center', fontsize=12, weight='bold')
        
        plt.subplots_adjust(wspace=0.1)
        plt.show()
    
    def predict_series(self, team1, team2):
        """Predict playoff series outcome with game details"""
        strength_diff = team1['STRENGTH'] - team2['STRENGTH']
        home_advantage = 0.05
        
        team1_wins = 0
        team2_wins = 0
        games = []
        
        while team1_wins < 4 and team2_wins < 4:
            game_number = len(games) + 1
            if game_number in [1, 2, 5, 7]:
                game_strength_diff = strength_diff + home_advantage
            else:
                game_strength_diff = strength_diff - home_advantage
            
            base_score = 100
            team1_score = int(base_score + (game_strength_diff * 10) + np.random.normal(0, 5))
            team2_score = int(base_score + np.random.normal(0, 5))
            
            if team1_score > team2_score:
                team1_wins += 1
                winner = team1['TEAM_NAME']
            else:
                team2_wins += 1
                winner = team2['TEAM_NAME']
            
            games.append({
                'game': game_number,
                'team1_score': team1_score,
                'team2_score': team2_score,
                'winner': winner
            })
        
        return team1 if team1_wins == 4 else team2, games, f"{team1_wins}-{team2_wins}"
    
    def predict_season_outcomes(self):
        """Predict regular season outcomes and future trends"""
        team_stats = self.nba_collector.get_team_stats()
        
        # Add conference information
        team_stats['CONFERENCE'] = team_stats['TEAM_NAME'].apply(
            lambda x: 'East' if any(team in x for team in self.eastern_teams) else 'West'
        )
        
        # Calculate projected final records
        TOTAL_GAMES = 82
        team_stats['GAMES_REMAINING'] = TOTAL_GAMES - team_stats['GP']
        team_stats['PROJECTED_FINAL_WINS'] = team_stats['W'] + (team_stats['W_PCT'] * team_stats['GAMES_REMAINING']).round()
        team_stats['PROJECTED_FINAL_LOSSES'] = TOTAL_GAMES - team_stats['PROJECTED_FINAL_WINS']
        
        # Calculate playoff probability
        team_stats['PLAYOFF_PROB'] = (
            (team_stats['W_PCT'] * 0.7) + 
            (team_stats['PLUS_MINUS'] / team_stats['PLUS_MINUS'].max() * 0.3)
        ) * 100
        
        # Print predictions
        print("\n=== 2024 NBA SEASON PREDICTIONS ===")
        print("\nProjected Final Standings:")
        
        for conference in ['East', 'West']:
            conf_teams = team_stats[team_stats['CONFERENCE'] == conference].sort_values(
                'PROJECTED_FINAL_WINS', ascending=False
            )
            
            print(f"\n{conference}ern Conference:")
            print("=" * 75)
            print(f"{'Team':<30} {'Current':<15} {'Projected':<15} {'Playoff %':<10}")
            print(f"{'':30} {'Record':<15} {'Final Record':<15}")
            print("-" * 75)
            
            for _, team in conf_teams.iterrows():
                current_record = f"{team['W']}-{team['L']}"
                projected_record = f"{int(team['PROJECTED_FINAL_WINS'])}-{int(team['PROJECTED_FINAL_LOSSES'])}"
                print(f"{team['TEAM_NAME']:<30} {current_record:<15} {projected_record:<15} {team['PLAYOFF_PROB']:.1f}%")
        
        return team_stats

def main():
    simulator = NBAPlayoffSimulator()
    # Add season predictions
    simulator.predict_season_outcomes()
    # Run playoff simulation
    simulator.simulate_and_visualize()

if __name__ == "__main__":
    print("Starting Complete NBA Playoff Simulation...")
    main()