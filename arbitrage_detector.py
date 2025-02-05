from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import math

@dataclass
class ArbitrageOpportunity:
    sport: str
    event: str
    market: str
    timestamp: datetime
    profit_margin: float
    required_bets: List[Dict]  # List of bets needed to execute arbitrage
    total_stake: float
    expected_profit: float
    confidence: float
    details: Dict

class ArbitrageDetector:
    def __init__(self, min_profit_margin: float = 0.01,
                 max_stake: float = 1000.0,
                 min_book_rating: float = 0.7):
        self.min_profit_margin = min_profit_margin
        self.max_stake = max_stake
        self.min_book_rating = min_book_rating
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def find_arbitrage(self, odds_data: Dict) -> Optional[ArbitrageOpportunity]:
        """Find arbitrage opportunities in current odds."""
        try:
            # Extract key information
            sport = odds_data["sport"]
            event = odds_data["event"]
            market = odds_data["market"]
            timestamp = datetime.now()
            
            # Get all available odds for this market
            market_odds = self._extract_market_odds(odds_data)
            if not market_odds:
                return None
            
            # Find best combination for arbitrage
            arb_combo = self._find_best_arbitrage(market_odds)
            if not arb_combo:
                return None
            
            profit_margin, bets, total_stake = arb_combo
            
            # Calculate expected profit
            expected_profit = total_stake * profit_margin
            
            # Calculate confidence based on books and margin
            confidence = self._calculate_confidence(bets, profit_margin)
            
            return ArbitrageOpportunity(
                sport=sport,
                event=event,
                market=market,
                timestamp=timestamp,
                profit_margin=profit_margin,
                required_bets=bets,
                total_stake=total_stake,
                expected_profit=expected_profit,
                confidence=confidence,
                details=self._generate_details(market_odds, bets)
            )
        
        except Exception as e:
            self.logger.error(f"Error finding arbitrage: {str(e)}")
            return None
    
    def _extract_market_odds(self, odds_data: Dict) -> List[Dict]:
        """Extract and validate odds for each outcome."""
        market_odds = []
        
        for book, book_data in odds_data.get("books", {}).items():
            # Skip books with low ratings
            if book_data.get("rating", 1.0) < self.min_book_rating:
                continue
            
            odds = book_data.get("odds", {})
            if not odds:
                continue
            
            for outcome, price in odds.items():
                if price > 0:  # Only consider valid positive odds
                    market_odds.append({
                        "book": book,
                        "outcome": outcome,
                        "price": price,
                        "rating": book_data.get("rating", 1.0)
                    })
        
        return market_odds
    
    def _find_best_arbitrage(self, market_odds: List[Dict]) -> Optional[Tuple[float, List[Dict], float]]:
        """Find the best arbitrage opportunity in the market odds."""
        best_margin = -1
        best_bets = None
        best_stake = 0
        
        # Group odds by outcome
        odds_by_outcome = {}
        for odd in market_odds:
            if odd["outcome"] not in odds_by_outcome:
                odds_by_outcome[odd["outcome"]] = []
            odds_by_outcome[odd["outcome"]].append(odd)
        
        # Check if we have odds for all outcomes
        if not all(odds_by_outcome.values()):
            return None
        
        # Find best odds for each outcome
        best_odds = {}
        for outcome, odds in odds_by_outcome.items():
            best_odds[outcome] = max(odds, key=lambda x: x["price"])
        
        # Calculate arbitrage opportunity
        total_inverse = sum(1 / odd["price"] for odd in best_odds.values())
        
        if total_inverse < 1:  # Arbitrage exists
            margin = 1 - total_inverse
            if margin >= self.min_profit_margin:
                # Calculate optimal stakes
                total_stake = min(
                    self.max_stake,
                    self._calculate_optimal_stake(margin)
                )
                
                bets = []
                for outcome, odd in best_odds.items():
                    stake = total_stake / (odd["price"] * total_inverse)
                    bets.append({
                        "book": odd["book"],
                        "outcome": outcome,
                        "odds": odd["price"],
                        "stake": stake,
                        "rating": odd["rating"]
                    })
                
                return margin, bets, total_stake
        
        return None
    
    def _calculate_optimal_stake(self, margin: float) -> float:
        """Calculate optimal stake based on margin and risk parameters."""
        # Start with base stake calculation
        base_stake = self.max_stake * (margin / 0.05)  # Scale with margin
        
        # Apply diminishing returns for very high margins
        if margin > 0.05:
            base_stake *= math.sqrt(0.05 / margin)
        
        return min(base_stake, self.max_stake)
    
    def _calculate_confidence(self, bets: List[Dict], margin: float) -> float:
        """Calculate confidence score for arbitrage opportunity."""
        # Start with base confidence from margin
        base_confidence = min(1.0, margin / 0.05)
        
        # Factor in book ratings
        avg_rating = sum(bet["rating"] for bet in bets) / len(bets)
        rating_factor = avg_rating ** 2  # Square to penalize low ratings more
        
        # Factor in number of books (more books = more complexity/risk)
        books_factor = 1.0 - (0.1 * (len(bets) - 2))  # Penalty for each book beyond 2
        books_factor = max(0.5, min(1.0, books_factor))
        
        return base_confidence * rating_factor * books_factor
    
    def _generate_details(self, market_odds: List[Dict], selected_bets: List[Dict]) -> Dict:
        """Generate detailed information about the arbitrage opportunity."""
        return {
            "market_overview": {
                "total_books": len(set(odd["book"] for odd in market_odds)),
                "total_outcomes": len(set(odd["outcome"] for odd in market_odds)),
                "avg_book_rating": sum(odd["rating"] for odd in market_odds) / len(market_odds)
            },
            "selected_books": [bet["book"] for bet in selected_bets],
            "odds_distribution": {
                bet["outcome"]: {
                    "selected": bet["odds"],
                    "market_avg": self._calculate_avg_odds(market_odds, bet["outcome"]),
                    "market_range": self._calculate_odds_range(market_odds, bet["outcome"])
                }
                for bet in selected_bets
            }
        }
    
    def _calculate_avg_odds(self, market_odds: List[Dict], outcome: str) -> float:
        """Calculate average odds for an outcome."""
        outcome_odds = [odd["price"] for odd in market_odds if odd["outcome"] == outcome]
        return sum(outcome_odds) / len(outcome_odds) if outcome_odds else 0
    
    def _calculate_odds_range(self, market_odds: List[Dict], outcome: str) -> Dict:
        """Calculate odds range for an outcome."""
        outcome_odds = [odd["price"] for odd in market_odds if odd["outcome"] == outcome]
        return {
            "min": min(outcome_odds) if outcome_odds else 0,
            "max": max(outcome_odds) if outcome_odds else 0
        } 