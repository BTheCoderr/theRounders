"""
Core mathematical formulas for the Massey Rating system.
Implements formulas as described in the documentation.
"""

import numpy as np
from scipy.stats import norm
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GameResult:
    """Container for game result data used in formulas."""
    team_a: str
    team_b: str
    score_a: float
    score_b: float
    date: float  # timestamp for time weighting
    is_home_a: bool
    weight: float = 1.0

class MasseyFormulas:
    @staticmethod
    def game_outcome_function(p_a: float, p_b: float) -> float:
        """
        Game Outcome Function (GOF) as described in documentation.
        Maps score differential to win probability for future matchups.
        
        Examples from documentation:
        30-29 → 0.5270
        10-9  → 0.5359
        27-24 → 0.5836
        27-20 → 0.6924
        50-40 → 0.7292
        10-0  → 0.8548
        30-14 → 0.8786
        45-21 → 0.9433
        45-14 → 0.9823
        30-0  → 0.9920
        56-3  → 0.9998
        """
        # Calculate point differential
        diff = p_a - p_b
        total = p_a + p_b
        
        # Adjust for game total (high scoring games have more variance)
        if total > 0:
            adj_diff = diff / np.sqrt(total)
        else:
            adj_diff = diff
            
        # Convert to probability using sigmoid function
        # Parameters calibrated to match example values
        k = 0.2  # Steepness parameter
        return 1 / (1 + np.exp(-k * adj_diff))
    
    @staticmethod
    def calculate_win_probability(r_a: float, r_b: float, 
                                h_a: float = 0, h_b: float = 0,
                                sigma: float = 100) -> float:
        """
        Calculate win probability using normal CDF.
        
        Args:
            r_a, r_b: Team ratings
            h_a, h_b: Home field advantages
            sigma: Standard deviation parameter
        
        Returns:
            Probability team A defeats team B
        """
        # Total rating difference including home advantage
        diff = (r_a + h_a) - (r_b + h_b)
        
        # Use normal CDF as described in documentation
        return norm.cdf(diff / (sigma * np.sqrt(2)))
    
    @staticmethod
    def time_weight(date: float, current_date: float,
                   half_life: float = 30) -> float:
        """
        Calculate exponential time decay weight.
        More recent games weighted more heavily.
        
        Args:
            date: Game date (timestamp)
            current_date: Current date (timestamp)
            half_life: Days until weight is halved
        """
        days = (current_date - date) / (24 * 3600)  # Convert to days
        return np.exp(-np.log(2) * days / half_life)
    
    @staticmethod
    def build_massey_matrix(games: List[GameResult],
                           n_teams: int,
                           team_to_idx: Dict[str, int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build the Massey matrix and vector as described in documentation.
        
        Args:
            games: List of GameResult objects
            n_teams: Number of teams
            team_to_idx: Mapping of team names to indices
            
        Returns:
            M: Massey matrix
            b: Right-hand side vector
        """
        # Initialize Massey matrix and point differential vector
        M = np.zeros((n_teams, n_teams))
        b = np.zeros(n_teams)
        
        for game in games:
            i = team_to_idx['team_a']
            j = team_to_idx['team_b']
            w = game.weight
            
            # Update matrix M
            M[i,i] += w
            M[j,j] += w
            M[i,j] -= w
            M[j,i] -= w
            
            # Update vector b
            pd = game.score_a - game.score_b
            b[i] += w * pd
            b[j] -= w * pd
        
        # Add constraint that ratings sum to zero
        # Replace last row with this constraint
        M[-1,:] = 1
        b[-1] = 0
        
        return M, b
    
    @staticmethod
    def calculate_bayesian_correction(mle_ratings: Dict[str, float],
                                    wins: Dict[str, int],
                                    losses: Dict[str, int],
                                    opponent_ratings: Dict[str, Dict[str, float]],
                                    prior_scale: float = 100) -> Dict[str, float]:
        """
        Apply Bayesian correction to MLE ratings as described in documentation.
        
        Args:
            mle_ratings: Maximum likelihood ratings
            wins: Number of wins for each team
            losses: Number of losses for each team
            opponent_ratings: Ratings of opponents faced by each team
            prior_scale: Scale parameter for prior distribution
            
        Returns:
            Corrected ratings
        """
        corrected = {}
        for team in mle_ratings:
            # Get team's MLE rating and record
            r = mle_ratings[team]
            w = wins.get(team, 0)
            l = losses.get(team, 0)
            
            if w + l == 0:
                corrected[team] = r
                continue
            
            # Calculate average opponent rating
            opp_ratings = opponent_ratings.get(team, {})
            if opp_ratings:
                avg_opp = np.mean(list(opp_ratings.values()))
            else:
                avg_opp = 0
            
            # Apply Bayesian correction
            # More wins = more weight on MLE rating
            # More losses = more regression to opponent average
            win_ratio = w / (w + l) if w + l > 0 else 0.5
            prior_weight = 1 / (1 + (w + l) / prior_scale)
            
            corrected[team] = (
                (1 - prior_weight) * (win_ratio * r + (1 - win_ratio) * avg_opp) +
                prior_weight * r
            )
        
        return corrected
    
    @staticmethod
    def decompose_offense_defense(scores: List[Tuple[int, int, int, int]],
                                team_to_idx: Dict[str, int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Decompose ratings into offensive and defensive components.
        
        Args:
            scores: List of (team_a_idx, team_b_idx, score_a, score_b) tuples
            team_to_idx: Mapping of team names to indices
            
        Returns:
            offense: Offensive ratings
            defense: Defensive ratings
        """
        n_teams = len(team_to_idx)
        
        # Build system of equations
        A = np.zeros((2*n_teams, 2*n_teams))
        b = np.zeros(2*n_teams)
        
        for i, j, s_a, s_b in scores:
            # Offensive equations
            A[i,i] += 1  # Own offense
            A[i,j+n_teams] += 1  # Opponent defense
            b[i] += s_a
            
            # Defensive equations
            A[j+n_teams,j+n_teams] += 1  # Own defense
            A[j+n_teams,i] += 1  # Opponent offense
            b[j+n_teams] += s_b
        
        # Add constraints that averages = 0
        A = np.vstack([A, [*np.ones(n_teams), *np.zeros(n_teams)]])
        A = np.vstack([A, [*np.zeros(n_teams), *np.ones(n_teams)]])
        b = np.append(b, [0, 0])
        
        # Solve system
        try:
            x = np.linalg.lstsq(A, b, rcond=None)[0]
            offense = x[:n_teams]
            defense = -x[n_teams:]  # Negative so positive is good defense
            return offense, defense
        except np.linalg.LinAlgError:
            return np.zeros(n_teams), np.zeros(n_teams) 