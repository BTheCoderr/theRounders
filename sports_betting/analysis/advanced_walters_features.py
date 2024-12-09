from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class AdvancedWaltersFeatures:
    def __init__(self):
        # Walters-style position management
        self.position_config = {
            'distribution': {
                'early_positions': 0.3,    # 30% of total position early
                'middle_positions': 0.4,    # 40% mid-market
                'late_positions': 0.3       # 30% near game time
            },
            'book_tiers': {
                'sharp': ['pinnacle', 'circa', 'cris'],
                'mid': ['bet365', 'draftkings'],
                'soft': ['bovada', 'betmgm']
            },
            'timing_windows': {
                'early': {'hours': 24, 'max_size': 0.3},
                'mid': {'hours': 12, 'max_size': 0.4},
                'late': {'hours': 4, 'max_size': 0.3}
            }
        }
        
        # Market impact thresholds
        self.impact_thresholds = {
            'NFL': {
                'max_per_book': 50000,
                'line_move_threshold': 0.5,
                'time_between_bets': 300  # 5 minutes
            },
            'NBA': {
                'max_per_book': 30000,
                'line_move_threshold': 0.5,
                'time_between_bets': 180  # 3 minutes
            }
        }
        
    def distribute_positions(self, total_position: float, game_data: Dict) -> Dict:
        """Walters-style position distribution"""
        distribution = {
            'positions': [],
            'timing': {},
            'books': {},
            'impact_analysis': {}
        }
        
        try:
            # 1. Calculate optimal position sizes
            position_sizes = self._calculate_position_sizes(total_position, game_data)
            
            # 2. Determine optimal timing
            timing_strategy = self._determine_optimal_timing(game_data)
            
            # 3. Select books for each position
            book_allocation = self._allocate_books(position_sizes, game_data)
            
            # 4. Analyze potential market impact
            impact_analysis = self._analyze_market_impact(position_sizes, book_allocation)
            
            # 5. Generate execution plan
            execution_plan = self._generate_execution_plan(
                position_sizes,
                timing_strategy,
                book_allocation,
                impact_analysis
            )
            
            distribution.update({
                'positions': execution_plan['positions'],
                'timing': execution_plan['timing'],
                'books': execution_plan['books'],
                'impact_analysis': impact_analysis
            })
            
        except Exception as e:
            print(f"Error in position distribution: {str(e)}")
            
        return distribution
        
    def _calculate_position_sizes(self, total_position: float, game_data: Dict) -> Dict:
        """Calculate optimal position sizes across different timing windows"""
        sport = game_data['sport']
        market_liquidity = self._analyze_market_liquidity(game_data)
        
        positions = {
            'early': [],
            'mid': [],
            'late': []
        }
        
        for window, config in self.position_config['timing_windows'].items():
            max_size = total_position * config['max_size']
            num_splits = self._calculate_optimal_splits(max_size, market_liquidity[window])
            
            positions[window] = self._split_position(max_size, num_splits)
            
        return positions
        
    def _analyze_market_liquidity(self, game_data: Dict) -> Dict:
        """Analyze market liquidity in different time windows"""
        liquidity = {
            'early': {'total': 0, 'per_book': {}},
            'mid': {'total': 0, 'per_book': {}},
            'late': {'total': 0, 'per_book': {}}
        }
        
        for book in game_data['books']:
            for window in liquidity.keys():
                book_liquidity = self._estimate_book_liquidity(
                    book,
                    window,
                    game_data['sport']
                )
                liquidity[window]['per_book'][book['name']] = book_liquidity
                liquidity[window]['total'] += book_liquidity
                
        return liquidity
        
    def _generate_execution_plan(self, positions: Dict, timing: Dict, 
                               books: Dict, impact: Dict) -> Dict:
        """Generate detailed execution plan"""
        plan = {
            'positions': [],
            'timing': {},
            'books': {},
            'sequence': []
        }
        
        # Sort positions by timing priority
        for window in ['early', 'mid', 'late']:
            window_positions = positions[window]
            window_timing = timing[window]
            window_books = books[window]
            
            for idx, position in enumerate(window_positions):
                execution_time = self._calculate_execution_time(
                    window_timing['start'],
                    window_timing['end'],
                    idx,
                    len(window_positions)
                )
                
                selected_book = self._select_optimal_book(
                    window_books,
                    position,
                    execution_time,
                    impact
                )
                
                plan['sequence'].append({
                    'time': execution_time,
                    'size': position,
                    'book': selected_book,
                    'expected_impact': impact['per_bet'][selected_book]
                })
                
        # Sort final sequence by execution time
        plan['sequence'] = sorted(plan['sequence'], key=lambda x: x['time'])
        
        return plan
        
    def _select_optimal_book(self, available_books: List, position_size: float,
                           execution_time: datetime, impact: Dict) -> str:
        """Select optimal book for position entry"""
        book_scores = {}
        
        for book in available_books:
            # Calculate book score based on multiple factors
            score = self._calculate_book_score(
                book,
                position_size,
                execution_time,
                impact
            )
            book_scores[book] = score
            
        return max(book_scores.items(), key=lambda x: x[1])[0]
        
    def _calculate_book_score(self, book: str, size: float, 
                            time: datetime, impact: Dict) -> float:
        """Calculate score for book selection"""
        score = 0
        
        # Liquidity score (0-40 points)
        liquidity_score = self._calculate_liquidity_score(book, size)
        score += liquidity_score * 0.4
        
        # Line movement sensitivity (0-30 points)
        movement_score = self._calculate_movement_score(book, impact)
        score += movement_score * 0.3
        
        # Historical execution success (0-30 points)
        execution_score = self._calculate_execution_score(book, time)
        score += execution_score * 0.3
        
        return score 