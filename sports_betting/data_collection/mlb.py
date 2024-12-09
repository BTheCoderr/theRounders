import pandas as pd
import numpy as np
from pybaseball import statcast_pitcher, statcast_batter, playerid_lookup
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio

class MLBDataCollector:
    def __init__(self):
        self.cache = {}
        self.start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        
    async def get_player_props_data(self, player_name: str, prop_type: str) -> Dict:
        """Get comprehensive player data for props"""
        try:
            # Get player ID
            first_name, last_name = player_name.split(' ', 1)
            player_info = playerid_lookup(last_name, first_name)
            
            if player_info.empty:
                return {}
                
            player_id = player_info.iloc[0]['key_mlbam']
            
            # Get stats based on prop type
            if prop_type in ['strikeouts', 'earned_runs', 'hits_allowed']:
                stats = await self._get_pitcher_stats(player_id)
            else:
                stats = await self._get_batter_stats(player_id)
                
            # Add advanced analytics
            analytics = self._calculate_advanced_stats(stats['raw_data'], prop_type)
            
            return {
                'player_info': {
                    'name': player_name,
                    'id': player_id,
                    'team': player_info.iloc[0]['team'],
                    'position': 'P' if prop_type in ['strikeouts', 'earned_runs', 'hits_allowed'] else 'B'
                },
                'recent_stats': stats['recent'],
                'advanced_stats': analytics,
                'splits': stats['splits'],
                'raw_data': stats['raw_data'].to_dict('records')
            }
            
        except Exception as e:
            print(f"Error getting MLB data for {player_name}: {e}")
            return {}
            
    async def _get_pitcher_stats(self, player_id: int) -> Dict:
        """Get detailed pitcher statistics"""
        if f"P_{player_id}" in self.cache:
            data = self.cache[f"P_{player_id}"]
        else:
            data = statcast_pitcher(self.start_date, self.end_date, player_id)
            self.cache[f"P_{player_id}"] = data
            
        recent_games = self._group_by_game(data)
        
        return {
            'raw_data': data,
            'recent': {
                'strikeouts': {
                    'avg': recent_games['strikeouts'].mean(),
                    'median': recent_games['strikeouts'].median(),
                    'std': recent_games['strikeouts'].std(),
                    'last_5': recent_games.head()['strikeouts'].tolist()
                },
                'pitches': {
                    'avg': recent_games['pitches'].mean(),
                    'max': recent_games['pitches'].max(),
                    'last_5': recent_games.head()['pitches'].tolist()
                },
                'whiff_rate': recent_games['whiff_rate'].mean(),
                'chase_rate': recent_games['chase_rate'].mean()
            },
            'splits': self._calculate_pitcher_splits(data)
        }
        
    async def _get_batter_stats(self, player_id: int) -> Dict:
        """Get detailed batter statistics"""
        if f"B_{player_id}" in self.cache:
            data = self.cache[f"B_{player_id}"]
        else:
            data = statcast_batter(self.start_date, self.end_date, player_id)
            self.cache[f"B_{player_id}"] = data
            
        recent_games = self._group_by_game(data)
        
        return {
            'raw_data': data,
            'recent': {
                'hits': {
                    'avg': recent_games['hits'].mean(),
                    'median': recent_games['hits'].median(),
                    'last_5': recent_games.head()['hits'].tolist()
                },
                'bases': {
                    'avg': recent_games['total_bases'].mean(),
                    'median': recent_games['total_bases'].median(),
                    'last_5': recent_games.head()['total_bases'].tolist()
                },
                'exit_velocity': recent_games['launch_speed'].mean(),
                'hard_hit_rate': (data['launch_speed'] >= 95).mean()
            },
            'splits': self._calculate_batter_splits(data)
        }
        
    def _calculate_advanced_stats(self, data: pd.DataFrame, prop_type: str) -> Dict:
        """Calculate advanced analytics based on prop type"""
        if prop_type in ['strikeouts', 'earned_runs', 'hits_allowed']:
            return {
                'pitch_mix': self._calculate_pitch_mix(data),
                'zone_profile': self._calculate_zone_profile(data),
                'platoon_splits': self._calculate_platoon_splits(data),
                'pitch_values': self._calculate_pitch_values(data)
            }
        else:
            return {
                'zone_contact': self._calculate_zone_contact(data),
                'pitch_type_value': self._calculate_pitch_type_value(data),
                'quality_of_contact': self._calculate_qoc_metrics(data)
            }
            
    def _group_by_game(self, data: pd.DataFrame) -> pd.DataFrame:
        """Group Statcast data by game"""
        return data.groupby('game_date').agg({
            'strikeouts': 'sum',
            'pitches': 'count',
            'whiff_rate': 'mean',
            'chase_rate': 'mean',
            'hits': 'sum',
            'total_bases': 'sum',
            'launch_speed': 'mean'
        }).sort_index(ascending=False)

# Usage example
async def main():
    collector = MLBDataCollector()
    
    # Get pitcher data
    degrom_data = await collector.get_player_props_data("Jacob deGrom", "strikeouts")
    
    print("\ndeGrom Recent Stats:")
    print(f"Strikeouts Avg: {degrom_data['recent_stats']['strikeouts']['avg']:.1f}")
    print(f"Last 5 Games:", degrom_data['recent_stats']['strikeouts']['last_5'])
    print("\nAdvanced Stats:", degrom_data['advanced_stats']['pitch_mix'])

if __name__ == "__main__":
    asyncio.run(main())