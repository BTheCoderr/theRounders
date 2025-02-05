import json
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import pandas as pd
from pathlib import Path

@dataclass
class BetDetails:
    date: str
    sport: str
    game: str
    pick_type: str  # Spread, Moneyline, Total, Prop
    pick: str
    confidence: int  # 1-100
    line: float
    odds: float
    bet_amount: float
    result: Optional[str] = None  # Won, Lost, Push, Pending
    closing_line: Optional[float] = None  # For closing line value analysis
    book: str = ""  # Sportsbook used
    bet_time: str = ""  # Time bet was placed
    weather: Optional[Dict] = None  # Weather conditions if relevant
    notes: str = ""  # Any relevant notes about the bet
    edge: Optional[float] = None  # Calculated edge at time of bet
    category: str = "Main"  # Categorize bets (Main, Live, Props, etc.)
    units: float = 1.0  # Number of units risked
    steam_move: bool = False  # Track if bet followed steam move
    injury_notes: str = ""  # Relevant injury information
    
class WaltersBetTracker:
    def __init__(self, history_file: str = "picks_history.json"):
        self.history_file = Path(history_file)
        self.bets: List[BetDetails] = []
        self.load_history()
        
    def load_history(self):
        """Load existing bet history."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                for bet in data:
                    self.bets.append(BetDetails(**bet))
    
    def add_bet(self, bet: BetDetails):
        """Add a new bet to the tracker."""
        self.bets.append(bet)
        self._save_history()
    
    def update_result(self, date: str, game: str, pick_type: str, result: str, closing_line: Optional[float] = None):
        """Update the result of a bet."""
        for bet in self.bets:
            if bet.date == date and bet.game == game and bet.pick_type == pick_type:
                bet.result = result
                if closing_line:
                    bet.closing_line = closing_line
                break
        self._save_history()
    
    def get_analytics(self) -> Dict:
        """Get comprehensive betting analytics."""
        df = pd.DataFrame([vars(bet) for bet in self.bets])
        
        if df.empty:
            return {"error": "No bets recorded"}
        
        # Filter completed bets
        completed = df[df['result'].isin(['Won', 'Lost', 'Push'])]
        
        analytics = {
            "overall": {
                "total_bets": len(completed),
                "win_rate": (completed['result'] == 'Won').mean() if not completed.empty else 0,
                "roi": ((completed[completed['result'] == 'Won']['odds'] - 1).sum() - 
                       len(completed[completed['result'] == 'Lost'])) / len(completed) if not completed.empty else 0,
            },
            "by_sport": {},
            "by_pick_type": {},
            "closing_line_value": self._calculate_clv(completed),
            "steam_move_performance": self._analyze_steam_moves(completed),
            "confidence_analysis": self._analyze_confidence(completed),
            "timing_analysis": self._analyze_timing(completed)
        }
        
        # Add sport-specific analytics
        for sport in df['sport'].unique():
            sport_df = completed[completed['sport'] == sport]
            analytics["by_sport"][sport] = {
                "total_bets": len(sport_df),
                "win_rate": (sport_df['result'] == 'Won').mean() if not sport_df.empty else 0,
                "roi": ((sport_df[sport_df['result'] == 'Won']['odds'] - 1).sum() - 
                       len(sport_df[sport_df['result'] == 'Lost'])) / len(sport_df) if not sport_df.empty else 0
            }
        
        return analytics
    
    def _calculate_clv(self, df: pd.DataFrame) -> Dict:
        """Calculate Closing Line Value metrics."""
        if df.empty or 'closing_line' not in df.columns:
            return {}
            
        df_with_clv = df.dropna(subset=['closing_line', 'line'])
        if df_with_clv.empty:
            return {}
            
        return {
            "average_clv": (df_with_clv['closing_line'] - df_with_clv['line']).mean(),
            "clv_win_rate": (df_with_clv[df_with_clv['closing_line'] > df_with_clv['line']]['result'] == 'Won').mean()
        }
    
    def _analyze_steam_moves(self, df: pd.DataFrame) -> Dict:
        """Analyze performance of bets following steam moves."""
        steam_bets = df[df['steam_move'] == True]
        if steam_bets.empty:
            return {}
            
        return {
            "total_steam_bets": len(steam_bets),
            "steam_win_rate": (steam_bets['result'] == 'Won').mean(),
            "steam_roi": ((steam_bets[steam_bets['result'] == 'Won']['odds'] - 1).sum() - 
                         len(steam_bets[steam_bets['result'] == 'Lost'])) / len(steam_bets)
        }
    
    def _analyze_confidence(self, df: pd.DataFrame) -> Dict:
        """Analyze bet performance by confidence levels."""
        if df.empty or 'confidence' not in df.columns:
            return {}
            
        confidence_groups = df.groupby(pd.qcut(df['confidence'], 4))
        return {
            f"confidence_{i+1}": {
                "range": f"{int(group.confidence.min())}-{int(group.confidence.max())}",
                "win_rate": (group['result'] == 'Won').mean(),
                "total_bets": len(group)
            }
            for i, (_, group) in enumerate(confidence_groups)
        }
    
    def _analyze_timing(self, df: pd.DataFrame) -> Dict:
        """Analyze bet performance by timing of placement."""
        if df.empty or 'bet_time' not in df.columns:
            return {}
            
        df['hour'] = pd.to_datetime(df['bet_time']).dt.hour
        timing_groups = df.groupby(pd.qcut(df['hour'], 4))
        return {
            f"timing_{i+1}": {
                "hours": f"{int(group.hour.min())}-{int(group.hour.max())}",
                "win_rate": (group['result'] == 'Won').mean(),
                "total_bets": len(group)
            }
            for i, (_, group) in enumerate(timing_groups)
        }
    
    def _save_history(self):
        """Save bet history to file."""
        with open(self.history_file, 'w') as f:
            json.dump([vars(bet) for bet in self.bets], f, indent=4) 