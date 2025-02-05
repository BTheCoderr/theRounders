import requests
from datetime import datetime, timedelta

class HistoricalAnalysis:
    def __init__(self):
        self.odds_api_key = "f4b284d121161d41abae2044e2f93ab1"
        
    def get_matchup_history(self, team1, team2, sport, years=3):
        """Get historical matchup data"""
        try:
            games = []
            current_year = datetime.now().year
            
            for year in range(current_year - years, current_year + 1):
                url = f"https://api.the-odds-api.com/v4/sports/{sport}/scores"
                params = {
                    'apiKey': self.odds_api_key,
                    'daysFrom': 365,
                    'year': year
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                # Filter for matchups between these teams
                matchups = [g for g in data if 
                          (g['home_team'] in [team1, team2] and 
                           g['away_team'] in [team1, team2])]
                games.extend(matchups)
            
            return self.analyze_matchup_history(games, team1)
            
        except Exception as e:
            print(f"Error fetching matchup history: {e}")
            return None
            
    def analyze_matchup_history(self, games, perspective_team):
        """Analyze historical matchup data"""
        if not games:
            return None
            
        analysis = {
            'total_games': len(games),
            'wins': 0,
            'avg_margin': 0,
            'avg_total': 0,
            'cover_rate': 0,
            'over_rate': 0,
            'home_record': {'wins': 0, 'losses': 0},
            'away_record': {'wins': 0, 'losses': 0},
            'recent_trend': [],
            'avg_line': 0,
            'line_covers': 0
        }
        
        for game in games:
            is_home = game['home_team'] == perspective_team
            team_score = game['home_score'] if is_home else game['away_score']
            opp_score = game['away_score'] if is_home else game['home_score']
            
            # Basic stats
            if team_score > opp_score:
                analysis['wins'] += 1
                if is_home:
                    analysis['home_record']['wins'] += 1
                else:
                    analysis['away_record']['wins'] += 1
            else:
                if is_home:
                    analysis['home_record']['losses'] += 1
                else:
                    analysis['away_record']['losses'] += 1
                    
            # Margin and totals
            margin = team_score - opp_score
            analysis['avg_margin'] += margin
            analysis['avg_total'] += team_score + opp_score
            
            # Spread and total results
            if 'odds' in game:
                spread = game['odds'].get('spread', 0)
                total = game['odds'].get('total', 0)
                
                if margin > spread:
                    analysis['line_covers'] += 1
                if team_score + opp_score > total:
                    analysis['over_rate'] += 1
                    
            # Recent trend (last 5)
            if len(analysis['recent_trend']) < 5:
                analysis['recent_trend'].append({
                    'margin': margin,
                    'total': team_score + opp_score,
                    'date': game['commence_time']
                })
                
        # Calculate averages
        analysis['avg_margin'] /= len(games)
        analysis['avg_total'] /= len(games)
        analysis['cover_rate'] = analysis['line_covers'] / len(games)
        analysis['over_rate'] /= len(games)
        
        return analysis 