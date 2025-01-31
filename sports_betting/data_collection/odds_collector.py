import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime
import pandas as pd
from ..config.settings import SPORTSBOOKS, SUPPORTED_SPORTS

logger = logging.getLogger(__name__)

class OddsCollector:
    def __init__(self):
        self.session = None
        self.odds_cache = {}
        self.last_update = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_odds(self, sportsbook: str, sport: str) -> Optional[Dict]:
        """Fetch odds from a specific sportsbook for a specific sport."""
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
                    self.odds_cache[f"{sportsbook}_{sport}"] = {
                        'data': data,
                        'timestamp': datetime.now()
                    }
                    return data
                else:
                    logger.error(f"Error fetching odds from {sportsbook} for {sport}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Exception fetching odds from {sportsbook} for {sport}: {str(e)}")
            return None
    
    async def fetch_all_odds(self) -> Dict[str, Dict]:
        """Fetch odds from all enabled sportsbooks for all enabled sports."""
        tasks = []
        for sportsbook in SPORTSBOOKS:
            if SPORTSBOOKS[sportsbook]['enabled']:
                for sport in SUPPORTED_SPORTS:
                    if SUPPORTED_SPORTS[sport]['enabled']:
                        tasks.append(self.fetch_odds(sportsbook, sport))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._process_odds_data(results)
    
    def _process_odds_data(self, results: List[Dict]) -> Dict[str, pd.DataFrame]:
        """Process raw odds data into structured DataFrames."""
        processed_data = {}
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error processing odds data: {str(result)}")
                continue
            if not result:
                continue
                
            try:
                # Convert to DataFrame and process based on sportsbook format
                df = pd.DataFrame(result)
                
                # Add basic derived features
                if 'home_team_odds' in df.columns and 'away_team_odds' in df.columns:
                    df['implied_prob_home'] = 1 / df['home_team_odds']
                    df['implied_prob_away'] = 1 / df['away_team_odds']
                    df['overround'] = (df['implied_prob_home'] + df['implied_prob_away'] - 1)
                
                # Store processed data
                key = f"{result.get('sportsbook')}_{result.get('sport')}"
                processed_data[key] = df
                
            except Exception as e:
                logger.error(f"Error processing odds data frame: {str(e)}")
                continue
        
        return processed_data
    
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
        """Detect arbitrage opportunities for an event across sportsbooks."""
        best_odds = self.get_best_odds(sport, event_id)
        
        # Check moneyline arbitrage
        if best_odds['moneyline']['home'] and best_odds['moneyline']['away']:
            imp_prob_home = 1 / best_odds['moneyline']['home']
            imp_prob_away = 1 / best_odds['moneyline']['away']
            
            if imp_prob_home + imp_prob_away < 1:
                return {
                    'type': 'moneyline',
                    'profit_percentage': (1 - (imp_prob_home + imp_prob_away)) * 100,
                    'home_odds': best_odds['moneyline']['home'],
                    'away_odds': best_odds['moneyline']['away'],
                    'home_sportsbook': best_odds['moneyline']['sportsbook'],
                    'away_sportsbook': best_odds['moneyline']['sportsbook']
                }
        
        return None
    
    def get_line_movement(self, sport: str, event_id: str, timeframe_minutes: int = 60) -> Dict:
        """Track line movement over a specified timeframe."""
        movements = {
            'moneyline': {'home': [], 'away': []},
            'spread': {'points': [], 'odds': []},
            'totals': {'points': [], 'odds': []}
        }
        
        # Implementation depends on historical data storage
        # This is a placeholder for the actual implementation
        return movements 