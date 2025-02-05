"""
Preseason ratings and time-based adjustments for the Massey Rating system.
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class PreseasonRatings:
    def __init__(self, 
                 historical_ratings: Dict[str, Dict[str, float]],
                 decay_factor: float = 0.5):
        """
        Initialize with historical ratings.
        
        Args:
            historical_ratings: Dict mapping years to team ratings
            decay_factor: Weight decay for older seasons
        """
        self.historical = historical_ratings
        self.decay = decay_factor
        
    def calculate_preseason_ratings(self, 
                                  teams: List[str],
                                  current_year: int,
                                  lookback_years: int = 3) -> Dict[str, float]:
        """
        Calculate preseason ratings based on historical performance.
        
        Args:
            teams: List of current teams
            current_year: Current year
            lookback_years: Number of previous years to consider
            
        Returns:
            Dict mapping teams to preseason ratings
        """
        preseason = {}
        
        for team in teams:
            ratings = []
            weights = []
            
            # Collect historical ratings with exponential decay
            for year in range(current_year - lookback_years, current_year):
                if year in self.historical and team in self.historical[year]:
                    rating = self.historical[year][team]
                    weight = self.decay ** (current_year - year)
                    
                    ratings.append(rating)
                    weights.append(weight)
            
            if ratings:
                # Weighted average of historical ratings
                preseason[team] = np.average(ratings, weights=weights)
            else:
                # No history - use average rating
                preseason[team] = 0.0
        
        return preseason
    
    def calculate_rating_weight(self,
                              games_played: int,
                              max_games: int = 12) -> float:
        """
        Calculate weight to apply to preseason rating.
        Weight decreases as more games are played.
        
        Args:
            games_played: Number of games played
            max_games: Games needed for preseason to be fully phased out
            
        Returns:
            Weight between 0 and 1
        """
        if games_played >= max_games:
            return 0.0
        
        # Exponential decay of preseason weight
        return np.exp(-3 * games_played / max_games)

class TimeAdjustments:
    def __init__(self,
                 current_date: datetime,
                 season_start: datetime,
                 season_end: datetime):
        """
        Initialize with season dates.
        
        Args:
            current_date: Current date
            season_start: Season start date
            season_end: Season end date
        """
        self.current_date = current_date
        self.season_start = season_start
        self.season_end = season_end
        
    def calculate_game_weight(self,
                            game_date: datetime,
                            recency_factor: float = 0.1) -> float:
        """
        Calculate time-based weight for a game.
        More recent games get higher weight.
        
        Args:
            game_date: Date of the game
            recency_factor: Controls how quickly weights decay
            
        Returns:
            Weight between 0 and 1
        """
        if game_date > self.current_date:
            return 0.0
            
        days_old = (self.current_date - game_date).days
        season_length = (self.season_end - self.season_start).days
        
        # Exponential decay based on age of game
        return np.exp(-recency_factor * days_old / season_length)
    
    def calculate_season_phase_adjustments(self) -> Dict[str, float]:
        """
        Calculate adjustments based on phase of season.
        
        Returns:
            Dict with adjustment factors:
            - variance_multiplier: Ratings more volatile early
            - home_advantage: Home advantage varies through season
            - upset_factor: Upsets more likely at certain times
        """
        season_progress = (self.current_date - self.season_start).days
        total_days = (self.season_end - self.season_start).days
        phase = season_progress / total_days
        
        adjustments = {
            # More variance early in season
            'variance_multiplier': 1.5 - 0.5 * phase,
            
            # Home advantage peaks mid-season
            'home_advantage': 50 * (1 + 0.2 * np.sin(np.pi * phase)),
            
            # Upsets more likely late in season
            'upset_factor': 1 + 0.3 * phase
        }
        
        return adjustments
    
    def apply_time_adjustments(self,
                             base_ratings: Dict[str, float],
                             games_played: Dict[str, int]) -> Dict[str, float]:
        """
        Apply time-based adjustments to ratings.
        
        Args:
            base_ratings: Raw team ratings
            games_played: Number of games played by each team
            
        Returns:
            Adjusted ratings
        """
        adjustments = self.calculate_season_phase_adjustments()
        
        # Apply variance multiplier based on games played
        adjusted = {}
        for team, rating in base_ratings.items():
            n_games = games_played.get(team, 0)
            
            # More variance for teams with fewer games
            team_variance = adjustments['variance_multiplier'] * np.exp(-0.1 * n_games)
            
            # Add random noise based on variance
            noise = np.random.normal(0, 20 * team_variance)
            adjusted[team] = rating + noise
        
        return adjusted 