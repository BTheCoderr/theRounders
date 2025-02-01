import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class TeamStats:
    """Container for team statistics."""
    rating: float
    power: float
    offense: float
    defense: float
    home_advantage: float
    schedule_strength: float
    expected_wins: float
    expected_losses: float
    std_dev: float
    parity_index: float

class RatingStatistics:
    def __init__(self, elos_ratings):
        """Initialize with an ElosRatings instance."""
        self.ratings = elos_ratings
    
    def calculate_power_ratings(self) -> Dict[str, float]:
        """
        Calculate power ratings that measure potential rather than past performance.
        Uses Bayesian smoothing and recent game weighting.
        """
        base_ratings = self.ratings.calculate_ratings()
        recent_perf = self._calculate_recent_performance()
        
        power_ratings = {}
        for team in self.ratings.teams:
            # Blend base rating with recent performance
            base = base_ratings[team]
            recent = recent_perf.get(team, base)
            power_ratings[team] = 0.7 * base + 0.3 * recent
        
        return power_ratings
    
    def _calculate_recent_performance(self) -> Dict[str, float]:
        """Helper method to calculate recent performance metrics."""
        recent_games = sorted(self.ratings.games, key=lambda g: g.date)[-5:]
        
        performances = {}
        for game in recent_games:
            # Calculate performance rating for team_a
            margin = game.score_a - game.score_b
            opp_rating = self.ratings.calculate_ratings()[game.team_b]
            perf_a = margin + opp_rating
            
            # Update running average
            if game.team_a not in performances:
                performances[game.team_a] = []
            performances[game.team_a].append(perf_a)
            
            # Do the same for team_b
            perf_b = -margin + self.ratings.calculate_ratings()[game.team_a]
            if game.team_b not in performances:
                performances[game.team_b] = []
            performances[game.team_b].append(perf_b)
        
        # Calculate weighted averages
        recent_ratings = {}
        for team, perfs in performances.items():
            # More weight to recent games
            weights = np.exp(np.linspace(-1, 0, len(perfs)))
            recent_ratings[team] = np.average(perfs, weights=weights)
        
        return recent_ratings
    
    def calculate_offense_defense_ratings(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Split team strength into offensive and defensive components.
        Uses scoring patterns and opponent adjustments.
        """
        games = self.ratings.games
        n_teams = len(self.ratings.teams)
        team_to_idx = {team: i for i, team in enumerate(self.ratings.teams)}
        
        # Build matrices for offense/defense decomposition
        A = np.zeros((2*n_teams, 2*n_teams))
        b = np.zeros(2*n_teams)
        
        for game in games:
            i = team_to_idx[game.team_a]
            j = team_to_idx[game.team_b]
            
            # Offensive contribution
            A[i, i] += 1  # Own offense
            A[i, j+n_teams] += 1  # Opponent defense
            b[i] += game.score_a
            
            # Defensive contribution
            A[j+n_teams, j+n_teams] += 1  # Own defense
            A[j+n_teams, i] += 1  # Opponent offense
            b[j+n_teams] += game.score_b
        
        # Add constraint that average offense = average defense = 0
        constraint_row = np.ones(n_teams)
        A = np.vstack([A, [*constraint_row, *np.zeros(n_teams)]])
        A = np.vstack([A, [*np.zeros(n_teams), *constraint_row]])
        b = np.append(b, [0, 0])
        
        try:
            # Solve system
            x = np.linalg.lstsq(A, b, rcond=None)[0]
            
            # Split into offense and defense ratings
            offense = {team: x[i] for team, i in team_to_idx.items()}
            defense = {team: -x[i+n_teams] for team, i in team_to_idx.items()}
            
            return offense, defense
            
        except np.linalg.LinAlgError:
            # Fallback to simpler calculation if system is singular
            return self._calculate_simple_off_def()
    
    def _calculate_simple_off_def(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Simplified offense/defense calculation as fallback."""
        offense = {team: 0.0 for team in self.ratings.teams}
        defense = {team: 0.0 for team in self.ratings.teams}
        
        for game in self.ratings.games:
            # Update offensive ratings
            offense[game.team_a] += game.score_a
            offense[game.team_b] += game.score_b
            
            # Update defensive ratings
            defense[game.team_a] += game.score_b
            defense[game.team_b] += game.score_a
        
        # Average and normalize
        for team in self.ratings.teams:
            games_played = len([g for g in self.ratings.games 
                              if g.team_a == team or g.team_b == team])
            if games_played > 0:
                offense[team] /= games_played
                defense[team] /= games_played
        
        # Center ratings
        off_mean = np.mean(list(offense.values()))
        def_mean = np.mean(list(defense.values()))
        
        for team in self.ratings.teams:
            offense[team] -= off_mean
            defense[team] -= def_mean
        
        return offense, defense
    
    def calculate_schedule_strength(self) -> Dict[str, float]:
        """
        Calculate schedule strength based on opponent ratings.
        Accounts for home/away games and opponent's power rating.
        """
        power_ratings = self.calculate_power_ratings()
        schedule_strength = {}
        
        for team in self.ratings.teams:
            # Get all games involving this team
            team_games = [g for g in self.ratings.games 
                         if g.team_a == team or g.team_b == team]
            
            if not team_games:
                schedule_strength[team] = 0.0
                continue
            
            # Calculate average opponent strength
            total_strength = 0.0
            for game in team_games:
                opp = game.team_b if game.team_a == team else game.team_a
                opp_rating = power_ratings[opp]
                
                # Adjust for home/away
                if (game.team_a == team and game.is_home_a) or \
                   (game.team_b == team and not game.is_home_a):
                    # Home game
                    opp_rating += 50  # Typical home advantage
                
                total_strength += opp_rating
            
            schedule_strength[team] = total_strength / len(team_games)
        
        return schedule_strength
    
    def calculate_expected_wins_losses(self) -> Dict[str, Tuple[float, float]]:
        """
        Calculate expected wins and losses for remaining schedule.
        Uses power ratings and home advantage.
        """
        power_ratings = self.calculate_power_ratings()
        expected = {team: [0.0, 0.0] for team in self.ratings.teams}
        
        for game in self.ratings.games:
            p_a = self.ratings.predict_game(game.team_a, game.team_b)
            
            # Update expected W-L
            expected[game.team_a][0] += p_a
            expected[game.team_a][1] += (1 - p_a)
            expected[game.team_b][0] += (1 - p_a)
            expected[game.team_b][1] += p_a
        
        return {team: tuple(vals) for team, vals in expected.items()}
    
    def calculate_parity_indices(self) -> Dict[str, float]:
        """
        Calculate parity indices to measure competitive balance.
        1.0 indicates perfect parity, 0.0 indicates complete imbalance.
        """
        ratings = self.ratings.calculate_ratings()
        
        # Calculate standard deviation of ratings
        rating_std = np.std(list(ratings.values()))
        
        # Calculate parity index for each team's games
        parity = {}
        for team in self.ratings.teams:
            team_games = [g for g in self.ratings.games 
                         if g.team_a == team or g.team_b == team]
            
            if not team_games:
                parity[team] = 1.0  # Default to perfect parity if no games
                continue
            
            # Calculate rating differences in team's games
            diffs = []
            for game in team_games:
                r_a = ratings[game.team_a]
                r_b = ratings[game.team_b]
                diffs.append(abs(r_a - r_b))
            
            # Convert to parity index
            avg_diff = np.mean(diffs)
            parity[team] = 1.0 / (1.0 + avg_diff/rating_std)
        
        return parity
    
    def get_complete_team_stats(self) -> Dict[str, TeamStats]:
        """
        Get comprehensive statistics for each team.
        Returns a dictionary mapping team names to TeamStats objects.
        """
        # Calculate all metrics
        ratings = self.ratings.calculate_ratings()
        power = self.calculate_power_ratings()
        offense, defense = self.calculate_offense_defense_ratings()
        schedule = self.calculate_schedule_strength()
        exp_wl = self.calculate_expected_wins_losses()
        parity = self.calculate_parity_indices()
        
        # Calculate standard deviations
        conf = self.ratings.calculate_rating_confidence()
        
        stats = {}
        for team in self.ratings.teams:
            stats[team] = TeamStats(
                rating=ratings[team],
                power=power[team],
                offense=offense[team],
                defense=defense[team],
                home_advantage=50.0,  # Default value
                schedule_strength=schedule[team],
                expected_wins=exp_wl[team][0],
                expected_losses=exp_wl[team][1],
                std_dev=conf[team]['std_error'],
                parity_index=parity[team]
            )
        
        return stats 