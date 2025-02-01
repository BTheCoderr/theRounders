"""
Implements the Sauceda Rating System for NBA games.
Based on Elo ratings with modifications for point differential and home court advantage.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import math

@dataclass
class GamePoints:
    winner_points: float
    loser_points: float
    win_probability: float

class SaucedaRatings:
    def __init__(self, k: float = 300, initial_rating: float = 1000, pd_factor: float = 11):
        """
        Initialize Sauceda Rating calculator.
        
        Args:
            k: Prediction constant (default 300 for NBA)
            initial_rating: Starting rating for new teams (default 1000)
            pd_factor: Point differential factor (default 11 for NBA)
        """
        self.k = k
        self.initial_rating = initial_rating
        self.pd_factor = pd_factor
        self.home_advantage = 100  # Initial home court advantage value
        self.ratings: Dict[str, float] = {}
        
    def calculate_game_points(self, point_differential: float) -> float:
        """Calculate game points based on point differential."""
        return 1 - 0.4 ** (1 + point_differential / self.pd_factor)
        
    def calculate_win_expectancy(self, rating_a: float, rating_b: float, is_a_home: bool) -> float:
        """
        Calculate expected win probability for team A vs team B.
        
        Args:
            rating_a: Rating of team A
            rating_b: Rating of team B
            is_a_home: Whether team A is home team
            
        Returns:
            Expected win probability for team A
        """
        home_adj = self.home_advantage if is_a_home else -self.home_advantage
        return 1 / (1 + 10 ** ((rating_b - rating_a + home_adj) / self.k))
        
    def update_ratings(self, game_result: 'GameResult') -> Dict[str, float]:
        """
        Update ratings based on game result.
        
        Args:
            game_result: GameResult object containing game details
            
        Returns:
            Dictionary with updated ratings for both teams
        """
        # Initialize ratings if needed
        if game_result.team_a not in self.ratings:
            self.ratings[game_result.team_a] = self.initial_rating
        if game_result.team_b not in self.ratings:
            self.ratings[game_result.team_b] = self.initial_rating
            
        # Calculate point differential and game points
        pd = game_result.score_a - game_result.score_b
        gp = self.calculate_game_points(abs(pd))
        
        # Determine winner and loser points
        if pd > 0:
            winner_gp = gp
            loser_gp = 1 - gp
            winner = game_result.team_a
            loser = game_result.team_b
        else:
            winner_gp = gp
            loser_gp = 1 - gp
            winner = game_result.team_b
            loser = game_result.team_a
            
        # Calculate win expectancy
        we = self.calculate_win_expectancy(
            self.ratings[game_result.team_a],
            self.ratings[game_result.team_b],
            game_result.is_home_a
        )
        
        # Update ratings
        if pd > 0:
            self.ratings[game_result.team_a] += self.k * (winner_gp - we)
            self.ratings[game_result.team_b] += self.k * (loser_gp - (1 - we))
        else:
            self.ratings[game_result.team_a] += self.k * (loser_gp - we)
            self.ratings[game_result.team_b] += self.k * (winner_gp - (1 - we))
            
        return self.ratings.copy()
        
    def predict_game(self, team_a: str, team_b: str, is_a_home: bool) -> GamePoints:
        """
        Predict outcome of a game between two teams.
        
        Args:
            team_a: Name of team A
            team_b: Name of team B
            is_a_home: Whether team A is home team
            
        Returns:
            GamePoints object with win probabilities
        """
        if team_a not in self.ratings or team_b not in self.ratings:
            raise ValueError("Both teams must have ratings")
            
        win_prob = self.calculate_win_expectancy(
            self.ratings[team_a],
            self.ratings[team_b],
            is_a_home
        )
        
        return GamePoints(
            winner_points=win_prob,
            loser_points=1 - win_prob,
            win_probability=win_prob
        )
        
    def get_rating_tier(self, rating: float) -> str:
        """
        Get the tier/category for a given rating.
        
        Args:
            rating: Team's Sauceda rating
            
        Returns:
            String describing the team's tier
        """
        if rating >= 1200:
            return "ELITE"
        elif rating >= 1100:
            return "STRONG"
        elif rating >= 1000:
            return "AVERAGE"
        elif rating >= 900:
            return "WEAK"
        else:
            return "POOR"
            
    def analyze_rating_distribution(self, ratings: Optional[Dict[str, float]] = None) -> Dict[str, List[str]]:
        """
        Analyze the distribution of teams across rating tiers.
        
        Args:
            ratings: Optional dictionary of team ratings (uses stored ratings if None)
            
        Returns:
            Dictionary mapping tiers to lists of team names
        """
        if ratings is None:
            ratings = self.ratings
            
        distribution = {
            "ELITE": [],
            "STRONG": [],
            "AVERAGE": [],
            "WEAK": [],
            "POOR": []
        }
        
        for team, rating in ratings.items():
            tier = self.get_rating_tier(rating)
            distribution[tier].append(team)
            
        return distribution 