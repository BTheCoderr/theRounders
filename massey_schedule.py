"""
Implements Massey's schedule rating methodology.
This module calculates schedule strength based on expected wins against different team qualities.
"""

from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class TeamQuality:
    name: str
    rating: float
    win_probabilities: Dict[str, float]

class MasseySchedule:
    def __init__(self):
        # Initialize the base team qualities adjusted for NBA rating scale
        self.team_qualities = {
            "GREAT": TeamQuality("GREAT", 1.45, {
                "GREAT": 0.50, "GOOD": 0.75, "AVERAGE": 0.90,
                "BAD": 0.97, "PATHETIC": 1.00
            }),
            "GOOD": TeamQuality("GOOD", 1.35, {
                "GREAT": 0.25, "GOOD": 0.50, "AVERAGE": 0.75,
                "BAD": 0.90, "PATHETIC": 0.97
            }),
            "AVERAGE": TeamQuality("AVERAGE", 1.30, {
                "GREAT": 0.10, "GOOD": 0.25, "AVERAGE": 0.50,
                "BAD": 0.75, "PATHETIC": 0.90
            }),
            "BAD": TeamQuality("BAD", 1.25, {
                "GREAT": 0.03, "GOOD": 0.10, "AVERAGE": 0.25,
                "BAD": 0.50, "PATHETIC": 0.75
            }),
            "PATHETIC": TeamQuality("PATHETIC", 1.20, {
                "GREAT": 0.00, "GOOD": 0.03, "AVERAGE": 0.10,
                "BAD": 0.25, "PATHETIC": 0.50
            })
        }

    def classify_team(self, rating: float) -> str:
        """Classify a team's rating into one of the five quality levels."""
        # Convert Sauceda rating (around 1000) to Massey scale
        adjusted_rating = (rating - 1000) / 100 + 1.30
        
        thresholds = {
            1.40: "GREAT",
            1.35: "GOOD",
            1.30: "AVERAGE",
            1.25: "BAD",
            float('-inf'): "PATHETIC"
        }
        for threshold, quality in sorted(thresholds.items(), reverse=True):
            if adjusted_rating >= threshold:
                return quality
        return "PATHETIC"

    def calculate_expected_wins(self, schedule: List[float], team_rating: float) -> float:
        """
        Calculate expected wins for a team with given rating against a schedule.
        
        Args:
            schedule: List of opponent ratings
            team_rating: Rating of the team playing the schedule
            
        Returns:
            Expected number of wins against the schedule
        """
        team_quality = self.classify_team(team_rating)
        expected_wins = 0.0
        
        for opp_rating in schedule:
            opp_quality = self.classify_team(opp_rating)
            win_prob = self.team_qualities[team_quality].win_probabilities[opp_quality]
            expected_wins += win_prob
            
        return expected_wins

    def calculate_schedule_strength(self, schedule: List[float]) -> float:
        """
        Calculate schedule strength using Massey's method.
        Finds the rating S such that a team rated S would have the same
        expected wins against itself as against the actual schedule.
        
        Args:
            schedule: List of opponent ratings
            
        Returns:
            Schedule strength rating
        """
        if not schedule:
            return 1.30  # Return average rating if no games played
            
        # Convert Sauceda ratings to Massey scale for calculation
        adjusted_schedule = [(r - 1000) / 100 + 1.30 for r in schedule]
        return np.mean(adjusted_schedule)

    def analyze_schedule_distribution(self, schedule: List[float]) -> Dict[str, int]:
        """
        Analyze the distribution of opponent qualities in a schedule.
        
        Args:
            schedule: List of opponent ratings
            
        Returns:
            Dictionary counting opponents of each quality level
        """
        distribution = {quality: 0 for quality in self.team_qualities.keys()}
        for rating in schedule:
            quality = self.classify_team(rating)
            distribution[quality] += 1
        return distribution

    def get_schedule_insight(self, schedule: List[float], team_rating: float) -> str:
        """
        Provide insight about whether the schedule distribution favors or
        disfavors the team based on Massey's heuristic.
        
        Args:
            schedule: List of opponent ratings
            team_rating: Rating of the team playing the schedule
            
        Returns:
            String describing how the schedule distribution affects the team
        """
        if not schedule:
            return "No games played yet"
            
        distribution = self.analyze_schedule_distribution(schedule)
        team_quality = self.classify_team(team_rating)
        
        # Calculate schedule variance using adjusted ratings
        adjusted_schedule = [(r - 1000) / 100 + 1.30 for r in schedule]
        variance = np.var(adjusted_schedule) if adjusted_schedule else 0
        
        # Determine if team is above or below average
        is_above_average = team_rating > 1000
        
        # Count games against teams of similar or better quality
        quality_levels = ["PATHETIC", "BAD", "AVERAGE", "GOOD", "GREAT"]
        team_level = quality_levels.index(team_quality)
        tough_games = sum(distribution[q] for q in quality_levels[team_level:])
        easy_games = sum(distribution[q] for q in quality_levels[:team_level])
        
        insights = []
        if variance > 0.01:
            insights.append("Highly varied schedule")
            if is_above_average:
                insights.append("More challenging for a strong team")
            else:
                insights.append("Favorable for a weaker team")
        else:
            insights.append("Consistent level of competition")
            if is_above_average:
                insights.append("Favorable for a strong team")
            else:
                insights.append("More challenging for a weaker team")
                
        if tough_games > easy_games:
            insights.append(f"Tough schedule ({tough_games} strong opponents)")
        elif easy_games > tough_games:
            insights.append(f"Easier schedule ({easy_games} weaker opponents)")
        
        return " - ".join(insights)

 