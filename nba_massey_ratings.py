import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sports_apis import SportsAPI, MasseyRatings
import logging
import time
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams
from typing import Dict, List, Tuple
from massey_ratings_base import MasseyRatings, Game

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NBAMasseyRatings(MasseyRatings):
    """NBA-specific implementation of Massey Ratings."""
    
    # Sport-specific constants
    HOME_ADVANTAGE = 3.5  # NBA home court advantage in points
    MARGIN_FACTOR = 0.8   # Factor to convert rating differences to predicted margins
    
    def __init__(self, min_games: int = 10, use_preseason: bool = True):
        """Initialize NBA Massey Ratings."""
        self.team_name_mapping = {
            'LA Clippers': 'Los Angeles Clippers',
            'LA Lakers': 'Los Angeles Lakers',
            'Team Tamika': None,
            'Team Pau': None,
            'Team Jalen': None,
            'Team Stephen A': None,
            'East NBA All Stars East': None,
            'Flamengo Flamengo': None,
            "Ra'anana Maccabi Ra'anana": None,
            'New Zealand Breakers': None,
            'Cairns Taipans': None,
            'Madrid Baloncesto': None
        }
        
        # Get all NBA teams
        all_teams = teams.get_teams()
        team_names = [team['full_name'] for team in all_teams]
        self.teams_dict = {team['full_name']: team['id'] for team in all_teams}
        
        # Initialize base class
        super().__init__(
            teams=team_names,
            min_games=min_games,
            use_preseason=use_preseason,
            score_transform=self._nba_score_transform
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f"Initialized NBA Massey Ratings with {len(team_names)} teams")
        
        # Log available teams for debugging
        self.logger.debug("Available NBA teams:")
        for team_name in sorted(self.teams_dict.keys()):
            self.logger.debug(f"  - {team_name}")
        
        self.preseason_ratings = {}
        self.sos_ratings = {}
        self.binary_mode = False  # For BCS-style ratings
        
        if use_preseason:
            self._initialize_preseason_ratings()
    
    def _nba_score_transform(self, margin: float) -> float:
        """NBA-specific score transformation."""
        # Use sigmoid with NBA-appropriate scaling
        return 2 / (1 + np.exp(-margin/10)) - 1
    
    def get_home_advantage(self) -> float:
        """Get NBA home court advantage value."""
        return self.HOME_ADVANTAGE
    
    def get_margin_factor(self) -> float:
        """Get NBA margin prediction factor."""
        return self.MARGIN_FACTOR
    
    def _initialize_preseason_ratings(self):
        """Initialize preseason ratings based on previous NBA season."""
        try:
            # Get previous season's final standings
            prev_year = datetime.now().year - 1
            prev_season = f"{prev_year-1}-{str(prev_year)[2:]}"
            
            gamefinder = leaguegamefinder.LeagueGameFinder(
                season_nullable=prev_season,
                league_id_nullable='00'
            )
            time.sleep(2)  # Rate limiting
            
            games_df = gamefinder.get_data_frames()[0]
            
            # Calculate team statistics
            team_stats = games_df.groupby('TEAM_NAME').agg({
                'WL': lambda x: (x == 'W').mean(),
                'PLUS_MINUS': 'mean'
            }).reset_index()
            
            # Normalize to rating scale
            max_plus_minus = team_stats['PLUS_MINUS'].max()
            min_plus_minus = team_stats['PLUS_MINUS'].min()
            
            for _, row in team_stats.iterrows():
                normalized_rating = 50 + (
                    25 * (row['PLUS_MINUS'] - min_plus_minus) / 
                    (max_plus_minus - min_plus_minus)
                )
                self.preseason_ratings[row['TEAM_NAME']] = normalized_rating
                
        except Exception as e:
            self.logger.error(f"Error initializing preseason ratings: {str(e)}")
            self.preseason_ratings = {team: 50.0 for team in self.teams}
    
    def _get_team_id(self, team_name: str) -> int:
        """Get NBA team ID from team name."""
        mapped_name = self.team_name_mapping.get(team_name, team_name)
        if mapped_name is None:
            self.logger.warning(f"Team {team_name} is mapped to None (excluded)")
            return None
        team_id = self.teams_dict.get(mapped_name)
        if team_id is None:
            self.logger.warning(f"Team not found: {team_name} (mapped to {mapped_name})")
        return team_id
    
    def load_season_games(self):
        """Load current NBA season games."""
        try:
            # Get current season
            current_year = datetime.now().year
            season = f"{current_year-1 if datetime.now().month < 7 else current_year}-{str(current_year if datetime.now().month < 7 else current_year+1)[2:]}"
            
            # Get game data
            gamefinder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                league_id_nullable='00'
            )
            time.sleep(2)
            
            games_df = gamefinder.get_data_frames()[0]
            
            # Process each unique game
            games_df['GAME_KEY'] = games_df['GAME_ID'] + games_df['TEAM_ID'].astype(str)
            unique_games = games_df.drop_duplicates('GAME_ID')
            
            for _, game in unique_games.iterrows():
                game_data = games_df[games_df['GAME_ID'] == game['GAME_ID']]
                if len(game_data) != 2:
                    continue
                    
                home_game = game_data[game_data['MATCHUP'].str.contains('vs')].iloc[0]
                away_game = game_data[game_data['MATCHUP'].str.contains('@')].iloc[0]
                
                home_team = self.team_name_mapping.get(home_game['TEAM_NAME'], 
                                                     home_game['TEAM_NAME'])
                away_team = self.team_name_mapping.get(away_game['TEAM_NAME'], 
                                                     away_game['TEAM_NAME'])
                
                if home_team and away_team:
                    self.add_game(
                        team_a=home_team,
                        team_b=away_team,
                        score_a=home_game['PTS'],
                        score_b=away_game['PTS'],
                        is_home_a=True,
                        date=str(game['GAME_DATE'])
                    )
            
            self.logger.info(f"Loaded {len(self.games)} NBA games")
            
        except Exception as e:
            self.logger.error(f"Error loading NBA games: {str(e)}")
    
    def calculate_sos(self) -> Dict[str, float]:
        """
        Calculate strength of schedule for each team.
        Returns dictionary of team: SOS rating pairs.
        """
        ratings = self.calculate_ratings()
        if not ratings:
            return {}
            
        sos = {}
        for team in ratings.keys():
            opponent_ratings = []
            for game in self.games:
                if game.team_a == team and game.team_b in ratings:
                    opponent_ratings.append(ratings[game.team_b])
                elif game.team_b == team and game.team_a in ratings:
                    opponent_ratings.append(ratings[game.team_a])
            
            if opponent_ratings:
                sos[team] = sum(opponent_ratings) / len(opponent_ratings)
            else:
                sos[team] = 0.0
        
        # Normalize SOS ratings
        min_sos = min(sos.values())
        max_sos = max(sos.values())
        self.sos_ratings = {
            team: 100 * (rating - min_sos) / (max_sos - min_sos)
            for team, rating in sos.items()
        }
        
        return self.sos_ratings
    
    def calculate_conference_strengths(self) -> Dict[str, float]:
        """
        Calculate implicit conference strengths based on inter-conference games.
        """
        # Map teams to conferences
        conference_map = {
            'Eastern': [
                'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
                'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers',
                'Miami Heat', 'Milwaukee Bucks', 'New York Knicks', 'Orlando Magic',
                'Philadelphia 76ers', 'Toronto Raptors', 'Washington Wizards'
            ],
            'Western': [
                'Dallas Mavericks', 'Denver Nuggets', 'Golden State Warriors', 'Houston Rockets',
                'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 
                'Minnesota Timberwolves', 'New Orleans Pelicans', 'Oklahoma City Thunder',
                'Phoenix Suns', 'Portland Trail Blazers', 'Sacramento Kings', 
                'San Antonio Spurs', 'Utah Jazz'
            ]
        }
        
        # Track inter-conference games
        conf_stats = {'Eastern': {'wins': 0, 'games': 0}, 'Western': {'wins': 0, 'games': 0}}
        
        for game in self.games:
            team_a_conf = next((conf for conf, teams in conference_map.items() 
                              if game.team_a in teams), None)
            team_b_conf = next((conf for conf, teams in conference_map.items() 
                              if game.team_b in teams), None)
            
            if team_a_conf and team_b_conf and team_a_conf != team_b_conf:
                conf_stats[team_a_conf]['games'] += 1
                conf_stats[team_b_conf]['games'] += 1
                if game.score_a > game.score_b:
                    conf_stats[team_a_conf]['wins'] += 1
                else:
                    conf_stats[team_b_conf]['wins'] += 1
        
        # Calculate conference ratings
        return {
            conf: stats['wins'] / stats['games'] if stats['games'] > 0 else 0.5
            for conf, stats in conf_stats.items()
        }
    
    def calculate_ratings_binary(self) -> Dict[str, float]:
        """
        Calculate BCS-style ratings using only wins/losses (no margin of victory).
        """
        self.binary_mode = True
        ratings = self.calculate_ratings()  # Will use binary mode
        self.binary_mode = False
        return ratings
    
    def calculate_ratings(self):
        """Calculate Massey ratings for all teams."""
        if len(self.games) < self.min_games * len(self.teams) / 2:
            # Early season: blend with preseason ratings
            current_ratings = self._calculate_ratings_core()
            if not current_ratings:
                return self.preseason_ratings if self.use_preseason else {}
            
            # Determine blend factor based on games played
            games_weight = min(1.0, len(self.games) / (self.min_games * len(self.teams)))
            
            blended_ratings = {}
            for team in self.teams:
                if team in current_ratings and team in self.preseason_ratings:
                    blended_ratings[team] = (
                        games_weight * current_ratings[team] +
                        (1 - games_weight) * self.preseason_ratings[team]
                    )
                elif team in current_ratings:
                    blended_ratings[team] = current_ratings[team]
                elif team in self.preseason_ratings:
                    blended_ratings[team] = self.preseason_ratings[team]
            
            return blended_ratings
        else:
            # Enough games played: use current ratings only
            return self._calculate_ratings_core()
    
    def _check_matrix_rank(self, X: np.ndarray) -> bool:
        """
        Check if matrix X has full column rank.
        Returns True if matrix has full rank (no null vectors).
        """
        return np.linalg.matrix_rank(X) == X.shape[1]
    
    def _calculate_pseudo_inverse(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate the pseudo-inverse of X using SVD for better numerical stability.
        """
        return np.linalg.pinv(X)
    
    def _build_design_matrix(self, teams_with_min_games: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build the design matrix X and response vector y according to Massey's formulation.
        
        Returns:
            X: Design matrix where each row represents a game and columns represent teams
            y: Response vector of point differentials
        """
        n_teams = len(teams_with_min_games)
        team_indices = {team: i for i, team in enumerate(teams_with_min_games)}
        
        # Initialize matrices
        n_games = len(self.games)
        X = np.zeros((n_games, n_teams))
        y = np.zeros(n_games)
        
        # Build matrices using indicator functions
        for i, game in enumerate(self.games):
            if game.team_a in team_indices and game.team_b in team_indices:
                # Set indicator functions: +1 for team_a, -1 for team_b
                i_a = team_indices[game.team_a]
                i_b = team_indices[game.team_b]
                X[i, i_a] = 1
                X[i, i_b] = -1
                
                # Set response variable (point differential)
                if self.binary_mode:
                    y[i] = 1 if game.score_a > game.score_b else -1
                else:
                    margin = game.score_a - game.score_b
                    y[i] = self._nba_score_transform(margin)
                    
                    # Apply home court adjustment
                    if hasattr(game, 'is_home_a') and game.is_home_a:
                        y[i] -= self.HOME_ADVANTAGE
                    elif hasattr(game, 'is_home_b') and game.is_home_b:
                        y[i] += self.HOME_ADVANTAGE
        
        return X, y
    
    def _check_matrix_properties(self, X: np.ndarray) -> Tuple[bool, bool, float]:
        """
        Check matrix properties according to Massey's theorems.
        
        Returns:
            has_full_rank: Whether matrix has full column rank
            has_null_vector: Whether matrix has null vectors
            condition_number: Condition number of X^T X
        """
        # Check rank (Theorem 2.2)
        rank = np.linalg.matrix_rank(X)
        has_full_rank = rank == X.shape[1]
        
        # Check for null vectors (Definition 2.3)
        # A null vector v ≠ 0 such that Av = 0
        XtX = X.T @ X
        eigenvals = np.linalg.eigvals(XtX)
        has_null_vector = np.any(np.abs(eigenvals) < 1e-10)
        
        # Calculate condition number
        condition_number = np.linalg.cond(XtX)
        
        return has_full_rank, has_null_vector, condition_number
    
    def _verify_hessian_positive_definite(self, X: np.ndarray) -> bool:
        """
        Verify that the Hessian matrix H = 2X^T X is positive definite.
        This ensures we have found a minimum (Massey's proof).
        """
        H = 2 * (X.T @ X)
        eigenvals = np.linalg.eigvals(H)
        return np.all(eigenvals > 0)
    
    def _calculate_ratings_core(self):
        """
        Core rating calculation using Massey's least squares method.
        Implements the theoretical framework from Massey's paper.
        """
        try:
            teams_with_min_games = [team for team, games in self.games_played.items() 
                                  if games >= self.min_games]
            
            if not teams_with_min_games:
                return {}
            
            # Build design matrix and response vector
            X, y = self._build_design_matrix(teams_with_min_games)
            
            # Check matrix properties (Theorems 2.2, 2.3, 2.4)
            has_full_rank, has_null_vector, condition_number = self._check_matrix_properties(X)
            
            if has_null_vector:
                self.logger.warning("Design matrix has null vectors - solution may not be unique")
            if not has_full_rank:
                self.logger.warning("Design matrix does not have full column rank")
            if condition_number > 1e10:
                self.logger.warning(f"Matrix is ill-conditioned (condition number: {condition_number:.2e})")
            
            # Calculate normal equations: X^T X b = X^T y
            XtX = X.T @ X
            Xty = X.T @ y
            
            # Verify Hessian is positive definite (ensures minimum)
            if not self._verify_hessian_positive_definite(X):
                self.logger.warning("Hessian matrix is not positive definite - solution may not be a minimum")
            
            # Solve system based on matrix properties
            if has_full_rank and not has_null_vector:
                # Unique solution exists (Theorem 2.4)
                try:
                    b = np.linalg.solve(XtX, Xty)
                except np.linalg.LinAlgError:
                    self.logger.warning("Failed to solve normal equations directly")
                    b = self._calculate_pseudo_inverse(X) @ y
            else:
                # Use pseudo-inverse for best fit solution
                self.logger.info("Using pseudo-inverse for non-unique solution")
                b = self._calculate_pseudo_inverse(X) @ y
            
            # Calculate error vector e = y - Xb (geometric interpretation)
            e = y - X @ b
            
            # Verify error vector is perpendicular to design matrix (Massey's geometric proof)
            error_perpendicular = np.allclose(X.T @ e, np.zeros_like(b), atol=1e-10)
            if not error_perpendicular:
                self.logger.warning("Error vector is not perpendicular to design matrix")
            
            # Calculate error statistics
            mse = np.mean(e**2)
            max_error = np.max(np.abs(e))
            self.logger.info(f"Mean squared error: {mse:.4f}, Max absolute error: {max_error:.4f}")
            
            # Convert to dictionary and normalize
            ratings_dict = {team: float(b[i]) 
                          for i, team in enumerate(teams_with_min_games)}
            
            # Normalize to 0-100 scale
            max_rating = max(ratings_dict.values())
            min_rating = min(ratings_dict.values())
            normalized_ratings = {
                team: 100 * (rating - min_rating) / (max_rating - min_rating)
                for team, rating in ratings_dict.items()
            }
            
            return normalized_ratings
            
        except Exception as e:
            self.logger.error(f"Error calculating ratings: {str(e)}")
            return {}
    
    def predict_game(self, team_a: str, team_b: str, 
                    neutral_site: bool = False) -> tuple[float, float]:
        """
        Predict the outcome of a game between two teams.
        Returns (win_probability, predicted_margin)
        """
        ratings = self.calculate_ratings()
        if not ratings or team_a not in ratings or team_b not in ratings:
            raise ValueError("Ratings not available for both teams")
            
        rating_diff = ratings[team_a] - ratings[team_b]
        
        # Adjust for home court if not neutral site
        if not neutral_site:
            rating_diff += self.HOME_ADVANTAGE
            
        # Convert rating difference to win probability using logistic function
        win_prob = 1 / (1 + np.exp(-rating_diff/15))
        
        # Estimate margin based on rating difference
        predicted_margin = rating_diff * self.MARGIN_FACTOR
        
        return win_prob, predicted_margin
    
    def predict_upcoming_games(self) -> pd.DataFrame:
        """Predict upcoming NBA games."""
        try:
            gamefinder = leaguegamefinder.LeagueGameFinder(
                date_from_nullable=datetime.now().strftime('%m/%d/%Y'),
                league_id_nullable='00'
            )
            time.sleep(2)
            
            games_df = gamefinder.get_data_frames()[0]
            upcoming_games = games_df[games_df['WL'].isna()].copy()
            
            predictions = []
            for _, game in upcoming_games.iterrows():
                try:
                    matchup = game['MATCHUP']
                    if 'vs.' in matchup:
                        home_team = game['TEAM_NAME']
                        away_team = matchup.split('vs.')[1].strip()
                        
                        win_prob, margin = self.predict_game(home_team, away_team)
                        
                        predictions.append({
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_win_prob': win_prob,
                            'predicted_margin': margin,
                            'game_time': game['GAME_DATE']
                        })
                except ValueError as e:
                    self.logger.warning(f"Skipping prediction: {str(e)}")
            
            return pd.DataFrame(predictions)
            
        except Exception as e:
            self.logger.error(f"Error predicting upcoming games: {str(e)}")
            return pd.DataFrame()

def main():
    try:
        # Initialize ratings system with preseason ratings
        nba = NBAMasseyRatings(min_games=5, use_preseason=True)
        nba.load_season_games()
        
        # Calculate different rating versions
        standard_ratings = nba.calculate_ratings()
        binary_ratings = nba.calculate_ratings_binary()
        sos_ratings = nba.calculate_sos()
        conference_strengths = nba.calculate_conference_strengths()
        
        if standard_ratings:
            # Create comprehensive ratings DataFrame
            df = pd.DataFrame({
                'team': list(standard_ratings.keys()),
                'rating': list(standard_ratings.values()),
                'binary_rating': [binary_ratings.get(team, 0) for team in standard_ratings.keys()],
                'sos': [sos_ratings.get(team, 0) for team in standard_ratings.keys()]
            })
            
            # Add conference info
            df['conference'] = df['team'].map(lambda x: 'Eastern' if x in conference_map['Eastern'] else 'Western')
            
            # Calculate z-scores
            for col in ['rating', 'binary_rating', 'sos']:
                mean_val = df[col].mean()
                std_val = df[col].std()
                df[f'{col}_zscore'] = (df[col] - mean_val) / std_val
            
            # Calculate tiers (1-5 based on rating z-score)
            df['tier'] = pd.qcut(df['rating_zscore'], q=5, labels=['5', '4', '3', '2', '1'])
            
            # Calculate win probability vs average team
            df['win_prob_vs_avg'] = 1 / (1 + np.exp(-df['rating_zscore']))
            
            # Sort by rating descending
            df = df.sort_values('rating', ascending=False)
            
            # Format columns
            for col in ['rating', 'binary_rating', 'sos']:
                df[col] = df[col].round(2)
                df[f'{col}_zscore'] = df[f'{col}_zscore'].round(3)
            df['win_prob_vs_avg'] = (df['win_prob_vs_avg'] * 100).round(1).astype(str) + '%'
            
            # Print results
            print("\nNBA Team Ratings Analysis")
            print("========================")
            print("\nStandard Ratings (with margin of victory):")
            print(df[['team', 'rating', 'tier', 'win_prob_vs_avg']].to_string(index=False))
            
            print("\nStrength of Schedule Analysis:")
            print(df[['team', 'sos', 'sos_zscore']].sort_values('sos', ascending=False).head(10).to_string(index=False))
            
            print("\nConference Strength Analysis:")
            for conf, strength in conference_strengths.items():
                print(f"{conf}: {strength:.3f} win rate in inter-conference games")
            
            print("\nBinary (BCS-Style) Ratings:")
            print(df[['team', 'binary_rating']].head(10).to_string(index=False))
            
            # Predict upcoming games
            upcoming = nba.predict_upcoming_games()
            if not upcoming.empty:
                print("\nUpcoming Game Predictions:")
                print("========================")
                for _, game in upcoming.iterrows():
                    print(f"{game['home_team']} vs {game['away_team']}")
                    print(f"Win Probability: {game['home_win_prob']:.1%}")
                    print(f"Predicted Margin: {game['predicted_margin']:.1f}")
                    print("---")
            else:
                print("\nNo upcoming games found.")
                
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()