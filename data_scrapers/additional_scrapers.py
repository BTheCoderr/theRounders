import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional, Union
import os

class TennisAbstractScraper:
    """Scraper for Tennis Abstract statistics"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.base_url = "http://www.tennisabstract.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; TheRoundersBot/1.0; +https://github.com/BTheCoderr/theRounders)'
        })
        self.cache_dir = cache_dir
        self._setup_cache_dir()
        self.logger = self._setup_logger()
        
    def _setup_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _setup_logger(self):
        logger = logging.getLogger('TennisAbstractScraper')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('tennis_scraper.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def _rate_limit(self):
        time.sleep(3)
        
    def get_player_stats(self, year: int) -> pd.DataFrame:
        """Get player statistics for a specific year"""
        # Implementation for tennis stats scraping
        pass

class EightTwoGamesScraper:
    """Scraper for 82games.com NBA statistics"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.base_url = "http://www.82games.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; TheRoundersBot/1.0; +https://github.com/BTheCoderr/theRounders)'
        })
        self.cache_dir = cache_dir
        self._setup_cache_dir()
        self.logger = self._setup_logger()
        
    def _setup_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _setup_logger(self):
        logger = logging.getLogger('EightTwoGamesScraper')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('nba_scraper.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def _rate_limit(self):
        time.sleep(3)
        
    def get_team_stats(self, team: str, season: str) -> pd.DataFrame:
        """
        Get team statistics from 82games.com
        
        Args:
            team: Team abbreviation or 'all' for all teams
            season: Season in format '2023-24'
            
        Returns:
            DataFrame with advanced team statistics
        """
        cache_key = f"82games_team_stats_{team}_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            self._rate_limit()
            if team.lower() == 'all':
                url = f"{self.base_url}/{season}/teams.html"
            else:
                url = f"{self.base_url}/{season}/teams/{team}.html"
                
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract team statistics
            stats = {}
            
            # Get offensive and defensive ratings
            ratings_table = soup.find('table', {'id': 'ratings'})
            if ratings_table:
                stats.update(self._parse_ratings_table(ratings_table))
            
            # Get lineup data
            lineup_table = soup.find('table', {'id': 'lineups'})
            if lineup_table:
                stats.update(self._parse_lineup_table(lineup_table))
            
            # Get opponent stats
            opp_table = soup.find('table', {'id': 'opponent'})
            if opp_table:
                stats.update(self._parse_opponent_table(opp_table))
            
            # Convert to DataFrame
            df = pd.DataFrame([stats])
            
            # Cache the data
            self._cache_data(df, cache_key)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching team stats for {team} {season}: {str(e)}")
            raise
            
    def get_player_stats(self, team: str, season: str) -> pd.DataFrame:
        """
        Get player statistics from 82games.com
        
        Args:
            team: Team abbreviation
            season: Season in format '2023-24'
            
        Returns:
            DataFrame with advanced player statistics
        """
        cache_key = f"82games_player_stats_{team}_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            self._rate_limit()
            url = f"{self.base_url}/{season}/teams/{team}/players.html"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find player stats table
            table = soup.find('table', {'id': 'players'})
            if not table:
                raise ValueError(f"Could not find player stats table for {team} {season}")
            
            # Parse the table
            df = pd.read_html(str(table))[0]
            
            # Clean up the DataFrame
            df = df.dropna(how='all')
            if 'Player' in df.columns:
                df = df[df['Player'] != 'Player']  # Remove header rows
            
            # Add team column
            df['Team'] = team
            
            # Cache the data
            self._cache_data(df, cache_key)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching player stats for {team} {season}: {str(e)}")
            raise
            
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
        
    def _parse_ratings_table(self, table) -> Dict:
        """Parse the team ratings table"""
        stats = {}
        try:
            df = pd.read_html(str(table))[0]
            stats['offensive_rating'] = float(df.iloc[0]['ORtg'])
            stats['defensive_rating'] = float(df.iloc[0]['DRtg'])
            stats['net_rating'] = float(df.iloc[0]['Net'])
            stats['pace'] = float(df.iloc[0]['Pace'])
        except Exception as e:
            self.logger.warning(f"Error parsing ratings table: {str(e)}")
        return stats
        
    def _parse_lineup_table(self, table) -> Dict:
        """Parse the lineup data table"""
        stats = {}
        try:
            df = pd.read_html(str(table))[0]
            stats['best_lineup_net_rating'] = float(df.iloc[0]['Net'])
            stats['worst_lineup_net_rating'] = float(df.iloc[-1]['Net'])
        except Exception as e:
            self.logger.warning(f"Error parsing lineup table: {str(e)}")
        return stats
        
    def _parse_opponent_table(self, table) -> Dict:
        """Parse the opponent stats table"""
        stats = {}
        try:
            df = pd.read_html(str(table))[0]
            stats['opp_efg'] = float(df.iloc[0]['eFG%'])
            stats['opp_tov_pct'] = float(df.iloc[0]['TOV%'])
            stats['opp_oreb_pct'] = float(df.iloc[0]['ORB%'])
            stats['opp_ft_rate'] = float(df.iloc[0]['FT/FGA'])
        except Exception as e:
            self.logger.warning(f"Error parsing opponent table: {str(e)}")
        return stats

class BaseballGuruScraper:
    """Scraper for Baseball Guru statistics"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.base_url = "http://baseballguru.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; TheRoundersBot/1.0; +https://github.com/BTheCoderr/theRounders)'
        })
        self.cache_dir = cache_dir
        self._setup_cache_dir()
        self.logger = self._setup_logger()
        
    def _setup_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _setup_logger(self):
        logger = logging.getLogger('BaseballGuruScraper')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('baseball_scraper.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def _rate_limit(self):
        time.sleep(3)
        
    def get_historical_stats(self, year: int) -> pd.DataFrame:
        """Get historical baseball statistics"""
        # Implementation for baseball stats scraping
        pass 