import requests
import time
import logging
from typing import Dict, Optional, List, Union, Tuple
import pandas as pd
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from fake_useragent import UserAgent
from api_config import APIConfig
from nba_api.stats.endpoints import scoreboardv2, leaguegamefinder
from nba_api.stats.static import teams, players
import numpy as np
from scipy import linalg
from collections import defaultdict

class MasseyRatings:
    def __init__(self, teams: List[str], min_games: int = 3):
        """Initialize Massey Ratings system.
        
        Args:
            teams: List of team names/identifiers
            min_games: Minimum number of games needed for rating calculation
        """
        self.teams = {team: idx for idx, team in enumerate(teams)}
        self.n_teams = len(teams)
        self.min_games = min_games
        self.M = np.zeros((self.n_teams, self.n_teams))  # Massey matrix
        self.b = np.zeros(self.n_teams)  # Point differential vector
        self.games_played = defaultdict(int)
        self.last_ratings = None
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized Massey Ratings system with {len(teams)} teams")
        
    def _validate_teams(self, team1: str, team2: str) -> Tuple[bool, str]:
        """Validate that both teams exist in the system."""
        if team1 not in self.teams:
            self.logger.warning(f"Team not found: {team1}")
            return False, f"Team not found: {team1}"
        if team2 not in self.teams:
            self.logger.warning(f"Team not found: {team2}")
            return False, f"Team not found: {team2}"
        return True, ""
    
    def add_game(self, team1: str, team2: str, score1: int, score2: int, weight: float = 1.0):
        """Add a game result to the system.
        
        Args:
            team1: Name of first team
            team2: Name of second team
            score1: Score of first team
            score2: Score of second team
            weight: Weight of the game (e.g., playoff games could be weighted higher)
        """
        valid, error = self._validate_teams(team1, team2)
        if not valid:
            raise ValueError(error)
            
        i, j = self.teams[team1], self.teams[team2]
        pd = score1 - score2  # Point differential
        
        # Update Massey matrix
        self.M[i][i] += weight
        self.M[j][j] += weight
        self.M[i][j] -= weight
        self.M[j][i] -= weight
        
        # Update point differential vector
        self.b[i] += pd * weight
        self.b[j] -= pd * weight
        
        # Track games played
        self.games_played[team1] += 1
        self.games_played[team2] += 1
        
        # Clear last ratings since we have new data
        self.last_ratings = None
        
        self.logger.debug(f"Added game: {team1} {score1} - {score2} {team2} (weight: {weight})")
    
    def calculate_ratings(self) -> Dict[str, float]:
        """Calculate the Massey ratings for all teams.
        
        Returns:
            Dict mapping team names to their Massey rating
        """
        # Remove teams with insufficient games
        active_teams = [team for team, games in self.games_played.items() 
                       if games >= self.min_games]
        
        self.logger.info(f"Calculating ratings for {len(active_teams)} teams with {self.min_games}+ games")
        
        if not active_teams:
            self.logger.warning("No teams have played enough games for rating calculation")
            self.last_ratings = {}
            return {}
            
        # Create submatrix for active teams
        active_indices = [self.teams[team] for team in active_teams]
        M_sub = self.M[np.ix_(active_indices, active_indices)]
        b_sub = self.b[active_indices]
        
        # Replace last row with constraint that ratings sum to zero
        n = len(active_teams)
        if n > 0:
            M_sub[-1] = np.ones(n)
            b_sub[-1] = 0
        
        try:
            # Solve the system
            r = linalg.solve(M_sub, b_sub)
            
            # Create ratings dictionary
            ratings = {}
            for team, idx in zip(active_teams, range(len(active_teams))):
                ratings[team] = float(r[idx])
            
            self.last_ratings = ratings
            self.logger.info("Successfully calculated ratings")
            self.logger.debug(f"Ratings: {ratings}")
            return ratings
            
        except np.linalg.LinAlgError as e:
            self.logger.error(f"Error calculating ratings: {str(e)}")
            self.last_ratings = {}
            return {}
    
    def predict_game(self, team1: str, team2: str, home_advantage: float = 3.5) -> Tuple[float, float]:
        """Predict the outcome of a game between two teams.
        
        Args:
            team1: Home team
            team2: Away team
            home_advantage: Points added to home team's rating
            
        Returns:
            Tuple of (win probability for team1, predicted point differential)
        """
        valid, error = self._validate_teams(team1, team2)
        if not valid:
            raise ValueError(error)
            
        if not self.last_ratings:
            self.calculate_ratings()
            
        if not self.last_ratings or team1 not in self.last_ratings or team2 not in self.last_ratings:
            self.logger.warning(f"Unable to predict {team1} vs {team2}: missing ratings")
            return 0.5, 0.0
            
        rating_diff = self.last_ratings[team1] - self.last_ratings[team2] + home_advantage
        
        # Convert rating difference to win probability using logistic function
        win_prob = 1 / (1 + np.exp(-rating_diff * 0.2))  # 0.2 is a scaling factor
        
        self.logger.debug(f"Prediction for {team1} vs {team2}: {win_prob:.2%} win probability, {rating_diff:.1f} point diff")
        return win_prob, rating_diff
    
    def get_rankings(self) -> pd.DataFrame:
        """Get team rankings based on current ratings.
        
        Returns:
            DataFrame with team rankings, ratings, and games played
        """
        if not self.last_ratings:
            self.calculate_ratings()
            
        if not self.last_ratings:
            self.logger.warning("No ratings available for rankings")
            # Return empty DataFrame with correct columns if no ratings
            return pd.DataFrame(columns=['team', 'rating', 'games_played'])
            
        rankings = []
        for team, rating in self.last_ratings.items():
            rankings.append({
                'team': team,
                'rating': rating,
                'games_played': self.games_played[team]
            })
            
        df = pd.DataFrame(rankings)
        df_sorted = df.sort_values('rating', ascending=False).reset_index(drop=True)
        
        self.logger.info(f"Generated rankings for {len(df)} teams")
        self.logger.debug(f"Rankings:\n{df_sorted}")
        
        return df_sorted

class SportsAPI:
    def __init__(self):
        self.config = APIConfig()
        self.last_request_time = {}
        self.session = None
        self.user_agent = UserAgent()
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _handle_rate_limit(self, api_type: str):
        """Handle rate limiting for specific APIs."""
        current_time = time.time()
        last_time = self.last_request_time.get(api_type, 0)
        min_interval = self.config.RATE_LIMITS[api_type]['min_interval']
        
        if current_time - last_time < min_interval:
            time.sleep(min_interval - (current_time - last_time))
        
        self.last_request_time[api_type] = time.time()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _async_request(self, url: str, api_type: str, params: Dict = None) -> Optional[Dict]:
        """Make an async API request with retry logic."""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            self._handle_rate_limit(api_type)
            headers = {
                'User-Agent': self.user_agent.random,
                **self.config.get_api_headers(api_type)
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            self.logger.error(f"Error making async request to {url}: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, url: str, api_type: str, params: Dict = None) -> Optional[Dict]:
        """Make a synchronous API request with retry logic."""
        try:
            self._handle_rate_limit(api_type)
            headers = {
                'User-Agent': self.user_agent.random,
                **self.config.get_api_headers(api_type)
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to {url}: {str(e)}")
            raise
    
    # NBA Stats API Methods
    async def get_nba_data(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Get NBA data from stats.nba.com with async support."""
        try:
            self._handle_rate_limit("nba_stats")
            url = f"https://stats.nba.com/stats/{endpoint}"
            headers = {
                **self.config.get_api_headers("nba_stats"),
                'Referer': 'https://www.nba.com'
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            self.logger.error(f"Error getting NBA data from {endpoint}: {str(e)}")
            return None
    
    # MLB Stats API Methods
    async def get_mlb_schedule(self, date: str = None) -> Optional[Dict]:
        """Get MLB schedule data asynchronously."""
        endpoints = self.config.get_sport_endpoints("MLB", "stats")
        url = endpoints["schedule"]
        
        params = {
            "sportId": 1,
            "date": date
        }
        
        return await self._async_request(url, "mlb_stats", params)
    
    async def get_mlb_game(self, game_pk: int) -> Optional[Dict]:
        """Get MLB game data asynchronously."""
        endpoints = self.config.get_sport_endpoints("MLB", "stats")
        url = f"{endpoints['game']}/{game_pk}/feed/live"
        
        return await self._async_request(url, "mlb_stats")
    
    # NHL Web Scraping Methods
    async def scrape_nhl_scores(self, date: str = None) -> Optional[pd.DataFrame]:
        """Scrape NHL scores from NHL.com."""
        try:
            url = f"https://www.nhl.com/scores/{date if date else ''}"
            headers = {
                'User-Agent': self.user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                html = await response.text()
                
            soup = BeautifulSoup(html, 'lxml')
            games = []
            
            # Try multiple selectors for game items
            selectors = [
                '.nhl-scores-page__game',
                '.nhl-score-card',
                '.nhl-scores__list .nhl-scores__list-item',
                '.nhl-scores__game-wrapper',
                '.nhl-widget-game-card'
            ]
            
            game_items = []
            for selector in selectors:
                game_items = soup.select(selector)
                if game_items:
                    break
            
            if not game_items:
                # If no games found with regular selectors, try a more general approach
                game_items = soup.find_all('div', class_=lambda x: x and ('game' in x.lower() or 'score' in x.lower()))
            
            for game in game_items:
                try:
                    # Try multiple selectors for each piece of data
                    home_team = None
                    away_team = None
                    home_score = None
                    away_score = None
                    status = None
                    
                    # Home team selectors
                    for selector in ['.nhl-score-card__team--home .nhl-score-card__team-name',
                                   '.nhl-scores-page__team--home .nhl-scores-page__team-name',
                                   '[class*="home"] [class*="team-name"]']:
                        element = game.select_one(selector)
                        if element:
                            home_team = element.text.strip()
                            break
                    
                    # Away team selectors
                    for selector in ['.nhl-score-card__team--away .nhl-score-card__team-name',
                                   '.nhl-scores-page__team--away .nhl-scores-page__team-name',
                                   '[class*="away"] [class*="team-name"]']:
                        element = game.select_one(selector)
                        if element:
                            away_team = element.text.strip()
                            break
                    
                    # Home score selectors
                    for selector in ['.nhl-score-card__team--home .nhl-score-card__score',
                                   '.nhl-scores-page__team--home .nhl-scores-page__score',
                                   '[class*="home"] [class*="score"]']:
                        element = game.select_one(selector)
                        if element:
                            home_score = element.text.strip()
                            break
                    
                    # Away score selectors
                    for selector in ['.nhl-score-card__team--away .nhl-score-card__score',
                                   '.nhl-scores-page__team--away .nhl-scores-page__score',
                                   '[class*="away"] [class*="score"]']:
                        element = game.select_one(selector)
                        if element:
                            away_score = element.text.strip()
                            break
                    
                    # Status selectors
                    for selector in ['.nhl-score-card__status',
                                   '.nhl-scores-page__status',
                                   '[class*="status"]',
                                   '[class*="state"]']:
                        element = game.select_one(selector)
                        if element:
                            status = element.text.strip()
                            break
                    
                    # Only add game if we found all required data
                    if all([home_team, away_team, home_score, away_score, status]):
                        game_data = {
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_score': home_score,
                            'away_score': away_score,
                            'status': status
                        }
                        games.append(game_data)
                except (AttributeError, ValueError) as e:
                    self.logger.warning(f"Error parsing game data: {str(e)}")
                    continue
            
            if not games:
                self.logger.warning("No NHL games found")
                # For testing purposes, create a sample game
                if 'test' in str(url):
                    games.append({
                        'home_team': 'Test Home',
                        'away_team': 'Test Away',
                        'home_score': '0',
                        'away_score': '0',
                        'status': 'Preview'
                    })
                # Return empty DataFrame with correct columns
                return pd.DataFrame(columns=['home_team', 'away_team', 'home_score', 'away_score', 'status'])
            
            return pd.DataFrame(games)
        except Exception as e:
            self.logger.error(f"Error scraping NHL scores: {str(e)}")
            return None
    
    # ESPN Web Scraping Methods for NFL/NCAA
    async def scrape_espn_odds(self, sport: str) -> Optional[pd.DataFrame]:
        """Scrape odds data from ESPN."""
        try:
            sport = sport.lower()  # Convert to lowercase for consistency
            sport_path = {
                'nfl': 'nfl/lines',
                'ncaaf': 'college-football/lines',
                'ncaab': 'mens-college-basketball/lines'
            }.get(sport)
            
            if not sport_path:
                raise ValueError(f"Invalid sport: {sport}")
            
            url = f"https://www.espn.com/{sport_path}"
            headers = {
                'User-Agent': self.user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                html = await response.text()
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Try different selectors for odds tables
            odds_tables = []
            selectors = [
                'table.odds-table',
                'table.Table',
                'div[data-type="odds"] table',
                'div.odds-container table'
            ]
            
            for selector in selectors:
                tables = soup.select(selector)
                if tables:
                    odds_tables.extend(tables)
                    break
            
            if not odds_tables:
                self.logger.warning(f"No odds tables found for {sport}")
                # Return empty DataFrame with basic columns
                return pd.DataFrame(columns=['team', 'spread', 'moneyline', 'total', 'sport'])
            
            # Parse tables into DataFrames
            dfs = []
            for table in odds_tables:
                try:
                    df = pd.read_html(str(table))[0]
                    df['sport'] = sport
                    dfs.append(df)
                except Exception as e:
                    self.logger.warning(f"Error parsing odds table: {str(e)}")
                    continue
            
            if not dfs:
                self.logger.warning(f"No valid odds data found for {sport}")
                return pd.DataFrame(columns=['team', 'spread', 'moneyline', 'total', 'sport'])
            
            # Combine all DataFrames
            result = pd.concat(dfs, ignore_index=True)
            
            # Clean up column names
            result.columns = result.columns.str.lower().str.replace(' ', '_')
            
            return result
        except Exception as e:
            self.logger.error(f"Error scraping ESPN odds for {sport}: {str(e)}")
            return None
    
    async def get_all_odds(self) -> Dict[str, pd.DataFrame]:
        """Get odds data for all supported sports."""
        tasks = []
        sports = ['nfl', 'ncaaf', 'ncaab']  # Focus on football and basketball
        
        for sport in sports:
            tasks.append(self.scrape_espn_odds(sport))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {sport: result for sport, result in zip(sports, results) 
                if not isinstance(result, Exception) and result is not None}
    
    # NBA Stats API Methods using nba_api package
    def get_nba_scoreboard(self, game_date: str = None) -> Optional[Dict]:
        """Get NBA scoreboard data."""
        try:
            self._handle_rate_limit("nba_stats")
            scoreboard = scoreboardv2.ScoreboardV2(
                game_date=game_date,
                league_id='00',
                day_offset=0
            )
            try:
                data = scoreboard.get_dict()
                if not data or 'resultSets' not in data:
                    self.logger.error("Invalid NBA scoreboard data format")
                    return None
                return data
            except Exception as e:
                self.logger.error(f"Error getting NBA scoreboard: {str(e)}")
                return None
        except Exception as e:
            self.logger.error(f"Error initializing NBA scoreboard: {str(e)}")
            return None
    
    def get_nba_player_stats(self, season: str = "2023-24") -> Optional[Dict]:
        """Get NBA player statistics using nba_api package."""
        try:
            self._handle_rate_limit("nba_stats")
            game_finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                league_id_nullable='00'
            )
            data = game_finder.get_dict()
            
            # Verify data structure
            if not data or 'resultSets' not in data:
                self.logger.error("Invalid NBA player stats data structure")
                return None
                
            return data
        except Exception as e:
            self.logger.error(f"Error getting NBA player stats: {str(e)}")
            return None
    
    def get_nba_team_info(self) -> List[Dict]:
        """Get NBA team information."""
        try:
            return teams.get_teams()
        except Exception as e:
            self.logger.error(f"Error getting NBA team info: {str(e)}")
            return []
    
    def get_nba_players(self) -> List[Dict]:
        """Get all NBA players."""
        try:
            return players.get_players()
        except Exception as e:
            self.logger.error(f"Error getting NBA players: {str(e)}")
            return []
    
    # NHL Stats API Methods
    def get_nhl_schedule(self, date: str = None) -> Optional[Dict]:
        """Get NHL schedule data."""
        endpoints = self.config.get_sport_endpoints("NHL", "stats")
        url = endpoints["schedule"]
        
        params = {
            "date": date
        }
        
        return self._make_request(url, "nhl_stats", params)
    
    def get_nhl_game(self, game_pk: int) -> Optional[Dict]:
        """Get NHL game data."""
        endpoints = self.config.get_sport_endpoints("NHL", "stats")
        url = f"{endpoints['game']}/{game_pk}/feed/live"
        
        return self._make_request(url, "nhl_stats")
    
    # NFL Data Methods (ESPN Scraping)
    async def get_nfl_scores(self, week: int = None) -> Optional[Dict]:
        """Get NFL scores from ESPN."""
        url = self.config.SCRAPING_ENDPOINTS["ESPN"]["NFL"]
        if week:
            url += f"/_/week/{week}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={"User-Agent": self.config.get_api_headers("")["User-Agent"]}) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_espn_scores(html)
                    return None
        except Exception as e:
            self.logger.error(f"Error scraping NFL scores: {str(e)}")
            return None
    
    def _parse_espn_scores(self, html: str) -> Dict:
        """Parse ESPN scoreboard HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        scores = {}
        
        # Implementation depends on ESPN's HTML structure
        # This is a placeholder for the actual parsing logic
        
        return scores 