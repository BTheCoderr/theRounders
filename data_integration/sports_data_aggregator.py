import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging
from ..data_scrapers.sports_reference_scraper import SportsReferenceScraper
from ..data_scrapers.additional_scrapers import (
    TennisAbstractScraper,
    EightTwoGamesScraper,
    BaseballGuruScraper
)

class SportsDataAggregator:
    """
    Aggregates and normalizes data from multiple free sports data sources
    """
    
    def __init__(self):
        self.sports_ref = SportsReferenceScraper()
        self.tennis = TennisAbstractScraper()
        self.nba_advanced = EightTwoGamesScraper()
        self.baseball = BaseballGuruScraper()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('SportsDataAggregator')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('aggregator.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def get_nba_team_analysis(self, season: int) -> pd.DataFrame:
        """
        Combines NBA team data from Sports Reference and 82games with advanced analytics
        
        Args:
            season: Year of the season (e.g., 2024 for 2023-24 season)
            
        Returns:
            DataFrame with combined team statistics and advanced metrics
        """
        try:
            # Get basic stats from Sports Reference
            basic_stats = self.sports_ref.get_team_stats('nba', season)
            
            # Get advanced stats from 82games
            season_str = f"{season-1}-{str(season)[-2:]}"
            advanced_stats = self.nba_advanced.get_team_stats('all', season_str)
            
            # Calculate shooting metrics
            basic_stats['efg_pct'] = (basic_stats['FG'] + 0.5 * basic_stats['3P']) / basic_stats['FGA']
            basic_stats['ts_pct'] = basic_stats['PTS'] / (2 * (basic_stats['FGA'] + 0.44 * basic_stats['FTA']))
            basic_stats['three_pt_rate'] = basic_stats['3PA'] / basic_stats['FGA']
            
            # Calculate possession-based metrics
            basic_stats['pace'] = 48 * ((basic_stats['FGA'] + 0.44 * basic_stats['FTA'] + basic_stats['TOV']) / basic_stats['MP'])
            basic_stats['poss'] = basic_stats['pace'] * basic_stats['MP'] / 48
            
            # Calculate Four Factors
            basic_stats['shooting_factor'] = basic_stats['efg_pct']
            basic_stats['turnover_rate'] = basic_stats['TOV'] / basic_stats['poss']
            basic_stats['reb_rate'] = basic_stats['TRB'] / (basic_stats['TRB'] + basic_stats['TRB.1'])
            basic_stats['ft_rate'] = basic_stats['FTA'] / basic_stats['FGA']
            
            # Calculate PIE (Player Impact Estimate) for teams
            basic_stats['pie'] = (
                (basic_stats['PTS'] + basic_stats['FG'] + basic_stats['FT'] - basic_stats['FGA'] - basic_stats['FTA'] +
                basic_stats['DRB'] + basic_stats['ORB'] + basic_stats['AST'] + basic_stats['STL'] + basic_stats['BLK'] -
                basic_stats['PF'] - basic_stats['TOV']) /
                (basic_stats['PTS'] + basic_stats['FG'] + basic_stats['FT'] - basic_stats['FGA'] - basic_stats['FTA'] +
                basic_stats['DRB'] + basic_stats['ORB'] + basic_stats['AST'] + basic_stats['STL'] + basic_stats['BLK'] -
                basic_stats['PF'] - basic_stats['TOV'] +
                basic_stats['PTS.1'] + basic_stats['FG.1'] + basic_stats['FT.1'] - basic_stats['FGA.1'] - basic_stats['FTA.1'] +
                basic_stats['DRB.1'] + basic_stats['ORB.1'] + basic_stats['AST.1'] + basic_stats['STL.1'] + basic_stats['BLK.1'] -
                basic_stats['PF.1'] - basic_stats['TOV.1'])
            )
            
            # Calculate Net Rating components
            basic_stats['ortg'] = 100 * basic_stats['PTS'] / basic_stats['poss']
            basic_stats['drtg'] = 100 * basic_stats['PTS.1'] / basic_stats['poss']
            basic_stats['net_rtg'] = basic_stats['ortg'] - basic_stats['drtg']
            
            # Calculate betting-related metrics
            basic_stats['ats_record'] = self._calculate_ats_record(basic_stats['Team'], season)
            basic_stats['over_under_record'] = self._calculate_over_under_record(basic_stats['Team'], season)
            basic_stats['home_cover_rate'] = self._calculate_home_cover_rate(basic_stats['Team'], season)
            basic_stats['away_cover_rate'] = self._calculate_away_cover_rate(basic_stats['Team'], season)
            basic_stats['avg_margin'] = basic_stats['PTS'] - basic_stats['PTS.1']
            basic_stats['margin_variance'] = self._calculate_margin_variance(basic_stats['Team'], season)
            
            # Calculate rest advantage metrics
            basic_stats['b2b_record'] = self._calculate_b2b_record(basic_stats['Team'], season)
            basic_stats['rest_advantage_record'] = self._calculate_rest_advantage_record(basic_stats['Team'], season)
            
            # Calculate home/away splits
            splits = self._calculate_home_away_splits(basic_stats['Team'], season)
            for key, value in splits.items():
                basic_stats[key] = value
            
            # Merge with advanced stats
            combined_stats = pd.merge(
                basic_stats,
                advanced_stats,
                on='Team',
                how='left',
                suffixes=('_basic', '_advanced')
            )
            
            # Calculate power rankings
            combined_stats['power_rating'] = self._calculate_nba_power_rating(combined_stats)
            
            # Calculate betting power rating (adjusted for recent form and betting metrics)
            combined_stats['betting_power_rating'] = self._calculate_betting_power_rating(combined_stats)
            
            # Sort by power rating
            combined_stats = combined_stats.sort_values('power_rating', ascending=False).reset_index(drop=True)
            
            return combined_stats
            
        except Exception as e:
            self.logger.error(f"Error aggregating NBA team data: {str(e)}")
            raise
            
    def get_nba_player_analysis(self, season: int, min_minutes: int = 500) -> pd.DataFrame:
        """
        Get comprehensive NBA player statistics and analytics
        
        Args:
            season: Year of the season
            min_minutes: Minimum minutes played to be included
            
        Returns:
            DataFrame with player statistics and advanced metrics
        """
        try:
            # Get basic player stats
            basic_stats = self.sports_ref.get_player_stats('nba', season)
            
            # Filter by minimum minutes
            basic_stats = basic_stats[basic_stats['MP'] >= min_minutes]
            
            # Calculate advanced metrics
            basic_stats['efg_pct'] = (basic_stats['FG'] + 0.5 * basic_stats['3P']) / basic_stats['FGA']
            basic_stats['ts_pct'] = basic_stats['PTS'] / (2 * (basic_stats['FGA'] + 0.44 * basic_stats['FTA']))
            
            # Get per-36 minutes stats
            per_36 = basic_stats.copy()
            stats_to_adjust = ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
            for stat in stats_to_adjust:
                if stat in per_36.columns:
                    per_36[f'{stat}_per_36'] = per_36[stat] * 36 / per_36['MP']
            
            # Calculate value metrics
            basic_stats['game_score'] = self._calculate_game_score(basic_stats)
            basic_stats['value_over_replacement'] = self._calculate_vorp(basic_stats)
            
            return basic_stats
            
        except Exception as e:
            self.logger.error(f"Error getting NBA player analysis: {str(e)}")
            raise
            
    def get_nba_matchup_analysis(self, team1: str, team2: str, season: int) -> Dict:
        """
        Analyze matchup between two NBA teams
        
        Args:
            team1: First team name
            team2: Second team name
            season: Season year
            
        Returns:
            Dictionary with matchup analysis
        """
        try:
            # Get team stats
            team_stats = self.get_nba_team_analysis(season)
            
            # Get head-to-head games
            games = self.sports_ref.get_game_scores('nba', season)
            h2h_games = games[
                ((games['Home'] == team1) & (games['Away'] == team2)) |
                ((games['Home'] == team2) & (games['Away'] == team1))
            ]
            
            # Calculate matchup metrics
            team1_stats = team_stats[team_stats['Team'] == team1].iloc[0]
            team2_stats = team_stats[team_stats['Team'] == team2].iloc[0]
            
            # Predict score based on offensive/defensive ratings
            avg_possessions = (team1_stats['pace'] + team2_stats['pace']) / 2
            team1_predicted_score = team1_stats['offensive_rating'] * avg_possessions / 100
            team2_predicted_score = team2_stats['offensive_rating'] * avg_possessions / 100
            
            # Calculate win probability
            point_diff = team1_predicted_score - team2_predicted_score
            win_prob = 1 / (1 + np.exp(-0.4 * point_diff))
            
            return {
                'team1_predicted_score': team1_predicted_score,
                'team2_predicted_score': team2_predicted_score,
                'team1_win_probability': win_prob,
                'head_to_head_games': h2h_games.to_dict('records'),
                'key_matchups': self._analyze_key_matchups(team1_stats, team2_stats),
                'pace_prediction': avg_possessions
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing NBA matchup: {str(e)}")
            raise
            
    def _calculate_nba_power_rating(self, stats: pd.DataFrame) -> pd.Series:
        """Calculate NBA power rating based on various metrics"""
        try:
            components = {
                'win_pct': stats['W'].astype(float) / (stats['W'].astype(float) + stats['L'].astype(float)),
                'point_diff': stats['PTS'].astype(float) - stats['PTS.1'].astype(float),
                'net_rating': stats['offensive_rating'] - stats['defensive_rating'],
                'sos': self._calculate_strength_of_schedule(stats)
            }
            
            # Convert to DataFrame and normalize
            df = pd.DataFrame(components)
            for col in df.columns:
                df[col] = (df[col] - df[col].mean()) / df[col].std()
            
            # Calculate weighted average
            weights = {
                'win_pct': 0.3,
                'point_diff': 0.3,
                'net_rating': 0.25,
                'sos': 0.15
            }
            
            return sum(df[col] * weight for col, weight in weights.items())
            
        except Exception as e:
            self.logger.error(f"Error calculating NBA power rating: {str(e)}")
            raise
            
    def _calculate_game_score(self, stats: pd.DataFrame) -> pd.Series:
        """Calculate John Hollinger's Game Score metric"""
        try:
            return (
                stats['PTS'] 
                + 0.4 * stats['FG'] 
                - 0.7 * stats['FGA'] 
                - 0.4 * (stats['FTA'] - stats['FT'])
                + 0.7 * stats['ORB']
                + 0.3 * stats['DRB']
                + stats['STL']
                + 0.7 * stats['AST']
                + 0.7 * stats['BLK']
                - 0.4 * stats['PF']
                - stats['TOV']
            )
        except Exception as e:
            self.logger.error(f"Error calculating game score: {str(e)}")
            raise
            
    def _calculate_vorp(self, stats: pd.DataFrame) -> pd.Series:
        """Calculate Value Over Replacement Player"""
        try:
            # League average stats per 36 minutes
            lg_pts_per_36 = 20
            lg_trb_per_36 = 8
            lg_ast_per_36 = 4
            
            # Calculate VORP components
            scoring_value = (stats['PTS_per_36'] - lg_pts_per_36) * stats['ts_pct']
            rebounding_value = (stats['TRB_per_36'] - lg_trb_per_36) * 0.5
            playmaking_value = (stats['AST_per_36'] - lg_ast_per_36) * 0.7
            defense_value = (stats['STL'] + stats['BLK']) * 0.5
            
            return (scoring_value + rebounding_value + playmaking_value + defense_value) * stats['MP'] / 36
            
        except Exception as e:
            self.logger.error(f"Error calculating VORP: {str(e)}")
            raise
            
    def _analyze_key_matchups(self, team1_stats: pd.Series, team2_stats: pd.Series) -> List[Dict]:
        """Analyze key matchup factors between two teams"""
        try:
            matchups = []
            
            # Pace matchup
            pace_diff = abs(team1_stats['pace'] - team2_stats['pace'])
            matchups.append({
                'factor': 'Pace',
                'advantage': team1_stats['Team'] if team1_stats['pace'] > team2_stats['pace'] else team2_stats['Team'],
                'significance': 'High' if pace_diff > 3 else 'Medium' if pace_diff > 1 else 'Low'
            })
            
            # Shooting matchup
            efg_diff = team1_stats['efg_pct'] - team2_stats['opp_efg']
            matchups.append({
                'factor': 'Shooting',
                'advantage': team1_stats['Team'] if efg_diff > 0 else team2_stats['Team'],
                'significance': 'High' if abs(efg_diff) > 0.03 else 'Medium' if abs(efg_diff) > 0.01 else 'Low'
            })
            
            # Rebounding matchup
            reb_diff = team1_stats['opp_oreb_pct'] - team2_stats['opp_oreb_pct']
            matchups.append({
                'factor': 'Rebounding',
                'advantage': team1_stats['Team'] if reb_diff < 0 else team2_stats['Team'],
                'significance': 'High' if abs(reb_diff) > 3 else 'Medium' if abs(reb_diff) > 1 else 'Low'
            })
            
            return matchups
            
        except Exception as e:
            self.logger.error(f"Error analyzing key matchups: {str(e)}")
            raise
            
    def get_mlb_historical_analysis(self, season: int) -> pd.DataFrame:
        """
        Gets MLB historical statistics and analysis
        
        Args:
            season: Year of the season
            
        Returns:
            DataFrame with MLB statistics
        """
        try:
            # Create a sample DataFrame for now
            data = {
                'Team': ['NYY', 'BOS', 'LAD', 'HOU', 'ATL'],
                'W': [92, 88, 94, 90, 89],
                'L': [70, 74, 68, 72, 73],
                'R': [780, 760, 800, 770, 750],
                'RA': [650, 680, 620, 640, 660],
                'AVG': [.265, .258, .270, .262, .260],
                'OBP': [.340, .335, .345, .338, .337],
                'SLG': [.445, .440, .450, .442, .441],
                'ERA': [3.50, 3.75, 3.25, 3.45, 3.60],
                'WHIP': [1.20, 1.25, 1.15, 1.22, 1.24]
            }
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.error(f"Error getting MLB historical analysis: {str(e)}")
            return pd.DataFrame()
            
    def get_tennis_player_analysis(self, year: int) -> pd.DataFrame:
        """
        Gets tennis player statistics and analytics
        
        Args:
            year: Year to analyze
            
        Returns:
            DataFrame with tennis player statistics
        """
        try:
            # Create a sample DataFrame for now
            data = {
                'Player': ['Djokovic', 'Alcaraz', 'Medvedev', 'Sinner', 'Rublev'],
                'Rank': [1, 2, 3, 4, 5],
                'Points': [11000, 9000, 7500, 6000, 5000],
                'Tournaments': [14, 16, 18, 17, 20],
                'W': [65, 60, 55, 50, 45],
                'L': [7, 10, 15, 18, 20],
                'Win_PCT': [0.903, 0.857, 0.786, 0.735, 0.692],
                'Sets_Won': [150, 140, 130, 120, 110],
                'Sets_Lost': [30, 35, 40, 45, 50],
                'Games_Won': [1200, 1150, 1100, 1050, 1000],
                'Games_Lost': [800, 850, 900, 950, 1000]
            }
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.error(f"Error getting tennis player analysis: {str(e)}")
            return pd.DataFrame()
            
    def calculate_power_rankings(self, sport: str, season: int) -> pd.DataFrame:
        """
        Calculates power rankings based on available data
        
        Args:
            sport: Sport to analyze ('nba', 'mlb', 'nfl')
            season: Season year
            
        Returns:
            DataFrame with power rankings and components
        """
        try:
            # Get team stats
            stats = self.sports_ref.get_team_stats(sport, season)
            
            # Get game results
            games = self.sports_ref.get_game_scores(sport, season)
            
            # Calculate basic power ranking components
            if sport == 'nba':
                ranking_components = {
                    'win_pct': stats['W'].astype(float) / (stats['W'].astype(float) + stats['L'].astype(float)),
                    'point_diff': stats['PTS'].astype(float) - stats['PTS.1'].astype(float),
                    'sos': self._calculate_strength_of_schedule(games)
                }
            elif sport == 'mlb':
                ranking_components = {
                    'win_pct': stats['W'].astype(float) / (stats['W'].astype(float) + stats['L'].astype(float)),
                    'run_diff': stats['R'].astype(float) - stats['RA'].astype(float),
                    'sos': self._calculate_strength_of_schedule(games)
                }
            elif sport == 'nfl':
                ranking_components = {
                    'win_pct': stats['W'].astype(float) / (stats['W'].astype(float) + stats['L'].astype(float)),
                    'point_diff': stats['PF'].astype(float) - stats['PA'].astype(float),
                    'sos': self._calculate_strength_of_schedule(games)
                }
            
            # Combine components into final ranking
            rankings = pd.DataFrame(ranking_components)
            
            # Normalize each component
            for col in rankings.columns:
                rankings[col] = (rankings[col] - rankings[col].mean()) / rankings[col].std()
            
            # Calculate final power rating
            rankings['power_rating'] = rankings.mean(axis=1)
            
            # Add team names and sort
            rankings['team'] = stats['Team']
            rankings = rankings.sort_values('power_rating', ascending=False).reset_index(drop=True)
            
            return rankings
            
        except Exception as e:
            self.logger.error(f"Error calculating power rankings: {str(e)}")
            raise
            
    def _calculate_strength_of_schedule(self, games: pd.DataFrame) -> pd.Series:
        """Helper method to calculate strength of schedule"""
        # Implementation will vary by sport
        # This is a placeholder that should be customized based on the sport
        return pd.Series([0.5] * len(games))

    def _calculate_ats_record(self, teams: pd.Series, season: int) -> pd.Series:
        """Calculate Against The Spread record for each team"""
        try:
            # Get games and betting lines
            games = self.sports_ref.get_game_scores('nba', season)
            # Add implementation to get historical betting lines
            # Return series of ATS records
            return pd.Series([0.5] * len(teams))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating ATS record: {str(e)}")
            return pd.Series([0.5] * len(teams))
            
    def _calculate_over_under_record(self, teams: pd.Series, season: int) -> pd.Series:
        """Calculate Over/Under record for each team"""
        try:
            # Get games and totals
            games = self.sports_ref.get_game_scores('nba', season)
            # Add implementation to get historical totals
            # Return series of O/U records
            return pd.Series([0.5] * len(teams))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating O/U record: {str(e)}")
            return pd.Series([0.5] * len(teams))
            
    def _calculate_home_cover_rate(self, teams: pd.Series, season: int) -> pd.Series:
        """Calculate home games cover rate"""
        try:
            # Implementation here
            return pd.Series([0.5] * len(teams))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating home cover rate: {str(e)}")
            return pd.Series([0.5] * len(teams))
            
    def _calculate_away_cover_rate(self, teams: pd.Series, season: int) -> pd.Series:
        """Calculate away games cover rate"""
        try:
            # Implementation here
            return pd.Series([0.5] * len(teams))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating away cover rate: {str(e)}")
            return pd.Series([0.5] * len(teams))
            
    def _calculate_margin_variance(self, teams: pd.Series, season: int) -> pd.Series:
        """Calculate variance in margin of victory/defeat"""
        try:
            games = self.sports_ref.get_game_scores('nba', season)
            # Calculate variance in point differential for each team
            return pd.Series([10.0] * len(teams))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating margin variance: {str(e)}")
            return pd.Series([10.0] * len(teams))
            
    def _calculate_b2b_record(self, teams: pd.Series, season: int) -> pd.Series:
        """Calculate record in back-to-back games"""
        try:
            # Implementation here
            return pd.Series(['0-0'] * len(teams))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating B2B record: {str(e)}")
            return pd.Series(['0-0'] * len(teams))
            
    def _calculate_rest_advantage_record(self, teams: pd.Series, season: int) -> pd.Series:
        """Calculate record when having rest advantage"""
        try:
            # Implementation here
            return pd.Series(['0-0'] * len(teams))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating rest advantage record: {str(e)}")
            return pd.Series(['0-0'] * len(teams))
            
    def _calculate_home_away_splits(self, teams: pd.Series, season: int) -> Dict[str, pd.Series]:
        """Calculate home/away splits for various metrics"""
        try:
            games = self.sports_ref.get_game_scores('nba', season)
            # Calculate splits
            return {
                'home_win_pct': pd.Series([0.5] * len(teams)),
                'away_win_pct': pd.Series([0.5] * len(teams)),
                'home_pts_avg': pd.Series([110.0] * len(teams)),
                'away_pts_avg': pd.Series([105.0] * len(teams))
            }
        except Exception as e:
            self.logger.error(f"Error calculating home/away splits: {str(e)}")
            return {
                'home_win_pct': pd.Series([0.5] * len(teams)),
                'away_win_pct': pd.Series([0.5] * len(teams)),
                'home_pts_avg': pd.Series([110.0] * len(teams)),
                'away_pts_avg': pd.Series([105.0] * len(teams))
            }
            
    def _calculate_betting_power_rating(self, stats: pd.DataFrame) -> pd.Series:
        """Calculate power rating adjusted for betting factors"""
        try:
            components = {
                'power_rating': stats['power_rating'],
                'ats_strength': (stats['ats_record'] - 0.5) * 10,
                'recent_form': self._calculate_recent_form(stats),
                'rest_factor': self._calculate_rest_factor(stats)
            }
            
            # Convert to DataFrame and normalize
            df = pd.DataFrame(components)
            for col in df.columns:
                df[col] = (df[col] - df[col].mean()) / df[col].std()
            
            # Calculate weighted average
            weights = {
                'power_rating': 0.4,
                'ats_strength': 0.3,
                'recent_form': 0.2,
                'rest_factor': 0.1
            }
            
            return sum(df[col] * weight for col, weight in weights.items())
            
        except Exception as e:
            self.logger.error(f"Error calculating betting power rating: {str(e)}")
            raise
            
    def _calculate_recent_form(self, stats: pd.DataFrame) -> pd.Series:
        """Calculate recent form rating"""
        try:
            # Implementation here
            return pd.Series([0.0] * len(stats))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating recent form: {str(e)}")
            return pd.Series([0.0] * len(stats))
            
    def _calculate_rest_factor(self, stats: pd.DataFrame) -> pd.Series:
        """Calculate rest factor rating"""
        try:
            # Implementation here
            return pd.Series([0.0] * len(stats))  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating rest factor: {str(e)}")
            return pd.Series([0.0] * len(stats)) 