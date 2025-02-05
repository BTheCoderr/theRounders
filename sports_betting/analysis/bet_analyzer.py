from datetime import datetime
import numpy as np
from typing import Dict, List, Optional
from .advanced_patterns import AdvancedPatterns
from .weight_calculator import WeightCalculator
from .betting_patterns import BettingPatterns
from .betting_config import BETTING_CONFIG, RESPECTED_BOOKS

class BetAnalyzer:
    def __init__(self):
        self.patterns = AdvancedPatterns()
        self.weight_calc = WeightCalculator()
        
        # Risk Management Parameters
        self.risk_params = {
            'max_daily_risk': 0.15,    # Maximum 15% of bankroll at risk per day
            'max_single_bet': 0.05,    # Maximum 5% of bankroll on single bet
            'max_sport_exposure': 0.25, # Maximum 25% exposure per sport
            'min_confidence': {
                'NFL': 0.67,
                'NBA': 0.65,
                'NCAAB': 0.68,
                'NHL': 0.66
            },
            'min_edge': {
                'NFL': 0.035,
                'NBA': 0.03,
                'NCAAB': 0.04,
                'NHL': 0.035
            }
        }
        
        # Sport-Specific Analysis Weights
        self.sport_weights = {
            'NFL': {
                'sharp_action': 0.35,
                'patterns': 0.25,
                'situational': 0.25,
                'market_edge': 0.15
            },
            'NBA': {
                'sharp_action': 0.30,
                'patterns': 0.20,
                'situational': 0.30,
                'market_edge': 0.20
            }
        }
        
    def analyze_bet_opportunity(self, game_data: Dict, odds_data: Dict, sport: str, 
                              current_exposure: Dict, bankroll: float) -> Dict:
        """Enhanced bet analysis with risk management"""
        
        analysis = {
            'confidence': 0,
            'recommended_bet': None,
            'bet_size': 0,
            'factors': [],
            'warnings': [],
            'edge': 0,
            'risk_assessment': {},
            'statistical_support': {}
        }
        
        try:
            # 1. Enhanced Pattern Analysis
            pattern_matches = self._analyze_patterns_by_sport(game_data, sport)
            
            # 2. Sharp Money Analysis with Book Weighting
            sharp_analysis = self._analyze_sharp_action(odds_data, sport)
            
            # 3. Market Analysis with Steam Detection
            market_edge = self._calculate_market_edge(odds_data, sharp_analysis)
            
            # 4. Sport-Specific Situational Analysis
            situational_factors = self._analyze_situational_factors(game_data, sport)
            
            # 5. Calculate Combined Confidence with Sport Weights
            confidence = self._calculate_sport_specific_confidence(
                pattern_matches,
                sharp_analysis,
                market_edge,
                situational_factors,
                sport
            )
            
            # 6. Risk Management Check
            risk_assessment = self._assess_risk(
                confidence,
                market_edge,
                current_exposure,
                bankroll,
                sport
            )
            
            if risk_assessment['approved']:
                # 7. Calculate Optimal Bet Size
                bet_size = self._calculate_optimal_bet_size(
                    confidence,
                    market_edge,
                    risk_assessment,
                    sport
                )
                
                recommended_bet = self._determine_best_bet(odds_data, confidence, sport)
                
                analysis.update({
                    'confidence': confidence,
                    'recommended_bet': recommended_bet,
                    'bet_size': bet_size,
                    'edge': market_edge,
                    'risk_assessment': risk_assessment,
                    'factors': self._get_supporting_factors(
                        pattern_matches,
                        sharp_analysis,
                        situational_factors,
                        sport
                    )
                })
                
            # 8. Add Statistical Support and Confidence Intervals
            analysis['statistical_support'] = self._generate_statistical_support(
                pattern_matches,
                sharp_analysis,
                market_edge,
                sport
            )
            
            return analysis
            
        except Exception as e:
            print(f"Error in bet analysis: {str(e)}")
            return None
            
    def _analyze_patterns_by_sport(self, game_data: Dict, sport: str) -> Dict:
        """Sport-specific pattern analysis"""
        if sport == 'NFL':
            return self._analyze_nfl_patterns(game_data)
        elif sport == 'NBA':
            return self._analyze_nba_patterns(game_data)
        # Add other sports...
        
    def _analyze_sharp_action(self, odds_data, sport):
        """Analyze sharp betting action"""
        sharp_indicators = {
            'steam_moves': [],
            'reverse_line_movement': False,
            'respected_book_movement': [],
            'sharp_consensus': 0
        }
        
        # Track movements from respected books
        for book in RESPECTED_BOOKS['primary']:
            if book in odds_data['line_history']:
                movement = self._analyze_book_movement(odds_data['line_history'][book])
                if movement['significant']:
                    sharp_indicators['respected_book_movement'].append(movement)
                    
        # Calculate sharp consensus
        if sharp_indicators['respected_book_movement']:
            consensus = sum(1 for m in sharp_indicators['respected_book_movement'] 
                          if m['direction'] == sharp_indicators['respected_book_movement'][0]['direction'])
            sharp_indicators['sharp_consensus'] = consensus / len(sharp_indicators['respected_book_movement'])
            
        return sharp_indicators
        
    def _calculate_market_edge(self, odds_data, sharp_analysis):
        """Calculate theoretical edge in the market"""
        best_odds = odds_data['best_odds']
        consensus_odds = odds_data['consensus']
        
        if not best_odds or not consensus_odds:
            return 0
            
        # Convert odds to probabilities and calculate edge
        implied_prob = self._convert_odds_to_probability(consensus_odds)
        best_prob = self._convert_odds_to_probability(best_odds)
        
        return max(0, best_prob - implied_prob)
        
    def _assess_risk(self, confidence, edge, current_exposure, bankroll, sport):
        """Assess risk based on current exposure and bankroll"""
        # Implement risk assessment logic here
        return {'approved': True}
        
    def _calculate_optimal_bet_size(self, confidence, edge, risk_assessment, sport):
        """Calculate optimal bet size using Kelly Criterion"""
        # Conservative Kelly (using 1/4 Kelly)
        kelly = (edge * confidence) / 0.25
        return min(kelly, 0.05)  # Cap at 5% of bankroll
        
    def _get_supporting_factors(self, patterns, sharp, situational, sport):
        """Compile supporting factors for the bet"""
        factors = []
        
        # Add pattern-based factors
        if patterns.get('win_rate', 0) > 0.53:
            factors.append({
                'type': 'pattern',
                'description': f"Historical win rate: {patterns['win_rate']:.3f}",
                'strength': 'strong' if patterns['win_rate'] > 0.55 else 'moderate'
            })
            
        # Add sharp action factors
        if sharp['sharp_consensus'] > 0.7:
            factors.append({
                'type': 'sharp_action',
                'description': f"Sharp consensus: {sharp['sharp_consensus']:.2f}",
                'strength': 'strong'
            })
            
        # Add situational factors
        for factor in situational:
            if factor['weight'] > 1.1:
                factors.append({
                    'type': 'situational',
                    'description': factor['description'],
                    'strength': 'strong' if factor['weight'] > 1.2 else 'moderate'
                })
                
        return factors
        
    def _generate_statistical_support(self, pattern_matches, sharp_analysis, market_edge, sport):
        """Generate statistical support and confidence intervals"""
        # Implement statistical support generation logic here
        return {
            'sample_size': pattern_matches.get('sample_size', 0),
            'historical_win_rate': pattern_matches.get('win_rate', 0),
            'confidence_interval': pattern_matches.get('confidence_interval', []),
            'variance': pattern_matches.get('variance', 0)
        }
        
    def _analyze_situational_factors(self, game_data, sport):
        """Analyze situational factors"""
        # Implement situational factors analysis logic here
        return []
        
    def _convert_odds_to_probability(self, odds):
        """Convert odds to probability"""
        if odds > 0:
            return 1 / (1 + odds / 100)
        else:
            return 1 / (1 - odds / 100)
        
    def _determine_best_bet(self, odds_data, confidence, sport):
        """Determine the best bet"""
        # Implement best bet determination logic here
        return None
        
    def _analyze_book_movement(self, book_history):
        """Analyze book movement"""
        # Implement book movement analysis logic here
        return {'significant': False}
        
    def _analyze_nfl_patterns(self, game_data):
        """Analyze NFL patterns"""
        # Implement NFL pattern analysis logic here
        return {}
        
    def _analyze_nba_patterns(self, game_data):
        """Analyze NBA patterns"""
        # Implement NBA pattern analysis logic here
        return {}
        
# Example usage
analyzer = BetAnalyzer()

game_data = {
    'home_team': 'Lakers',
    'away_team': 'Warriors',
    'sport': 'NBA',
    'conditions': {
        'rest_advantage': True,
        'back_to_back': False
    }
}

odds_data = {
    'line_history': {...},
    'best_odds': -110,
    'consensus': -110
}

analysis = analyzer.analyze_bet_opportunity(game_data, odds_data, 'NBA')

if analysis['recommended_bet']:
    print(f"Recommended Bet: {analysis['recommended_bet']}")
    print(f"Confidence: {analysis['confidence']:.2f}")
    print(f"Bet Size: {analysis['bet_size']:.2f}% of bankroll")
    print("\nSupporting Factors:")
    for factor in analysis['factors']:
        print(f"- {factor['description']} ({factor['strength']})")