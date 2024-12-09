import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
from sports_betting.analysis.betting_config import RESPECTED_BOOKS

class LineMovementAnalyzer:
    def __init__(self):
        self.threshold_sharp = 0.5  # Sharp money threshold
        self.threshold_public = 70   # Public betting percentage threshold
        
    def analyze(self, odds_data, public_betting_data=None):
        """Analyze line movements and betting patterns"""
        self.movements = {}
        
        # Track line movements over time
        for game_id, odds_history in odds_data.groupby('game_id'):
            self.movements[game_id] = self.analyze_game_movement(
                odds_history,
                public_betting_data.get(game_id) if public_betting_data else None
            )
            
        return pd.DataFrame.from_dict(self.movements, orient='index')
    
    def analyze_game_movement(self, odds_history, public_betting=None):
        """Analyze line movement for a specific game"""
        
        # Sort odds history by timestamp
        odds_history = odds_history.sort_values('timestamp')
        
        # Calculate key metrics
        opening_line = self.get_opening_line(odds_history)
        current_line = self.get_current_line(odds_history)
        line_movement = current_line - opening_line
        
        # Analyze movement patterns
        sharp_movement = self.detect_sharp_movement(
            odds_history,
            public_betting
        )
        
        steam_move = self.detect_steam_move(odds_history)
        reverse_line_movement = self.detect_reverse_line_movement(
            odds_history,
            public_betting
        )
        
        # Additional market factors
        consensus_line = self.calculate_consensus_line(odds_history)
        line_volatility = self.calculate_line_volatility(odds_history)
        
        return {
            'opening_line': opening_line,
            'current_line': current_line,
            'line_movement': line_movement,
            'sharp_movement': sharp_movement,
            'steam_move': steam_move,
            'reverse_line_movement': reverse_line_movement,
            'consensus_line': consensus_line,
            'line_volatility': line_volatility,
            'movement_strength': self.calculate_movement_strength(
                line_movement,
                sharp_movement,
                steam_move,
                line_volatility
            ),
            'recommended_play': self.get_recommended_play(
                line_movement,
                sharp_movement,
                reverse_line_movement,
                line_volatility
            )
        }
    
    def detect_sharp_movement(self, odds_history, public_betting=None):
        """Detect sharp money movement"""
        if public_betting is None:
            return self.detect_sharp_movement_by_odds(odds_history)
            
        # Compare line movement to public betting percentages
        line_movement = self.get_current_line(odds_history) - self.get_opening_line(odds_history)
        public_pct = public_betting.get('public_percentage', 50)
        
        # Reverse line movement indicator
        if (public_pct > self.threshold_public and line_movement < 0) or \
           (public_pct < (100 - self.threshold_public) and line_movement > 0):
            return True
            
        return False
    
    def detect_steam_move(self, odds_history):
        """Detect steam moves (sudden line movements across multiple books)"""
        movements = odds_history.sort_values('timestamp')
        
        # Look for significant moves within short time windows
        for i in range(len(movements) - 1):
            time_diff = movements.iloc[i+1]['timestamp'] - movements.iloc[i]['timestamp']
            line_diff = abs(movements.iloc[i+1]['spread'] - movements.iloc[i]['spread'])
            
            # If big move happens quickly across books
            if time_diff.total_seconds() < 300 and line_diff >= 0.5:  # 5 minutes, half point
                return True
        
        return False
    
    def detect_reverse_line_movement(self, odds_history, public_betting=None):
        """Detect reverse line movement"""
        if public_betting is None:
            return False
            
        public_side = 'favorite' if public_betting.get('public_percentage', 50) > 60 else 'underdog'
        line_movement = self.get_current_line(odds_history) - self.get_opening_line(odds_history)
        
        # Line moving opposite to public betting
        if public_side == 'favorite' and line_movement > 0:
            return True
        if public_side == 'underdog' and line_movement < 0:
            return True
            
        return False
    
    def calculate_consensus_line(self, odds_history):
        """Calculate consensus line across multiple sportsbooks"""
        return odds_history['spread'].mean()
    
    def calculate_line_volatility(self, odds_history):
        """Calculate line volatility as a measure of market uncertainty"""
        return odds_history['spread'].std()
    
    def calculate_movement_strength(self, line_movement, sharp_movement, steam_move, line_volatility):
        """Calculate the strength of the line movement signal"""
        strength = 0
        
        # Factor in size of line movement
        strength += abs(line_movement) * 2
        
        # Add weight for sharp movement
        if sharp_movement:
            strength += 2
            
        # Add weight for steam move
        if steam_move:
            strength += 1.5
        
        # Add weight for line volatility
        strength += line_volatility
        
        return min(strength, 10)  # Cap at 10
    
    def get_recommended_play(self, line_movement, sharp_movement, reverse_line_movement, line_volatility):
        """Get recommended play based on line movement analysis"""
        if not any([sharp_movement, reverse_line_movement]):
            return 'NO_PLAY'
            
        if sharp_movement and reverse_line_movement and line_volatility > 0.5:
            return 'STRONG_PLAY'
            
        if sharp_movement or reverse_line_movement:
            return 'CONSIDER_PLAY'
            
        return 'NO_PLAY'
    
    @staticmethod
    def get_opening_line(odds_history):
        """Get the opening line"""
        return odds_history.iloc[0]['spread']
    
    @staticmethod
    def get_current_line(odds_history):
        """Get the current line"""
        return odds_history.iloc[-1]['spread']

class LineMovementTracker:
    def __init__(self):
        self.historical_lines = {}
        
    def track_line_movement(self, game_id, current_odds):
        """Track line movement for a game"""
        if game_id not in self.historical_lines:
            self.historical_lines[game_id] = []
            
        self.historical_lines[game_id].append({
            'timestamp': datetime.now(),
            'spread': current_odds['spread'],
            'total': current_odds['total'],
            'moneyline': current_odds['moneyline']
        })
        
    def analyze_line_movement(self, game_id):
        """Analyze line movement patterns"""
        if game_id not in self.historical_lines:
            return None
            
        movements = self.historical_lines[game_id]
        if len(movements) < 2:
            return None
            
        analysis = {
            'spread_movement': movements[-1]['spread'] - movements[0]['spread'],
            'total_movement': movements[-1]['total'] - movements[0]['total'],
            'ml_movement': movements[-1]['moneyline'] - movements[0]['moneyline'],
            'sharp_action': self.detect_sharp_action(movements),
            'steam_moves': self.detect_steam_moves(movements),
            'reverse_line_movement': self.detect_reverse_movement(movements)
        }
        
        return analysis
        
    def detect_sharp_action(self, movements):
        """Detect potential sharp betting patterns"""
        # Implementation of sharp betting detection
        pass
        
    def detect_steam_moves(self, movements):
        """Detect steam moves (sudden line movements)"""
        # Implementation of steam move detection
        pass
        
    def detect_reverse_movement(self, movements):
        """Detect reverse line movement"""
        # Implementation of reverse line movement detection
        pass

class LineMovement:
    def __init__(self):
        self.line_history = {}
        self.sharp_books = RESPECTED_BOOKS[:3]  # Pinnacle, Circa, Westgate are considered sharpest
        
    def track_movement(self, game_id: str, current_lines: Dict[str, float], timestamp: datetime) -> None:
        """Track line movement for a specific game"""
        if game_id not in self.line_history:
            self.line_history[game_id] = []
        
        self.line_history[game_id].append({
            'timestamp': timestamp,
            'lines': current_lines
        })
        
    def get_line_history(self, game_id: str) -> List[Dict]:
        """Get line movement history for a game"""
        return self.line_history.get(game_id, [])
        
    def analyze_movement(self, game_id: str) -> Dict:
        """Analyze line movement patterns for a game"""
        history = self.get_line_history(game_id)
        if not history:
            return {}
            
        try:
            # Get opening and current lines
            opening_lines = history[0]['lines']
            current_lines = history[-1]['lines']
            
            # Calculate movement
            spread_movement = current_lines.get('spread') - opening_lines.get('spread', 0)
            total_movement = current_lines.get('total') - opening_lines.get('total', 0)
            
            # Check for steam moves
            steam_moves = self._detect_steam_moves(history)
            
            # Check for reverse line movement
            sharp_action = self._detect_sharp_action(history)
            
            return {
                'spread_movement': spread_movement,
                'total_movement': total_movement,
                'steam_moves': steam_moves,
                'sharp_action': sharp_action,
                'significant_movement': abs(spread_movement) >= 2 or abs(total_movement) >= 3
            }
            
        except Exception as e:
            logger.error(f"Error analyzing line movement for game {game_id}: {str(e)}")
            return {}
            
    def _detect_steam_moves(self, history: List[Dict]) -> List[Dict]:
        """Detect steam moves (rapid line movement across books)"""
        steam_moves = []
        
        for i in range(1, len(history)):
            prev_lines = history[i-1]['lines']
            curr_lines = history[i]['lines']
            time_diff = history[i]['timestamp'] - history[i-1]['timestamp']
            
            # Check for rapid movement across multiple books
            if time_diff <= timedelta(minutes=5):
                spread_change = curr_lines.get('spread') - prev_lines.get('spread', 0)
                if abs(spread_change) >= 1.5:
                    steam_moves.append({
                        'timestamp': history[i]['timestamp'],
                        'movement': spread_change
                    })
                    
        return steam_moves
        
    def _detect_sharp_action(self, history: List[Dict]) -> List[Dict]:
        """Detect sharp action based on line movement in respected books"""
        sharp_moves = []
        
        for i in range(1, len(history)):
            sharp_lines = {book: lines for book, lines in history[i]['lines'].items() 
                         if book in self.sharp_books}
            
            if sharp_lines:
                avg_sharp_spread = sum(lines.get('spread', 0) for lines in sharp_lines.values()) / len(sharp_lines)
                public_lines = {book: lines for book, lines in history[i]['lines'].items() 
                              if book not in self.sharp_books}
                
                if public_lines:
                    avg_public_spread = sum(lines.get('spread', 0) for lines in public_lines.values()) / len(public_lines)
                    
                    # If sharp books move opposite to public books
                    if (avg_sharp_spread - avg_public_spread) >= 1:
                        sharp_moves.append({
                            'timestamp': history[i]['timestamp'],
                            'sharp_spread': avg_sharp_spread,
                            'public_spread': avg_public_spread
                        })
                        
        return sharp_moves
        
    def get_recommendations(self, game_id: str) -> List[str]:
        """Get betting recommendations based on line movement analysis"""
        analysis = self.analyze_movement(game_id)
        recommendations = []
        
        if analysis.get('sharp_action'):
            sharp_move = analysis['sharp_action'][-1]
            recommendations.append(f"Sharp action detected: {sharp_move['sharp_spread']} vs {sharp_move['public_spread']}")
            
        if analysis.get('steam_moves'):
            steam = analysis['steam_moves'][-1]
            recommendations.append(f"Steam move detected: {steam['movement']} point movement")
            
        if analysis.get('significant_movement'):
            recommendations.append("Significant line movement detected - monitor for additional movement")
            
        return recommendations