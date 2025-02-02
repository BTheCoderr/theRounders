import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import os
import time
from nba_api.stats.endpoints import leaguedashteamstats, leaguedashplayerstats
from nba_api.stats.library.parameters import Season, SeasonType

class NBAAdvancedScraper:
    """
    Scraper for NBA.com advanced statistics and additional sources
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self._setup_cache_dir()
        self.logger = self._setup_logger()
        
    def _setup_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger('NBAAdvancedScraper')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('nba_advanced_scraper.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def _rate_limit(self):
        """Implement rate limiting"""
        time.sleep(2)
        
    def _get_cached_data(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Retrieve cached data if available and not expired"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.csv")
        if os.path.exists(cache_file):
            if time.time() - os.path.getmtime(cache_file) < 86400:  # 24 hours
                return pd.read_csv(cache_file)
        return None
        
    def _cache_data(self, data: pd.DataFrame, cache_key: str):
        """Cache the scraped data"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.csv")
        data.to_csv(cache_file, index=False)
        
    def get_advanced_team_stats(self, season: str) -> pd.DataFrame:
        """
        Get advanced team statistics from NBA.com
        
        Args:
            season: Season in format '2023-24'
            
        Returns:
            DataFrame with advanced team statistics
        """
        cache_key = f"nba_advanced_team_stats_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            self._rate_limit()
            
            # Get traditional stats
            traditional_stats = leaguedashteamstats.LeagueDashTeamStats(
                season=season,
                season_type_all_star=SeasonType.regular,
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Get advanced stats
            advanced_stats = leaguedashteamstats.LeagueDashTeamStats(
                season=season,
                season_type_all_star=SeasonType.regular,
                measure_type_detailed_defense='Advanced',
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Get hustle stats
            hustle_stats = leaguedashteamstats.LeagueDashTeamStats(
                season=season,
                season_type_all_star=SeasonType.regular,
                measure_type_detailed_defense='Hustle',
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Merge all stats
            stats = pd.merge(
                traditional_stats,
                advanced_stats,
                on='TEAM_ID',
                suffixes=('', '_advanced')
            )
            
            stats = pd.merge(
                stats,
                hustle_stats,
                on='TEAM_ID',
                suffixes=('', '_hustle')
            )
            
            # Add derived metrics
            stats['NET_RATING'] = stats['OFF_RATING'] - stats['DEF_RATING']
            stats['EFG_PCT'] = (stats['FGM'] + 0.5 * stats['FG3M']) / stats['FGA']
            stats['TS_PCT'] = stats['PTS'] / (2 * (stats['FGA'] + 0.44 * stats['FTA']))
            
            # Cache the data
            self._cache_data(stats, cache_key)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error fetching advanced team stats: {str(e)}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['TEAM_NAME', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE'])
            
    def get_advanced_player_stats(self, season: str) -> pd.DataFrame:
        """
        Get advanced player statistics from NBA.com
        
        Args:
            season: Season in format '2023-24'
            
        Returns:
            DataFrame with advanced player statistics
        """
        cache_key = f"nba_advanced_player_stats_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            self._rate_limit()
            
            # Get traditional stats
            traditional_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                season_type_all_star=SeasonType.regular,
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Get advanced stats
            advanced_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                season_type_all_star=SeasonType.regular,
                measure_type_detailed_defense='Advanced',
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Get tracking stats
            tracking_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                season_type_all_star=SeasonType.regular,
                measure_type_detailed_defense='Tracking',
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Merge all stats
            stats = pd.merge(
                traditional_stats,
                advanced_stats,
                on='PLAYER_ID',
                suffixes=('', '_advanced')
            )
            
            stats = pd.merge(
                stats,
                tracking_stats,
                on='PLAYER_ID',
                suffixes=('', '_tracking')
            )
            
            # Add derived metrics
            stats['NET_RATING'] = stats['OFF_RATING'] - stats['DEF_RATING']
            stats['EFG_PCT'] = (stats['FGM'] + 0.5 * stats['FG3M']) / stats['FGA']
            stats['TS_PCT'] = stats['PTS'] / (2 * (stats['FGA'] + 0.44 * stats['FTA']))
            
            # Cache the data
            self._cache_data(stats, cache_key)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error fetching advanced player stats: {str(e)}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'PTS', 'NET_RATING'])
            
    def get_team_lineup_stats(self, season: str) -> pd.DataFrame:
        """
        Get team lineup statistics
        
        Args:
            season: Season in format '2023-24'
            
        Returns:
            DataFrame with lineup statistics
        """
        cache_key = f"nba_lineup_stats_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            self._rate_limit()
            
            from nba_api.stats.endpoints import leaguedashlineups
            
            # Get 5-man lineup stats
            lineup_stats = leaguedashlineups.LeagueDashLineups(
                season=season,
                season_type_all_star=SeasonType.regular,
                measure_type_detailed_defense='Advanced',
                group_quantity=5,
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Add derived metrics
            lineup_stats['NET_RATING'] = lineup_stats['OFF_RATING'] - lineup_stats['DEF_RATING']
            lineup_stats['MIN_PER_GAME'] = lineup_stats['MIN'] / lineup_stats['GP']
            
            # Cache the data
            self._cache_data(lineup_stats, cache_key)
            
            return lineup_stats
            
        except Exception as e:
            self.logger.error(f"Error fetching lineup stats: {str(e)}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame({
                'GROUP_NAME': [],
                'MIN': [],
                'OFF_RATING': [],
                'DEF_RATING': [],
                'NET_RATING': [],
                'MIN_PER_GAME': []
            })
            
    def get_team_clutch_stats(self, season: str) -> pd.DataFrame:
        """
        Get team performance in clutch situations
        
        Args:
            season: Season in format '2023-24'
            
        Returns:
            DataFrame with clutch performance statistics
        """
        cache_key = f"nba_clutch_stats_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            self._rate_limit()
            
            from nba_api.stats.endpoints import leaguedashteamclutch
            
            # Get clutch stats (last 5 minutes, +/- 5 points)
            clutch_stats = leaguedashteamclutch.LeagueDashTeamClutch(
                season=season,
                season_type_all_star=SeasonType.regular,
                clutch_time=5,
                point_diff=5,
                measure_type_detailed_defense='Advanced',
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Add derived metrics
            clutch_stats['CLUTCH_NET_RATING'] = clutch_stats['OFF_RATING'] - clutch_stats['DEF_RATING']
            clutch_stats['CLUTCH_WIN_PCT'] = clutch_stats['W'] / (clutch_stats['W'] + clutch_stats['L'])
            
            # Cache the data
            self._cache_data(clutch_stats, cache_key)
            
            return clutch_stats
            
        except Exception as e:
            self.logger.error(f"Error fetching clutch stats: {str(e)}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame({
                'TEAM_NAME': [],
                'W': [],
                'L': [],
                'CLUTCH_WIN_PCT': [],
                'CLUTCH_NET_RATING': []
            })
            
    def get_team_shooting_stats(self, season: str) -> pd.DataFrame:
        """
        Get detailed team shooting statistics
        
        Args:
            season: Season in format '2023-24'
            
        Returns:
            DataFrame with shooting statistics
        """
        cache_key = f"nba_shooting_stats_{season}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            self._rate_limit()
            
            from nba_api.stats.endpoints import leaguedashteamshotlocations, leaguedashptteamdefend
            
            # Get shot location stats
            shot_location_stats = leaguedashteamshotlocations.LeagueDashTeamShotLocations(
                season=season,
                season_type_all_star=SeasonType.regular,
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Get defensive stats
            defense_stats = leaguedashptteamdefend.LeagueDashPtTeamDefend(
                season=season,
                season_type_all_star=SeasonType.regular,
                per_mode_detailed='PerGame'
            ).get_data_frames()[0]
            
            # Merge stats
            stats = pd.merge(
                shot_location_stats,
                defense_stats,
                on='TEAM_ID',
                suffixes=('_OFF', '_DEF')
            )
            
            # Add derived metrics
            stats['EFG_PCT'] = (stats['FGM'] + 0.5 * stats['FG3M']) / stats['FGA']
            stats['TS_PCT'] = stats['PTS'] / (2 * (stats['FGA'] + 0.44 * stats['FTA']))
            
            # Cache the data
            self._cache_data(stats, cache_key)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error fetching shooting stats: {str(e)}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame({
                'TEAM_NAME': [],
                'FG_PCT': [],
                'FG3_PCT': [],
                'EFG_PCT': [],
                'TS_PCT': []
            })
            
    def get_all_stats(self, season: str) -> Dict[str, pd.DataFrame]:
        """
        Get all available statistics for a season
        
        Args:
            season: Season in format '2023-24'
            
        Returns:
            Dictionary containing all statistical DataFrames
        """
        return {
            'team_advanced': self.get_advanced_team_stats(season),
            'player_advanced': self.get_advanced_player_stats(season),
            'lineups': self.get_team_lineup_stats(season),
            'clutch': self.get_team_clutch_stats(season),
            'shooting': self.get_team_shooting_stats(season)
        } 