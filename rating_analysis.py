"""
Comprehensive analysis module for Massey Ratings system.
Combines formulas, statistics, and decision-making tools.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from massey_formulas import MasseyFormulas, GameResult
from datetime import datetime

@dataclass
class RatingAnalysis:
    """Container for comprehensive rating analysis."""
    rating: float
    power: float
    offense: float
    defense: float
    schedule_strength: float
    expected_wins: float
    win_probability: float
    confidence_interval: Tuple[float, float]
    variance: float
    trend: float  # Recent performance trend

@dataclass
class MatchupAnalysis:
    """Analysis of a specific matchup between two teams."""
    win_probability: float
    expected_margin: float
    upset_probability: float
    key_factors: List[str]
    confidence: float
    historical_results: List[Dict[str, Any]]

class RatingAnalyzer:
    def __init__(self, formulas: MasseyFormulas):
        """Initialize with MasseyFormulas instance."""
        self.formulas = formulas
        
    def analyze_team(self, 
                    team: str,
                    ratings: Dict[str, float],
                    games: List[GameResult],
                    current_date: float) -> RatingAnalysis:
        """
        Perform comprehensive analysis of a team's performance.
        
        Args:
            team: Team name
            ratings: Current ratings for all teams
            games: List of all games played
            current_date: Current timestamp
        
        Returns:
            RatingAnalysis object with comprehensive metrics
        """
        # Get team's games
        team_games = [g for g in games 
                     if team in [g.team_a, g.team_b]]
        
        if not team_games:
            return self._empty_analysis()
        
        # Calculate basic metrics
        rating = ratings[team]
        
        # Calculate recent performance trend
        recent_games = sorted(team_games, key=lambda g: g.date)[-5:]
        trend = self._calculate_trend(team, recent_games)
        
        # Calculate win probability against average team
        avg_rating = np.mean(list(ratings.values()))
        win_prob = self.formulas.calculate_win_probability(rating, avg_rating)
        
        # Calculate confidence interval
        ci = self._calculate_confidence_interval(team, team_games, rating)
        
        # Calculate variance in performance
        variance = self._calculate_performance_variance(team, team_games)
        
        return RatingAnalysis(
            rating=rating,
            power=rating + trend,  # Adjust for recent performance
            offense=self._calculate_offense(team, team_games),
            defense=self._calculate_defense(team, team_games),
            schedule_strength=self._calculate_schedule_strength(team, team_games, ratings),
            expected_wins=self._calculate_expected_wins(team, ratings, games),
            win_probability=win_prob,
            confidence_interval=ci,
            variance=variance,
            trend=trend
        )
    
    def analyze_matchup(self,
                       team_a: str,
                       team_b: str,
                       ratings: Dict[str, float],
                       games: List[GameResult]) -> MatchupAnalysis:
        """
        Analyze a specific matchup between two teams.
        
        Args:
            team_a, team_b: Teams to analyze
            ratings: Current ratings
            games: All games played
        
        Returns:
            MatchupAnalysis object with matchup-specific metrics
        """
        # Get head-to-head games
        h2h_games = [g for g in games 
                    if {g.team_a, g.team_b} == {team_a, team_b}]
        
        # Calculate win probability
        r_a = ratings[team_a]
        r_b = ratings[team_b]
        win_prob = self.formulas.calculate_win_probability(r_a, r_b)
        
        # Calculate expected margin
        exp_margin = (r_a - r_b) * 3.5  # Typical scaling factor
        
        # Calculate upset probability
        favorite = team_a if r_a > r_b else team_b
        upset_prob = self._calculate_upset_probability(
            favorite, h2h_games, ratings
        )
        
        # Identify key factors
        key_factors = self._identify_key_factors(
            team_a, team_b, ratings, games
        )
        
        # Calculate confidence in prediction
        confidence = self._calculate_prediction_confidence(
            team_a, team_b, h2h_games, ratings
        )
        
        # Get historical results
        historical = self._get_historical_results(h2h_games)
        
        return MatchupAnalysis(
            win_probability=win_prob,
            expected_margin=exp_margin,
            upset_probability=upset_prob,
            key_factors=key_factors,
            confidence=confidence,
            historical_results=historical
        )
    
    def get_decision_factors(self,
                           team_a: str,
                           team_b: str,
                           ratings: Dict[str, float],
                           games: List[GameResult]) -> Dict[str, Any]:
        """
        Get key factors for decision making.
        
        Returns dict with:
        - Prediction confidence
        - Key matchup advantages
        - Risk factors
        - Historical patterns
        - Situational factors
        """
        # Get analyses
        team_a_analysis = self.analyze_team(team_a, ratings, games, datetime.now().timestamp())
        team_b_analysis = self.analyze_team(team_b, ratings, games, datetime.now().timestamp())
        matchup = self.analyze_matchup(team_a, team_b, ratings, games)
        
        # Identify advantages
        advantages = []
        if team_a_analysis.offense > team_b_analysis.defense:
            advantages.append(f"{team_a} offense vs {team_b} defense")
        if team_a_analysis.defense > team_b_analysis.offense:
            advantages.append(f"{team_a} defense vs {team_b} offense")
            
        # Identify risk factors
        risks = []
        if team_a_analysis.variance > 0.2:
            risks.append(f"High variance in {team_a} performance")
        if abs(team_a_analysis.trend) > 50:
            risks.append(f"Significant recent trend for {team_a}")
            
        return {
            'prediction': {
                'win_probability': matchup.win_probability,
                'expected_margin': matchup.expected_margin,
                'confidence': matchup.confidence
            },
            'advantages': advantages,
            'risks': risks,
            'key_factors': matchup.key_factors,
            'historical': matchup.historical_results
        }
    
    def _calculate_trend(self, team: str, recent_games: List[GameResult]) -> float:
        """Calculate recent performance trend."""
        if not recent_games:
            return 0.0
            
        performances = []
        for game in recent_games:
            if game.team_a == team:
                perf = game.score_a - game.score_b
            else:
                perf = game.score_b - game.score_a
            performances.append(perf)
            
        # Calculate weighted average with more recent games weighted higher
        weights = np.exp(np.linspace(-1, 0, len(performances)))
        return np.average(performances, weights=weights)
    
    def _calculate_confidence_interval(self,
                                    team: str,
                                    games: List[GameResult],
                                    rating: float) -> Tuple[float, float]:
        """Calculate 95% confidence interval for rating."""
        if not games:
            return (float('-inf'), float('inf'))
            
        # Calculate standard error
        performances = []
        for game in games:
            if game.team_a == team:
                perf = game.score_a - game.score_b
            else:
                perf = game.score_b - game.score_a
            performances.append(perf)
            
        std_error = np.std(performances) / np.sqrt(len(games))
        
        # 95% confidence interval
        return (
            rating - 1.96 * std_error,
            rating + 1.96 * std_error
        )
    
    def _calculate_performance_variance(self,
                                     team: str,
                                     games: List[GameResult]) -> float:
        """Calculate variance in team's performance."""
        if not games:
            return float('inf')
            
        performances = []
        for game in games:
            if game.team_a == team:
                perf = game.score_a - game.score_b
            else:
                perf = game.score_b - game.score_a
            performances.append(perf)
            
        return np.var(performances)
    
    def _calculate_offense(self,
                         team: str,
                         games: List[GameResult]) -> float:
        """Calculate offensive rating."""
        if not games:
            return 0.0
            
        scores = []
        for game in games:
            if game.team_a == team:
                scores.append(game.score_a)
            else:
                scores.append(game.score_b)
                
        return np.mean(scores)
    
    def _calculate_defense(self,
                         team: str,
                         games: List[GameResult]) -> float:
        """Calculate defensive rating."""
        if not games:
            return 0.0
            
        scores = []
        for game in games:
            if game.team_a == team:
                scores.append(game.score_b)
            else:
                scores.append(game.score_a)
                
        return -np.mean(scores)  # Negative so higher is better
    
    def _calculate_schedule_strength(self,
                                   team: str,
                                   games: List[GameResult],
                                   ratings: Dict[str, float]) -> float:
        """Calculate strength of schedule."""
        if not games:
            return 0.0
            
        opp_ratings = []
        for game in games:
            opp = game.team_b if game.team_a == team else game.team_a
            opp_ratings.append(ratings[opp])
            
        return np.mean(opp_ratings)
    
    def _calculate_expected_wins(self,
                               team: str,
                               ratings: Dict[str, float],
                               games: List[GameResult]) -> float:
        """Calculate expected wins for remaining schedule."""
        exp_wins = 0.0
        team_rating = ratings[team]
        
        for game in games:
            if game.team_a == team:
                opp = game.team_b
                exp_wins += self.formulas.calculate_win_probability(
                    team_rating, ratings[opp]
                )
            elif game.team_b == team:
                opp = game.team_a
                exp_wins += self.formulas.calculate_win_probability(
                    team_rating, ratings[opp]
                )
                
        return exp_wins
    
    def _calculate_upset_probability(self,
                                   favorite: str,
                                   h2h_games: List[GameResult],
                                   ratings: Dict[str, float]) -> float:
        """Calculate probability of an upset based on historical data."""
        if not h2h_games:
            return 0.3  # Default upset probability
            
        # Calculate historical upset rate
        upsets = 0
        for game in h2h_games:
            pre_game_favorite = game.team_a if ratings[game.team_a] > ratings[game.team_b] else game.team_b
            winner = game.team_a if game.score_a > game.score_b else game.team_b
            if winner != pre_game_favorite:
                upsets += 1
                
        return (upsets / len(h2h_games) + 0.3) / 2  # Blend with prior
    
    def _identify_key_factors(self,
                            team_a: str,
                            team_b: str,
                            ratings: Dict[str, float],
                            games: List[GameResult]) -> List[str]:
        """Identify key factors that could influence the game."""
        factors = []
        
        # Get team analyses
        a_analysis = self.analyze_team(team_a, ratings, games, datetime.now().timestamp())
        b_analysis = self.analyze_team(team_b, ratings, games, datetime.now().timestamp())
        
        # Check offensive/defensive matchups
        if abs(a_analysis.offense - b_analysis.defense) > 10:
            factors.append(f"Significant {'advantage' if a_analysis.offense > b_analysis.defense else 'disadvantage'} for {team_a} offense")
            
        # Check recent form
        if abs(a_analysis.trend) > 20:
            factors.append(f"{team_a} has {'positive' if a_analysis.trend > 0 else 'negative'} momentum")
            
        # Check schedule strength
        if abs(a_analysis.schedule_strength - b_analysis.schedule_strength) > 100:
            factors.append(f"{team_a if a_analysis.schedule_strength > b_analysis.schedule_strength else team_b} has played tougher schedule")
            
        return factors
    
    def _calculate_prediction_confidence(self,
                                      team_a: str,
                                      team_b: str,
                                      h2h_games: List[GameResult],
                                      ratings: Dict[str, float]) -> float:
        """Calculate confidence in prediction (0-1)."""
        # Start with base confidence
        confidence = 0.7
        
        # Adjust based on number of games
        confidence *= min(1.0, len(h2h_games) / 5)
        
        # Adjust based on rating difference
        rating_diff = abs(ratings[team_a] - ratings[team_b])
        confidence *= min(1.0, rating_diff / 200)
        
        return min(1.0, confidence)
    
    def _get_historical_results(self,
                              h2h_games: List[GameResult]) -> List[Dict[str, Any]]:
        """Get historical head-to-head results."""
        return [{
            'date': game.date,
            'score': (game.score_a, game.score_b),
            'winner': game.team_a if game.score_a > game.score_b else game.team_b,
            'margin': abs(game.score_a - game.score_b)
        } for game in h2h_games]
    
    def _empty_analysis(self) -> RatingAnalysis:
        """Return empty analysis for teams with no games."""
        return RatingAnalysis(
            rating=0.0,
            power=0.0,
            offense=0.0,
            defense=0.0,
            schedule_strength=0.0,
            expected_wins=0.0,
            win_probability=0.5,
            confidence_interval=(float('-inf'), float('inf')),
            variance=float('inf'),
            trend=0.0
        ) 