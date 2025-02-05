class WeightCalculator:
    """Calculate and apply weights to betting patterns"""
    
    def __init__(self):
        self.base_weights = {
            'sample_size': 0.3,
            'win_rate': 0.3,
            'roi': 0.2,
            'recency': 0.2
        }
        
    def calculate_total_weight(self, pattern_data, current_conditions):
        """Calculate final weight for a pattern"""
        weights = {
            'historical': self._calculate_historical_weight(pattern_data),
            'situational': self._calculate_situational_weight(current_conditions),
            'market': self._calculate_market_weight(current_conditions),
            'timing': self._calculate_timing_weight(current_conditions)
        }
        
        return sum(w * self.base_weights.get(k, 0.25) for k, w in weights.items())
        
    def _calculate_historical_weight(self, pattern_data):
        """Calculate weight based on historical performance"""
        sample_weight = min(pattern_data['sample_size'] / 1000, 1.0)
        win_rate_weight = (pattern_data['win_rate'] - 0.5) * 4  # Scale win rate impact
        roi_weight = pattern_data['roi'] * 5  # Scale ROI impact
        
        return (sample_weight + win_rate_weight + roi_weight) / 3
        
    def _calculate_situational_weight(self, conditions):
        """Calculate weight based on current situation"""
        weights = []
        
        if conditions.get('rest_advantage'):
            weights.append(1.1)
        if conditions.get('travel_impact'):
            weights.append(0.9)
        if conditions.get('weather_impact'):
            weights.append(1.2)
            
        return sum(weights) / len(weights) if weights else 1.0 