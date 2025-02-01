"""
MLB Rating System incorporating team, pitcher, and ballpark effects.
Based on Massey's MLB-specific methodology.
"""

from typing import Dict, List, Optional, NamedTuple
from dataclasses import dataclass
import numpy as np
from scipy.special import erf

@dataclass
class PitcherRating:
    name: str
    offensive_rating: float  # Run support
    defensive_rating: float  # Run prevention
    home_field: float       # Home/away impact
    team_starts: int        # Number of starts for current team
    total_starts: int       # Total starts this season

@dataclass
class TeamRating:
    name: str
    offensive_rating: float  # Team offense minus starting pitching
    defensive_rating: float  # Team defense (fielding + bullpen)
    home_field: float       # Ballpark effect
    games_played: int

@dataclass
class GamePrediction:
    home_score: float
    away_score: float
    home_win_prob: float
    total_runs: float
    description: str

class MLBRatings:
    def __init__(self):
        self.teams: Dict[str, TeamRating] = {}
        self.pitchers: Dict[str, PitcherRating] = {}
        self.universal_home_advantage = 0.25  # Default MLB home advantage in runs
        self.std_dev_runs = 4.5  # Standard deviation of run differential
        
    def add_team(self, name: str, off_rating: float = 0.0, def_rating: float = 0.0, 
                 home_field: float = 0.0, games: int = 0):
        """Add or update a team's ratings."""
        self.teams[name] = TeamRating(
            name=name,
            offensive_rating=off_rating,
            defensive_rating=def_rating,
            home_field=home_field,
            games_played=games
        )
        
    def add_pitcher(self, name: str, team: str, off_rating: float = 0.0, 
                   def_rating: float = 0.0, home_field: float = 0.0, 
                   team_starts: int = 0, total_starts: int = 0):
        """Add or update a pitcher's ratings."""
        self.pitchers[name] = PitcherRating(
            name=name,
            offensive_rating=off_rating,
            defensive_rating=def_rating,
            home_field=home_field,
            team_starts=team_starts,
            total_starts=total_starts
        )
        
    def predict_game(self, home_team: str, away_team: str, 
                    home_pitcher: Optional[str] = None, 
                    away_pitcher: Optional[str] = None) -> GamePrediction:
        """
        Predict the outcome of a game using Massey's MLB formula.
        
        Args:
            home_team: Name of home team
            away_team: Name of away team
            home_pitcher: Name of home team's starting pitcher (optional)
            away_pitcher: Name of away team's starting pitcher (optional)
            
        Returns:
            GamePrediction with expected scores and win probability
        """
        if home_team not in self.teams or away_team not in self.teams:
            raise ValueError("Both teams must have ratings")
            
        home = self.teams[home_team]
        away = self.teams[away_team]
        
        # Base run prediction without pitchers
        home_runs = (home.offensive_rating - away.defensive_rating + 
                    (home.home_field + away.home_field) / 4 +
                    self.universal_home_advantage)
        away_runs = (away.offensive_rating - home.defensive_rating - 
                    (home.home_field + away.home_field) / 4 -
                    self.universal_home_advantage)
        
        description = []
        
        # Adjust for starting pitchers if provided
        if home_pitcher and home_pitcher in self.pitchers:
            hp = self.pitchers[home_pitcher]
            home_runs += hp.offensive_rating
            away_runs -= hp.defensive_rating
            description.append(f"{home_pitcher} starting for {home_team}")
            
        if away_pitcher and away_pitcher in self.pitchers:
            ap = self.pitchers[away_pitcher]
            away_runs += ap.offensive_rating
            home_runs -= ap.defensive_rating
            description.append(f"{away_pitcher} starting for {away_team}")
            
        # Calculate win probability using normal distribution
        run_diff = home_runs - away_runs
        win_prob = 0.5 + 0.5 * erf(run_diff / (self.std_dev_runs * np.sqrt(2)))
        
        description.append(f"Expected run differential: {run_diff:.1f}")
        description.append(f"Home team win probability: {win_prob:.3f}")
        
        return GamePrediction(
            home_score=home_runs,
            away_score=away_runs,
            home_win_prob=win_prob,
            total_runs=home_runs + away_runs,
            description="\n".join(description)
        )
        
    def analyze_pitcher_impact(self, pitcher_name: str) -> str:
        """Analyze a pitcher's impact on game outcomes."""
        if pitcher_name not in self.pitchers:
            return "Pitcher not found"
            
        p = self.pitchers[pitcher_name]
        impact = []
        
        # Analyze run prevention
        if p.defensive_rating < -1.0:
            impact.append(f"Elite run prevention: {p.defensive_rating:.2f} runs below average")
        elif p.defensive_rating < 0:
            impact.append(f"Above average run prevention: {p.defensive_rating:.2f} runs below average")
        else:
            impact.append(f"Below average run prevention: {p.defensive_rating:.2f} runs above average")
            
        # Analyze run support
        if p.offensive_rating > 1.0:
            impact.append(f"High run support: {p.offensive_rating:.2f} runs above average")
        elif p.offensive_rating > 0:
            impact.append(f"Above average run support: {p.offensive_rating:.2f} runs above average")
        else:
            impact.append(f"Low run support: {p.offensive_rating:.2f} runs below average")
            
        # Analyze home/away splits
        if abs(p.home_field) > 0.5:
            split = "better" if p.home_field > 0 else "worse"
            impact.append(f"Significant home/away split: {abs(p.home_field):.2f} runs {split} at home")
            
        # Usage analysis
        impact.append(f"Started {p.team_starts} games for current team ({p.total_starts} total)")
        
        return "\n".join(impact)
        
    def analyze_ballpark_factors(self, team_name: str) -> str:
        """Analyze how a team's ballpark affects scoring."""
        if team_name not in self.teams:
            return "Team not found"
            
        team = self.teams[team_name]
        factors = []
        
        # Overall park effect
        if abs(team.home_field) > 0.5:
            effect = "hitter" if team.home_field > 0 else "pitcher"
            factors.append(f"{effect}-friendly park: {abs(team.home_field):.2f} run impact")
            
        # Team performance adjustments
        if abs(team.offensive_rating) > 1.0:
            quality = "strong" if team.offensive_rating > 0 else "weak"
            factors.append(f"{quality} offense: {abs(team.offensive_rating):.2f} runs per game")
            
        if abs(team.defensive_rating) > 1.0:
            quality = "strong" if team.defensive_rating < 0 else "weak"
            factors.append(f"{quality} defense: {abs(team.defensive_rating):.2f} runs per game")
            
        factors.append(f"Based on {team.games_played} games")
        
        return "\n".join(factors) 