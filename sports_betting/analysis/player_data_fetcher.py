import nfl_data_py as nfl
from nba_api.stats.endpoints import playergamelog, commonplayerinfo
import pandas as pd
from datetime import datetime
import asyncio
from typing import Dict, List

class PlayerDataFetcher:
    def __init__(self):
        self.nfl_data = self._load_nfl_data()
        self.nba_data = {}
        
    def _load_nfl_data(self) -> pd.DataFrame:
        """Load NFL player stats"""
        try:
            # Get last 3 seasons of player stats
            years = [2021, 2022, 2023]
            data = nfl.import_weekly_data(years)
            print(f"Loaded {len(data)} NFL player records")
            return data
        except Exception as e:
            print(f"Error loading NFL data: {e}")
            return pd.DataFrame()
            
    async def get_player_stats(self, player_name: str, sport: str) -> Dict:
        """Get comprehensive player stats"""
        if sport == 'NFL':
            return self._get_nfl_player_stats(player_name)
        elif sport == 'NBA':
            return await self._get_nba_player_stats(player_name)
        else:
            raise ValueError(f"Sport {sport} not supported")
            
    def _get_nfl_player_stats(self, player_name: str) -> Dict:
        """Get NFL player stats"""
        player_data = self.nfl_data[self.nfl_data['player_name'] == player_name]
        
        if len(player_data) == 0:
            return {}
            
        recent_games = player_data.sort_values('week', ascending=False).head(5)
        
        return {
            'recent_games': recent_games.to_dict('records'),
            'season_stats': {
                'passing_yards': player_data['passing_yards'].mean(),
                'rushing_yards': player_data['rushing_yards'].mean(),
                'receptions': player_data['receptions'].mean(),
                'receiving_yards': player_data['receiving_yards'].mean(),
                'touchdowns': player_data['touchdowns'].mean()
            },
            'trends': self._analyze_trends(player_data)
        }
        
    async def _get_nba_player_stats(self, player_name: str) -> Dict:
        """Get NBA player stats"""
        try:
            # Get player ID
            player_info = commonplayerinfo.CommonPlayerInfo(player_name=player_name)
            player_id = player_info.get_data_frames()[0]['PERSON_ID'][0]
            
            # Get game logs
            game_logs = playergamelog.PlayerGameLog(player_id=player_id)
            games_df = game_logs.get_data_frames()[0]
            
            recent_games = games_df.head(5)
            
            return {
                'recent_games': recent_games.to_dict('records'),
                'season_stats': {
                    'points': games_df['PTS'].mean(),
                    'rebounds': games_df['REB'].mean(),
                    'assists': games_df['AST'].mean(),
                    'minutes': games_df['MIN'].mean()
                },
                'trends': self._analyze_trends(games_df)
            }
            
        except Exception as e:
            print(f"Error getting NBA stats for {player_name}: {e}")
            return {}
            
    def _analyze_trends(self, data: pd.DataFrame) -> Dict:
        """Analyze player trends"""
        # Add trend analysis logic here
        return {
            'improving': True,
            'consistency': 0.8,
            'recent_form': 'good'
        }

# Usage example
async def main():
    fetcher = PlayerDataFetcher()
    
    # Get NFL player stats
    mahomes_stats = await fetcher.get_player_stats("Patrick Mahomes", "NFL")
    print("\nMahomes Stats:")
    print(mahomes_stats['season_stats'])
    
    # Get NBA player stats
    jokic_stats = await fetcher.get_player_stats("Nikola Jokic", "NBA")
    print("\nJokic Stats:")
    print(jokic_stats['season_stats'])

if __name__ == "__main__":
    asyncio.run(main()) 