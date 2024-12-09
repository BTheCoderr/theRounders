import aiohttp
import asyncio
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger

class ESPNDataFetcher:
    def __init__(self):
        self.base_url = "http://site.api.espn.com/apis/site/v2/sports"
        self.endpoints = {
            'NFL': f"{self.base_url}/football/nfl",
            'NBA': f"{self.base_url}/basketball/nba",
            'MLB': f"{self.base_url}/baseball/mlb",
            'NHL': f"{self.base_url}/hockey/nhl",
            'NCAAF': f"{self.base_url}/football/college-football",
            'NCAAB': f"{self.base_url}/basketball/mens-college-basketball"
        }
        
    async def fetch_data(self, url: str) -> Dict:
        """Generic data fetcher with error handling"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error fetching data from {url}: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {str(e)}")
            return {}

    async def fetch_current_games(self, sport: str) -> Dict:
        """Fetch current games for a given sport"""
        if sport not in self.endpoints:
            logger.error(f"Sport {sport} not supported")
            return {}
        return await self.fetch_data(f"{self.endpoints[sport]}/scoreboard")

    async def fetch_historical_games(self, sport: str, date: str) -> Dict:
        """Fetch historical games for a given sport and date"""
        return await self.fetch_data(f"{self.endpoints[sport]}/scoreboard?dates={date}")

    async def fetch_team_stats(self, sport: str, team_id: str) -> Dict:
        """Fetch detailed team statistics"""
        return await self.fetch_data(f"{self.endpoints[sport]}/teams/{team_id}/statistics")

    async def fetch_player_stats(self, sport: str, team_id: str) -> Dict:
        """Fetch player statistics for a team"""
        return await self.fetch_data(f"{self.endpoints[sport]}/teams/{team_id}/roster")

    async def fetch_team_details(self, sport: str, team_id: str) -> Dict[str, pd.DataFrame]:
        """Fetch comprehensive team details including roster, stats, and rankings"""
        try:
            # Fetch multiple endpoints concurrently
            tasks = [
                self.fetch_data(f"{self.endpoints[sport]}/teams/{team_id}"),  # Basic info
                self.fetch_data(f"{self.endpoints[sport]}/teams/{team_id}/statistics"),  # Team stats
                self.fetch_data(f"{self.endpoints[sport]}/teams/{team_id}/roster"),  # Roster
                self.fetch_data(f"{self.endpoints[sport]}/teams/{team_id}/schedule")  # Schedule
            ]
            
            results = await asyncio.gather(*tasks)
            
            return {
                'team_info': self._process_team_info(results[0]),
                'team_stats': self._process_team_stats(results[1], sport),
                'roster': self._process_roster(results[2]),
                'schedule': self._process_schedule(results[3])
            }
            
        except Exception as e:
            logger.error(f"Error fetching team details: {str(e)}")
            return {}

    def _process_team_stats(self, raw_stats: Dict, sport: str) -> pd.DataFrame:
        """Process team statistics based on sport"""
        try:
            if not raw_stats or 'statistics' not in raw_stats:
                return pd.DataFrame()

            stats_dict = {}
            
            # Process based on sport type
            if sport in ['NFL', 'NCAAF']:
                stats_dict = self._process_football_team_stats(raw_stats)
            elif sport in ['NBA', 'NCAAB']:
                stats_dict = self._process_basketball_team_stats(raw_stats)
            elif sport == 'MLB':
                stats_dict = self._process_baseball_team_stats(raw_stats)
            elif sport == 'NHL':
                stats_dict = self._process_hockey_team_stats(raw_stats)
                
            return pd.DataFrame([stats_dict])
            
        except Exception as e:
            logger.error(f"Error processing team stats: {str(e)}")
            return pd.DataFrame()

    def _process_football_team_stats(self, raw_stats: Dict) -> Dict:
        """Process football-specific team statistics"""
        stats = {
            # Offense
            'points_per_game': self._extract_stat(raw_stats, 'pointsPerGame'),
            'total_yards_per_game': self._extract_stat(raw_stats, 'totalYardsPerGame'),
            'passing_yards_per_game': self._extract_stat(raw_stats, 'passingYardsPerGame'),
            'rushing_yards_per_game': self._extract_stat(raw_stats, 'rushingYardsPerGame'),
            'third_down_pct': self._extract_stat(raw_stats, 'thirdDownConversionPct'),
            'red_zone_pct': self._extract_stat(raw_stats, 'redZoneConversionPct'),
            
            # Defense
            'points_allowed_per_game': self._extract_stat(raw_stats, 'pointsAllowedPerGame'),
            'total_yards_allowed_per_game': self._extract_stat(raw_stats, 'totalYardsAllowedPerGame'),
            'sacks': self._extract_stat(raw_stats, 'sacks'),
            'interceptions': self._extract_stat(raw_stats, 'interceptions'),
            
            # Special Teams
            'field_goal_pct': self._extract_stat(raw_stats, 'fieldGoalPct'),
            'punt_return_avg': self._extract_stat(raw_stats, 'puntReturnAverage')
        }
        return stats

    def _process_basketball_team_stats(self, raw_stats: Dict) -> Dict:
        """Process basketball-specific team statistics"""
        stats = {
            # Offense
            'points_per_game': self._extract_stat(raw_stats, 'pointsPerGame'),
            'field_goal_pct': self._extract_stat(raw_stats, 'fieldGoalPct'),
            'three_point_pct': self._extract_stat(raw_stats, 'threePointPct'),
            'free_throw_pct': self._extract_stat(raw_stats, 'freeThrowPct'),
            'assists_per_game': self._extract_stat(raw_stats, 'assistsPerGame'),
            
            # Defense
            'rebounds_per_game': self._extract_stat(raw_stats, 'reboundsPerGame'),
            'blocks_per_game': self._extract_stat(raw_stats, 'blocksPerGame'),
            'steals_per_game': self._extract_stat(raw_stats, 'stealsPerGame'),
            
            # Advanced
            'true_shooting_pct': self._calculate_true_shooting(raw_stats),
            'pace': self._calculate_pace(raw_stats),
            'offensive_rating': self._calculate_offensive_rating(raw_stats)
        }
        return stats

    def _process_roster(self, raw_roster: Dict) -> pd.DataFrame:
        """Process team roster data"""
        try:
            if not raw_roster or 'athletes' not in raw_roster:
                return pd.DataFrame()

            players = []
            for player in raw_roster['athletes']:
                player_dict = {
                    'player_id': player['id'],
                    'name': player.get('fullName', ''),
                    'position': player.get('position', {}).get('abbreviation', ''),
                    'jersey': player.get('jersey', ''),
                    'height': player.get('height', ''),
                    'weight': player.get('weight', ''),
                    'age': player.get('age', 0),
                    'experience': player.get('experience', {}).get('years', 0)
                }
                
                # Add statistics if available
                if 'statistics' in player:
                    for stat in player['statistics']:
                        stat_name = stat.get('name', '').lower().replace(' ', '_')
                        stat_value = stat.get('value', 0)
                        player_dict[stat_name] = stat_value
                        
                players.append(player_dict)
                
            return pd.DataFrame(players)
            
        except Exception as e:
            logger.error(f"Error processing roster: {str(e)}")
            return pd.DataFrame()

    def _extract_stat(self, raw_stats: Dict, stat_name: str) -> float:
        """Safely extract a statistic from raw data"""
        try:
            return float(raw_stats.get('statistics', {}).get(stat_name, 0))
        except (ValueError, TypeError):
            return 0.0

    def _calculate_true_shooting(self, stats: Dict) -> float:
        """Calculate true shooting percentage"""
        try:
            points = self._extract_stat(stats, 'points')
            fga = self._extract_stat(stats, 'fieldGoalsAttempted')
            fta = self._extract_stat(stats, 'freeThrowsAttempted')
            
            if fga == 0 and fta == 0:
                return 0.0
                
            return (points / (2 * (fga + 0.44 * fta))) * 100
            
        except Exception:
            return 0.0

    def process_games_data(self, raw_data: Dict, sport: str) -> pd.DataFrame:
        """Process raw ESPN data into a DataFrame with sport-specific processing"""
        try:
            if not raw_data or 'events' not in raw_data:
                return pd.DataFrame()

            games_list = []
            
            for event in raw_data['events']:
                # Base game information
                game_dict = self._extract_base_game_info(event)
                
                # Sport-specific statistics
                if sport in ['NFL', 'NCAAF']:
                    game_dict.update(self._process_football_stats(event))
                elif sport in ['NBA', 'NCAAB']:
                    game_dict.update(self._process_basketball_stats(event))
                elif sport == 'MLB':
                    game_dict.update(self._process_baseball_stats(event))
                elif sport == 'NHL':
                    game_dict.update(self._process_hockey_stats(event))
                
                games_list.append(game_dict)
                
            return pd.DataFrame(games_list)
            
        except Exception as e:
            logger.error(f"Error processing {sport} games data: {str(e)}")
            return pd.DataFrame()

    def _extract_base_game_info(self, event: Dict) -> Dict:
        """Extract basic game information common to all sports"""
        game_dict = {
            'game_id': event['id'],
            'date': event['date'],
            'name': event['name'],
            'short_name': event['shortName'],
            'status': event['status']['type']['name'],
            'venue': event['competitions'][0].get('venue', {}).get('fullName', ''),
            'neutral_site': event['competitions'][0].get('neutralSite', False)
        }
        
        # Extract team data
        for team in event['competitions'][0]['competitors']:
            team_type = 'home' if team['homeAway'] == 'home' else 'away'
            game_dict.update({
                f'{team_type}_team': team['team']['abbreviation'],
                f'{team_type}_team_id': team['team']['id'],
                f'{team_type}_score': team.get('score', 0),
                f'{team_type}_record': team.get('records', [{'summary': '0-0'}])[0]['summary'],
                f'{team_type}_rank': team['team'].get('rank', 0)  # Important for college sports
            })
            
        return game_dict

    def _process_football_stats(self, event: Dict) -> Dict:
        """Process football-specific statistics"""
        stats = {}
        competition = event['competitions'][0]
        
        # Extract detailed statistics if available
        for team in competition['competitors']:
            team_type = 'home' if team['homeAway'] == 'home' else 'away'
            team_stats = team.get('statistics', [])
            
            for stat in team_stats:
                name = stat.get('name', '').lower().replace(' ', '_')
                value = stat.get('displayValue', '0')
                stats[f'{team_type}_{name}'] = value
                
        # Add betting information if available
        odds = competition.get('odds', [{}])[0]
        if odds:
            stats.update({
                'spread': odds.get('spread', 0),
                'over_under': odds.get('overUnder', 0),
                'home_moneyline': odds.get('homeMoneyLine', 0),
                'away_moneyline': odds.get('awayMoneyLine', 0)
            })
            
        return stats

    # ... (I'll continue with basketball, baseball, and hockey processing in the next message)

async def analyze_team(sport: str, team_id: str):
    fetcher = ESPNDataFetcher()
    team_data = await fetcher.fetch_team_details(sport, team_id)
    
    if team_data:
        # Access different aspects of team data
        team_stats = team_data['team_stats']
        roster = team_data['roster']
        
        # Print some key statistics
        print("\nTeam Statistics:")
        print(team_stats)
        
        print("\nRoster Information:")
        print(roster[['name', 'position', 'experience']])

# Example usage
if __name__ == "__main__":
    # Example team IDs
    CHIEFS_ID = "12"  # Kansas City Chiefs
    LAKERS_ID = "13"  # Los Angeles Lakers
    
    asyncio.run(analyze_team('NFL', CHIEFS_ID)) 