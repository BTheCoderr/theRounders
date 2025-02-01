from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from massey_ratings_base import Game

class ElosRatings:
    """
    Implements the Elos Rating method developed by Dr. Eugene Potanin.
    
    Key features:
    - Binary ratings representing win/loss ratios
    - Direct proportionality to game win percentages
    - Handles incomplete game schedules
    - Supports anti-ratings for relative weakness analysis
    """
    
    def __init__(self, teams: List[str], k: float = 32.0):
        """
        Initialize Elos Rating system.
        
        Args:
            teams: List of team names
            k: Rating adjustment factor (default 32.0)
        """
        self.teams = sorted(teams)
        self.k = k
        self.ratings: Dict[str, float] = {team: 1500.0 for team in teams}  # Initial rating 1500
        self.binary_ratings: Dict[Tuple[str, str], float] = {}  # (team_i, team_j) -> bij
        self.games: List[Game] = []
        
    def add_game(self, game: Game) -> None:
        """Add a game result and update ratings."""
        self.games.append(game)
        self._update_binary_ratings(game)
        self._update_ratings(game)
    
    def _update_binary_ratings(self, game: Game) -> None:
        """
        Update binary ratings bij based on game result.
        bij represents the win ratio in games between teams i and j.
        """
        team_pair = (game.team_a, game.team_b)
        if team_pair not in self.binary_ratings:
            self.binary_ratings[team_pair] = 0
            self.binary_ratings[(game.team_b, game.team_a)] = 0
        
        # Update win counts
        if game.score_a > game.score_b:
            self.binary_ratings[team_pair] += 1
        else:
            self.binary_ratings[(game.team_b, game.team_a)] += 1
    
    def _update_ratings(self, game: Game) -> None:
        """
        Update Elos ratings based on game result.
        Uses logistic probability function and K-factor adjustment.
        """
        # Get current ratings
        ra = self.ratings[game.team_a]
        rb = self.ratings[game.team_b]
        
        # Calculate expected probability
        ea = 1 / (1 + 10**((rb - ra)/400))
        
        # Calculate actual outcome (1 for win, 0 for loss)
        sa = 1.0 if game.score_a > game.score_b else 0.0
        
        # Update ratings
        delta = self.k * (sa - ea)
        self.ratings[game.team_a] += delta
        self.ratings[game.team_b] -= delta
    
    def get_binary_rating(self, team_i: str, team_j: str) -> float:
        """Get binary rating (win ratio) between two teams."""
        wins_ij = self.binary_ratings.get((team_i, team_j), 0)
        wins_ji = self.binary_ratings.get((team_j, team_i), 0)
        total_games = wins_ij + wins_ji
        return wins_ij / total_games if total_games > 0 else 0.5
    
    def calculate_ratings(self) -> Dict[str, float]:
        """
        Calculate final ratings using Elos method.
        
        This implements equation 6.2 from the paper:
        ri = Σj(bij * rj) / gi
        where:
        - bij is binary rating between teams i and j
        - rj is rating of team j
        - gi is number of games played by team i
        """
        n_teams = len(self.teams)
        M = np.zeros((n_teams, n_teams))
        
        # Build system matrix
        for i, team_i in enumerate(self.teams):
            games_i = 0
            for j, team_j in enumerate(self.teams):
                if i != j:
                    bij = self.get_binary_rating(team_i, team_j)
                    M[i,j] = bij
                    games_i += 1
            M[i,i] = -1  # Diagonal
            
        # Add constraint that ratings sum to a constant
        M[-1,:] = 1
        
        # Solve system
        b = np.zeros(n_teams)
        b[-1] = n_teams * 1500  # Sum of ratings equals average * n_teams
        
        try:
            r = np.linalg.solve(M, b)
            return {team: float(r[i]) for i, team in enumerate(self.teams)}
        except np.linalg.LinAlgError:
            return self.ratings  # Fall back to current ratings if system is singular
    
    def calculate_anti_ratings(self) -> Dict[str, float]:
        """
        Calculate anti-ratings to measure relative weakness.
        
        This implements equation 6.4 from the paper:
        gi = Σj Lij
        wij = Σj Lji
        where:
        - Lij is number of losses to team j
        - gi is total games played
        """
        anti_ratings = {}
        for team_i in self.teams:
            losses = sum(1 for g in self.games 
                       if (g.team_a == team_i and g.score_a < g.score_b) or
                          (g.team_b == team_i and g.score_b < g.score_a))
            games = sum(1 for g in self.games 
                       if g.team_a == team_i or g.team_b == team_i)
            anti_ratings[team_i] = losses / games if games > 0 else 0
            
        return anti_ratings
    
    def predict_game(self, team_a: str, team_b: str) -> float:
        """
        Predict probability of team_a winning against team_b.
        Uses both Elos ratings and binary ratings for prediction.
        """
        # Get Elos rating difference
        ra = self.ratings[team_a]
        rb = self.ratings[team_b]
        
        # Calculate base probability from ratings
        p_elos = 1 / (1 + 10**((rb - ra)/400))
        
        # Get binary rating if available
        p_binary = self.get_binary_rating(team_a, team_b)
        
        # Combine predictions (weighted average)
        # Weight binary rating more if teams have played each other
        games_played = len([g for g in self.games 
                          if (g.team_a == team_a and g.team_b == team_b) or
                             (g.team_a == team_b and g.team_b == team_a)])
        
        binary_weight = min(games_played / 5, 0.5)  # Cap at 0.5
        p = (1 - binary_weight) * p_elos + binary_weight * p_binary
        
        return p 

    def calculate_transition_matrix(self) -> np.ndarray:
        """
        Calculate the Markov chain transition matrix Q.
        
        As shown in the paper, the Elos system is equivalent to a continuous time
        Markov chain where:
        - Each team represents a state
        - Transitions occur when teams play games
        - qij = -wij (rate at which team i loses control to team j)
        - qii = Σj wij (total rate of losing control)
        """
        n_teams = len(self.teams)
        Q = np.zeros((n_teams, n_teams))
        
        # Calculate transition rates
        for i, team_i in enumerate(self.teams):
            for j, team_j in enumerate(self.teams):
                if i != j:
                    # Get win ratio of j over i
                    wij = self.get_binary_rating(team_j, team_i)
                    games_ij = len([g for g in self.games 
                                  if (g.team_a == team_i and g.team_b == team_j) or
                                     (g.team_a == team_j and g.team_b == team_i)])
                    
                    # Set transition rate
                    Q[i,j] = wij * games_ij
        
            # Set diagonal to negative sum of row
            Q[i,i] = -np.sum(Q[i,:])
        
        return Q

    def calculate_equilibrium_distribution(self) -> Dict[str, float]:
        """
        Calculate equilibrium probabilities of the Markov chain.
        
        These probabilities are proportional to the Elos ratings
        (up to a constant factor) and represent the long-term
        proportion of time the system spends in each state.
        """
        Q = self.calculate_transition_matrix()
        n_teams = len(self.teams)
        
        # Add constraint that probabilities sum to 1
        A = np.vstack([Q.T, np.ones(n_teams)])
        b = np.zeros(n_teams + 1)
        b[-1] = 1
        
        try:
            # Solve system to get equilibrium probabilities
            p = np.linalg.lstsq(A, b, rcond=None)[0]
            return {team: float(p[i]) for i, team in enumerate(self.teams)}
        except np.linalg.LinAlgError:
            return {team: 1/n_teams for team in self.teams}

    def calculate_market_values(self) -> Dict[str, float]:
        """
        Calculate team values using economic interpretation.
        
        As described in the paper, the Elos model can be viewed as a market where:
        - Teams exchange "products" (games)
        - Winning creates demand (wij)
        - Price is proportional to rating
        - Market reaches equilibrium when supply matches demand
        """
        n_teams = len(self.teams)
        
        # Calculate demand matrix (wij)
        W = np.zeros((n_teams, n_teams))
        for i, team_i in enumerate(self.teams):
            for j, team_j in enumerate(self.teams):
                if i != j:
                    W[i,j] = self.get_binary_rating(team_i, team_j)
        
        # Calculate total demand for each team
        demand = np.sum(W, axis=1)
        
        # Calculate market values (proportional to demand)
        total_value = n_teams * 1500  # Same scale as ratings
        values = demand / np.sum(demand) * total_value
        
        return {team: float(values[i]) for i, team in enumerate(self.teams)}

    def get_complete_analysis(self) -> Dict[str, Dict[str, float]]:
        """
        Get comprehensive analysis of team performance including:
        - Standard Elos ratings
        - Anti-ratings (relative weakness)
        - Market values
        - Equilibrium probabilities
        - Combined metrics
        """
        standard_ratings = self.calculate_ratings()
        anti_ratings = self.calculate_anti_ratings()
        market_values = self.calculate_market_values()
        equilibrium_probs = self.calculate_equilibrium_distribution()
        
        analysis = {}
        for team in self.teams:
            # Calculate combined rating using equation from paper
            r = standard_ratings[team]
            a = anti_ratings[team]
            combined = r * (1 - a)  # Higher rating, lower anti-rating is better
            
            analysis[team] = {
                'rating': standard_ratings[team],
                'anti_rating': anti_ratings[team],
                'market_value': market_values[team],
                'equilibrium_prob': equilibrium_probs[team],
                'combined_score': combined
            }
        
        return analysis 

    def analyze_markov_properties(self) -> Dict[str, Any]:
        """
        Analyze properties of the Markov chain representation.
        
        Returns:
            Dict containing:
            - eigenvalues: Principal eigenvalues of Q matrix
            - mixing_time: Estimated mixing time (time to convergence)
            - stationary_distribution: Equilibrium probabilities
            - convergence_rate: Rate of convergence to equilibrium
        """
        Q = self.calculate_transition_matrix()
        
        # Calculate eigenvalues
        try:
            eigenvals = np.linalg.eigvals(Q)
            # Sort by real part (descending)
            eigenvals = sorted(eigenvals, key=lambda x: x.real, reverse=True)
        except np.linalg.LinAlgError:
            eigenvals = []
        
        # Get stationary distribution
        pi = self.calculate_equilibrium_distribution()
        
        # Calculate mixing time (if possible)
        # Based on second largest eigenvalue
        mixing_time = None
        convergence_rate = None
        if len(eigenvals) >= 2:
            # Mixing time proportional to 1/|λ2|
            lambda2 = eigenvals[1]
            if abs(lambda2) > 0:
                mixing_time = -1.0 / lambda2.real
                convergence_rate = abs(lambda2)
        
        return {
            'eigenvalues': eigenvals,
            'mixing_time': mixing_time,
            'stationary_distribution': pi,
            'convergence_rate': convergence_rate
        }
    
    def calculate_rating_confidence(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate confidence intervals for ratings based on:
        1. Number of games played
        2. Consistency of performance
        3. Quality of opponents
        
        Returns:
            Dict mapping team to:
            - rating: Point estimate
            - std_error: Standard error
            - conf_interval: (lower, upper) 95% confidence bounds
        """
        ratings = self.calculate_ratings()
        n_teams = len(self.teams)
        
        confidence = {}
        for team in self.teams:
            # Get games involving this team
            team_games = [g for g in self.games 
                         if g.team_a == team or g.team_b == team]
            n_games = len(team_games)
            
            if n_games == 0:
                confidence[team] = {
                    'rating': ratings[team],
                    'std_error': float('inf'),
                    'conf_interval': (float('-inf'), float('inf'))
                }
                continue
            
            # Calculate variance in performance
            performances = []
            for game in team_games:
                if game.team_a == team:
                    opp = game.team_b
                    margin = game.score_a - game.score_b
                else:
                    opp = game.team_a
                    margin = game.score_b - game.score_a
                
                # Adjust for opponent strength
                opp_rating = ratings[opp]
                adj_margin = margin + (ratings[team] - opp_rating)
                performances.append(adj_margin)
            
            # Calculate standard error
            if len(performances) >= 2:
                std_error = np.std(performances) / np.sqrt(n_games)
            else:
                std_error = float('inf')
            
            # 95% confidence interval
            z_score = 1.96
            conf_interval = (
                ratings[team] - z_score * std_error,
                ratings[team] + z_score * std_error
            )
            
            confidence[team] = {
                'rating': ratings[team],
                'std_error': std_error,
                'conf_interval': conf_interval
            }
        
        return confidence
    
    def calculate_predictive_accuracy(self) -> Dict[str, float]:
        """
        Calculate various measures of predictive accuracy:
        1. Binary prediction accuracy (win/loss)
        2. Mean absolute error in point spread
        3. Log likelihood of outcomes
        """
        total_games = len(self.games)
        if total_games == 0:
            return {
                'accuracy': 0.0,
                'mae_spread': 0.0,
                'log_likelihood': 0.0
            }
        
        correct = 0
        total_error = 0
        total_ll = 0
        
        for game in self.games:
            # Get predicted probability
            p_a = self.predict_game(game.team_a, game.team_b)
            
            # Binary outcome
            actual_a_win = game.score_a > game.score_b
            pred_a_win = p_a > 0.5
            if actual_a_win == pred_a_win:
                correct += 1
            
            # Point spread error
            pred_spread = self.predict_spread(game.team_a, game.team_b)
            actual_spread = game.score_a - game.score_b
            total_error += abs(pred_spread - actual_spread)
            
            # Log likelihood
            if actual_a_win:
                total_ll += np.log(p_a)
            else:
                total_ll += np.log(1 - p_a)
        
        return {
            'accuracy': correct / total_games,
            'mae_spread': total_error / total_games,
            'log_likelihood': total_ll / total_games
        }
    
    def predict_spread(self, team_a: str, team_b: str) -> float:
        """
        Predict point spread for a game between team_a and team_b.
        Positive spread means team_a is predicted to win by that amount.
        """
        ratings = self.calculate_ratings()
        rating_diff = ratings[team_a] - ratings[team_b]
        
        # Convert rating difference to predicted spread
        # Using empirical scaling factor from paper
        return rating_diff * 3.5  # Typical scaling factor 