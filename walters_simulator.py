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
        """Initialize Walters' betting rules with advanced edge detection."""
        return [
            # Core Walters Rules
            WaltersRule(
                name="CLV Edge",
                condition="expected_clv",
                threshold=0.07,  # 7% CLV edge
                weight=0.25,
                description="Bet when expected CLV exceeds 7%"
            ),
            WaltersRule(
                name="Reverse Line Movement",
                condition="rlm_strength",
                threshold=0.15,  # 15% RLM threshold
                weight=0.20,
                description="Bet when line moves against >15% public money"
            ),
            WaltersRule(
                name="Steam Move",
                condition="steam_strength",
                threshold=0.02,  # 2% line movement in 5 minutes
                weight=0.15,
                description="Bet on steam moves >2% in 5 minutes"
            ),
            WaltersRule(
                name="Sharp Money",
                condition="sharp_ratio",
                threshold=0.80,  # 80% sharp money
                weight=0.15,
                description="Bet when >80% of money is sharp"
            ),
            
            # Advanced Market Analysis
            WaltersRule(
                name="Book Disagreement",
                condition="book_disagreement",
                threshold=0.15,  # 15% odds difference
                weight=0.10,
                description="Bet when sharp books disagree with public books"
            ),
            WaltersRule(
                name="Line Efficiency",
                condition="line_efficiency",
                threshold=0.85,  # 85% efficiency
                weight=0.05,
                description="Bet when market is inefficiently pricing factors"
            ),
            
            # Hidden Edges
            WaltersRule(
                name="Situational Advantage",
                condition="situation_edge",
                threshold=0.20,  # 20% edge
                weight=0.05,
                description="Bet when situational factors provide edge"
            ),
            WaltersRule(
                name="Information Edge",
                condition="info_advantage",
                threshold=0.25,  # 25% information advantage
                weight=0.05,
                description="Bet when you have superior information"
            )
        ]
    
    def analyze_bet(self, bet_data: Dict, bankroll: float, daily_risk: float) -> Dict:
        """Analyze a bet using enhanced Walters' criteria."""
        # Calculate rule scores with context
        rule_scores = {}
        total_score = 0
        context_multiplier = 1.0
        
        # Analyze market context
        market_state = self._analyze_market_state(bet_data)
        if market_state["is_efficient"]:
            context_multiplier *= 0.8  # Reduce edge in efficient markets
        
        # Check for correlated factors
        correlated_edges = self._find_correlated_edges(bet_data)
        if correlated_edges:
            context_multiplier *= 1.2  # Increase edge when factors align
        
        for rule in self.rules:
            if rule.condition in bet_data:
                value = bet_data[rule.condition]
                base_score = self._calculate_rule_score(value, rule)
                
                # Apply context-specific adjustments
                adjusted_score = base_score * self._get_context_multiplier(
                    rule.name,
                    bet_data,
                    market_state
                )
                
                rule_scores[rule.name] = {
                    "score": adjusted_score,
                    "weight": rule.weight,
                    "status": "Pass" if adjusted_score >= rule.threshold else "Fail",
                    "details": f"{value:.2f} vs threshold {rule.threshold:.2f}",
                    "context_adjustment": f"{adjusted_score/base_score:.2f}x"
                }
                total_score += adjusted_score * rule.weight
        
        # Apply overall context multiplier
        confidence = total_score * 100 * context_multiplier
        edge = self._calculate_edge(bet_data, rule_scores) * context_multiplier
        
        # Enhanced bet sizing
        max_bet = self._calculate_optimal_bet_size(
            bankroll,
            confidence,
            edge,
            market_state
        )
        remaining_risk = (bankroll * self.max_daily_risk) - daily_risk
        
        # Risk management checks
        risk_assessment = self._assess_risk(
            confidence,
            edge,
            daily_risk,
            bankroll,
            bet_data
        )
        
        if risk_assessment["status"] == "reject":
            recommended_size = 0
            status = f"Reject - {risk_assessment['reason']}"
        else:
            # Scale bet size by confidence, edge, and context
            base_size = min(max_bet, remaining_risk)
            recommended_size = base_size * (confidence/100) * (edge/100) * risk_assessment["multiplier"]
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
                "bankroll_impact": recommended_size / bankroll * 100,
                "market_state": market_state,
                "risk_assessment": risk_assessment,
                "correlated_edges": correlated_edges
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
    
    def _analyze_market_state(self, bet_data: Dict) -> Dict:
        """Analyze current market state and efficiency."""
        return {
            "is_efficient": self._check_market_efficiency(bet_data),
            "liquidity": self._assess_liquidity(bet_data),
            "volatility": self._calculate_volatility(bet_data),
            "sharp_activity": self._measure_sharp_activity(bet_data)
        }
    
    def _find_correlated_edges(self, bet_data: Dict) -> List[Dict]:
        """Find edges that reinforce each other."""
        edges = []
        
        # Check for steam move + RLM correlation
        if (bet_data.get("steam_strength", 0) > 0.02 and 
            bet_data.get("rlm_strength", 0) > 0.15):
            edges.append({
                "type": "steam_rlm_correlation",
                "strength": min(bet_data["steam_strength"], bet_data["rlm_strength"]),
                "description": "Steam move aligned with RLM"
            })
        
        # Check for sharp money + CLV correlation
        if (bet_data.get("sharp_ratio", 0) > 0.8 and 
            bet_data.get("expected_clv", 0) > 0.07):
            edges.append({
                "type": "sharp_clv_correlation",
                "strength": bet_data["sharp_ratio"] * bet_data["expected_clv"],
                "description": "Sharp money aligned with expected CLV"
            })
        
        return edges
    
    def _get_context_multiplier(self, rule_name: str, bet_data: Dict, market_state: Dict) -> float:
        """Get context-specific multiplier for rule scores."""
        multiplier = 1.0
        
        # Adjust for market state
        if not market_state["is_efficient"]:
            multiplier *= 1.2
        
        # Adjust for liquidity
        if market_state["liquidity"] < 0.5:
            multiplier *= 0.8
        
        # Rule-specific adjustments
        if rule_name == "Steam Move" and market_state["volatility"] > 0.8:
            multiplier *= 1.3
        elif rule_name == "CLV Edge" and market_state["sharp_activity"] > 0.7:
            multiplier *= 1.2
        
        return multiplier
    
    def _assess_risk(self, confidence: float, edge: float, daily_risk: float, 
                    bankroll: float, bet_data: Dict) -> Dict:
        """Enhanced risk assessment."""
        assessment = {
            "status": "accept",
            "multiplier": 1.0,
            "reason": None
        }
        
        # Check for overexposure
        if daily_risk > bankroll * 0.12:  # Getting close to daily limit
            assessment["multiplier"] *= 0.7
        
        # Check for correlation risk
        if bet_data.get("correlation_risk", 0) > 0.7:
            assessment["multiplier"] *= 0.8
        
        # Check for market volatility risk
        if bet_data.get("market_volatility", 0) > 0.8:
            assessment["multiplier"] *= 0.9
        
        # Reject if too many risk factors
        if (assessment["multiplier"] < 0.6 or 
            daily_risk > bankroll * 0.15 or
            confidence < self.min_confidence):
            assessment["status"] = "reject"
            assessment["reason"] = "Multiple risk factors present"
        
        return assessment
    
    def _calculate_optimal_bet_size(self, bankroll: float, confidence: float,
                                  edge: float, market_state: Dict) -> float:
        """Calculate optimal bet size considering market conditions."""
        # Start with standard Kelly
        base_size = bankroll * self.max_bet_size
        
        # Adjust for market state
        if not market_state["is_efficient"]:
            base_size *= 1.2
        
        # Adjust for liquidity
        if market_state["liquidity"] < 0.5:
            base_size *= 0.8
        
        # Cap at maximum allowed
        return min(base_size, bankroll * self.max_bet_size)
    
    def get_strategy_rules(self) -> List[Dict]:
        """Get detailed explanation of enhanced Walters strategy rules."""
        return [
            {
                "name": rule.name,
                "description": rule.description,
                "threshold": rule.threshold,
                "weight": rule.weight,
                "importance": "High" if rule.weight >= 0.2 else "Medium",
                "category": self._get_rule_category(rule.name)
            }
            for rule in self.rules
        ]
    
    def _get_rule_category(self, rule_name: str) -> str:
        """Categorize rules by type."""
        categories = {
            "CLV Edge": "Market Efficiency",
            "Reverse Line Movement": "Sharp Action",
            "Steam Move": "Market Movement",
            "Sharp Money": "Smart Money",
            "Book Disagreement": "Market Inefficiency",
            "Line Efficiency": "Market Analysis",
            "Situational Advantage": "Hidden Edge",
            "Information Edge": "Information Advantage"
        }
        return categories.get(rule_name, "Other") 