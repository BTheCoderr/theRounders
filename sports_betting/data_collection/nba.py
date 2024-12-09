from datetime import datetime
import requests
import pandas as pd
from sports_betting.utils.logging_config import logger
import json
from sports_betting.data_collection.odds_api import OddsAPICollector

class NBADataCollector:
    def __init__(self):
        self.odds_api = OddsAPICollector()
        self.BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
        self.SEASON = datetime.now().year if datetime.now().month >= 10 else datetime.now().year - 1

    def get_odds(self) -> pd.DataFrame:
        """Get odds from the Odds API"""
        return self.odds_api.get_odds(sport='basketball_nba')

    def get_team_stats(self) -> pd.DataFrame:
        """Get current team statistics"""
        try:
            url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/standings"
            response = requests.get(url)
            response.raise_for_status()
            
            stats_data = []
            for entry in response.json().get('standings', []):
                team = entry.get('team', {})
                stats = entry.get('stats', [])
                
                team_stats = {
                    'team_name': team.get('abbreviation'),
                    'wins': self._get_stat_value(stats, 'wins'),
                    'losses': self._get_stat_value(stats, 'losses'),
                    'win_pct': self._get_stat_value(stats, 'winPercent'),
                    'ppg': self._get_stat_value(stats, 'pointsFor'),
                    'oppg': self._get_stat_value(stats, 'pointsAgainst'),
                    'point_diff': self._get_stat_value(stats, 'pointDifferential')
                }
                
                team_stats['rating'] = (team_stats['point_diff'] * 2) + (team_stats['win_pct'] * 10)
                stats_data.append(team_stats)
                
            return pd.DataFrame(stats_data)
            
        except Exception as e:
            logger.error(f"Error fetching team stats: {str(e)}")
            return pd.DataFrame()

    def _get_stat_value(self, stats: list, stat_name: str) -> float:
        """Get stat value from stats list - verified working from tests"""
        try:
            stat = next((s for s in stats if s.get('name') == stat_name), {})
            return float(stat.get('value', 0))
        except:
            return 0.0
