from typing import Dict, List, Optional
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime
from abc import ABC, abstractmethod

class SportPropsBase(ABC):
    """Base class for sport-specific prop analysis"""
    @abstractmethod
    def get_prop_types(self) -> List[str]:
        pass
        
    @abstractmethod
    def get_player_metrics(self) -> Dict:
        pass
        
    @abstractmethod
    def analyze_matchup(self, player_id: str, opponent_id: str) -> Dict:
        pass

class NFLProps(SportPropsBase):
    def get_prop_types(self) -> List[str]:
        return [
            'passing_yards', 'passing_tds', 'interceptions',
            'rushing_yards', 'rushing_attempts', 'rushing_tds',
            'receiving_yards', 'receptions', 'receiving_tds',
            'tackles_assists', 'sacks', 'qb_hits',
            'kicking_points', 'field_goals'
        ]
        
    def get_player_metrics(self) -> Dict:
        return {
            'QB': ['cpoe', 'air_yards', 'pressure_rate', 'time_to_throw'],
            'RB': ['yards_after_contact', 'broken_tackles', 'stuff_rate'],
            'WR': ['separation', 'catch_rate', 'target_share'],
            'TE': ['route_participation', 'blocking_rate', 'redzone_targets'],
            'DEF': ['pressure_rate', 'missed_tackle_rate', 'coverage_grade']
        }

class NBAProps(SportPropsBase):
    def get_prop_types(self) -> List[str]:
        return [
            'points', 'rebounds', 'assists',
            'threes_made', 'blocks', 'steals',
            'pts_reb_ast', 'pts_reb', 'pts_ast',
            'stocks', 'double_double', 'triple_double',
            'turnovers', 'minutes'
        ]
        
    def get_player_metrics(self) -> Dict:
        return {
            'usage_rate', 'true_shooting', 'assist_rate',
            'rebound_rate', 'defensive_rating', 'pace_impact',
            'minutes_per_game', 'rest_impact', 'b2b_impact'
        }

class NHLProps(SportPropsBase):
    def get_prop_types(self) -> List[str]:
        return [
            'goals', 'assists', 'points',
            'shots_on_goal', 'blocked_shots',
            'power_play_points', 'hits',
            'saves', 'goals_against',
            'time_on_ice'
        ]
        
    def get_player_metrics(self) -> Dict:
        return {
            'shooting_percentage', 'time_on_ice',
            'power_play_time', 'zone_starts',
            'quality_of_competition', 'line_combination',
            'rest_impact', 'home_away_split'
        }

class MultiSportPropScanner:
    def __init__(self):
        self.sports = {
            'NFL': NFLProps(),
            'NBA': NBAProps(),
            'NHL': NHLProps()
        }
        self.prop_history = {}
        self.correlations = {}
        
    def scan_all_props(self, date: str) -> Dict:
        """Scan all available props across sports"""
        opportunities = {}
        
        for sport, analyzer in self.sports.items():
            try:
                props = self._get_available_props(sport, date)
                analyzed_props = self._analyze_props(props, sport)
                opportunities[sport] = self._filter_best_opportunities(analyzed_props)
                
            except Exception as e:
                logger.error(f"Error scanning {sport} props: {str(e)}")
                
        return opportunities
        
    def _analyze_props(self, props: List[Dict], sport: str) -> List[Dict]:
        """Analyze each prop for edges"""
        analyzed = []
        
        for prop in props:
            analysis = {
                'sport': sport,
                'player': prop['player'],
                'prop_type': prop['type'],
                'line': prop['line'],
                'odds': prop['odds'],
                'prediction': self._get_prediction(prop, sport),
                'metrics': self._get_player_metrics(prop, sport),
                'matchup': self._analyze_matchup(prop, sport),
                'correlations': self._get_correlated_props(prop, sport)
            }
            
            analysis['edge'] = self._calculate_edge(analysis)
            analysis['confidence'] = self._calculate_confidence(analysis)
            
            analyzed.append(analysis)
            
        return analyzed
        
    def _filter_best_opportunities(self, props: List[Dict]) -> List[Dict]:
        """Filter for best betting opportunities"""
        filtered = []
        
        for prop in props:
            if (prop['edge'] > 5 and prop['confidence'] > 0.65):  # Customizable thresholds
                filtered.append(prop)
                
        # Sort by edge * confidence
        return sorted(filtered, 
                     key=lambda x: x['edge'] * x['confidence'],
                     reverse=True)
                     
    def _get_correlated_props(self, prop: Dict, sport: str) -> Dict:
        """Find correlated props for the same player/game"""
        correlations = {}
        
        if sport == 'NBA':
            if prop['type'] == 'points':
                correlations['related_props'] = ['pts_reb_ast', 'pts_reb', 'pts_ast']
                correlations['impact'] = self._calculate_correlation_impact(prop)
                
        elif sport == 'NHL':
            if prop['type'] == 'shots_on_goal':
                correlations['related_props'] = ['goals', 'points']
                correlations['impact'] = self._calculate_correlation_impact(prop)
                
        return correlations
        
    def get_best_bets(self, min_edge: float = 5.0, 
                      min_confidence: float = 0.65) -> List[Dict]:
        """Get best betting opportunities across all sports"""
        all_opportunities = self.scan_all_props(datetime.now().strftime('%Y-%m-%d'))
        
        best_bets = []
        for sport, props in all_opportunities.items():
            for prop in props:
                if (prop['edge'] >= min_edge and 
                    prop['confidence'] >= min_confidence):
                    
                    bet_size = self._calculate_bet_size(prop)
                    prop['recommended_bet'] = bet_size
                    best_bets.append(prop)
                    
        return sorted(best_bets, 
                     key=lambda x: x['edge'] * x['confidence'],
                     reverse=True)

# Initialize scanner
scanner = MultiSportPropScanner()

# Get today's best opportunities
best_bets = scanner.get_best_bets(min_edge=6.0, min_confidence=0.70)

# Print recommendations
for bet in best_bets:
    print(f"\nSport: {bet['sport']}")
    print(f"Player: {bet['player']}")
    print(f"Prop: {bet['prop_type']}")
    print(f"Line: {bet['line']}")
    print(f"Edge: {bet['edge']:.1f}%")
    print(f"Confidence: {bet['confidence']:.1f}%")
    print(f"Recommended Bet: {bet['recommended_bet']:.1f}% of bankroll")
    
    if bet['correlations']:
        print("\nCorrelated Props:")
        for related in bet['correlations']['related_props']:
            print(f"- {related}") 