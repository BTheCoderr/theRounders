from typing import Dict, List, Optional
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

@dataclass
class SharpData:
    timestamp: datetime
    book: str
    line: float
    odds: float
    volume: float
    sharp_money_pct: float

class SharpBettingAnalytics:
    def __init__(self):
        self.sharp_tracker = SharpMoneyTracker()
        self.steam_detector = SteamMoveDetector()
        self.clv_tracker = ClosingLineValueTracker()
        
    async def analyze_market(self, prop: Dict) -> Dict:
        """Analyze market for sharp betting patterns"""
        analysis = {
            'sharp_money': await self.sharp_tracker.track_sharp_action(prop),
            'steam_moves': await self.steam_detector.detect_steam(prop),
            'clv_data': await self.clv_tracker.analyze_clv(prop)
        }
        
        # Generate recommendations based on sharp action
        recommendations = self._generate_sharp_recommendations(analysis)
        
        return {
            'analysis': analysis,
            'recommendations': recommendations,
            'timestamp': datetime.now()
        }

class SharpMoneyTracker:
    def __init__(self):
        self.sharp_books = ['pinnacle', 'circa', 'betcris']
        self.volume_threshold = 10000  # $10k minimum for sharp consideration
        
    async def track_sharp_action(self, prop: Dict) -> Dict:
        """Track sharp betting patterns"""
        try:
            # Get betting percentages and volumes
            market_data = await self._get_market_data(prop)
            
            # Analyze sharp vs public money
            sharp_analysis = self._analyze_sharp_action(market_data)
            
            # Track line movements
            line_moves = self._analyze_line_moves(market_data)
            
            # Calculate sharp confidence
            sharp_confidence = self._calculate_sharp_confidence(
                sharp_analysis,
                line_moves
            )
            
            return {
                'sharp_side': sharp_analysis['sharp_side'],
                'sharp_money_pct': sharp_analysis['sharp_money_pct'],
                'line_movement': line_moves,
                'confidence': sharp_confidence,
                'volume': market_data['total_volume'],
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error tracking sharp action: {str(e)}")
            return None
            
    def _analyze_sharp_action(self, market_data: Dict) -> Dict:
        """Analyze sharp vs public betting patterns"""
        sharp_money = 0
        public_money = 0
        
        for book, data in market_data.items():
            if book in self.sharp_books:
                sharp_money += data['volume']
            else:
                public_money += data['volume']
                
        sharp_pct = sharp_money / (sharp_money + public_money)
        
        return {
            'sharp_money_pct': sharp_pct,
            'sharp_side': 'over' if sharp_pct > 0.6 else 'under',
            'sharp_volume': sharp_money,
            'public_volume': public_money
        }

class SteamMoveDetector:
    def __init__(self):
        self.move_threshold = 0.5  # Line move threshold
        self.time_threshold = 300  # 5 minutes
        self.min_books = 3  # Minimum books for steam move
        
    async def detect_steam(self, prop: Dict) -> Dict:
        """Detect and analyze steam moves"""
        try:
            # Get real-time line movement data
            line_data = await self._get_line_movement_data(prop)
            
            # Analyze for steam moves
            steam_moves = self._analyze_steam_moves(line_data)
            
            # Calculate steam move impact
            impact = self._calculate_steam_impact(steam_moves)
            
            return {
                'steam_moves': steam_moves,
                'impact': impact,
                'affected_books': self._get_affected_books(steam_moves),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error detecting steam moves: {str(e)}")
            return None
            
    def _analyze_steam_moves(self, line_data: List[Dict]) -> List[Dict]:
        """Analyze line movements for steam patterns"""
        steam_moves = []
        
        for timestamp, moves in self._group_by_time(line_data):
            if self._is_steam_move(moves):
                steam_moves.append({
                    'timestamp': timestamp,
                    'direction': moves['direction'],
                    'magnitude': moves['magnitude'],
                    'books': moves['books']
                })
                
        return steam_moves

class ClosingLineValueTracker:
    def __init__(self):
        self.closing_window = 300  # 5 minutes before game
        self.min_clv = 0.02  # 2% minimum CLV
        
    async def analyze_clv(self, prop: Dict) -> Dict:
        """Analyze closing line value"""
        try:
            # Get historical closing lines
            historical_data = await self._get_historical_closes(prop)
            
            # Calculate CLV metrics
            clv_metrics = self._calculate_clv_metrics(historical_data)
            
            # Analyze CLV patterns
            patterns = self._analyze_clv_patterns(historical_data)
            
            return {
                'average_clv': clv_metrics['average_clv'],
                'clv_win_rate': clv_metrics['win_rate'],
                'patterns': patterns,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CLV: {str(e)}")
            return None
            
    def _calculate_clv_metrics(self, historical_data: List[Dict]) -> Dict:
        """Calculate CLV metrics from historical data"""
        clv_values = []
        wins = 0
        
        for bet in historical_data:
            clv = self._calculate_single_clv(
                bet['open_line'],
                bet['close_line'],
                bet['side']
            )
            clv_values.append(clv)
            
            if clv > 0:
                wins += 1
                
        return {
            'average_clv': np.mean(clv_values),
            'win_rate': wins / len(historical_data) if historical_data else 0
        } 