from abc import ABC, abstractmethod
import pandas as pd
from loguru import logger

class BaseDataCollector(ABC):
    def __init__(self):
        self.logger = logger

    def get_team_stats(self) -> pd.DataFrame:
        """Public method to get team statistics"""
        try:
            return self._fetch_team_stats()
        except Exception as e:
            self.logger.error(f"Error getting team stats: {str(e)}")
            return pd.DataFrame()

    def get_player_stats(self) -> pd.DataFrame:
        """Public method to get player statistics"""
        try:
            return self._fetch_player_stats()
        except Exception as e:
            self.logger.error(f"Error getting player stats: {str(e)}")
            return pd.DataFrame()

    def get_advanced_metrics(self) -> pd.DataFrame:
        """Public method to get advanced metrics"""
        try:
            team_stats = self._fetch_team_stats()
            return self._calculate_advanced_metrics(team_stats)
        except Exception as e:
            self.logger.error(f"Error getting advanced metrics: {str(e)}")
            return pd.DataFrame()

    @abstractmethod
    def _fetch_team_stats(self) -> pd.DataFrame:
        """Protected method to fetch team statistics"""
        pass

    @abstractmethod
    def _fetch_player_stats(self) -> pd.DataFrame:
        """Protected method to fetch player statistics"""
        pass

    @abstractmethod
    def _fetch_betting_trends(self) -> pd.DataFrame:
        """Protected method to fetch betting trends"""
        pass

    @abstractmethod
    def _fetch_injury_data(self) -> pd.DataFrame:
        """Protected method to fetch injury reports"""
        pass

    @abstractmethod
    def _fetch_weather_data(self) -> pd.DataFrame:
        """Protected method to fetch weather data"""
        pass

    @abstractmethod
    def _calculate_advanced_metrics(self, team_stats: pd.DataFrame) -> pd.DataFrame:
        """Protected method to calculate advanced metrics"""
        pass