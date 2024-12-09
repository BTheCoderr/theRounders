from datetime import datetime
from typing import Dict, List
from .advanced_features import AdvancedFeatureEngineering
from .modern_ml_system import ModernMLSystem
from .advanced_ml_system import AdvancedBettingML
from .modern_sharp_system import ModernSharpSystem
from .automated_execution import AutomatedExecution
from sports_betting.analysis.walters_inspired_system import WaltersInspiredSystem

class MainBettingSystem:
    def __init__(self, bankroll: float):
        self.bankroll = bankroll
        
        # Initialize all subsystems
        self.feature_engineering = AdvancedFeatureEngineering()
        self.ml_system = ModernMLSystem()
        self.advanced_ml = AdvancedBettingML(sport='ALL')
        self.sharp_system = ModernSharpSystem()
        self.execution = AutomatedExecution()
        self.walters = WaltersInspiredSystem(bankroll=bankroll)
        
    async def analyze_opportunities(self):
        """Main analysis pipeline"""
        print(f"\n=== BETTING SYSTEM ANALYSIS ===")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
        print("=" * 50)
        
        try:
            # 1. Get current market state
            market_data = await self.sharp_system.get_market_state()
            
            # 2. Generate features for each sport
            features = {}
            for sport in ['NFL', 'NBA', 'NHL', 'NCAAB', 'MLB']:
                if sport in market_data:
                    features[sport] = self.feature_engineering.create_features(
                        market_data[sport], sport
                    )
            
            # 3. Get predictions from different systems
            predictions = {
                'ml_system': self.ml_system.predict_line_movement(features),
                'advanced_ml': await self.advanced_ml.process_predictions(features),
                'sharp': await self.sharp_system.analyze_opportunity(market_data),
                'walters': self.walters.analyze_opportunities(market_data)
            }
            
            # 4. Combine and filter predictions
            opportunities = self._combine_predictions(predictions)
            
            # 5. Risk management and position sizing
            positions = self._calculate_positions(opportunities)
            
            # 6. Display recommendations
            self._display_recommendations(positions)
            
            return positions
            
        except Exception as e:
            print(f"Error in analysis pipeline: {str(e)}")
            return []
            
    def _combine_predictions(self, predictions: Dict) -> List:
        """Combine predictions from different systems"""
        combined = []
        
        for game_id in predictions['ml_system'].keys():
            consensus = {
                'game_id': game_id,
                'confidence': 0,
                'systems_agreeing': 0
            }
            
            # Check each system's prediction
            for system, preds in predictions.items():
                if game_id in preds and preds[game_id]['confidence'] > 65:
                    consensus['confidence'] += preds[game_id]['confidence']
                    consensus['systems_agreeing'] += 1
                    
            # Only include if multiple systems agree
            if consensus['systems_agreeing'] >= 2:
                consensus['avg_confidence'] = consensus['confidence'] / consensus['systems_agreeing']
                combined.append(consensus)
                
        return sorted(combined, key=lambda x: x['avg_confidence'], reverse=True)
        
    def _calculate_positions(self, opportunities: List) -> List:
        """Calculate position sizes based on confidence and bankroll"""
        positions = []
        
        for opp in opportunities:
            # Basic Kelly Criterion calculation
            edge = (opp['avg_confidence'] / 100) - 0.5
            bet_size = self.bankroll * (edge / 2)  # Half Kelly
            
            # Apply limits
            max_bet = self.bankroll * 0.05  # Max 5% per bet
            bet_size = min(bet_size, max_bet)
            
            positions.append({
                **opp,
                'recommended_bet': round(bet_size, 2)
            })
            
        return positions
        
    def _display_recommendations(self, positions: List):
        """Display betting recommendations"""
        print("\nTOP BETTING OPPORTUNITIES:")
        print("=" * 50)
        
        for pos in positions:
            print(f"\nGame ID: {pos['game_id']}")
            print(f"Systems Agreeing: {pos['systems_agreeing']}")
            print(f"Average Confidence: {pos['avg_confidence']:.1f}%")
            print(f"Recommended Bet: ${pos['recommended_bet']:.2f}")
            print("-" * 40)
            
if __name__ == "__main__":
    import asyncio
    
    system = MainBettingSystem(bankroll=400.00)
    asyncio.run(system.analyze_opportunities()) 