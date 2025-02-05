from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
from datetime import datetime
import aiohttp
import asyncio
from fake_useragent import UserAgent
from api_config import APIConfig
import numpy as np

class DataScraper:
    def __init__(self):
        self.config = APIConfig()
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize last request times for rate limiting
        self.last_requests = {
            'understat': 0,
            'ufc_stats': 0,
            'espn': 0
        }
    
    def _get_headers(self) -> Dict:
        """Get randomized headers for scraping."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def _handle_rate_limit(self, source: str):
        """Handle rate limiting for different sources."""
        current_time = time.time()
        time_since_last = current_time - self.last_requests.get(source, 0)
        min_interval = self.config.get_rate_limit(source)['min_interval']
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self.last_requests[source] = time.time()
    
    async def _async_get(self, url: str, source: str) -> Optional[str]:
        """Make async HTTP GET request."""
        try:
            self._handle_rate_limit(source)
            headers = self._get_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self.logger.error(f"Error {response.status} for {url}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    # UFC Stats Scraping
    async def scrape_ufc_stats(self, fighter_id: str) -> Optional[Dict]:
        """Scrape fighter stats from UFCStats."""
        url = f"{self.config.UFC_STATS_URL}/fighter-details/{fighter_id}"
        html = await self._async_get(url, 'ufc_stats')
        
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            stats = {}
            
            # Basic info
            stats['name'] = soup.select_one('.b-content__title-highlight').text.strip()
            
            # Record
            record = soup.select_one('.b-content__title-record').text
            stats['record'] = self._parse_ufc_record(record)
            
            # Detailed stats
            stats.update(self._parse_ufc_stats_table(soup))
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error parsing UFC stats: {str(e)}")
            return None
    
    def _parse_ufc_record(self, record: str) -> Dict:
        """Parse UFC fighter record string."""
        try:
            parts = record.strip().split('-')
            return {
                'wins': int(parts[0]),
                'losses': int(parts[1]),
                'draws': int(parts[2]) if len(parts) > 2 else 0
            }
        except:
            return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def _parse_ufc_stats_table(self, soup: BeautifulSoup) -> Dict:
        """Parse UFC fighter stats table."""
        stats = {}
        
        # Strike stats
        strike_stats = soup.select('.b-fight-details__table-col')
        if strike_stats:
            stats['striking'] = {
                'sig_strikes_landed_per_min': self._extract_float(strike_stats[0]),
                'sig_strike_accuracy': self._extract_percentage(strike_stats[1]),
                'sig_strikes_absorbed_per_min': self._extract_float(strike_stats[2]),
                'sig_strike_defense': self._extract_percentage(strike_stats[3])
            }
        
        # Grappling stats
        grappling_stats = soup.select('.b-fight-details__table-col')[4:]
        if grappling_stats:
            stats['grappling'] = {
                'takedown_avg': self._extract_float(grappling_stats[0]),
                'takedown_accuracy': self._extract_percentage(grappling_stats[1]),
                'takedown_defense': self._extract_percentage(grappling_stats[2]),
                'submission_avg': self._extract_float(grappling_stats[3])
            }
        
        return stats
    
    # Understat Soccer Scraping
    async def scrape_understat_match(self, match_id: str) -> Optional[Dict]:
        """Scrape match stats from Understat."""
        url = f"{self.config.UNDERSTAT_BASE_URL}/match/{match_id}"
        html = await self._async_get(url, 'understat')
        
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            stats = {}
            
            # Match info
            stats['teams'] = self._get_understat_teams(soup)
            stats['score'] = self._get_understat_score(soup)
            
            # xG stats
            stats['xg'] = self._get_understat_xg(soup)
            
            # Shot maps
            stats['shots'] = self._get_understat_shots(soup)
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error parsing Understat match: {str(e)}")
            return None
    
    def _get_understat_teams(self, soup: BeautifulSoup) -> Dict:
        """Get team names from Understat match."""
        teams = soup.select('.team-name')
        return {
            'home': teams[0].text.strip() if teams else '',
            'away': teams[1].text.strip() if len(teams) > 1 else ''
        }
    
    def _get_understat_score(self, soup: BeautifulSoup) -> Dict:
        """Get match score from Understat."""
        score = soup.select('.score-unit')
        return {
            'home': int(score[0].text) if score else 0,
            'away': int(score[1].text) if len(score) > 1 else 0
        }
    
    def _get_understat_xg(self, soup: BeautifulSoup) -> Dict:
        """Get xG stats from Understat match."""
        xg = soup.select('.xg-unit')
        return {
            'home': float(xg[0].text) if xg else 0.0,
            'away': float(xg[1].text) if len(xg) > 1 else 0.0
        }
    
    def _get_understat_shots(self, soup: BeautifulSoup) -> List[Dict]:
        """Get shot map data from Understat match."""
        shots = []
        shot_elements = soup.select('.shot-unit')
        
        for shot in shot_elements:
            try:
                shots.append({
                    'minute': int(shot.get('data-minute', 0)),
                    'team': shot.get('data-team', ''),
                    'player': shot.get('data-player', ''),
                    'xg': float(shot.get('data-xg', 0)),
                    'result': shot.get('data-result', ''),
                    'x': float(shot.get('data-x', 0)),
                    'y': float(shot.get('data-y', 0))
                })
            except:
                continue
        
        return shots
    
    # Helper methods
    def _extract_float(self, element) -> float:
        """Extract float from element text."""
        try:
            return float(element.text.strip())
        except:
            return 0.0
    
    def _extract_percentage(self, element) -> float:
        """Extract percentage from element text."""
        try:
            return float(element.text.strip('%')) / 100
        except:
            return 0.0
    
    # Public methods for batch scraping
    async def scrape_ufc_card(self, event_id: str) -> Dict[str, Dict]:
        """Scrape stats for all fighters on a UFC card."""
        url = f"{self.config.UFC_STATS_URL}/event-details/{event_id}"
        html = await self._async_get(url, 'ufc_stats')
        
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'lxml')
        fighter_links = soup.select('.b-fight-details__person-link')
        fighter_ids = [link['href'].split('/')[-1] for link in fighter_links]
        
        tasks = [self.scrape_ufc_stats(fighter_id) for fighter_id in fighter_ids]
        results = await asyncio.gather(*tasks)
        
        return {
            fighter_id: result 
            for fighter_id, result in zip(fighter_ids, results)
            if result is not None
        }
    
    async def scrape_understat_matches(self, match_ids: List[str]) -> Dict[str, Dict]:
        """Scrape stats for multiple soccer matches."""
        tasks = [self.scrape_understat_match(match_id) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        
        return {
            match_id: result
            for match_id, result in zip(match_ids, results)
            if result is not None
        }
    
    def transform_margin_of_victory(self, margin: float) -> float:
        """
        Transform margin of victory using diminishing returns as per Massey's method.
        Converts raw margin to a number between 0 and 1.
        """
        # Use sigmoid function with scaling
        return 2 / (1 + np.exp(-margin/10)) - 1
    
    def calculate_home_advantage(self, home_team: str, away_team: str, 
                               historical_games: List[Dict]) -> float:
        """
        Calculate home field advantage factor based on historical matchups.
        """
        home_wins = 0
        total_games = 0
        
        for game in historical_games:
            if (game['home_team'] == home_team and game['away_team'] == away_team) or \
               (game['home_team'] == away_team and game['away_team'] == home_team):
                total_games += 1
                if game['home_team_score'] > game['away_team_score']:
                    home_wins += 1
        
        return (home_wins / total_games) if total_games > 0 else 0.6  # Default to 60% if no history
    
    async def fetch_historical_matchups(self, team_a: str, team_b: str, 
                                     seasons: Optional[List[int]] = None) -> List[Dict]:
        """
        Fetch historical matchups between two teams across specified seasons.
        """
        if not seasons:
            current_year = datetime.now().year
            seasons = list(range(current_year-5, current_year+1))
            
        matchups = []
        for season in seasons:
            await self._handle_rate_limit('espn')
            # Fetch from ESPN API
            url = f"{self.config.get_api_url('espn')}/teams/{team_a}/matchups"
            params = {
                'season': season,
                'opponent': team_b
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        matchups.extend(self._parse_matchup_data(data))
                        
        return matchups
    
    def _parse_matchup_data(self, data: Dict) -> List[Dict]:
        """Parse matchup data from ESPN API response."""
        games = []
        for event in data.get('events', []):
            try:
                game = {
                    'date': event['date'],
                    'home_team': event['competitions'][0]['competitors'][0]['team']['name'],
                    'away_team': event['competitions'][0]['competitors'][1]['team']['name'],
                    'home_team_score': int(event['competitions'][0]['competitors'][0]['score']),
                    'away_team_score': int(event['competitions'][0]['competitors'][1]['score']),
                    'neutral_site': event['competitions'][0].get('neutralSite', False)
                }
                games.append(game)
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error parsing game data: {e}")
                continue
                
        return games 