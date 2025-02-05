from .base_collector import BaseDataCollector
import pandas as pd
import requests
from loguru import logger
from ..utils.season_utils import get_current_season
import urllib3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class NCAABDataCollector(BaseDataCollector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball"
        self.current_season = get_current_season('NCAAB')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        urllib3.disable_warnings()

    def _make_request(self, url: str, params: dict = None) -> dict:
        """Make request with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=30,
                    verify=False
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
                continue

    def _fetch_team_roster(self, team_id: int) -> List[Dict]:
        """Fetch roster for a single team"""
        # Try current season first
        url = f"{self.base_url}/teams/{team_id}/roster?season={self.current_season}"
        try:
            response = requests.get(url)
            if response.status_code == 404:
                # If 404, try previous season
                prev_season = f"{int(self.current_season.split('-')[0])-1}-{int(self.current_season.split('-')[1])-1}"
                url = f"{self.base_url}/teams/{team_id}/roster?season={prev_season}"
                response = requests.get(url)
            response.raise_for_status()
            return response.json().get('athletes', [])
        except Exception as e:
            logger.warning(f"Error fetching roster for team {team_id}: {str(e)}")
            return []

    def _fetch_team_stats(self) -> pd.DataFrame:
        """Fetch team statistics"""
        try:
            # Use teams endpoint for initial data
            url = f"{self.base_url}/teams"
            params = {
                'limit': 400,  # Get all D1 teams
                'group': 50    # Division I filter
            }
            
            data = self._make_request(url, params)
            teams = []
            
            # Map conference names
            conference_map = {
                'Atlantic Coast': 'ACC',
                'Atlantic Coast Conference': 'ACC',
                'Southeastern': 'SEC',
                'Southeastern Conference': 'SEC',
                'Big Ten': 'Big Ten',
                'Big 12': 'Big 12',
                'Pacific 12': 'Pac-12',
                'Pacific-12': 'Pac-12',
                'Big East': 'Big East'
            }
            
            # Navigate the correct path in response
            sports_data = data.get('sports', [{}])[0]
            leagues_data = sports_data.get('leagues', [{}])[0]
            teams_data = leagues_data.get('teams', [])
            
            for team_entry in teams_data:
                team = team_entry.get('team', {})
                conf_data = team.get('conference', {})
                conf_name = conf_data.get('name', '')
                
                # Map conference name or keep original
                conference = conference_map.get(conf_name, conf_name)
                
                teams.append({
                    'team_id': str(team.get('id')),
                    'team_name': team.get('name', ''),
                    'conference': conference
                })
            
            df = pd.DataFrame(teams)
            logger.info(f"Found {len(df)} teams with conferences: {df['conference'].unique().tolist()}")
            return df
                
        except Exception as e:
            logger.error(f"Error fetching NCAAB team stats: {str(e)}")
            return pd.DataFrame(columns=['team_id', 'team_name', 'conference'])

    def _fetch_player_stats(self) -> pd.DataFrame:
        """Fetch player statistics using parallel requests"""
        try:
            teams_df = self._fetch_team_stats()
            all_players = []
            for team_id in teams_df['team_id']:
                try:
                    roster = self._fetch_team_roster(team_id)
                    if roster:
                        all_players.extend(roster)
                except Exception as e:
                    logger.warning(f"Error processing team {team_id}: {str(e)}")
                    continue
            
            if not all_players:
                raise ValueError("No player data collected - check API endpoints and season dates")
            return pd.DataFrame(all_players)
                
        except Exception as e:
            logger.error(f"Error fetching NCAAB player stats: {str(e)}")
            return pd.DataFrame(columns=['player_id', 'player_name', 'team_id'])

    def _fetch_betting_trends(self) -> pd.DataFrame:
        """Fetch betting trends data"""
        # Placeholder implementation
        return pd.DataFrame()

    def _fetch_injury_data(self) -> pd.DataFrame:
        """Fetch injury report data"""
        # Placeholder implementation
        return pd.DataFrame()

    def _fetch_weather_data(self) -> pd.DataFrame:
        """Fetch weather data - Not applicable for indoor sport"""
        # Placeholder implementation
        return pd.DataFrame()

    def _calculate_advanced_metrics(self) -> pd.DataFrame:
        """Calculate advanced metrics"""
        return self.get_advanced_metrics()

    def _create_session(self):
        session = requests.Session()
        retries = Retry(total=5,
                       backoff_factor=0.1,
                       status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def get_advanced_metrics(self) -> pd.DataFrame:
        """Fetch advanced team metrics"""
        try:
            session = self._create_session()
            teams_df = self._fetch_team_stats()
            teams_stats = []
            
            for team_id in teams_df['team_id']:
                stats_url = f"{self.base_url}/teams/{team_id}/statistics"
                stats_response = session.get(stats_url, headers=self.headers, timeout=10)
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    stats = stats_data.get('stats', [])
                    
                    pts_per_game = float(next((s.get('value') for s in stats if s.get('name') == 'ppg'), 0))
                    opp_pts_per_game = float(next((s.get('value') for s in stats if s.get('name') == 'oppg'), 0))
                    fg_pct = float(next((s.get('value') for s in stats if s.get('name') == 'fgPct'), 0))
                    possessions = float(next((s.get('value') for s in stats if s.get('name') == 'possessions'), 100))
                    
                    teams_stats.append({
                        'offensive_rating': pts_per_game * 100 / possessions,
                        'defensive_rating': opp_pts_per_game * 100 / possessions,
                        'net_rating': (pts_per_game - opp_pts_per_game) * 100 / possessions,
                        'pace': possessions,
                        'true_shooting_percentage': fg_pct / 100
                    })
            
            return pd.DataFrame(teams_stats)
                
        except Exception as e:
            logger.error(f"Error fetching NCAAB advanced metrics: {str(e)}")
            return pd.DataFrame(columns=[
                'offensive_rating', 'defensive_rating',
                'net_rating', 'pace', 'true_shooting_percentage'
            ])