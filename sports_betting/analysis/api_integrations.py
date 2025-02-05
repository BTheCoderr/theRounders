import requests
from datetime import datetime, timedelta
import os
from .betting_analysis import BettingAnalysis

class SportsDataAPI:
    def __init__(self):
        self.nhl_base_url = "https://api-web.nhle.com/v1"
        self.nba_base_url = "https://api.sportsdata.io/v3/nba"
        self.nfl_base_url = "https://api.sportsdata.io/v3/nfl"
        self.ncaab_base_url = "https://api.sportsdata.io/v3/cbb"
        self.api_key = "YOUR_API_KEY"
        self.odds_api_key = "f4b284d121161d41abae2044e2f93ab1"
        self.betting_analysis = BettingAnalysis()
        
    def get_nhl_team_stats(self, team):
        """Fetch NHL team statistics"""
        try:
            url = f"{self.nhl_base_url}/standings/now"
            response = requests.get(url)
            data = response.json()
            
            # Find team in standings
            team_data = next((t for t in data['standings'] 
                            if team.lower() in t['teamCommonName']['default'].lower()), None)
            
            if team_data:
                return {
                    'win_rate': team_data['pointPctg'],
                    'goals_per_game': team_data['goalFor'] / team_data['gamesPlayed'],
                    'goals_against': team_data['goalAgainst'] / team_data['gamesPlayed'],
                    'power_play_pct': team_data.get('powerPlayPct', 0),
                    'penalty_kill_pct': team_data.get('penaltyKillPct', 0)
                }
            return None
            
        except Exception as e:
            print(f"Error fetching NHL stats: {e}")
            return None
            
    def get_nba_team_stats(self, team):
        """Fetch NBA team statistics"""
        try:
            url = f"{self.nba_base_url}/stats/json/TeamSeasonStats/2024"
            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            response = requests.get(url, headers=headers)
            data = response.json()
            
            team_data = next((t for t in data if team.lower() in t['Name'].lower()), None)
            
            if team_data:
                return {
                    'win_rate': team_data['Percentage'],
                    'points_per_game': team_data['PointsPerGame'],
                    'points_allowed': team_data['PointsAllowedPerGame'],
                    'rebounds_per_game': team_data['ReboundsPerGame'],
                    'assists_per_game': team_data['AssistsPerGame'],
                    'three_pt_percentage': team_data['ThreePointPercentage']
                }
            return None
            
        except Exception as e:
            print(f"Error fetching NBA stats: {e}")
            return None
            
    def get_rest_days(self, team, sport):
        """Calculate days since last game"""
        try:
            if sport == 'NHL':
                url = f"{self.nhl_base_url}/schedule/{team}"
            else:  # NBA
                url = f"{self.nba_base_url}/scores/json/Games/2024"
                
            response = requests.get(url)
            games = response.json()
            
            # Find most recent game
            last_game_date = None
            today = datetime.now()
            
            # Process based on sport-specific API response structure
            if sport == 'NHL':
                # Process NHL schedule
                pass 
            
        except Exception as e:
            print(f"Error fetching rest days: {e}")
            return None
            
    def get_head_to_head(self, team1, team2, sport, seasons=3):
        """Fetch head-to-head history"""
        try:
            if sport == 'NHL':
                url = f"{self.nhl_base_url}/head-to-head/{team1}/{team2}"
            elif sport == 'NBA':
                url = f"{self.nba_base_url}/stats/json/Games/{seasons}"
            elif sport == 'NFL':
                url = f"{self.nfl_base_url}/stats/json/Games/{seasons}"
            else:  # NCAAB
                url = f"{self.ncaab_base_url}/stats/json/Games/{seasons}"
                
            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            response = requests.get(url, headers=headers)
            games = response.json()
            
            h2h_stats = {
                'total_games': 0,
                'team1_wins': 0,
                'avg_score_diff': 0,
                'last_meeting': None,
                'streak': 0
            }
            
            # Process games based on sport-specific response structure
            for game in games:
                if sport == 'NHL':
                    # Process NHL games
                    pass
                elif sport == 'NBA':
                    # Process NBA games
                    pass
                # ... Add NFL and NCAAB processing
                
            return h2h_stats
            
        except Exception as e:
            print(f"Error fetching head-to-head stats: {e}")
            return None
            
    def get_nfl_team_stats(self, team):
        """Fetch NFL team statistics"""
        try:
            url = f"{self.nfl_base_url}/stats/json/TeamSeasonStats/2024"
            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            response = requests.get(url, headers=headers)
            data = response.json()
            
            team_data = next((t for t in data if team.lower() in t['Team'].lower()), None)
            
            if team_data:
                return {
                    'win_rate': team_data['WinPercentage'],
                    'points_per_game': team_data['PointsPerGame'],
                    'points_allowed': team_data['PointsAllowed'],
                    'yards_per_game': team_data['OffensiveYardsPerGame'],
                    'yards_allowed': team_data['DefensiveYardsPerGame'],
                    'turnover_diff': team_data['TurnoverDifferential']
                }
            return None
            
        except Exception as e:
            print(f"Error fetching NFL stats: {e}")
            return None
            
    def get_ncaab_team_stats(self, team):
        """Fetch NCAAB team statistics"""
        try:
            url = f"{self.ncaab_base_url}/stats/json/TeamSeasonStats/2024"
            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            response = requests.get(url, headers=headers)
            data = response.json()
            
            team_data = next((t for t in data if team.lower() in t['Team'].lower()), None)
            
            if team_data:
                return {
                    'win_rate': team_data['WinPercentage'],
                    'points_per_game': team_data['PointsPerGame'],
                    'points_allowed': team_data['PointsAllowedPerGame'],
                    'field_goal_pct': team_data['FieldGoalsPercentage'],
                    'rebounds_per_game': team_data['ReboundsPerGame'],
                    'assists_per_game': team_data['AssistsPerGame']
                }
            return None
            
        except Exception as e:
            print(f"Error fetching NCAAB stats: {e}")
            return None
            
    def get_live_games(self, sport):
        """Fetch today's real games with detailed odds"""
        try:
            sport_key = {
                'NFL': 'americanfootball_nfl',
                'NCAAF': 'americanfootball_ncaaf',
                'NBA': 'basketball_nba',
                'NCAAB': 'basketball_ncaab',
                'NHL': 'icehockey_nhl'
            }.get(sport)
            
            if not sport_key:
                return []
                
            url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds'
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us',
                'markets': 'spreads,totals',
                'oddsFormat': 'american'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                print(f"API Error: {response.text}")
                return []
                
            games = response.json()
            print(f"\nFound {len(games)} {sport} games")
            
            formatted_games = []
            for game in games:
                formatted_game = {
                    'id': game.get('id'),
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'game_time': datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00')),
                    'sport': sport,
                    'odds': self.parse_odds(game.get('bookmakers', [])),
                    'line_movement': self.get_line_movement(game.get('id')),
                    'betting_analysis': self.betting_analysis.analyze_sharp_action(self.line_history.get(game.get('id'), [])),
                    'consensus': self.betting_analysis.calculate_consensus(self.parse_odds(game.get('bookmakers', [])))
                }
                formatted_games.append(formatted_game)
            
            return formatted_games
            
        except Exception as e:
            print(f"Error fetching {sport} games: {e}")
            print(f"Full error details: {str(e)}")
            return []
            
    def parse_odds(self, bookmakers):
        """Parse odds from bookmakers"""
        try:
            if not bookmakers:
                return {}
                
            odds = {
                'spread': None,
                'total': None,
                'moneyline': None
            }
            
            # Use first bookmaker with available odds
            for book in bookmakers:
                for market in book.get('markets', []):
                    if market['key'] == 'spreads' and not odds['spread']:
                        odds['spread'] = float(market['outcomes'][0]['point'])
                    elif market['key'] == 'totals' and not odds['total']:
                        odds['total'] = float(market['outcomes'][0]['point'])
                    elif market['key'] == 'h2h' and not odds['moneyline']:
                        odds['moneyline'] = market['outcomes'][0]['price']
                        
            return odds
            
        except Exception as e:
            print(f"Error parsing odds: {e}")
            return {}
        
    def get_ncaab_rankings(self):
        """Get current NCAAB rankings"""
        try:
            # You might want to add a different API endpoint for rankings
            # For now, returning empty dict
            return {}
        except Exception as e:
            print(f"Error fetching NCAAB rankings: {e}")
            return {}
            
    def get_team_stats(self, team, sport):
        """Get team statistics"""
        try:
            # Implement team stats fetching based on sport
            # For now, returning placeholder
            return {
                'win_rate': 0.0,
                'points_per_game': 0.0,
                'points_allowed': 0.0,
                'last_10_record': '0-0'
            }
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            return {}

class OddsAPI:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"

    def get_todays_games(self):
        """Get games and implied odds from news and sports articles"""
        try:
            # Get sports news from multiple sources
            url = f"{self.base_url}/everything"
            params = {
                'apiKey': self.news_api_key,
                'q': 'odds OR spreads OR betting lines',
                'domains': 'espn.com,cbssports.com,sportingnews.com',
                'language': 'en',
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params)
            news_data = response.json()

            # Parse articles to extract game information
            games = self._parse_games_from_news(news_data['articles'])
            return games

        except Exception as e:
            print(f"Error fetching games data: {e}")
            return []

    def _parse_games_from_news(self, articles):
        """Extract game information from news articles"""
        games = []
        for article in articles:
            # Extract game info using title and description
            game_info = self._extract_game_info(article['title'], article['description'])
            if game_info:
                games.append(game_info)
        
        return self._deduplicate_games(games)

    def _extract_game_info(self, title, description):
        """Parse game details from article text"""
        # Basic game info structure
        game = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sport': self._determine_sport(title),
            'game': '',
            'pick_type': '',
            'pick': '',
            'confidence': 0,
            'odds': 0
        }

        # Add parsing logic here
        return game

    def _determine_sport(self, text):
        """Determine sport from text"""
        sports = {
            'NBA': ['NBA', 'basketball'],
            'NFL': ['NFL', 'football'],
            'MLB': ['MLB', 'baseball'],
            'NHL': ['NHL', 'hockey'],
            'NCAAB': ['NCAA basketball', 'college basketball'],
            'NCAAF': ['NCAA football', 'college football']
        }

        for sport, keywords in sports.items():
            if any(keyword.lower() in text.lower() for keyword in keywords):
                return sport
        return None

    def _deduplicate_games(self, games):
        """Remove duplicate games based on teams playing"""
        unique_games = {}
        for game in games:
            key = f"{game['sport']}_{game['game']}"
            if key not in unique_games:
                unique_games[key] = game
        return list(unique_games.values())