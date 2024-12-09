from typing import Dict, List
import asyncio
import aiohttp
import numpy as np
from datetime import datetime

class AutomatedExecution:
    def __init__(self):
        self.execution_rules = {
            'max_bet_size': {
                'per_book': 0.1,    # 10% of bankroll per book
                'per_game': 0.2,    # 20% of bankroll per game
                'daily': 0.3        # 30% of bankroll per day
            },
            'timing_rules': {
                'min_delay': 2,     # Minimum seconds between bets
                'max_window': 300   # Maximum seconds to complete distribution
            },
            'book_rules': {
                'min_books': 3,     # Minimum books to spread action
                'max_per_book': 0.4 # Maximum 40% of total position per book
            }
        }
        
    async def execute_position(self, position_data: Dict, 
                             market_state: Dict) -> Dict:
        """Execute position across multiple books"""
        execution_result = {
            'success': False,
            'positions_placed': [],
            'average_odds': 0,
            'total_exposure': 0
        }
        
        try:
            # 1. Validate Position
            if not self._validate_position(position_data, market_state):
                return execution_result
                
            # 2. Calculate Distribution
            distribution = self._calculate_distribution(
                position_data,
                market_state
            )
            
            # 3. Execute Orders
            async with aiohttp.ClientSession() as session:
                execution_tasks = []
                
                for book, amount in distribution['books'].items():
                    task = self._place_order(
                        session,
                        book,
                        amount,
                        position_data['odds']
                    )
                    execution_tasks.append(task)
                    
                # Execute all orders with small delays
                results = await self._staggered_execution(execution_tasks)
                
            # 4. Process Results
            execution_result = self._process_execution_results(results)
            
        except Exception as e:
            print(f"Execution error: {str(e)}")
            
        return execution_result
        
    def _calculate_distribution(self, position_data: Dict, 
                              market_state: Dict) -> Dict:
        """Calculate optimal bet distribution"""
        distribution = {
            'books': {},
            'timing': {},
            'backup_plans': {}
        }
        
        total_amount = position_data['size']
        available_books = self._get_available_books(market_state)
        
        # Sort books by liquidity and odds
        ranked_books = self._rank_books(available_books, position_data)
        
        # Calculate distribution
        remaining = total_amount
        for book in ranked_books:
            max_for_book = min(
                remaining,
                total_amount * self.execution_rules['book_rules']['max_per_book'],
                book['max_capacity']
            )
            
            if max_for_book > 0:
                distribution['books'][book['name']] = max_for_book
                remaining -= max_for_book
                
        # Add timing strategy
        distribution['timing'] = self._calculate_timing_strategy(
            distribution['books'],
            market_state
        )
        
        return distribution
        
    async def _staggered_execution(self, tasks: List) -> List:
        """Execute orders with staggered timing"""
        results = []
        
        for task in tasks:
            # Add random delay between executions
            delay = np.random.uniform(
                self.execution_rules['timing_rules']['min_delay'],
                self.execution_rules['timing_rules']['min_delay'] * 2
            )
            
            await asyncio.sleep(delay)
            result = await task
            results.append(result)
            
        return results
        
    async def _place_order(self, session: aiohttp.ClientSession,
                          book: str, amount: float, odds: float) -> Dict:
        """Place individual order at book"""
        try:
            # Add randomization to bet size
            jittered_amount = self._add_size_jitter(amount)
            
            # Place bet
            async with session.post(f"{book}/api/place_bet",
                                  json={
                                      'amount': jittered_amount,
                                      'odds': odds
                                  }) as resp:
                result = await resp.json()
                
            return {
                'book': book,
                'amount': jittered_amount,
                'odds': odds,
                'success': result['success'],
                'bet_id': result.get('bet_id')
            }
            
        except Exception as e:
            print(f"Error placing bet at {book}: {str(e)}")
            return {
                'book': book,
                'success': False,
                'error': str(e)
            } 