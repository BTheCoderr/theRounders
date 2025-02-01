from typing import Dict, List, Tuple, Optional, Callable
import numpy as np
import pandas as pd
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from scipy import linalg
from scipy.stats import norm

@dataclass
class Game:
    """
    Represents a single game result with metadata.
    
    Attributes:
        team_a: First team identifier
        team_b: Second team identifier
        score_a: Score of team_a
        score_b: Score of team_b
        is_home_a: Whether team_a was home team
        date: Date of the game
        weight: Game weight (default 1.0)
        importance: Game importance factor (e.g. playoff=2.0)
        recency: Time-based weight factor
    """
    team_a: str
    team_b: str
    score_a: float
    score_b: float
    is_home_a: bool
    date: datetime
    weight: float = 1.0
    importance: float = 1.0
    recency: float = 1.0
    
    @property
    def total_weight(self) -> float:
        """Calculate total weight combining importance and recency."""
        return self.weight * self.importance * self.recency

    @property
    def margin(self) -> float:
        """Get score margin (positive for team_a win)."""
        return self.score_a - self.score_b
    
    @property
    def is_close_game(self) -> bool:
        """Determine if game was close based on margin."""
        return abs(self.margin) <= 10  # Can be customized per sport

class MasseyRatings(ABC):
    """
    Abstract base class implementing Massey's Rating method.
    
    The system uses a weighted least squares approach to solve:
    M * r = p
    
    where:
    - M is the Massey matrix (teams × teams)
    - r is the ratings vector we want to solve for
    - p is the point differential vector
    
    Key features:
    - Handles weighted games (more recent games can have higher weight)
    - Supports score transformation (e.g. diminishing returns on margin)
    - Includes home field advantage
    - Handles minimum game requirements
    - Supports preseason ratings initialization
    - Implements iterative rating refinement
    - Provides statistical inference
    """
    
    def __init__(self, 
                 teams: List[str],
                 min_games: int = 10,
                 use_preseason: bool = True,
                 score_transform: Optional[Callable[[float], float]] = None,
                 max_iterations: int = 100,
                 convergence_threshold: float = 1e-6):
        """Initialize Massey Ratings system."""
        self.teams = sorted(teams)
        self.team_indices = {team: i for i, team in enumerate(self.teams)}
        self.min_games = min_games
        self.use_preseason = use_preseason
        self.score_transform = score_transform
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        
        # Game storage
        self.games: List[Game] = []
        self.team_games: Dict[str, int] = {team: 0 for team in teams}
        
        # Rating storage
        self.current_ratings: Dict[str, float] = {}
        self.preseason_ratings: Dict[str, float] = {}
        
        # Statistical storage
        self.rating_variances: Dict[str, float] = {}
        self.confidence_intervals: Dict[str, Tuple[float, float]] = {}
        self.prediction_errors: List[float] = []
        self.convergence_history: List[float] = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def get_home_advantage(self) -> float:
        """Return the home field advantage value for this sport."""
        pass
    
    @abstractmethod
    def get_margin_factor(self) -> float:
        """Return the factor to convert rating differences to predicted margins."""
        pass
    
    @abstractmethod
    def _initialize_preseason_ratings(self):
        """Initialize preseason ratings based on historical data."""
        pass
    
    def _calculate_game_weights(self) -> None:
        """
        Calculate weights for all games based on:
        1. Recency (more recent games weighted higher)
        2. Game importance (playoffs, rivalries, etc)
        3. Margin closeness (closer games get more weight)
        """
        if not self.games:
            return
        
        # Get most recent date
        latest_date = max(game.date for game in self.games)
        
        for game in self.games:
            # Calculate recency weight (exponential decay)
            days_old = (latest_date - game.date).days
            game.recency = np.exp(-days_old / 365.0)  # Half-life of ~6 months
            
            # Adjust weight for close games
            if game.is_close_game:
                game.weight *= 1.25  # 25% boost for close games
            
            # Note: game.importance should be set when adding the game
            
    def add_game(self, team_a: str, team_b: str, score_a: float, score_b: float,
                 is_home_a: bool = True, date: Optional[str] = None,
                 importance: float = 1.0) -> None:
        """
        Add a game result to the system.
        
        Args:
            team_a: First team identifier
            team_b: Second team identifier
            score_a: Score of team_a
            score_b: Score of team_b
            is_home_a: Whether team_a was home team
            date: Game date (defaults to current date)
            importance: Game importance factor (e.g. playoffs=2.0)
        """
        if team_a not in self.teams or team_b not in self.teams:
            raise ValueError(f"Invalid team(s): {team_a}, {team_b}")
        
        # Parse date
        if date is None:
            game_date = datetime.now()
        else:
            game_date = datetime.strptime(date, '%Y-%m-%d')
        
        game = Game(
            team_a=team_a,
            team_b=team_b,
            score_a=score_a,
            score_b=score_b,
            is_home_a=is_home_a,
            date=game_date,
            importance=importance
        )
        
        self.games.append(game)
        self.team_games[team_a] += 1
        self.team_games[team_b] += 1
        
        # Recalculate all game weights
        self._calculate_game_weights()
    
    def _build_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build the weighted design matrix X and response vector y.
        
        The system is formulated as (A^T)Xr = (A^T)y where:
        - Each row of X corresponds to a game
        - X has +1 for winner, -1 for loser
        - y contains game score differentials
        - A is diagonal matrix of weights
        - Additional constraint Σrᵢ = 0 is added
        """
        n_teams = len(self.teams)
        n_games = len(self.games)
        
        # Initialize design matrix and response vector
        X = np.zeros((n_games, n_teams))
        y = np.zeros(n_games)
        W = np.zeros((n_games, n_games))  # Weight matrix
        
        # Fill matrices based on game results
        for i, game in enumerate(self.games):
            # Get team indices
            team_a_idx = self.team_indices[game.team_a]
            team_b_idx = self.team_indices[game.team_b]
            
            # Set indicator variables (+1/-1)
            X[i, team_a_idx] = 1
            X[i, team_b_idx] = -1
            
            # Calculate score differential
            margin = game.margin
            
            # Apply home advantage adjustment
            if game.is_home_a:
                margin -= self.get_home_advantage()
            
            # Apply score transformation if specified
            if self.score_transform:
                margin = self.score_transform(margin)
            
            # Set response variable
            y[i] = margin
            
            # Set weight
            W[i,i] = game.total_weight
        
        # Form weighted normal equations (A^T)X and (A^T)y
        WX = W @ X
        Wy = W @ y
        
        # Form final system
        XtWX = X.T @ WX
        XtWy = X.T @ Wy
        
        # Add constraint that ratings sum to zero
        XtWX[-1,:] = 1
        XtWy[-1] = 0
        
        return XtWX, XtWy
    
    def _calculate_gom(self, margin: float) -> float:
        """
        Calculate Game Outcome Measure (GOM) with diminishing returns.
        
        This implements the diminishing returns principle described in Chapter 4,
        where the marginal value of additional points decreases as the margin grows.
        """
        if self.score_transform:
            return self.score_transform(margin)
        
        # Default GOM function (can be overridden by subclasses)
        # Uses signed square root as default diminishing returns function
        sign = np.sign(margin)
        return sign * np.sqrt(abs(margin))
    
    def _build_offense_defense_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build matrices for offense/defense ratings system.
        
        This expands the system to solve for both offensive and defensive ratings:
        [X₁ X₂][r₁] = [y]
        [X₃ X₄][r₂]   [z]
        
        where r₁ are offensive ratings and r₂ are defensive ratings.
        """
        n_teams = len(self.teams)
        n_games = len(self.games)
        
        # Initialize expanded matrices
        X = np.zeros((2 * n_games, 2 * n_teams))
        y = np.zeros(2 * n_games)
        
        for i, game in enumerate(self.games):
            # Get team indices
            a_idx = self.team_indices[game.team_a]
            b_idx = self.team_indices[game.team_b]
            
            # Offensive contributions (points scored)
            X[i, a_idx] = 1  # Team A's offense
            X[i, n_teams + b_idx] = 1  # Team B's defense
            y[i] = game.score_a
            
            # Defensive contributions (points allowed)
            X[i + n_games, b_idx] = 1  # Team B's offense
            X[i + n_games, n_teams + a_idx] = 1  # Team A's defense
            y[i + n_games] = game.score_b
        
        # Form normal equations
        XtX = X.T @ X
        Xty = X.T @ y
        
        # Add constraints that offensive and defensive ratings sum to zero
        XtX[-2,:] = 0
        XtX[-2,:n_teams] = 1  # Sum of offensive ratings = 0
        XtX[-1,:] = 0
        XtX[-1,n_teams:] = 1  # Sum of defensive ratings = 0
        Xty[-2:] = 0
        
        return XtX, Xty
    
    def _check_matrix_properties(self, M: np.ndarray) -> bool:
        """Check important properties of the Massey matrix."""
        # Check symmetry
        if not np.allclose(M, M.T):
            self.logger.warning("Massey matrix is not symmetric")
            return False
            
        # Check conditioning
        cond = np.linalg.cond(M)
        if cond > 1e10:
            self.logger.warning(f"Massey matrix is poorly conditioned: {cond}")
            return False
            
        return True
    
    def _lup_decomposition(self, A: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute the LUP decomposition of matrix A.
        Returns (L, U, P) where PA = LU
        L is unit lower triangular
        U is upper triangular
        P is permutation matrix
        """
        n = A.shape[0]
        L = np.eye(n)  # Unit lower triangular
        U = A.copy()
        P = np.eye(n)  # Permutation matrix
        
        for k in range(n-1):
            # Find pivot
            pivot_idx = k + np.argmax(np.abs(U[k:, k]))
            if pivot_idx != k:
                # Swap rows in U
                U[[k, pivot_idx]] = U[[pivot_idx, k]]
                # Update permutation matrix
                P[[k, pivot_idx]] = P[[pivot_idx, k]]
                # Swap already computed parts of L
                if k > 0:
                    L[[k, pivot_idx], :k] = L[[pivot_idx, k], :k]
            
            # Check for singularity
            if np.abs(U[k,k]) < 1e-10:
                raise np.linalg.LinAlgError("Matrix is singular")
            
            # Compute multipliers
            for i in range(k+1, n):
                L[i,k] = U[i,k] / U[k,k]
                U[i,k:] -= L[i,k] * U[k,k:]
        
        return L, U, P
    
    def _lup_solve(self, L: np.ndarray, U: np.ndarray, P: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Solve Ax = b using LUP decomposition where PA = LU.
        First solves Ly = Pb for y using forward substitution,
        then solves Ux = y for x using backward substitution.
        """
        # Forward substitution to solve Ly = Pb
        Pb = P @ b
        n = len(b)
        y = np.zeros(n)
        for i in range(n):
            y[i] = Pb[i] - L[i,:i] @ y[:i]
        
        # Backward substitution to solve Ux = y
        x = np.zeros(n)
        for i in range(n-1, -1, -1):
            x[i] = (y[i] - U[i,i+1:] @ x[i+1:]) / U[i,i]
        
        return x
    
    def _solve_ratings_system(self, M: np.ndarray, p: np.ndarray) -> np.ndarray:
        """
        Solve the ratings system Mr = p using LUP decomposition.
        Includes checks for matrix properties and conditioning.
        """
        try:
            # Check matrix properties
            if not self._check_matrix_properties(M):
                raise np.linalg.LinAlgError("Matrix fails property checks")
            
            # Compute LUP decomposition
            L, U, P = self._lup_decomposition(M)
            
            # Solve system
            r = self._lup_solve(L, U, P, p)
            
            # Verify solution
            residual = np.linalg.norm(M @ r - p)
            if residual > 1e-10:
                self.logger.warning(f"Large residual in solution: {residual:.2e}")
            
            return r
            
        except np.linalg.LinAlgError as e:
            self.logger.error(f"Error in LUP decomposition: {str(e)}")
            # Fall back to iterative method
            return self._solve_iterative(M, p)
    
    def _solve_iterative(self, M: np.ndarray, p: np.ndarray) -> np.ndarray:
        """
        Solve Mr = p using Gauss-Seidel iteration.
        Used as fallback when direct method fails.
        """
        n = len(p)
        r = np.zeros(n)  # Initial guess
        prev_r = np.inf * np.ones(n)
        iteration = 0
        
        D = np.diag(np.diag(M))  # Diagonal
        L = np.tril(M, -1)       # Strictly lower triangular
        U = np.triu(M, 1)        # Strictly upper triangular
        
        while (iteration < self.max_iterations and 
               np.max(np.abs(r - prev_r)) > self.convergence_threshold):
            prev_r = r.copy()
            
            # Gauss-Seidel iteration
            for i in range(n):
                r[i] = (p[i] - L[i,:] @ r - U[i,:] @ prev_r) / M[i,i]
            
            iteration += 1
        
        if iteration == self.max_iterations:
            self.logger.warning("Iterative solver reached maximum iterations")
        else:
            self.logger.info(f"Iterative solver converged in {iteration} iterations")
        
        return r
    
    def calculate_ratings(self) -> Dict[str, float]:
        """Calculate ratings using Massey's least squares method."""
        if len(self.games) < self.min_games:
            self.logger.warning("Not enough games played")
            return {}
            
        try:
            # Build matrices using proper least squares formulation
            M, p = self._build_matrices()
            
            # Solve system
            r = self._solve_ratings_system(M, p)
            
            # Convert to dictionary and normalize
            ratings = {team: float(r[i]) for i, team in enumerate(self.teams)}
            
            # Scale ratings to desired range (0-100)
            min_rating = min(ratings.values())
            max_rating = max(ratings.values())
            self.current_ratings = {
                team: 50 + (50 * (rating - min_rating) / (max_rating - min_rating))
                for team, rating in ratings.items()
            }
            
            return self.current_ratings
            
        except Exception as e:
            self.logger.error(f"Error calculating ratings: {str(e)}")
            return self.preseason_ratings if self.use_preseason else {}
    
    def predict_game(self, team_a: str, team_b: str, 
                    neutral_site: bool = False) -> Tuple[float, float]:
        """
        Predict outcome of a game between team_a and team_b.
        Returns (win probability for team_a, predicted margin).
        """
        if not self.current_ratings:
            if not self.calculate_ratings():
                raise ValueError("Unable to calculate ratings")
        
        if team_a not in self.current_ratings or team_b not in self.current_ratings:
            raise ValueError(f"Invalid team(s): {team_a}, {team_b}")
        
        # Get rating difference
        rating_diff = self.current_ratings[team_a] - self.current_ratings[team_b]
        
        # Adjust for home advantage if not neutral site
        if not neutral_site:
            rating_diff += self.get_home_advantage()
        
        # Calculate win probability using logistic function
        win_prob = 1 / (1 + np.exp(-rating_diff/8))
        
        # Calculate predicted margin
        predicted_margin = rating_diff * self.get_margin_factor()
        
        return win_prob, predicted_margin
    
    def get_ratings_dataframe(self) -> pd.DataFrame:
        """Return ratings as a sorted DataFrame with additional statistics."""
        if not self.current_ratings:
            if not self.calculate_ratings():
                return pd.DataFrame()
        
        data = []
        for team in self.teams:
            rating = self.current_ratings.get(team, 0)
            games_played = self.team_games.get(team, 0)
            
            # Calculate offensive and defensive stats
            team_games = [g for g in self.games 
                         if g.team_a == team or g.team_b == team]
            
            points_for = sum(g.score_a if g.team_a == team else g.score_b 
                           for g in team_games)
            points_against = sum(g.score_b if g.team_a == team else g.score_a 
                               for g in team_games)
            
            if games_played > 0:
                ppg = points_for / games_played
                papg = points_against / games_played
                point_diff = (points_for - points_against) / games_played
            else:
                ppg = papg = point_diff = 0
            
            data.append({
                'Team': team,
                'Rating': rating,
                'Games': games_played,
                'PPG': ppg,
                'PAPG': papg,
                'Point_Diff': point_diff
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Rating', ascending=False).reset_index(drop=True)
    
    def get_rating_statistics(self, team: str) -> Dict[str, float]:
        """Get statistical information about a team's rating."""
        if team not in self.current_ratings:
            raise ValueError(f"No rating available for team: {team}")
            
        return {
            'rating': self.current_ratings[team],
            'variance': self.rating_variances.get(team, 0),
            'ci_lower': self.confidence_intervals.get(team, (0, 0))[0],
            'ci_upper': self.confidence_intervals.get(team, (0, 0))[1],
            'games_played': self.team_games[team]
        }
    
    def get_convergence_info(self) -> Dict[str, float]:
        """Get information about the convergence of the iterative solution."""
        if not self.convergence_history:
            return {}
            
        return {
            'iterations': len(self.convergence_history),
            'final_delta': self.convergence_history[-1],
            'average_delta': np.mean(self.convergence_history),
            'max_delta': np.max(self.convergence_history)
        }
    
    def _calculate_mle_ratings(self) -> Dict[str, float]:
        """
        Calculate ratings using Maximum Likelihood Estimation with improved convergence.
        
        This implements the modified Newton's method from Chapter 5, which:
        1. Uses a modified step size to prevent divergence
        2. Includes boundary conditions for numerical stability
        3. Implements fixed point iteration as a fallback
        
        Returns:
            Dict mapping team names to MLE ratings
        """
        n_teams = len(self.teams)
        max_iter = 100
        tol = 1e-6
        c = 2.0  # Scaling factor for modified Newton's method
        
        # Initialize ratings randomly
        r = np.random.normal(0, 0.1, n_teams)
        
        def fixed_point_iteration(r_init: np.ndarray) -> np.ndarray:
            """Implement fixed point iteration method (equation 9)."""
            r = r_init.copy()
            for _ in range(max_iter):
                r_old = r.copy()
                
                # Calculate new ratings using fixed point formula
                for i in range(n_teams):
                    numerator = 0
                    denominator = 0
                    for game in self.games:
                        if game.team_a == self.teams[i]:
                            j = self.team_indices[game.team_b]
                            p = 1 / (1 + np.exp(r[j] - r[i]))
                            numerator += game.total_weight * (1 if game.score_a > game.score_b else 0)
                            denominator += game.total_weight * p
                        elif game.team_b == self.teams[i]:
                            j = self.team_indices[game.team_a]
                            p = 1 / (1 + np.exp(r[j] - r[i]))
                            numerator += game.total_weight * (1 if game.score_b > game.score_a else 0)
                            denominator += game.total_weight * p
                    
                    if denominator > 0:
                        r[i] = np.log(numerator / denominator)
                
                # Check convergence
                if np.max(np.abs(r - r_old)) < tol:
                    break
            
            return r
        
        try:
            for iteration in range(max_iter):
                r_old = r.copy()
                
                # Calculate gradients using modified Newton's method
                grad = np.zeros(n_teams)
                hess = np.zeros((n_teams, n_teams))
                
                for game in self.games:
                    i = self.team_indices[game.team_a]
                    j = self.team_indices[game.team_b]
                    
                    # Calculate probability using logistic function
                    r_diff = r[i] - r[j]
                    p = 1 / (1 + np.exp(-r_diff))
                    
                    # Binary outcome (1 for win, 0 for loss)
                    y = float(game.score_a > game.score_b)
                    
                    # Modified gradient calculation
                    w = game.total_weight
                    grad[i] += w * (y - p)
                    grad[j] += w * (p - y)
                    
                    # Modified Hessian calculation
                    h = w * p * (1 - p)
                    hess[i,i] += h
                    hess[j,j] += h
                    hess[i,j] -= h
                    hess[j,i] -= h
                
                # Add constraint that sum of ratings = 0
                grad[-1] = np.sum(r)
                hess[-1,:] = 1
                hess[:,-1] = 1
                
                # Modified Newton step
                try:
                    # Calculate step size using equation from page 61
                    q1 = np.max(np.abs(grad / np.diag(hess)))
                    q2 = np.min(np.abs(grad / np.diag(hess)))
                    
                    if q1 > c * q2:
                        # Use modified step size
                        delta = -grad / np.diag(hess)
                    else:
                        # Regular Newton step
                        delta = np.linalg.solve(hess, -grad)
                    
                    r = r + delta
                    
                    # Check convergence
                    if np.max(np.abs(r - r_old)) < tol:
                        break
                        
                except np.linalg.LinAlgError:
                    # Fall back to fixed point iteration
                    self.logger.info("Switching to fixed point iteration")
                    r = fixed_point_iteration(r)
                    break
                
        except Exception as e:
            self.logger.error(f"Error in MLE calculation: {str(e)}")
            # Fall back to fixed point iteration
            r = fixed_point_iteration(r)
        
        # Scale ratings to be non-negative
        r = r - np.min(r)
        
        # Convert to dictionary
        return {team: float(r[i]) for i, team in enumerate(self.teams)}
    
    def calculate_win_probability(self, team_a: str, team_b: str,
                                neutral_site: bool = False,
                                use_mle: bool = True) -> float:
        """
        Calculate probability of team_a defeating team_b.
        
        Args:
            team_a: First team
            team_b: Second team
            neutral_site: Whether game is at neutral site
            use_mle: Whether to use MLE ratings (vs least squares)
        
        Returns:
            Probability of team_a victory
        """
        if use_mle:
            ratings = self._calculate_mle_ratings()
        else:
            ratings = self.current_ratings
        
        if not ratings:
            raise ValueError("No ratings available")
        
        if team_a not in ratings or team_b not in ratings:
            raise ValueError(f"Invalid team(s): {team_a}, {team_b}")
        
        # Get rating difference
        r_diff = ratings[team_a] - ratings[team_b]
        
        # Add home advantage if applicable
        if not neutral_site:
            r_diff += self.get_home_advantage()
        
        # Convert to probability using logistic function
        return 1 / (1 + np.exp(-r_diff))
    
    def predict_score(self, team_a: str, team_b: str,
                     neutral_site: bool = False) -> Tuple[float, float]:
        """
        Predict score for a game between team_a and team_b.
        
        This combines both the least squares ratings (for margin)
        and MLE ratings (for win probability) to make predictions.
        
        Returns:
            Tuple of (team_a_score, team_b_score)
        """
        # Get win probability from MLE
        p_win = self.calculate_win_probability(team_a, team_b, neutral_site)
        
        # Get predicted margin from least squares
        _, margin = self.predict_game(team_a, team_b, neutral_site)
        
        # Adjust margin based on win probability
        if p_win > 0.5:
            margin = abs(margin)  # Ensure positive margin for favored team
        else:
            margin = -abs(margin)  # Ensure negative margin for underdog
        
        # Convert margin to scores (centered around average)
        avg_score = 100  # Can be customized per sport
        team_a_score = avg_score + margin/2
        team_b_score = avg_score - margin/2
        
        return team_a_score, team_b_score 