import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import leaguedashteamstats, leaguedashplayerstats

class SportsDataCollector:
    def __init__(self):
        self.nba_teams = None
    
    def collect_nba_data(self, year=datetime.now().year):
        """Collect NBA team data for specified year"""
        # Get team stats using nba_api
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season=f"{year}-{str(year + 1)[-2:]}",  # Format: "2023-24"
            per_mode_detailed='PerGame',
            measure_type_detailed_defense='Base',
            season_type_all_star='Regular Season'
        )
        
        # Convert to DataFrame
        df = stats.get_data_frames()[0]
        
        # Select and rename relevant columns
        return df[[
            'TEAM_NAME',
            'W',
            'L',
            'PTS',
            'OPP_PTS',
            'PACE',
            'OFF_RATING',
            'DEF_RATING'
        ]].rename(columns={
            'TEAM_NAME': 'name',
            'W': 'wins',
            'L': 'losses',
            'PTS': 'points_per_game',
            'OPP_PTS': 'opp_points_per_game',
            'PACE': 'pace',
            'OFF_RATING': 'offensive_rating',
            'DEF_RATING': 'defensive_rating'
        })

    def collect_nba_player_data(self, year=datetime.now().year):
        """Collect NBA player statistics for specified year"""
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=f"{year}-{str(year + 1)[-2:]}",
            per_mode_detailed='PerGame',
            measure_type_detailed_defense='Base',
            season_type_all_star='Regular Season'
        )
        
        df = player_stats.get_data_frames()[0]
        
        return df[[
            'PLAYER_NAME',
            'TEAM_ABBREVIATION',
            'GP',
            'MIN',
            'PTS',
            'REB',
            'AST',
            'STL',
            'BLK',
            'FG_PCT',
            'FG3_PCT',
            'FT_PCT'
        ]].rename(columns={
            'PLAYER_NAME': 'name',
            'TEAM_ABBREVIATION': 'team',
            'GP': 'games_played',
            'MIN': 'minutes',
            'PTS': 'points',
            'REB': 'rebounds',
            'AST': 'assists',
            'STL': 'steals',
            'BLK': 'blocks',
            'FG_PCT': 'fg_percentage',
            'FG3_PCT': 'three_pt_percentage',
            'FT_PCT': 'ft_percentage'
        })

    def create_nba_rankings(self, team_data, player_data):
        """Create comprehensive NBA rankings using both team and player data"""
        # Calculate team strength score
        team_rankings = team_data.copy()
        team_rankings['strength_score'] = (
            team_rankings['offensive_rating'] - 
            team_rankings['defensive_rating'] + 
            (team_rankings['wins'] / (team_rankings['wins'] + team_rankings['losses'])) * 100
        )
        
        # Calculate player impact scores
        player_rankings = player_data.copy()
        player_rankings['impact_score'] = (
            player_rankings['points'] + 
            player_rankings['rebounds'] * 1.2 + 
            player_rankings['assists'] * 1.5 + 
            player_rankings['steals'] * 2 + 
            player_rankings['blocks'] * 2
        ) * (player_rankings['minutes'] / 48)  # Normalize by minutes played
        
        return {
            'team_rankings': team_rankings.sort_values('strength_score', ascending=False),
            'player_rankings': player_rankings.sort_values('impact_score', ascending=False)
        }

    # Add similar methods for NFL and NHL