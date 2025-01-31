import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class WaltersRule:
    name: str
    condition: str
    threshold: float
    weight: float
    description: str

class WaltersSimulator:
    def __init__(self):
        self.rules = self._initialize_rules()
        self.min_confidence = 70  # Minimum confidence to recommend a bet
        self.max_daily_risk = 0.15  # Maximum 15% of bankroll at risk per day
        self.max_bet_size = 0.05   # Maximum 5% of bankroll per bet
        
    def _initialize_rules(self) -> List[WaltersRule]:
        """Initialize Walters' betting rules."""
        return [
            WaltersRule(
                name="CLV Edge",
                condition="expected_clv",
                threshold=0.07,  # 7% CLV edge
                weight=0.35,
                description="Bet when expected CLV exceeds 7%"
            ),
            WaltersRule(
                name="Reverse Line Movement",
                condition="rlm_strength",
                threshold=0.15,  # 15% RLM threshold
                weight=0.25,
                description="Bet when line moves against >15% public money"
            ),
            WaltersRule(
                name="Steam Move",
                condition="steam_strength",
                threshold=0.02,  # 2% line movement in 5 minutes
                weight=0.20,
                description="Bet on steam moves >2% in 5 minutes"
            ),
            WaltersRule(
                name="Sharp Money",
                condition="sharp_ratio",
                threshold=0.80,  # 80% sharp money
                weight=0.20,
                description="Bet when >80% of money is sharp"
            )
        ]
    
    def analyze_bet(self, bet_data: Dict, bankroll: float, daily_risk: float) -> Dict:
        """Analyze a bet using Walters' criteria."""
        # Calculate rule scores
        rule_scores = {}
        total_score = 0
        
        for rule in self.rules:
            if rule.condition in bet_data:
                value = bet_data[rule.condition]
                score = self._calculate_rule_score(value, rule)
                rule_scores[rule.name] = {
                    "score": score,
                    "weight": rule.weight,
                    "status": "Pass" if score >= rule.threshold else "Fail",
                    "details": f"{value:.2f} vs threshold {rule.threshold:.2f}"
                }
                total_score += score * rule.weight
        
        # Calculate confidence and edge
        confidence = total_score * 100
        edge = self._calculate_edge(bet_data, rule_scores)
        
        # Calculate optimal bet size
        max_bet = bankroll * self.max_bet_size
        remaining_risk = (bankroll * self.max_daily_risk) - daily_risk
        
        if remaining_risk <= 0:
            recommended_size = 0
            status = "Reject - Daily risk limit exceeded"
        elif confidence < self.min_confidence:
            recommended_size = 0
            status = "Reject - Insufficient confidence"
        else:
            # Scale bet size by confidence and edge
            base_size = min(max_bet, remaining_risk)
            recommended_size = base_size * (confidence/100) * (edge/100)
            status = "Accept"
        
        return {
            "confidence": confidence,
            "edge": edge,
            "recommended_size": recommended_size,
            "status": status,
            "rule_scores": rule_scores,
            "analysis": {
                "max_bet": max_bet,
                "remaining_risk": remaining_risk,
                "bankroll_impact": recommended_size / bankroll * 100
            }
        }
    
    def _calculate_rule_score(self, value: float, rule: WaltersRule) -> float:
        """Calculate how well a value meets a rule's criteria."""
        if value >= rule.threshold:
            # Scale score based on how much it exceeds threshold
            return min(1.0, value / (rule.threshold * 1.5))
        return 0.0
    
    def _calculate_edge(self, bet_data: Dict, rule_scores: Dict) -> float:
        """Calculate betting edge based on rules and market data."""
        edge = 0.0
        
        # CLV edge
        if "expected_clv" in bet_data:
            edge += bet_data["expected_clv"] * 0.4  # 40% weight to CLV
        
        # Sharp money edge
        if "sharp_ratio" in bet_data:
            edge += (bet_data["sharp_ratio"] - 0.5) * 0.3  # 30% weight
        
        # Steam move edge
        if "steam_strength" in bet_data:
            edge += bet_data["steam_strength"] * 0.2  # 20% weight
        
        # RLM edge
        if "rlm_strength" in bet_data:
            edge += bet_data["rlm_strength"] * 0.1  # 10% weight
        
        return max(0, edge * 100)  # Convert to percentage
    
    def simulate_strategy(self, historical_data: pd.DataFrame) -> Dict:
        """Simulate Walters strategy on historical data."""
        results = []
        bankroll = 10000  # Starting bankroll
        daily_risk = 0
        current_date = None
        
        for _, bet in historical_data.iterrows():
            # Reset daily risk on new day
            if current_date != bet['date']:
                daily_risk = 0
                current_date = bet['date']
            
            # Analyze bet using Walters criteria
            analysis = self.analyze_bet(
                bet_data={
                    "expected_clv": bet['closing_line'] - bet['odds'],
                    "rlm_strength": bet.get('rlm_strength', 0),
                    "steam_strength": bet.get('steam_strength', 0),
                    "sharp_ratio": bet.get('sharp_ratio', 0.5)
                },
                bankroll=bankroll,
                daily_risk=daily_risk
            )
            
            if analysis['status'] == "Accept":
                # Record bet result
                bet_size = analysis['recommended_size']
                profit = bet_size * (bet['result'] == 'Won')
                bankroll += profit
                daily_risk += bet_size
                
                results.append({
                    'date': bet['date'],
                    'bet_size': bet_size,
                    'confidence': analysis['confidence'],
                    'edge': analysis['edge'],
                    'profit': profit,
                    'bankroll': bankroll
                })
        
        return {
            'results': pd.DataFrame(results),
            'final_bankroll': bankroll,
            'roi': (bankroll - 10000) / 10000 * 100,
            'bet_count': len(results)
        }
    
    def get_strategy_rules(self) -> List[Dict]:
        """Get detailed explanation of Walters strategy rules."""
        return [
            {
                "name": rule.name,
                "description": rule.description,
                "threshold": rule.threshold,
                "weight": rule.weight,
                "importance": "High" if rule.weight >= 0.3 else "Medium"
            }
            for rule in self.rules
        ] 