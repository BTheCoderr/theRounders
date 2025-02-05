from datetime import datetime, timedelta
from .betting_config import BETTING_CONFIG, RESPECTED_BOOKS, HISTORICAL_PATTERNS

class BettingAnalysis:
    def __init__(self):
        self.sharp_threshold = 2.0
        self.steam_threshold = 1.5
        self.time_window = 300
        
    def analyze_sharp_action(self, odds_history, sport='NFL'):
        """Enhanced sharp betting analysis with sport-specific factors"""
        config = BETTING_CONFIG.get(sport, BETTING_CONFIG['NFL'])
        
        indicators = {
            'reverse_line_movement': False,
            'steam_moves': [],
            'sharp_money': False,
            'line_freeze': False,
            'key_number_analysis': self.analyze_key_numbers(odds_history, config),
            'respected_books': self.analyze_respected_books(odds_history),
            'historical_patterns': self.analyze_historical_patterns(odds_history, sport),
            'consensus': self.calculate_consensus(odds_history[-1]['odds']) if odds_history else {}
        }
        
        if len(odds_history) < 2:
            return indicators
            
        # Analyze line movement patterns
        for i in range(1, len(odds_history)):
            current = odds_history[i]
            previous = odds_history[i-1]
            time_diff = (current['timestamp'] - previous['timestamp']).total_seconds()
            
            # Check for reverse line movement
            if self.is_reverse_line_movement(current, previous):
                indicators['reverse_line_movement'] = True
                
            # Check for steam moves
            if self.is_steam_move(current, previous, time_diff):
                indicators['steam_moves'].append({
                    'timestamp': current['timestamp'],
                    'movement': self.calculate_movement(previous['odds'], current['odds']),
                    'strength': self.calculate_steam_strength(current, previous, time_diff)
                })
                
            # Check for sharp money signals
            if self.is_sharp_money(current, previous):
                indicators['sharp_money'] = True
                
            # Check for line freezes (no movement despite heavy betting)
            if self.is_line_freeze(current, previous):
                indicators['line_freeze'] = True
                
        return indicators
        
    def is_reverse_line_movement(self, current, previous):
        """Detect reverse line movement"""
        try:
            current_spread = current['odds']['spread'][0]['spread']
            previous_spread = previous['odds']['spread'][0]['spread']
            current_money = current['odds']['moneyline'][0]['odds']
            previous_money = previous['odds']['moneyline'][0]['odds']
            
            # Line moves opposite to money movement
            spread_move = current_spread - previous_spread
            money_move = current_money - previous_money
            
            return (spread_move * money_move) < 0 and abs(spread_move) >= self.sharp_threshold
            
        except (KeyError, IndexError):
            return False
            
    def is_steam_move(self, current, previous, time_diff):
        """Detect steam moves"""
        try:
            # Check for significant quick movements
            spread_move = abs(current['odds']['spread'][0]['spread'] - 
                            previous['odds']['spread'][0]['spread'])
            
            # Steam move criteria:
            # 1. Quick movement (within time window)
            # 2. Significant movement size
            # 3. Multiple books moving together
            is_quick = time_diff <= self.time_window
            is_significant = spread_move >= self.steam_threshold
            books_moving = self.count_books_moving(current, previous)
            
            return is_quick and is_significant and books_moving >= 3
            
        except (KeyError, IndexError):
            return False
            
    def calculate_steam_strength(self, current, previous, time_diff):
        """Calculate the strength of a steam move"""
        try:
            spread_move = abs(current['odds']['spread'][0]['spread'] - 
                            previous['odds']['spread'][0]['spread'])
            books_moving = self.count_books_moving(current, previous)
            
            # Factors:
            # 1. Size of movement
            # 2. Speed of movement
            # 3. Number of books moving
            movement_factor = spread_move / self.steam_threshold
            time_factor = 1 - (time_diff / self.time_window)
            books_factor = books_moving / len(current['odds']['spread'])
            
            return (movement_factor * 0.4 + time_factor * 0.3 + books_factor * 0.3) * 100
            
        except (KeyError, IndexError):
            return 0
            
    def is_sharp_money(self, current, previous):
        """Detect sharp money signals"""
        try:
            # Multiple indicators for sharp money:
            # 1. Line movement against consensus
            # 2. Movement at key numbers
            # 3. Early market movement
            # 4. Respected book movement
            
            key_numbers = [3, 7, 10, 14]  # Key numbers in football
            current_spread = current['odds']['spread'][0]['spread']
            previous_spread = previous['odds']['spread'][0]['spread']
            
            # Check if movement crosses key numbers
            crosses_key = any(
                (previous_spread < num and current_spread > num) or
                (previous_spread > num and current_spread < num)
                for num in key_numbers
            )
            
            # Check if respected books (Pinnacle, Circa) are moving
            respected_books_moving = self.check_respected_books(current, previous)
            
            return crosses_key or respected_books_moving
            
        except (KeyError, IndexError):
            return False
            
    def calculate_consensus(self, current_odds):
        """Calculate betting consensus percentages"""
        consensus = {
            'spread': {'home': 0, 'away': 0},
            'moneyline': {'home': 0, 'away': 0},
            'total': {'over': 0, 'under': 0}
        }
        
        try:
            # Calculate spread consensus
            for spread in current_odds['spread']:
                if spread['team'] == 'home':
                    consensus['spread']['home'] += 1
                else:
                    consensus['spread']['away'] += 1
                    
            # Calculate moneyline consensus
            for ml in current_odds['moneyline']:
                if ml['team'] == 'home':
                    consensus['moneyline']['home'] += 1
                else:
                    consensus['moneyline']['away'] += 1
                    
            # Calculate totals consensus
            for total in current_odds['total']:
                if total['position'] == 'over':
                    consensus['total']['over'] += 1
                else:
                    consensus['total']['under'] += 1
                    
            # Convert to percentages
            total_spread = sum(consensus['spread'].values())
            total_ml = sum(consensus['moneyline'].values())
            total_total = sum(consensus['total'].values())
            
            if total_spread > 0:
                consensus['spread'] = {k: v/total_spread*100 for k, v in consensus['spread'].items()}
            if total_ml > 0:
                consensus['moneyline'] = {k: v/total_ml*100 for k, v in consensus['moneyline'].items()}
            if total_total > 0:
                consensus['total'] = {k: v/total_total*100 for k, v in consensus['total'].items()}
            
            return consensus
            
        except (KeyError, IndexError):
            return consensus 
        
    def analyze_key_numbers(self, odds_history, config):
        """Analyze movement around key numbers"""
        if not odds_history:
            return {}
            
        analysis = {
            'spread_key_crosses': [],
            'total_key_crosses': [],
            'key_number_resistance': []
        }
        
        for i in range(1, len(odds_history)):
            current = odds_history[i]
            previous = odds_history[i-1]
            
            # Check spread key numbers
            current_spread = current['odds']['spread'][0]['spread']
            previous_spread = previous['odds']['spread'][0]['spread']
            
            for key in config['key_numbers']['spread']:
                if (previous_spread < key < current_spread) or \
                   (previous_spread > key > current_spread):
                    analysis['spread_key_crosses'].append({
                        'number': key,
                        'time': current['timestamp'],
                        'direction': 'up' if current_spread > previous_spread else 'down'
                    })
                    
            # Similar analysis for totals
            # ... implementation ...
            
        return analysis
        
    def analyze_respected_books(self, odds_history):
        """Analyze movements of respected books"""
        if not odds_history:
            return {}
            
        analysis = {
            'sharp_moves': [],
            'book_disagreement': [],
            'leading_indicators': []
        }
        
        for i in range(1, len(odds_history)):
            current = odds_history[i]
            previous = odds_history[i-1]
            
            # Track moves by respected books
            for book in RESPECTED_BOOKS['primary']:
                current_odds = self.get_book_odds(current, book)
                previous_odds = self.get_book_odds(previous, book)
                
                if current_odds and previous_odds:
                    move = self.calculate_move_significance(
                        current_odds, 
                        previous_odds,
                        RESPECTED_BOOKS['weight'][book]
                    )
                    
                    if move['significant']:
                        analysis['sharp_moves'].append({
                            'book': book,
                            'time': current['timestamp'],
                            'move': move
                        })
                        
        return analysis
        
    def analyze_historical_patterns(self, odds_history, sport):
        """Analyze historical betting patterns"""
        if not odds_history or sport not in HISTORICAL_PATTERNS:
            return {}
            
        patterns = HISTORICAL_PATTERNS[sport]
        analysis = {
            'matching_patterns': [],
            'pattern_strength': 0,
            'recommended_adjustments': []
        }
        
        # Analyze each relevant pattern
        for pattern, config in patterns.items():
            if self.pattern_matches(odds_history, pattern, config):
                analysis['matching_patterns'].append({
                    'pattern': pattern,
                    'weight': config['weight'],
                    'confidence': self.calculate_pattern_confidence(odds_history, pattern)
                })
                
        # Calculate overall pattern strength
        if analysis['matching_patterns']:
            analysis['pattern_strength'] = sum(p['weight'] * p['confidence'] 
                                            for p in analysis['matching_patterns']) / \
                                        len(analysis['matching_patterns'])
            
        return analysis
        
    def pattern_matches(self, odds_history, pattern, config):
        """Check if a specific pattern matches the current game"""
        # Pattern-specific matching logic
        if pattern == 'home_dog_prime_time':
            return self.is_home_dog_prime_time(odds_history, config)
        elif pattern == 'division_dog':
            return self.is_division_dog(odds_history, config)
        # ... other patterns ...
        
        return False
        
    def calculate_pattern_confidence(self, odds_history, pattern):
        """Calculate confidence level for a pattern match"""
        # Pattern-specific confidence calculation
        # Returns value between 0 and 1
        return 0.8  # Placeholder