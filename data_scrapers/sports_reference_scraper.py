import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional, Union
import os

class SportsReferenceScraper:
    """
    A scraper class for Sports Reference family of websites
    Includes: Pro Football Reference, Basketball Reference, Baseball Reference
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.base_urls = {
            'nfl': 'https://www.pro-football-reference.com',
            'nba': 'https://www.basketball-reference.com',
            'mlb': 'https://www.baseball-reference.com'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; TheRoundersBot/1.0; +https://github.com/BTheCoderr/theRounders)'
        })
        self.cache_dir = cache_dir
        self._setup_cache_dir()
        self.logger = self._setup_logger()
        
    def _setup_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger('SportsReferenceScraper')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('scraper.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _rate_limit(self):
        """Implement rate limiting to be respectful to the servers"""
        time.sleep(3)  # Wait 3 seconds between requests
        
    def _get_cached_data(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Retrieve cached data if available and not expired"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.csv")
        if os.path.exists(cache_file):
            # Check if cache is less than 24 hours old
            if time.time() - os.path.getmtime(cache_file) < 86400:
                return pd.read_csv(cache_file)
        return None
        
    def _cache_data(self, data: pd.DataFrame, cache_key: str):
        """Cache the scraped data"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.csv")
        data.to_csv(cache_file, index=False)
        
    def get_team_stats(self, sport: str, season: int) -> pd.DataFrame:
        """
        Get team statistics for a specific sport and season
        
        Args:
            sport: One of 'nfl', 'nba', 'mlb'
            season: Year of the season
            
        Returns:
            DataFrame containing team statistics
        """
        cache_key = f"{sport}_team_stats_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        if sport not in self.base_urls:
            raise ValueError(f"Sport {sport} not supported. Must be one of {list(self.base_urls.keys())}")
            
        url = f"{self.base_urls[sport]}/years/{season}"
        
        try:
            self._rate_limit()
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main stats table
            if sport == 'nfl':
                table = soup.find('table', {'id': 'team_stats'})
            elif sport == 'nba':
                table = soup.find('table', {'id': 'per_game-team'})
            elif sport == 'mlb':
                table = soup.find('table', {'id': 'teams_standard_batting'})
                
            if not table:
                raise ValueError(f"Could not find stats table for {sport} season {season}")
                
            # Convert table to DataFrame
            df = pd.read_html(str(table))[0]
            
            # Clean up the DataFrame
            df = df.dropna(how='all')
            if 'Rk' in df.columns:
                df = df[df['Rk'] != 'Rk']  # Remove header rows if present
                
            # Cache the data
            self._cache_data(df, cache_key)
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {sport} team stats for {season}: {str(e)}")
            raise
            
    def get_player_stats(self, sport: str, season: int) -> pd.DataFrame:
        """
        Get player statistics for a specific sport and season
        
        Args:
            sport: One of 'nfl', 'nba', 'mlb'
            season: Year of the season
            
        Returns:
            DataFrame containing player statistics
        """
        cache_key = f"{sport}_player_stats_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        if sport not in self.base_urls:
            raise ValueError(f"Sport {sport} not supported. Must be one of {list(self.base_urls.keys())}")
            
        url = f"{self.base_urls[sport]}/years/{season}/players.html"
        
        try:
            self._rate_limit()
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main stats table
            if sport == 'nfl':
                table = soup.find('table', {'id': 'passing'})  # Can be modified for different stat types
            elif sport == 'nba':
                table = soup.find('table', {'id': 'per_game_stats'})
            elif sport == 'mlb':
                table = soup.find('table', {'id': 'players_standard_batting'})
                
            if not table:
                raise ValueError(f"Could not find player stats table for {sport} season {season}")
                
            # Convert table to DataFrame
            df = pd.read_html(str(table))[0]
            
            # Clean up the DataFrame
            df = df.dropna(how='all')
            if 'Rk' in df.columns:
                df = df[df['Rk'] != 'Rk']  # Remove header rows if present
                
            # Cache the data
            self._cache_data(df, cache_key)
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {sport} player stats for {season}: {str(e)}")
            raise
            
    def get_game_scores(self, sport: str, season: int) -> pd.DataFrame:
        """
        Get game scores for a specific sport and season
        
        Args:
            sport: One of 'nfl', 'nba', 'mlb'
            season: Year of the season
            
        Returns:
            DataFrame containing game scores
        """
        cache_key = f"{sport}_game_scores_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        if sport not in self.base_urls:
            raise ValueError(f"Sport {sport} not supported. Must be one of {list(self.base_urls.keys())}")
            
        url = f"{self.base_urls[sport]}/years/{season}/games.html"
        
        try:
            self._rate_limit()
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main scores table
            table = soup.find('table', {'id': 'games'})
            if not table:
                raise ValueError(f"Could not find games table for {sport} season {season}")
                
            # Convert table to DataFrame
            df = pd.read_html(str(table))[0]
            
            # Clean up the DataFrame
            df = df.dropna(how='all')
            if 'Week' in df.columns:  # NFL specific
                df = df[df['Week'] != 'Week']  # Remove header rows if present
                
            # Cache the data
            self._cache_data(df, cache_key)
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {sport} game scores for {season}: {str(e)}")
            raise 