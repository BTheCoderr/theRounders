import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NBAOddsAnalyzer:
    def __init__(self):
        self.model_path = Path('models/nba_line_predictor.joblib')
        self.scaler_path = Path('models/nba_scaler.joblib')
        self.model = self._load_model()
        self.scaler = self._load_scaler()
        self.key_injuries = {}  # Cache for injury impacts
        self.rest_days = {}  # Cache for team rest days
        self.back_to_back = {}  # Cache for B2B games
        self.home_away_splits = {}  # Cache for team performance splits
        
    def _load_model(self):
        """Load or create the prediction model"""
        if self.model_path.exists():
            return joblib.load(self.model_path)
        return self._create_model()
    
    def _load_scaler(self):
        """Load or create the feature scaler"""
        if self.scaler_path.exists():
            return joblib.load(self.scaler_path)
        return StandardScaler()
    
    def _create_model(self):
        """Create a new prediction model"""
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def analyze_nba_game(self, game_id: str, odds_data: Dict) -> Dict:
        """Comprehensive NBA game analysis"""
        analysis = {
            'line_prediction': self.predict_line(game_id, odds_data),
            'injury_impact': self.analyze_injuries(game_id),
            'situational_spots': self.analyze_situational_spots(game_id),
            'arbitrage_opportunities': self.find_nba_arbitrage(odds_data),
            'value_bets': self.find_nba_value_bets(odds_data),
            'live_betting_opportunities': self.analyze_live_betting_spots(game_id)
        }
        
        # Calculate overall edge
        analysis['edge'] = self.calculate_edge(analysis)
        return analysis
    
    def predict_line(self, game_id: str, odds_data: Dict) -> Dict:
        """Predict the fair line using machine learning"""
        features = self._extract_features(game_id, odds_data)
        if features is None:
            return None
            
        scaled_features = self.scaler.transform([features])
        predicted_line = self.model.predict(scaled_features)[0]
        
        return {
            'predicted_line': predicted_line,
            'sharp_consensus': self._get_sharp_consensus(odds_data),
            'model_confidence': self._calculate_model_confidence(predicted_line, odds_data)
        }
    
    def analyze_injuries(self, game_id: str) -> Dict:
        """Analyze impact of injuries on the line"""
        if game_id in self.key_injuries:
            return self.key_injuries[game_id]
            
        # Fetch latest injury data
        injuries = self._fetch_injury_data(game_id)
        impact = self._calculate_injury_impact(injuries)
        
        self.key_injuries[game_id] = impact
        return impact
    
    def analyze_situational_spots(self, game_id: str) -> Dict:
        """Analyze situational betting spots"""
        return {
            'rest_advantage': self._analyze_rest_advantage(game_id),
            'back_to_back': self._check_back_to_back(game_id),
            'travel_impact': self._analyze_travel_impact(game_id),
            'schedule_spot': self._analyze_schedule_spot(game_id)
        }
    
    def find_nba_arbitrage(self, odds_data: Dict) -> List[Dict]:
        """Find NBA-specific arbitrage opportunities"""
        opportunities = []
        
        # Check quarter lines arbitrage
        quarter_arb = self._check_quarter_lines_arbitrage(odds_data)
        if quarter_arb:
            opportunities.extend(quarter_arb)
        
        # Check player props arbitrage
        props_arb = self._check_player_props_arbitrage(odds_data)
        if props_arb:
            opportunities.extend(props_arb)
        
        # Check alternative lines arbitrage
        alt_lines_arb = self._check_alternative_lines_arbitrage(odds_data)
        if alt_lines_arb:
            opportunities.extend(alt_lines_arb)
        
        return opportunities
    
    def find_nba_value_bets(self, odds_data: Dict) -> List[Dict]:
        """Find NBA-specific value betting opportunities"""
        value_bets = []
        
        # Check first quarter/half lines
        period_value = self._analyze_period_lines(odds_data)
        if period_value:
            value_bets.extend(period_value)
        
        # Check player props value
        props_value = self._analyze_player_props(odds_data)
        if props_value:
            value_bets.extend(props_value)
        
        # Check team totals value
        totals_value = self._analyze_team_totals(odds_data)
        if totals_value:
            value_bets.extend(totals_value)
        
        return value_bets
    
    def analyze_live_betting_spots(self, game_id: str) -> Dict:
        """Analyze potential live betting opportunities"""
        return {
            'momentum_shifts': self._analyze_momentum(game_id),
            'key_numbers': self._get_nba_key_numbers(),
            'live_betting_triggers': self._get_live_triggers(game_id)
        }
    
    def _extract_features(self, game_id: str, odds_data: Dict) -> Optional[List[float]]:
        """Extract features for prediction model"""
        try:
            features = []
            
            # Team performance metrics
            team_stats = self._get_team_stats(game_id)
            features.extend([
                team_stats['home_team_rating'],
                team_stats['away_team_rating'],
                team_stats['home_team_pace'],
                team_stats['away_team_pace'],
                team_stats['home_team_efficiency'],
                team_stats['away_team_efficiency']
            ])
            
            # Rest and schedule factors
            schedule_factors = self._get_schedule_factors(game_id)
            features.extend([
                schedule_factors['home_rest_days'],
                schedule_factors['away_rest_days'],
                schedule_factors['home_games_last_7'],
                schedule_factors['away_games_last_7']
            ])
            
            # Market factors
            market_factors = self._get_market_factors(odds_data)
            features.extend([
                market_factors['opening_line'],
                market_factors['sharp_money_percentage'],
                market_factors['public_money_percentage']
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features for game {game_id}: {str(e)}")
            return None
    
    def _get_sharp_consensus(self, odds_data: Dict) -> float:
        """Calculate sharp books consensus line"""
        sharp_lines = []
        for book in ["Pinnacle", "Circa", "Bookmaker"]:
            if book in odds_data and 'spread' in odds_data[book]:
                sharp_lines.append(odds_data[book]['spread'])
        
        return np.mean(sharp_lines) if sharp_lines else None
    
    def _calculate_model_confidence(self, predicted_line: float, odds_data: Dict) -> float:
        """Calculate confidence in the model's prediction"""
        sharp_consensus = self._get_sharp_consensus(odds_data)
        if sharp_consensus is None:
            return 0.5
            
        # Calculate confidence based on difference from sharp consensus
        diff = abs(predicted_line - sharp_consensus)
        return max(0, 1 - (diff / 2))  # Scale confidence down as difference increases
    
    def _analyze_rest_advantage(self, game_id: str) -> Dict:
        """Analyze rest advantage between teams"""
        home_rest = self.rest_days.get(f"{game_id}_home", 0)
        away_rest = self.rest_days.get(f"{game_id}_away", 0)
        
        rest_advantage = home_rest - away_rest
        impact = 0.5 * rest_advantage  # Each day of rest worth 0.5 points
        
        return {
            'rest_advantage': rest_advantage,
            'line_impact': impact,
            'significant': abs(rest_advantage) >= 2
        }
    
    def _check_back_to_back(self, game_id: str) -> Dict:
        """Check for back-to-back situations"""
        return {
            'home_b2b': self.back_to_back.get(f"{game_id}_home", False),
            'away_b2b': self.back_to_back.get(f"{game_id}_away", False),
            'line_impact': self._calculate_b2b_impact(game_id)
        }
    
    def _analyze_travel_impact(self, game_id: str) -> Dict:
        """Analyze impact of travel on teams"""
        # Implementation would analyze travel distance and time zones crossed
        return {}
    
    def _analyze_schedule_spot(self, game_id: str) -> Dict:
        """Analyze schedule spot factors"""
        # Implementation would look for look-ahead spots, letdown spots, etc.
        return {}
    
    def _check_quarter_lines_arbitrage(self, odds_data: Dict) -> List[Dict]:
        """Check for arbitrage in quarter and half lines"""
        opportunities = []
        
        # Check each quarter and half line combination
        for period in ['1Q', '2Q', '3Q', '4Q', '1H', '2H']:
            if f"{period}_lines" in odds_data:
                period_odds = odds_data[f"{period}_lines"]
                arb = self._check_period_arbitrage(period_odds)
                if arb:
                    opportunities.append(arb)
        
        return opportunities
    
    def _check_player_props_arbitrage(self, odds_data: Dict) -> List[Dict]:
        """Check for arbitrage in player props"""
        opportunities = []
        
        if 'player_props' in odds_data:
            for player, props in odds_data['player_props'].items():
                for prop_type, lines in props.items():
                    arb = self._check_prop_arbitrage(lines)
                    if arb:
                        opportunities.append({
                            'player': player,
                            'prop_type': prop_type,
                            **arb
                        })
        
        return opportunities
    
    def _check_alternative_lines_arbitrage(self, odds_data: Dict) -> List[Dict]:
        """Check for arbitrage in alternative lines"""
        opportunities = []
        
        if 'alternative_lines' in odds_data:
            alt_lines = odds_data['alternative_lines']
            for line in alt_lines:
                arb = self._check_line_arbitrage(line)
                if arb:
                    opportunities.append(arb)
        
        return opportunities
    
    def _analyze_period_lines(self, odds_data: Dict) -> List[Dict]:
        """Analyze value in quarter and half lines"""
        value_bets = []
        
        for period in ['1Q', '2Q', '3Q', '4Q', '1H', '2H']:
            if f"{period}_lines" in odds_data:
                period_odds = odds_data[f"{period}_lines"]
                value = self._find_period_value(period_odds)
                if value:
                    value_bets.append(value)
        
        return value_bets
    
    def _analyze_player_props(self, odds_data: Dict) -> List[Dict]:
        """Analyze value in player props"""
        value_bets = []
        
        if 'player_props' in odds_data:
            for player, props in odds_data['player_props'].items():
                for prop_type, lines in props.items():
                    value = self._find_prop_value(lines)
                    if value:
                        value_bets.append({
                            'player': player,
                            'prop_type': prop_type,
                            **value
                        })
        
        return value_bets
    
    def _analyze_team_totals(self, odds_data: Dict) -> List[Dict]:
        """Analyze value in team totals"""
        value_bets = []
        
        if 'team_totals' in odds_data:
            for team, total in odds_data['team_totals'].items():
                value = self._find_total_value(total)
                if value:
                    value_bets.append({
                        'team': team,
                        **value
                    })
        
        return value_bets
    
    def _analyze_momentum(self, game_id: str) -> Dict:
        """Analyze game momentum for live betting"""
        # Implementation would analyze scoring runs, momentum shifts, etc.
        return {}
    
    def _get_nba_key_numbers(self) -> List[int]:
        """Get key numbers for NBA betting"""
        return [3, 4, 5, 6, 7, 8, 9, 10]  # Common NBA margins
    
    def _get_live_triggers(self, game_id: str) -> List[Dict]:
        """Get triggers for live betting opportunities"""
        # Implementation would define scenarios to watch for live betting
        return []
    
    def calculate_edge(self, analysis: Dict) -> float:
        """Calculate overall betting edge"""
        edge = 0.0
        
        # Factor in model prediction
        if analysis['line_prediction']:
            edge += self._calculate_prediction_edge(analysis['line_prediction'])
        
        # Factor in injuries
        if analysis['injury_impact']:
            edge += self._calculate_injury_edge(analysis['injury_impact'])
        
        # Factor in situational spots
        if analysis['situational_spots']:
            edge += self._calculate_situational_edge(analysis['situational_spots'])
        
        return edge
    
    def _calculate_prediction_edge(self, prediction: Dict) -> float:
        """Calculate edge from model prediction"""
        if not prediction['predicted_line'] or not prediction['sharp_consensus']:
            return 0.0
            
        raw_edge = abs(prediction['predicted_line'] - prediction['sharp_consensus'])
        return raw_edge * prediction['model_confidence']
    
    def _calculate_injury_edge(self, injury_impact: Dict) -> float:
        """Calculate edge from injury analysis"""
        # Implementation would calculate edge based on injury impacts
        return 0.0
    
    def _calculate_situational_edge(self, situational: Dict) -> float:
        """Calculate edge from situational spots"""
        edge = 0.0
        
        if situational['rest_advantage']['significant']:
            edge += abs(situational['rest_advantage']['line_impact'])
        
        if situational['back_to_back']['home_b2b'] or situational['back_to_back']['away_b2b']:
            edge += abs(situational['back_to_back']['line_impact'])
        
        return edge 