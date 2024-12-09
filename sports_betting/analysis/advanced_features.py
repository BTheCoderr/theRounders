import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from loguru import logger
import nfl_data_py as nfl

class AdvancedFeatureEngineering:
    def __init__(self):
        self.feature_sets = {
            'NFL': NFLFeatures(),
            'NBA': NBAFeatures(),
            'NHL': NHLFeatures(),
            'NCAAB': NCAABFeatures(),
            'MLB': MLBFeatures()
        }
        
    def create_features(self, data: Dict, sport: str) -> pd.DataFrame:
        """Create sport-specific features"""
        try:
            # Convert dict to DataFrame if needed
            if isinstance(data, dict):
                data = pd.DataFrame(data)
            
            # Create sport-specific features
            if sport == 'NFL':
                return self.feature_sets[sport].create_features(data)
            elif sport == 'NBA':
                return self.feature_sets[sport].create_features(data)
            # ... handle other sports ...
            
        except Exception as e:
            logger.error(f"Error creating features for {sport}: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

class NFLFeatures:
    def __init__(self):
        logger.info("Initializing NFL Features Calculator")
        # Load the data when initializing
        self.pbp_data = nfl.import_pbp_data([2021, 2022, 2023, 2024])
        self.weekly_data = nfl.import_weekly_data([2021, 2022, 2023, 2024])
        # TODO: Fix roster data import
        # self.roster_data = nfl.import_rosters([2021, 2022, 2023, 2024])
        
        # Print columns to debug what's available
        logger.info("Available columns in weekly data:")
        logger.info(self.weekly_data.columns)
        
        self.league_averages = self._get_league_averages()
        self.required_columns = {
            'pass': ['pass_yards', 'attempts', 'completions', 'pass_tds'],
            'rush': ['rush_yards', 'rush_attempts', 'rush_tds'],
            'defense': ['points_allowed', 'sacks', 'interceptions']
        }
        
    def _get_league_averages(self) -> Dict:
        """Fetch league averages from weekly data"""
        try:
            return {
                'passing_yards': self.weekly_data['passing_yards'].mean(),
                'rushing_yards': self.weekly_data['rushing_yards'].mean(),
                'passing_tds': self.weekly_data['passing_tds'].mean(),
                'rushing_tds': self.weekly_data['rushing_tds'].mean()
            }
        except KeyError as e:
            logger.error(f"Error loading league averages: {str(e)}")
            return self._get_fallback_averages()
            
    def _validate_data(self, data: pd.DataFrame, category: str) -> bool:
        """Validate required columns are present"""
        missing_cols = [col for col in self.required_columns[category] 
                       if col not in data.columns]
        
        if missing_cols:
            logger.warning(f"Missing required columns for {category}: {missing_cols}")
            return False
        return True
        
    def _calculate_dvoa(self, data: Dict, play_type: str) -> float:
        """Calculate DVOA (Defense-adjusted Value Over Average)"""
        try:
            # Convert dict to DataFrame if needed
            if isinstance(data, dict):
                data = pd.DataFrame(data)
            
            if play_type == 'pass':
                if 'passing_yards' not in data.columns:
                    logger.error("Missing 'passing_yards' column for pass DVOA calculation")
                    return 0.0
                baseline = self.league_averages.get('passing_yards', 0)
                actual = data['passing_yards'].mean()
            elif play_type == 'rush':
                if 'rushing_yards' not in data.columns:
                    logger.error("Missing 'rushing_yards' column for rush DVOA calculation")
                    return 0.0
                baseline = self.league_averages.get('rushing_yards', 0)
                actual = data['rushing_yards'].mean()
            elif play_type == 'defense':
                logger.error("Defense play type not implemented")
                return 0.0
            else:
                raise ValueError(f"Invalid play type: {play_type}")
            
            if baseline == 0:
                logger.error(f"Baseline for {play_type} is zero, cannot calculate DVOA")
                return 0.0
            
            dvoa = ((actual - baseline) / baseline) * 100
            return dvoa
            
        except Exception as e:
            logger.error(f"Error calculating DVOA for {play_type}: {str(e)}")
            return 0.0
        
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create NFL-specific features"""
        features = pd.DataFrame()
        
        try:
            # Basic offensive metrics
            if 'passing_yards' in data.columns and 'rushing_yards' in data.columns:
                features['total_yards'] = data['passing_yards'] + data['rushing_yards']
            
            # Passing efficiency
            if 'completions' in data.columns and 'attempts' in data.columns:
                features['completion_pct'] = data['completions'] / data['attempts']
            
            # Scoring efficiency
            if 'passing_tds' in data.columns and 'rushing_tds' in data.columns:
                features['total_tds'] = data['passing_tds'] + data['rushing_tds']
            
            # EPA metrics
            if 'passing_epa' in data.columns and 'rushing_epa' in data.columns:
                features['total_epa'] = data['passing_epa'] + data['rushing_epa']
            
            # Advanced stats (only if available)
            if 'air_yards_share' in data.columns:
                features['air_yards_share'] = data['air_yards_share']
            
            if 'wopr' in data.columns:
                features['wopr'] = data['wopr']
            
            return features
        
        except Exception as e:
            logger.error(f"Error creating features: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def _get_fallback_averages(self):
        # Return some reasonable default values
        return {
            'points': 23.0,  # NFL average points per game
            # ... other default values
        }

class NBAFeatures:
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create team-level features from player stats"""
        features = pd.DataFrame()
        
        try:
            # Group by team and game to get team-level stats
            team_stats = data.groupby(['recent_team', 'season', 'week']).agg({
                # Offensive stats
                'passing_yards': 'sum',
                'rushing_yards': 'sum',
                'passing_tds': 'sum',
                'rushing_tds': 'sum',
                'interceptions': 'sum',
                'sacks': 'sum',
                
                # Efficiency stats
                'passing_epa': 'mean',
                'rushing_epa': 'mean',
                'completions': 'sum',
                'attempts': 'sum',
                
                # Advanced stats if available
                'air_yards_share': 'mean',
                'wopr': 'mean'
            }).reset_index()
            
            # Calculate derived metrics
            features['total_yards'] = team_stats['passing_yards'] + team_stats['rushing_yards']
            features['total_tds'] = team_stats['passing_tds'] + team_stats['rushing_tds']
            features['yards_per_play'] = features['total_yards'] / (team_stats['attempts'] + team_stats['completions'])
            features['completion_rate'] = team_stats['completions'] / team_stats['attempts']
            features['turnover_rate'] = team_stats['interceptions'] / team_stats['attempts']
            features['sack_rate'] = team_stats['sacks'] / team_stats['attempts']
            
            # Offensive efficiency
            features['total_epa'] = team_stats['passing_epa'] + team_stats['rushing_epa']
            
            # Add any available advanced metrics
            if 'air_yards_share' in team_stats.columns:
                features['air_yards_share'] = team_stats['air_yards_share']
            if 'wopr' in team_stats.columns:
                features['wopr'] = team_stats['wopr']
            
            return features
            
        except Exception as e:
            logger.error(f"Error creating team features: {str(e)}")
            return pd.DataFrame()

    def _calculate_rolling_averages(self, data: pd.DataFrame, window: int = 4) -> pd.DataFrame:
        """Calculate rolling averages for key metrics"""
        try:
            rolling_stats = data.sort_values(['recent_team', 'season', 'week']).groupby('recent_team').rolling(window=window).mean()
            return rolling_stats
        except Exception as e:
            logger.error(f"Error calculating rolling averages: {str(e)}")
            return pd.DataFrame()

class MLBFeatures:
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame()
        
        # Pitching metrics
        features['fip'] = self._calculate_fip(data)
        features['xfip'] = self._calculate_xfip(data)
        
        # Batting metrics
        features['woba'] = self._calculate_woba(data)
        features['babip'] = self._calculate_babip(data)
        
        return features 

class NCAABFeatures:
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame()
        
        # Advanced metrics
        features['offensive_efficiency'] = self._calculate_off_efficiency(data)
        features['defensive_efficiency'] = self._calculate_def_efficiency(data)
        features['tempo'] = self._calculate_tempo(data)
        
        # Team specific
        features['experience_factor'] = self._calculate_experience(data)
        features['home_court_advantage'] = self._calculate_home_advantage(data)
        
        # Tournament metrics (if applicable)
        features['tournament_exp'] = self._calculate_tournament_exp(data)
        
        return features

class NHLFeatures:
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame()
        
        # Advanced metrics
        features['corsi'] = self._calculate_corsi(data)
        features['fenwick'] = self._calculate_fenwick(data)
        features['pdo'] = self._calculate_pdo(data)
        
        # Special teams
        features['power_play_pct'] = data['pp_goals'] / data['pp_opportunities']
        features['penalty_kill_pct'] = 1 - (data['pk_goals_against'] / data['times_shorthanded'])
        
        # Goalie metrics
        features['save_pct'] = self._calculate_save_pct(data)
        features['goals_saved_above_avg'] = self._calculate_gsaa(data)
        
        return features