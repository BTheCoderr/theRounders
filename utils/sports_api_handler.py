"""Unified sports API handler integrating multiple data sources."""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from nba_api.stats.endpoints import leaguegamefinder, playergamelog
from espn_api.basketball import Basketball
from utils.api_config import APIConfig
import pandas as pd

logger = logging.getLogger(__name__)

class SportsAPIHandler:
    """Unified handler for multiple sports data APIs."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.espn_nba = Basketball()  # ESPN API
        
    def get_nba_games(self, date: Optional[datetime] = None) -> List[Dict]:
        """Get NBA games from multiple sources and combine data."""
        games = []
        
        try:
            # SportRadar data
            sr_games = self.api_config.make_api_call(
                api_name='nba',
                endpoint=f'http://api.sportradar.us/nba/trial/v7/en/games/{date.year}/{date.month}/{date.day}/schedule.json'
            )
            games.extend(self._parse_sportradar_games(sr_games))
            
            # NBA API data
            nba_games = leaguegamefinder.LeagueGameFinder(
                date_from_nullable=date.strftime('%m/%d/%Y'),
                date_to_nullable=date.strftime('%m/%d/%Y')
            ).get_normalized_dict()
            games.extend(self._parse_nba_api_games(nba_games))
            
            # ESPN API data
            espn_games = self.espn_nba.get_games(date)
            games.extend(self._parse_espn_games(espn_games))
            
        except Exception as e:
            logger.error(f"Error fetching NBA games: {str(e)}")
        
        return self._merge_game_data(games)
    
    def get_odds(self, sport: str, game_id: str) -> Dict:
        """Get odds from multiple sources."""
        odds = {}
        
        try:
            # Pinnacle odds
            pinnacle_odds = self.api_config.make_api_call(
                api_name='odds_regular',
                endpoint=f'https://api.pinnacle.com/v1/odds/{sport}/{game_id}'
            )
            odds['pinnacle'] = self._parse_pinnacle_odds(pinnacle_odds)
            
            # BetMGM odds
            betmgm_odds = self.api_config.make_api_call(
                api_name='odds_regular',
                endpoint=f'https://sports.betmgm.com/api/v2/sports/{sport}/events/{game_id}/markets'
            )
            odds['betmgm'] = self._parse_betmgm_odds(betmgm_odds)
            
            # DraftKings odds
            dk_odds = self.api_config.make_api_call(
                api_name='odds_regular',
                endpoint=f'https://api.draftkings.com/odds/v1/sports/{sport}/events/{game_id}/odds'
            )
            odds['draftkings'] = self._parse_draftkings_odds(dk_odds)
            
        except Exception as e:
            logger.error(f"Error fetching odds: {str(e)}")
        
        return odds
    
    def get_player_props(self, sport: str, game_id: str) -> Dict:
        """Get player props from multiple sources."""
        props = {}
        
        try:
            # Pinnacle props
            pinnacle_props = self.api_config.make_api_call(
                api_name='odds_props',
                endpoint=f'https://api.pinnacle.com/v1/odds/{sport}/{game_id}/special'
            )
            props['pinnacle'] = self._parse_pinnacle_props(pinnacle_props)
            
            # BetMGM props
            betmgm_props = self.api_config.make_api_call(
                api_name='odds_props',
                endpoint=f'https://sports.betmgm.com/api/v2/sports/{sport}/events/{game_id}/player-props'
            )
            props['betmgm'] = self._parse_betmgm_props(betmgm_props)
            
            # DraftKings props
            dk_props = self.api_config.make_api_call(
                api_name='odds_props',
                endpoint=f'https://api.draftkings.com/odds/v1/sports/{sport}/events/{game_id}/player-props'
            )
            props['draftkings'] = self._parse_draftkings_props(dk_props)
            
        except Exception as e:
            logger.error(f"Error fetching player props: {str(e)}")
        
        return props
    
    def get_player_stats(self, player_id: str, season: str) -> pd.DataFrame:
        """Get player statistics from multiple sources."""
        stats = pd.DataFrame()
        
        try:
            # NBA API stats
            nba_stats = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season
            ).get_normalized_dict()
            stats = pd.concat([stats, pd.DataFrame(nba_stats['PlayerGameLog'])])
            
            # ESPN API stats
            espn_stats = self.espn_nba.get_player_stats(player_id)
            stats = pd.concat([stats, pd.DataFrame(espn_stats)])
            
            # SportRadar stats
            sr_stats = self.api_config.make_api_call(
                api_name='nba',
                endpoint=f'http://api.sportradar.us/nba/trial/v7/en/players/{player_id}/profile.json'
            )
            stats = pd.concat([stats, pd.DataFrame(self._parse_sportradar_stats(sr_stats))])
            
        except Exception as e:
            logger.error(f"Error fetching player stats: {str(e)}")
        
        return stats.drop_duplicates()
    
    def _parse_sportradar_games(self, data: Dict) -> List[Dict]:
        """Parse SportRadar game data."""
        games = []
        if 'games' in data:
            for game in data['games']:
                games.append({
                    'source': 'sportradar',
                    'game_id': game.get('id'),
                    'home_team': game.get('home', {}).get('name'),
                    'away_team': game.get('away', {}).get('name'),
                    'start_time': game.get('scheduled'),
                    'venue': game.get('venue', {}).get('name'),
                    'status': game.get('status')
                })
        return games
    
    def _parse_nba_api_games(self, data: Dict) -> List[Dict]:
        """Parse NBA API game data."""
        games = []
        if 'LeagueGameFinder' in data:
            for game in data['LeagueGameFinder']:
                games.append({
                    'source': 'nba_api',
                    'game_id': game.get('GAME_ID'),
                    'home_team': game.get('HOME_TEAM_NAME'),
                    'away_team': game.get('VISITOR_TEAM_NAME'),
                    'start_time': game.get('GAME_DATE'),
                    'venue': game.get('ARENA'),
                    'status': game.get('GAME_STATUS')
                })
        return games
    
    def _parse_espn_games(self, games: List) -> List[Dict]:
        """Parse ESPN API game data."""
        return [{
            'source': 'espn',
            'game_id': game.id,
            'home_team': game.home_team.name,
            'away_team': game.away_team.name,
            'start_time': game.date,
            'venue': game.venue,
            'status': game.status
        } for game in games]
    
    def _merge_game_data(self, games: List[Dict]) -> List[Dict]:
        """Merge game data from multiple sources."""
        merged = {}
        
        for game in games:
            game_id = game['game_id']
            if game_id not in merged:
                merged[game_id] = game
            else:
                # Update with additional information from other sources
                merged[game_id].update({
                    k: v for k, v in game.items()
                    if k != 'source' and v is not None
                })
                merged[game_id]['sources'] = merged[game_id].get('sources', []) + [game['source']]
        
        return list(merged.values())
    
    def _parse_pinnacle_odds(self, data: Dict) -> Dict:
        """Parse Pinnacle odds data."""
        # Implementation depends on Pinnacle API response structure
        pass
    
    def _parse_betmgm_odds(self, data: Dict) -> Dict:
        """Parse BetMGM odds data."""
        # Implementation depends on BetMGM API response structure
        pass
    
    def _parse_draftkings_odds(self, data: Dict) -> Dict:
        """Parse DraftKings odds data."""
        # Implementation depends on DraftKings API response structure
        pass
    
    def _parse_sportradar_stats(self, data: Dict) -> Dict:
        """Parse SportRadar player statistics."""
        # Implementation depends on SportRadar API response structure
        pass 