import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import pandas as pd
from ..config.settings import SPORTSBOOKS, SUPPORTED_SPORTS

logger = logging.getLogger(__name__)

class OddsCollector:
    def __init__(self):
        self.session = None
        self.odds_cache = {}
        self.last_update = {}
        self.sharp_books = ["Pinnacle", "Circa", "Bookmaker"]
        self.retail_books = ["DraftKings", "FanDuel", "BetMGM", "Caesars"]
        self.min_arb_profit = 1.0  # Minimum arbitrage profit percentage
        self.min_edge = 2.0  # Minimum edge percentage for value bets
        self.line_history = {}
        self.db = self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for historical odds storage"""
        import sqlite3
        from pathlib import Path
        
        db_path = Path('data/odds_history.db')
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        
        # Create tables if they don't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS odds_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT,
                event_id TEXT,
                book TEXT,
                market_type TEXT,
                line REAL,
                odds REAL,
                timestamp DATETIME,
                UNIQUE(sport, event_id, book, market_type, timestamp)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS line_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT,
                event_id TEXT,
                movement_type TEXT,
                old_line REAL,
                new_line REAL,
                books_involved TEXT,
                confidence REAL,
                timestamp DATETIME
            )
        ''')
        
        conn.commit()
        return conn
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_odds(self, sportsbook: str, sport: str) -> Optional[Dict]:
        """Enhanced odds fetching with historical storage"""
        if not SPORTSBOOKS[sportsbook]['enabled'] or not SUPPORTED_SPORTS[sport]['enabled']:
            return None
            
        try:
            endpoint = SPORTSBOOKS[sportsbook]['api_endpoint']
            api_key = SPORTSBOOKS[sportsbook]['api_key']
            
            async with self.session.get(
                f"{endpoint}/odds/{sport}",
                headers={"Authorization": f"Bearer {api_key}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Store in cache
                    self.odds_cache[f"{sportsbook}_{sport}"] = {
                        'data': data,
                        'timestamp': datetime.now()
                    }
                    
                    # Store in historical database
                    self._store_odds_history(sportsbook, sport, data)
                    
                    # Analyze for significant movements
                    self._analyze_new_odds(sportsbook, sport, data)
                    
                    return data
                else:
                    logger.error(f"Error fetching odds from {sportsbook} for {sport}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Exception fetching odds from {sportsbook} for {sport}: {str(e)}")
            return None
    
    def _store_odds_history(self, sportsbook: str, sport: str, data: List[Dict]):
        """Store odds data in historical database"""
        timestamp = datetime.now()
        
        c = self.db.cursor()
        for event in data:
            event_id = event['event_id']
            
            # Store moneyline odds
            if 'moneyline' in event:
                c.execute('''
                    INSERT OR REPLACE INTO odds_history 
                    (sport, event_id, book, market_type, line, odds, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sport,
                    event_id,
                    sportsbook,
                    'moneyline',
                    0,  # No line for moneyline
                    event['moneyline']['home'],
                    timestamp
                ))
            
            # Store spread odds
            if 'spread' in event:
                c.execute('''
                    INSERT OR REPLACE INTO odds_history 
                    (sport, event_id, book, market_type, line, odds, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sport,
                    event_id,
                    sportsbook,
                    'spread',
                    event['spread']['points'],
                    event['spread']['odds'],
                    timestamp
                ))
            
            # Store total odds
            if 'total' in event:
                c.execute('''
                    INSERT OR REPLACE INTO odds_history 
                    (sport, event_id, book, market_type, line, odds, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sport,
                    event_id,
                    sportsbook,
                    'total',
                    event['total']['points'],
                    event['total']['odds'],
                    timestamp
                ))
        
        self.db.commit()
    
    def _analyze_new_odds(self, sportsbook: str, sport: str, data: List[Dict]):
        """Analyze new odds data for significant movements"""
        c = self.db.cursor()
        
        for event in data:
            event_id = event['event_id']
            
            # Get previous odds
            c.execute('''
                SELECT market_type, line, odds, timestamp
                FROM odds_history
                WHERE sport = ? AND event_id = ? AND book = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (sport, event_id, sportsbook))
            
            prev_odds = c.fetchone()
            if prev_odds:
                market_type, prev_line, prev_odds, prev_timestamp = prev_odds
                
                # Check for significant movements
                if market_type == 'spread' and 'spread' in event:
                    current_line = event['spread']['points']
                    line_diff = current_line - prev_line
                    
                    if abs(line_diff) >= 0.5:  # Significant spread movement
                        self._record_line_movement(
                            sport,
                            event_id,
                            'spread',
                            prev_line,
                            current_line,
                            sportsbook,
                            self._calculate_movement_confidence(line_diff, sportsbook)
                        )
                
                elif market_type == 'total' and 'total' in event:
                    current_line = event['total']['points']
                    line_diff = current_line - prev_line
                    
                    if abs(line_diff) >= 1.0:  # Significant total movement
                        self._record_line_movement(
                            sport,
                            event_id,
                            'total',
                            prev_line,
                            current_line,
                            sportsbook,
                            self._calculate_movement_confidence(line_diff, sportsbook)
                        )
    
    def _record_line_movement(self, sport: str, event_id: str, movement_type: str,
                            old_line: float, new_line: float, book: str, confidence: float):
        """Record significant line movements"""
        c = self.db.cursor()
        
        c.execute('''
            INSERT INTO line_movements
            (sport, event_id, movement_type, old_line, new_line, books_involved, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sport,
            event_id,
            movement_type,
            old_line,
            new_line,
            book,
            confidence,
            datetime.now()
        ))
        
        self.db.commit()
    
    def _calculate_movement_confidence(self, line_diff: float, book: str) -> float:
        """Calculate confidence score for line movement"""
        base_confidence = min(abs(line_diff) / 2, 1.0)  # Scale based on movement size
        
        # Adjust based on book reputation
        if book in self.sharp_books:
            base_confidence *= 1.5  # Higher confidence in sharp book movements
        
        return min(base_confidence, 1.0)  # Cap at 1.0
    
    def get_line_history(self, sport: str, event_id: str, timeframe_minutes: int = 60) -> Dict:
        """Enhanced line movement tracking with sharp vs. public book analysis"""
        c = self.db.cursor()
        
        # Get line history for the specified timeframe
        cutoff_time = datetime.now() - timedelta(minutes=timeframe_minutes)
        
        c.execute('''
            SELECT book, market_type, line, odds, timestamp
            FROM odds_history
            WHERE sport = ? AND event_id = ? AND timestamp > ?
            ORDER BY timestamp ASC
        ''', (sport, event_id, cutoff_time))
        
        history = c.fetchall()
        
        movements = {
            'moneyline': {'home': [], 'away': []},
            'spread': {'points': [], 'odds': []},
            'totals': {'points': [], 'odds': []},
            'sharp_vs_public': {
                'sharp_consensus': self._get_sharp_consensus(sport, event_id),
                'public_consensus': self._get_public_consensus(sport, event_id)
            }
        }
        
        # Process line movement data
        for book, market_type, line, odds, timestamp in history:
            if market_type in movements:
                movements[market_type]['points'].append({
                    'timestamp': timestamp,
                    'line': line,
                    'book': book
                })
                movements[market_type]['odds'].append({
                    'timestamp': timestamp,
                    'odds': odds,
                    'book': book
                })
        
        # Add movement analysis
        movements['analysis'] = {
            'steam_moves': self._get_steam_moves(sport, event_id, cutoff_time),
            'sharp_moves': self._get_sharp_moves(sport, event_id, cutoff_time),
            'value_opportunities': self._find_value_opportunities(movements)
        }
        
        return movements
    
    def _get_steam_moves(self, sport: str, event_id: str, cutoff_time: datetime) -> List[Dict]:
        """Get steam moves from line_movements table"""
        c = self.db.cursor()
        
        c.execute('''
            SELECT movement_type, old_line, new_line, books_involved, confidence, timestamp
            FROM line_movements
            WHERE sport = ? AND event_id = ? AND timestamp > ?
            AND confidence >= 0.8  -- High confidence moves only
            ORDER BY timestamp DESC
        ''', (sport, event_id, cutoff_time))
        
        return [{
            'type': move_type,
            'old_line': old_line,
            'new_line': new_line,
            'books': books,
            'confidence': conf,
            'timestamp': ts
        } for move_type, old_line, new_line, books, conf, ts in c.fetchall()]
    
    def _get_sharp_moves(self, sport: str, event_id: str, cutoff_time: datetime) -> List[Dict]:
        """Get sharp moves (movements from respected books)"""
        c = self.db.cursor()
        
        sharp_books_str = ','.join(f"'{book}'" for book in self.sharp_books)
        
        c.execute(f'''
            SELECT movement_type, old_line, new_line, books_involved, confidence, timestamp
            FROM line_movements
            WHERE sport = ? AND event_id = ? AND timestamp > ?
            AND books_involved IN ({sharp_books_str})
            ORDER BY timestamp DESC
        ''', (sport, event_id, cutoff_time))
        
        return [{
            'type': move_type,
            'old_line': old_line,
            'new_line': new_line,
            'books': books,
            'confidence': conf,
            'timestamp': ts
        } for move_type, old_line, new_line, books, conf, ts in c.fetchall()]
    
    def get_best_odds(self, sport: str, event_id: str) -> Dict:
        """Get the best available odds across all sportsbooks for an event."""
        best_odds = {
            'moneyline': {'home': 0, 'away': 0, 'sportsbook': None},
            'spread': {'home': 0, 'away': 0, 'points': 0, 'sportsbook': None},
            'totals': {'over': 0, 'under': 0, 'points': 0, 'sportsbook': None}
        }
        
        for sportsbook in SPORTSBOOKS:
            key = f"{sportsbook}_{sport}"
            if key in self.odds_cache:
                odds = self.odds_cache[key]['data']
                event_odds = next((e for e in odds if e['event_id'] == event_id), None)
                
                if event_odds:
                    # Check moneyline
                    if event_odds.get('home_ml') > best_odds['moneyline']['home']:
                        best_odds['moneyline']['home'] = event_odds['home_ml']
                        best_odds['moneyline']['sportsbook'] = sportsbook
                    if event_odds.get('away_ml') > best_odds['moneyline']['away']:
                        best_odds['moneyline']['away'] = event_odds['away_ml']
                        best_odds['moneyline']['sportsbook'] = sportsbook
                    
                    # Check spread
                    if event_odds.get('spread_odds_home') > best_odds['spread']['home']:
                        best_odds['spread']['home'] = event_odds['spread_odds_home']
                        best_odds['spread']['points'] = event_odds['spread']
                        best_odds['spread']['sportsbook'] = sportsbook
                    
                    # Check totals
                    if event_odds.get('over_odds') > best_odds['totals']['over']:
                        best_odds['totals']['over'] = event_odds['over_odds']
                        best_odds['totals']['points'] = event_odds['total']
                        best_odds['totals']['sportsbook'] = sportsbook
        
        return best_odds
    
    def detect_arbitrage(self, sport: str, event_id: str) -> Optional[Dict]:
        """Enhanced arbitrage detection across sportsbooks."""
        best_odds = self.get_best_odds(sport, event_id)
        opportunities = []
        
        # Check moneyline arbitrage
        if best_odds['moneyline']['home'] and best_odds['moneyline']['away']:
            ml_arb = self._check_moneyline_arbitrage(
                best_odds['moneyline']['home'],
                best_odds['moneyline']['away'],
                best_odds['moneyline']['sportsbook'],
                best_odds['moneyline']['sportsbook']
            )
            if ml_arb:
                opportunities.append(ml_arb)
        
        # Check spread arbitrage
        if best_odds['spread']['home'] and best_odds['spread']['away']:
            spread_arb = self._check_spread_arbitrage(
                best_odds['spread']['home'],
                best_odds['spread']['away'],
                best_odds['spread']['points'],
                best_odds['spread']['sportsbook'],
                best_odds['spread']['sportsbook']
            )
            if spread_arb:
                opportunities.append(spread_arb)
        
        # Check totals arbitrage
        if best_odds['totals']['over'] and best_odds['totals']['under']:
            totals_arb = self._check_totals_arbitrage(
                best_odds['totals']['over'],
                best_odds['totals']['under'],
                best_odds['totals']['points'],
                best_odds['totals']['sportsbook'],
                best_odds['totals']['sportsbook']
            )
            if totals_arb:
                opportunities.append(totals_arb)
        
        return opportunities if opportunities else None
    
    def _check_moneyline_arbitrage(self, home_odds: float, away_odds: float,
                                 home_book: str, away_book: str) -> Optional[Dict]:
        """Check for moneyline arbitrage opportunities."""
        imp_prob_home = self._convert_odds_to_probability(home_odds)
        imp_prob_away = self._convert_odds_to_probability(away_odds)
        
        if imp_prob_home + imp_prob_away < 1:
            profit_pct = (1 - (imp_prob_home + imp_prob_away)) * 100
            if profit_pct >= self.min_arb_profit:
                return {
                    'type': 'moneyline',
                    'profit_percentage': profit_pct,
                    'home_odds': home_odds,
                    'away_odds': away_odds,
                    'home_sportsbook': home_book,
                    'away_sportsbook': away_book,
                    'optimal_bets': self._calculate_arbitrage_bets(
                        imp_prob_home,
                        imp_prob_away
                    )
                }
        return None
    
    def _check_spread_arbitrage(self, home_odds: float, away_odds: float,
                              points: float, home_book: str, away_book: str) -> Optional[Dict]:
        """Check for spread arbitrage opportunities."""
        imp_prob_home = self._convert_odds_to_probability(home_odds)
        imp_prob_away = self._convert_odds_to_probability(away_odds)
        
        if imp_prob_home + imp_prob_away < 1:
            profit_pct = (1 - (imp_prob_home + imp_prob_away)) * 100
            if profit_pct >= self.min_arb_profit:
                return {
                    'type': 'spread',
                    'profit_percentage': profit_pct,
                    'home_odds': home_odds,
                    'away_odds': away_odds,
                    'points': points,
                    'home_sportsbook': home_book,
                    'away_sportsbook': away_book,
                    'optimal_bets': self._calculate_arbitrage_bets(
                        imp_prob_home,
                        imp_prob_away
                    )
                }
        return None
    
    def _check_totals_arbitrage(self, over_odds: float, under_odds: float,
                              points: float, over_book: str, under_book: str) -> Optional[Dict]:
        """Check for totals arbitrage opportunities."""
        imp_prob_over = self._convert_odds_to_probability(over_odds)
        imp_prob_under = self._convert_odds_to_probability(under_odds)
        
        if imp_prob_over + imp_prob_under < 1:
            profit_pct = (1 - (imp_prob_over + imp_prob_under)) * 100
            if profit_pct >= self.min_arb_profit:
                return {
                    'type': 'totals',
                    'profit_percentage': profit_pct,
                    'over_odds': over_odds,
                    'under_odds': under_odds,
                    'points': points,
                    'over_sportsbook': over_book,
                    'under_sportsbook': under_book,
                    'optimal_bets': self._calculate_arbitrage_bets(
                        imp_prob_over,
                        imp_prob_under
                    )
                }
        return None
    
    def _convert_odds_to_probability(self, odds: float) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def _calculate_arbitrage_bets(self, prob1: float, prob2: float) -> Dict:
        """Calculate optimal bet distribution for arbitrage."""
        total = prob1 + prob2
        stake1 = prob1 / total
        stake2 = prob2 / total
        return {
            'stake1_percentage': stake1 * 100,
            'stake2_percentage': stake2 * 100
        }
    
    def get_line_movement(self, sport: str, event_id: str, timeframe_minutes: int = 60) -> Dict:
        """Enhanced line movement tracking with sharp vs. public book analysis."""
        movements = {
            'moneyline': {'home': [], 'away': []},
            'spread': {'points': [], 'odds': []},
            'totals': {'points': [], 'odds': []},
            'sharp_vs_public': {
                'sharp_consensus': self._get_sharp_consensus(sport, event_id),
                'public_consensus': self._get_public_consensus(sport, event_id)
            }
        }
        
        # Get historical line data
        history = self._get_line_history(sport, event_id, timeframe_minutes)
        
        if history:
            # Process line movement data
            for entry in history:
                for market_type in ['moneyline', 'spread', 'totals']:
                    self._process_market_movement(movements[market_type], entry, market_type)
            
            # Add movement analysis
            movements['analysis'] = {
                'steam_moves': self._detect_steam_moves(history),
                'sharp_moves': self._detect_sharp_moves(history),
                'value_opportunities': self._find_value_opportunities(history)
            }
        
        return movements
    
    def _get_sharp_consensus(self, sport: str, event_id: str) -> Dict:
        """Get consensus lines from sharp books."""
        sharp_lines = {}
        for book in self.sharp_books:
            lines = self._get_current_lines(sport, event_id, book)
            if lines:
                sharp_lines[book] = lines
        
        if not sharp_lines:
            return None
            
        return {
            'spread': self._calculate_consensus(
                [lines['spread']['points'] for lines in sharp_lines.values()]
            ),
            'total': self._calculate_consensus(
                [lines['totals']['points'] for lines in sharp_lines.values()]
            ),
            'books_reporting': len(sharp_lines)
        }
    
    def _get_public_consensus(self, sport: str, event_id: str) -> Dict:
        """Get consensus lines from retail books."""
        public_lines = {}
        for book in self.retail_books:
            lines = self._get_current_lines(sport, event_id, book)
            if lines:
                public_lines[book] = lines
        
        if not public_lines:
            return None
            
        return {
            'spread': self._calculate_consensus(
                [lines['spread']['points'] for lines in public_lines.values()]
            ),
            'total': self._calculate_consensus(
                [lines['totals']['points'] for lines in public_lines.values()]
            ),
            'books_reporting': len(public_lines)
        }
    
    def _calculate_consensus(self, values: List[float]) -> Dict:
        """Calculate consensus metrics from a list of values."""
        if not values:
            return None
            
        return {
            'average': sum(values) / len(values),
            'median': sorted(values)[len(values)//2],
            'range': max(values) - min(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0
        }
    
    def _find_value_opportunities(self, history: List[Dict]) -> List[Dict]:
        """Find potential value betting opportunities."""
        opportunities = []
        
        latest = history[-1]
        sharp_consensus = self._get_sharp_consensus(
            latest['sport'],
            latest['event_id']
        )
        
        if not sharp_consensus:
            return opportunities
            
        for book in self.retail_books:
            lines = self._get_current_lines(
                latest['sport'],
                latest['event_id'],
                book
            )
            if lines:
                # Check spread value
                spread_edge = self._calculate_edge(
                    lines['spread']['points'],
                    sharp_consensus['spread']['average']
                )
                if abs(spread_edge) >= self.min_edge:
                    opportunities.append({
                        'type': 'spread',
                        'book': book,
                        'line': lines['spread']['points'],
                        'consensus': sharp_consensus['spread']['average'],
                        'edge': spread_edge
                    })
                
                # Check total value
                total_edge = self._calculate_edge(
                    lines['totals']['points'],
                    sharp_consensus['total']['average']
                )
                if abs(total_edge) >= self.min_edge:
                    opportunities.append({
                        'type': 'total',
                        'book': book,
                        'line': lines['totals']['points'],
                        'consensus': sharp_consensus['total']['average'],
                        'edge': total_edge
                    })
        
        return opportunities
    
    def _calculate_edge(self, line: float, consensus: float) -> float:
        """Calculate the edge percentage between a line and consensus."""
        return ((line - consensus) / consensus) * 100

    def _get_line_history(self, sport: str, event_id: str, timeframe_minutes: int) -> List[Dict]:
        """Retrieve historical line data for a given event."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return []
    
    def _process_market_movement(self, movements: Dict, entry: Dict, market_type: str):
        """Process line movement data for a specific market."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        pass
    
    def _detect_steam_moves(self, history: List[Dict]) -> List[Dict]:
        """Detect steam moves in historical line data."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return []
    
    def _detect_sharp_moves(self, history: List[Dict]) -> List[Dict]:
        """Detect sharp moves in historical line data."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return []
    
    def _get_current_lines(self, sport: str, event_id: str, book: str) -> Dict:
        """Retrieve current lines for a specific event from a specific sportsbook."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return {}
    
    def _get_current_lines(self, sport: str, event_id: str, book: str) -> Dict:
        """Retrieve current lines for a specific event from a specific sportsbook."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return {}
    
    def _get_current_lines(self, sport: str, event_id: str, book: str) -> Dict:
        """Retrieve current lines for a specific event from a specific sportsbook."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return {}
    
    def _get_current_lines(self, sport: str, event_id: str, book: str) -> Dict:
        """Retrieve current lines for a specific event from a specific sportsbook."""
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return {} 