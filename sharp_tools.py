import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

class SharpTools:
    def __init__(self, odds_api_key: Optional[str] = None):
        self.odds_api_key = odds_api_key
        
    def fetch_odds(self, sport: str = "basketball_nba") -> Dict:
        """Fetch real-time odds from The Odds API."""
        if not self.odds_api_key:
            return {"error": "No API key provided"}
            
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
        params = {
            "apiKey": self.odds_api_key,
            "regions": "us",
            "markets": "h2h,spreads",
            "oddsFormat": "american"
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def detect_steam_move(self, line_movements: pd.DataFrame, 
                         time_window: int = 5,
                         threshold: float = 1.0) -> bool:
        """
        Detect steam moves based on rapid line movement.
        
        Args:
            line_movements: DataFrame with columns [timestamp, odds]
            time_window: Minutes to check for movement
            threshold: Minimum line movement to qualify as steam
        """
        if len(line_movements) < 2:
            return False
            
        recent_moves = line_movements[
            line_movements['timestamp'] >= datetime.now() - timedelta(minutes=time_window)
        ]
        
        if len(recent_moves) < 2:
            return False
            
        total_movement = abs(recent_moves['odds'].iloc[-1] - recent_moves['odds'].iloc[0])
        return total_movement >= threshold
    
    def detect_reverse_line_movement(self, 
                                   public_percentage: float,
                                   opening_line: float,
                                   current_line: float,
                                   threshold: float = 60.0) -> bool:
        """
        Detect reverse line movement (line moving against public betting).
        
        Args:
            public_percentage: Percentage of public bets on one side
            opening_line: Opening line value
            current_line: Current line value
            threshold: Minimum public percentage to consider
        """
        if public_percentage > threshold:
            # If public heavily favors one side but line moves the other way
            line_movement = current_line - opening_line
            return (line_movement > 0 and public_percentage > threshold) or \
                   (line_movement < 0 and public_percentage < (100 - threshold))
        return False
    
    def calculate_closing_line_value(self, 
                                   bet_line: float,
                                   closing_line: float,
                                   bet_type: str = "spread") -> float:
        """
        Calculate Closing Line Value (CLV).
        
        Args:
            bet_line: Line you bet at
            closing_line: Final line before game started
            bet_type: Type of bet (spread, moneyline, total)
        """
        if bet_type == "spread":
            return closing_line - bet_line
        elif bet_type == "moneyline":
            # Convert American odds to decimal for comparison
            def american_to_decimal(odds):
                if odds > 0:
                    return (odds / 100) + 1
                else:
                    return (100 / abs(odds)) + 1
            return american_to_decimal(closing_line) - american_to_decimal(bet_line)
        return 0.0
    
    def get_sharp_confidence(self, 
                           steam_move: bool,
                           reverse_line_movement: bool,
                           clv_history: List[float],
                           bet_size: float,
                           avg_bet_size: float) -> float:
        """
        Calculate sharp confidence score (0-100).
        
        Args:
            steam_move: Whether a steam move was detected
            reverse_line_movement: Whether RLM was detected
            clv_history: List of historical CLV values
            bet_size: Current bet size
            avg_bet_size: Average bet size
        """
        score = 0.0
        
        # Steam move indicates sharp action
        if steam_move:
            score += 30
            
        # Reverse line movement is a strong sharp indicator
        if reverse_line_movement:
            score += 25
            
        # Historical CLV success
        if clv_history:
            avg_clv = sum(clv_history) / len(clv_history)
            if avg_clv > 0:
                score += min(20, avg_clv * 10)
                
        # Unusual bet size can indicate sharp action
        size_ratio = bet_size / avg_bet_size if avg_bet_size > 0 else 1
        if size_ratio > 2:
            score += min(25, size_ratio * 5)
            
        return min(100, score)
    
    def calculate_optimal_kelly(self,
                              win_probability: float,
                              odds: float,
                              kelly_fraction: float = 0.5) -> float:
        """
        Calculate Kelly Criterion bet size with adjustable fraction.
        
        Args:
            win_probability: Estimated probability of winning (0-1)
            odds: American odds
            kelly_fraction: Fraction of Kelly to use (0-1)
        """
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
            
        # Calculate full Kelly
        b = decimal_odds - 1  # Decimal odds minus 1
        q = 1 - win_probability  # Probability of losing
        p = win_probability  # Probability of winning
        
        kelly = (b * p - q) / b
        
        # Apply Kelly fraction
        return max(0, kelly * kelly_fraction) 