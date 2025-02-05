from datetime import datetime
import numpy as np

class WaltersStrategy:
    def __init__(self, bankroll=400.00):
        self.bankroll = bankroll
        self.max_bet_percent = 0.05  # Max 5% of bankroll per bet ($20)
        self.min_edge = 0.05  # Minimum 5% edge required
        self.confidence_threshold = 65
        
    def apply_strategy(self, picks):
        """Apply comprehensive Bill Walters betting principles"""
        validated_picks = []
        
        for pick in picks:
            if self._has_sufficient_edge(pick) and \
               self._validate_line_movement(pick) and \
               self._check_market_liquidity(pick) and \
               self._analyze_situational_spots(pick) and \
               self._detect_steam_moves(pick) and \
               self._analyze_correlations(pick) and \
               self._evaluate_market_psychology(pick) and \
               self._apply_ml_analysis(pick):
                
                pick = self._calculate_optimal_bet_size(pick)
                pick = self._apply_timing_strategy(pick)
                pick = self._apply_risk_management(pick)
                validated_picks.append(pick)
                
        return self._diversify_portfolio(validated_picks)
    
    def _has_sufficient_edge(self, pick):
        """Calculate true edge using advanced probability models"""
        market_prob = self._convert_odds_to_probability(pick.get('odds', 0))
        model_prob = pick.get('confidence', 0) / 100
        edge = model_prob - market_prob
        return edge >= self.min_edge
    
    def _validate_line_movement(self, pick):
        """Analyze line movement and sharp money signals"""
        opening_line = pick.get('opening_line', 0)
        current_line = pick.get('current_line', 0)
        sharp_money = pick.get('sharp_money_percentage', 0)
        
        return sharp_money > 60 and self._is_line_movement_favorable(opening_line, current_line)
    
    def _check_market_liquidity(self, pick):
        """Ensure market can handle desired bet size without significant line movement"""
        market_volume = pick.get('market_volume', 0)
        return market_volume >= self.bankroll * self.max_bet_percent * 10
    
    def _analyze_situational_spots(self, pick):
        """Deep analysis of situational factors"""
        factors = {
            'rest_advantage': pick.get('rest_days', 0),
            'travel_situation': pick.get('travel_distance', 0),
            'motivation_factor': pick.get('motivation_rating', 0),
            'weather_impact': pick.get('weather_rating', 0),
            'key_injuries': pick.get('injury_impact', 0)
        }
        
        return sum(factors.values()) / len(factors) >= 0.7
    
    def _calculate_optimal_bet_size(self, pick):
        """Kelly Criterion with adjustments"""
        edge = pick.get('edge', 0)
        odds = pick.get('odds', 0)
        
        kelly_bet = (edge * odds) / (odds - 1)
        conservative_bet = kelly_bet * 0.25  # Quarter Kelly
        
        max_bet = self.bankroll * self.max_bet_percent
        optimal_bet = min(conservative_bet, max_bet)
        
        pick['recommended_bet'] = optimal_bet
        return pick
    
    def _apply_timing_strategy(self, pick):
        """Determine optimal timing for bet placement"""
        current_time = datetime.now()
        game_time = pick.get('game_time')
        line_movement_trend = pick.get('line_movement_trend', [])
        
        pick['bet_timing'] = self._determine_optimal_bet_time(
            current_time, game_time, line_movement_trend
        )
        return pick
    
    def _apply_risk_management(self, picks):
        """Apply sophisticated risk management rules"""
        risk_factors = {
            'correlation_risk': self._calculate_correlation_risk(picks),
            'exposure_risk': self._calculate_exposure_risk(picks),
            'timing_risk': self._calculate_timing_risk(picks),
            'market_risk': self._calculate_market_risk(picks)
        }
        
        return self._adjust_for_risk(picks, risk_factors)
    
    def _diversify_portfolio(self, picks):
        """Ensure proper bankroll distribution across sports/bet types"""
        total_exposure = sum(p['recommended_bet'] for p in picks)
        
        if total_exposure > self.bankroll * 0.15:  # Max 15% total exposure
            adjustment_factor = (self.bankroll * 0.15) / total_exposure
            for pick in picks:
                pick['recommended_bet'] *= adjustment_factor
                
        return self._balance_bet_types(picks)
    
    def _balance_bet_types(self, picks):
        """Balance between spreads, totals, and money lines"""
        bet_types = {'spread': 0, 'total': 0, 'moneyline': 0}
        
        for pick in picks:
            bet_type = pick.get('pick_type', '').lower()
            bet_types[bet_type] += pick['recommended_bet']
            
        # Adjust if any bet type exceeds 40% of total exposure
        total_bets = sum(bet_types.values())
        for bet_type in bet_types:
            if bet_types[bet_type] / total_bets > 0.4:
                self._rebalance_bets(picks, bet_type)
                
        return picks
    
    def _convert_odds_to_probability(self, odds):
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def _is_line_movement_favorable(self, opening, current):
        """Analyze if line movement indicates sharp action"""
        return abs(current - opening) >= 1.5  # Significant movement threshold
    
    def _determine_optimal_bet_time(self, current, game_time, movement_trend):
        """Calculate optimal timing for bet placement"""
        if not movement_trend:
            return current
            
        # Analyze historical line movement patterns
        peak_value_time = self._analyze_movement_pattern(movement_trend)
        return peak_value_time
    
    def _analyze_movement_pattern(self, trend):
        """Analyze line movement trend to find optimal entry point"""
        # Implementation would analyze historical patterns
        return datetime.now()  # Placeholder
    
    def _detect_steam_moves(self, pick):
        """Detect coordinated sharp betting activity"""
        recent_moves = pick.get('line_moves', [])
        sharp_books = ['Pinnacle', 'CRIS', 'Bookmaker']
        
        # Look for coordinated line moves across sharp books
        for move in recent_moves:
            if (move['time_window'] < 300 and  # Within 5 minutes
                move['books_moved'] >= 2 and
                any(book in sharp_books for book in move['books'])):
                return True
        return False
    
    def _analyze_correlations(self, pick):
        """Analyze correlations between different bets"""
        correlated_factors = {
            'weather_impact': pick.get('weather_correlation', 0),
            'pace_correlation': pick.get('pace_correlation', 0),
            'injury_impact': pick.get('injury_correlation', 0),
            'system_correlation': pick.get('system_correlation', 0)
        }
        return np.mean(list(correlated_factors.values())) > 0.7
    
    def _evaluate_market_psychology(self, pick):
        """Evaluate public betting patterns and overreactions"""
        public_betting = pick.get('public_betting_percentage', 0)
        sharp_action = pick.get('sharp_money_percentage', 0)
        recent_trends = pick.get('recent_trends', {})
        
        # Look for opportunities where public is heavily on one side
        return (public_betting > 70 and sharp_action < 40) or \
               (public_betting < 30 and sharp_action > 60)
    
    def _apply_ml_analysis(self, pick):
        """Apply machine learning models for prediction validation"""
        from .ml_models import AdvancedMLModels
        
        ml_models = AdvancedMLModels()
        features = self._extract_ml_features(pick)
        
        confidence_scores = {
            'random_forest': ml_models.predict_proba(features),
            'neural_network': ml_models.predict_nn_proba(features),
            'gradient_boost': ml_models.predict_gb_proba(features)
        }
        
        # Require consensus among models
        return np.mean(list(confidence_scores.values())) > 0.65
    
    def _monitor_live_odds(self, pick):
        """Monitor real-time odds movement and liquidity"""
        from .api_integrations import OddsAPI
        
        odds_api = OddsAPI()
        current_odds = odds_api.get_live_odds(pick['game'])
        historical_odds = odds_api.get_odds_history(pick['game'])
        
        return {
            'current': current_odds,
            'movement': self._analyze_odds_movement(historical_odds),
            'liquidity': self._assess_market_liquidity(current_odds),
            'arbitrage': self._check_arbitrage_opportunities(current_odds)
        }
    
    def _find_arbitrage_opportunities(self, pick):
        """Identify potential arbitrage situations"""
        all_bookmaker_odds = pick.get('all_odds', {})
        best_prices = {
            'back': max(all_bookmaker_odds.values()),
            'lay': min(all_bookmaker_odds.values())
        }
        
        margin = (1/best_prices['back'] + 1/best_prices['lay'] - 1) * 100
        return margin < -1  # Profitable if negative margin
    
    def _analyze_weather_impact(self, pick):
        """Analyze weather conditions and historical performance"""
        from .weather_analysis import WeatherAnalyzer
        
        weather = WeatherAnalyzer()
        conditions = weather.get_game_conditions(pick['game'])
        
        impact_factors = {
            'wind_impact': weather.calculate_wind_impact(conditions),
            'precipitation': weather.calculate_precipitation_impact(conditions),
            'temperature': weather.calculate_temperature_impact(conditions),
            'historical_performance': weather.get_historical_weather_performance(pick)
        }
        
        return weather.get_overall_impact(impact_factors)
    
    def _dynamic_bankroll_management(self, pick):
        """Implement dynamic bankroll management based on various factors"""
        factors = {
            'form': self._analyze_recent_form(),
            'variance': self._calculate_variance(),
            'drawdown': self._track_drawdown(),
            'win_rate': self._calculate_win_rate(),
            'roi': self._calculate_roi()
        }
        
        base_kelly = self._calculate_kelly_criterion(pick)
        return self._adjust_bet_size(base_kelly, factors)