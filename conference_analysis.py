from typing import Dict, List, Tuple, Any
import numpy as np
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ConferenceStats:
    """Container for conference-level statistics."""
    rating: float
    parity: float
    intra_record: Tuple[int, int, int]  # W-L-T within conference
    inter_record: Tuple[int, int, int]  # W-L-T against other conferences
    strength_of_schedule: float
    top_team: str
    bottom_team: str
    average_margin: float
    home_advantage: float

class ConferenceAnalysis:
    def __init__(self, elos_ratings, conference_mapping: Dict[str, str]):
        """
        Initialize with ElosRatings instance and conference mapping.
        
        Args:
            elos_ratings: ElosRatings instance
            conference_mapping: Dict mapping team names to conference names
        """
        self.ratings = elos_ratings
        self.conference_mapping = conference_mapping
        self.conferences = set(conference_mapping.values())
    
    def calculate_conference_ratings(self) -> Dict[str, float]:
        """Calculate overall conference ratings."""
        team_ratings = self.ratings.calculate_ratings()
        conf_ratings = defaultdict(list)
        
        # Group team ratings by conference
        for team, rating in team_ratings.items():
            conf = self.conference_mapping.get(team)
            if conf:
                conf_ratings[conf].append(rating)
        
        # Calculate average rating for each conference
        return {conf: np.mean(ratings) for conf, ratings in conf_ratings.items()}
    
    def calculate_conference_records(self) -> Dict[str, Dict[str, Tuple[int, int, int]]]:
        """
        Calculate conference records (both intra and inter-conference).
        Returns dict mapping conference to dict of opponent conference to W-L-T record.
        """
        records = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
        
        for game in self.ratings.games:
            conf_a = self.conference_mapping.get(game.team_a)
            conf_b = self.conference_mapping.get(game.team_b)
            
            if not (conf_a and conf_b):
                continue
                
            # Determine winner
            if game.score_a > game.score_b:
                records[conf_a][conf_b][0] += 1  # Win
                records[conf_b][conf_a][1] += 1  # Loss
            elif game.score_b > game.score_a:
                records[conf_a][conf_b][1] += 1  # Loss
                records[conf_b][conf_a][0] += 1  # Win
            else:
                records[conf_a][conf_b][2] += 1  # Tie
                records[conf_b][conf_a][2] += 1  # Tie
        
        return {c1: {c2: tuple(r) for c2, r in recs.items()}
                for c1, recs in records.items()}
    
    def calculate_conference_parity(self) -> Dict[str, float]:
        """
        Calculate parity index for each conference.
        1.0 indicates perfect parity, 0.0 indicates complete imbalance.
        """
        team_ratings = self.ratings.calculate_ratings()
        conf_parity = {}
        
        for conf in self.conferences:
            # Get ratings for teams in this conference
            conf_teams = [t for t, c in self.conference_mapping.items() if c == conf]
            if not conf_teams:
                continue
                
            ratings = [team_ratings[t] for t in conf_teams]
            
            # Calculate standard deviation
            rating_std = np.std(ratings)
            rating_range = max(ratings) - min(ratings)
            
            # Parity index based on rating distribution
            if rating_range > 0:
                conf_parity[conf] = 1.0 / (1.0 + rating_std/100)
            else:
                conf_parity[conf] = 1.0
        
        return conf_parity
    
    def calculate_conference_strength_of_schedule(self) -> Dict[str, float]:
        """Calculate average strength of schedule for each conference."""
        team_sos = self.ratings.calculate_schedule_strength()
        conf_sos = defaultdict(list)
        
        for team, sos in team_sos.items():
            conf = self.conference_mapping.get(team)
            if conf:
                conf_sos[conf].append(sos)
        
        return {conf: np.mean(scores) for conf, scores in conf_sos.items()}
    
    def get_conference_stats(self) -> Dict[str, ConferenceStats]:
        """Get comprehensive statistics for each conference."""
        ratings = self.calculate_conference_ratings()
        parity = self.calculate_conference_parity()
        records = self.calculate_conference_records()
        sos = self.calculate_conference_strength_of_schedule()
        team_ratings = self.ratings.calculate_ratings()
        
        stats = {}
        for conf in self.conferences:
            # Get teams in this conference
            conf_teams = [t for t, c in self.conference_mapping.items() if c == conf]
            if not conf_teams:
                continue
            
            # Find top and bottom teams
            conf_team_ratings = {t: team_ratings[t] for t in conf_teams}
            top_team = max(conf_team_ratings.items(), key=lambda x: x[1])[0]
            bottom_team = min(conf_team_ratings.items(), key=lambda x: x[1])[0]
            
            # Calculate average margin in conference games
            margins = []
            home_margins = []
            for game in self.ratings.games:
                if game.team_a in conf_teams and game.team_b in conf_teams:
                    margin = abs(game.score_a - game.score_b)
                    margins.append(margin)
                    if game.is_home_a:
                        home_margins.append(game.score_a - game.score_b)
            
            avg_margin = np.mean(margins) if margins else 0
            home_adv = np.mean(home_margins) if home_margins else 0
            
            # Get intra-conference record
            intra_record = records[conf][conf] if conf in records else (0, 0, 0)
            
            # Get combined inter-conference record
            inter_w = inter_l = inter_t = 0
            for opp_conf, record in records.get(conf, {}).items():
                if opp_conf != conf:
                    inter_w += record[0]
                    inter_l += record[1]
                    inter_t += record[2]
            
            stats[conf] = ConferenceStats(
                rating=ratings.get(conf, 0.0),
                parity=parity.get(conf, 1.0),
                intra_record=intra_record,
                inter_record=(inter_w, inter_l, inter_t),
                strength_of_schedule=sos.get(conf, 0.0),
                top_team=top_team,
                bottom_team=bottom_team,
                average_margin=avg_margin,
                home_advantage=home_adv
            )
        
        return stats
    
    def get_rivalry_stats(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Analyze conference rivalries based on game history."""
        rivalries = {}
        
        for conf1 in self.conferences:
            for conf2 in self.conferences:
                if conf1 >= conf2:  # Avoid duplicates
                    continue
                
                # Get all games between these conferences
                games = []
                for game in self.ratings.games:
                    conf_a = self.conference_mapping.get(game.team_a)
                    conf_b = self.conference_mapping.get(game.team_b)
                    if {conf_a, conf_b} == {conf1, conf2}:
                        games.append(game)
                
                if not games:
                    continue
                
                # Calculate rivalry metrics
                margins = [abs(g.score_a - g.score_b) for g in games]
                avg_margin = np.mean(margins)
                close_games = sum(1 for m in margins if m <= 7)  # One score games
                
                rivalries[(conf1, conf2)] = {
                    'games_played': len(games),
                    'average_margin': avg_margin,
                    'close_games': close_games,
                    'close_game_pct': close_games / len(games)
                }
        
        return rivalries 