from sports_betting.data_collection.base_collector import BaseDataCollector
import pandas as pd
import requests
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime

class NCAAFDataCollector(BaseDataCollector):
    """NCAAF Data Collector implementation"""
    
    def __init__(self):
        super().__init__()
        self.BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/college-football"
        self.sport = "football"
        self.league = "college-football"
        # Get current season based on current date
        current_year = datetime.now().year
        # If we're in the first few months of the year, use previous year's season
        self.SEASON = current_year if datetime.now().month > 6 else current_year - 1

    def _fetch_team_stats(self) -> pd.DataFrame:
        """Fetch FBS team statistics"""
        try:
            # Group 80 is FBS teams
            url = f"{self.BASE_URL}/teams?limit=1000&groups=80&season={self.SEASON}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            teams_data = []
            for team_entry in teams:
                team = team_entry.get('team', {})
                if team:
                    teams_data.append({
                        'team_id': team.get('id'),
                        'team_name': team.get('name'),
                        'conference': team.get('conference', {}).get('name', ''),
                        'division': 'FBS'  # All teams in group 80 are FBS
                    })
            
            df = pd.DataFrame(teams_data)
            logger.info(f"Found {len(df)} FBS teams")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching teams: {str(e)}")
            return pd.DataFrame()

    def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            return {}

    def _fetch_player_stats(self) -> pd.DataFrame:
        """Fetch NCAAF player statistics"""
        return pd.DataFrame(columns=["player_id", "player_name", "team_id"])

    def _fetch_betting_trends(self) -> pd.DataFrame:
        """Fetch NCAAF betting trends"""
        return pd.DataFrame()

    def _fetch_injury_data(self) -> pd.DataFrame:
        """Fetch NCAAF injury reports"""
        return pd.DataFrame()

    def _fetch_weather_data(self) -> pd.DataFrame:
        """Fetch NCAAF game weather data"""
        return pd.DataFrame()

    def _calculate_advanced_metrics(self, team_stats: pd.DataFrame) -> pd.DataFrame:
        """Calculate NCAAF advanced metrics"""
        return pd.DataFrame(columns=[
            "offensive_rating",
            "defensive_rating",
            "net_rating",
            "pace",
            "turnover_margin"
        ])

    def get_player_stats(self) -> pd.DataFrame:
        """Get player statistics for all FBS teams"""
        team_data = self.get_team_stats()
        all_players = []
        
        for _, team in team_data.iterrows():
            team_id = team['team_id']
            try:
                url = f"{self.BASE_URL}/teams/{team_id}/roster?season={self.SEASON}"
                response = requests.get(url)
                response.raise_for_status()
                
                roster = response.json().get('athletes', [])
                for player in roster:
                    player_info = {
                        'player_id': player.get('id'),
                        'player_name': player.get('fullName'),
                        'team_id': team_id,
                        'position': player.get('position', {}).get('abbreviation'),
                        'jersey': player.get('jersey'),
                        'year': player.get('experience', {}).get('name')
                    }
                    all_players.append(player_info)
                    
            except Exception as e:
                logger.warning(f"Error fetching roster for team {team_id}: {str(e)}")
                continue
        
        df = pd.DataFrame(all_players)
        logger.info(f"Found {len(df)} players")
        return df

    def get_advanced_metrics(self) -> pd.DataFrame:
        """Get advanced metrics for all teams"""
        try:
            teams_df = self._fetch_team_stats()
            metrics_data = []
            
            for _, team in teams_df.iterrows():
                team_id = team['team_id']
                # Use the scoreboard endpoint which includes team stats
                url = f"{self.BASE_URL}/scoreboard"
                params = {
                    'groups': '80',  # FBS teams
                    'limit': 1,
                    'team': team_id
                }
                
                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract team data from the response
                    team_data = None
                    for event in data.get('events', []):
                        for competitor in event.get('competitions', [{}])[0].get('competitors', []):
                            if competitor.get('id') == str(team_id):
                                team_data = competitor
                                break
                        if team_data:
                            break
                    
                    if team_data:
                        metrics = self._calculate_team_metrics(team_data, team_id)
                        if metrics:
                            metrics_data.append(metrics)
                            
                except Exception as e:
                    logger.warning(f"Error calculating metrics for team {team_id}: {str(e)}")
                    continue
                    
            return pd.DataFrame(metrics_data)
            
        except Exception as e:
            logger.error(f"Error getting advanced metrics: {str(e)}")
            return pd.DataFrame()

    def _get_stat(self, stats: Dict, category: str, stat_name: str) -> float:
        """Helper method to extract specific stats"""
        try:
            categories = stats.get('statistics', [])
            for cat in categories:
                if cat.get('name') == category:
                    for stat in cat.get('stats', []):
                        if stat.get('name') == stat_name:
                            return float(stat.get('value', 0))
            return 0.0
        except Exception:
            return 0.0

    def get_odds(self) -> pd.DataFrame:
        """Get current NCAAF odds and game information"""
        try:
            url = f"{self.BASE_URL}/scoreboard?limit=100&dates={self.SEASON}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            games_data = []
            for event in events:
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [{}, {}])
                
                # Ensure we have both teams
                if len(competitors) != 2:
                    continue
                    
                # Get home and away teams
                home_team = next((team for team in competitors if team.get('homeAway') == 'home'), {})
                away_team = next((team for team in competitors if team.get('homeAway') == 'away'), {})
                
                if not home_team or not away_team:
                    continue
                    
                # Get odds information
                odds = competition.get('odds', [{}])[0] if competition.get('odds') else {}
                
                game_info = {
                    'game_id': event.get('id'),
                    'start_time': event.get('date'),
                    'home_team': home_team.get('team', {}).get('name'),
                    'away_team': away_team.get('team', {}).get('name'),
                    'home_id': home_team.get('team', {}).get('id'),
                    'away_id': away_team.get('team', {}).get('id'),
                    'spread': odds.get('details', ''),  # Get spread from details
                    'over_under': odds.get('overUnder', ''),
                    'home_moneyline': odds.get('homeTeamOdds', {}).get('moneyLine', ''),
                    'away_moneyline': odds.get('awayTeamOdds', {}).get('moneyLine', '')
                }
                
                # Only add games with valid teams
                if game_info['home_team'] and game_info['away_team']:
                    games_data.append(game_info)
            
            df = pd.DataFrame(games_data)
            
            # Convert spread string to numeric value
            def parse_spread(spread_str):
                try:
                    if not spread_str:
                        return None
                    # Extract numeric value from spread string (e.g., "TEAM -7.5" -> -7.5)
                    return float(spread_str.split()[-1])
                except:
                    return None
                    
            if 'spread' in df.columns:
                df['spread'] = df['spread'].apply(parse_spread)
                
            logger.info(f"Found {len(df)} games with odds")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching NCAAF odds: {str(e)}")
            return pd.DataFrame()

    def _calculate_team_metrics(self, data: dict, team_id: str) -> dict:
        """Calculate advanced metrics for a team"""
        try:
            stats = data.get('statistics', [])
            if not stats:
                return None
            
            # Convert stats list to dictionary
            stats_dict = {}
            for stat in stats:
                name = stat.get('name', '').lower().replace(' ', '_')
                value = stat.get('value', 0)
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0
                stats_dict[name] = value
            
            # Calculate metrics
            metrics = {
                'team_id': team_id,
                'points_per_game': stats_dict.get('points_per_game', 0),
                'total_offense': stats_dict.get('total_offense_per_game', 0),
                'total_defense': stats_dict.get('total_defense_per_game', 0),
                'turnover_margin': stats_dict.get('turnover_margin', 0),
                'third_down_pct': stats_dict.get('third_down_conversion_pct', 0),
                'red_zone_pct': stats_dict.get('red_zone_efficiency', 0)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics for team {team_id}: {str(e)}")
            return None
