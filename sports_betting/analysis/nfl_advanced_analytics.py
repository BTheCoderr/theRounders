from sports_betting.data_collection.nfl import NFLDataCollector
from datetime import datetime
import requests

class NFLAdvancedAnalytics:
    def __init__(self):
        self.collector = NFLDataCollector()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _compare_offense(self, home_stats, away_stats):
        """Compare offensive stats between teams"""
        try:
            # Get offensive stats from the API data
            home_offense = home_stats.get('stats', [])
            away_offense = away_stats.get('stats', [])
            
            # Compare key offensive metrics
            comparison = {
                'points_per_game': {
                    'home': home_offense[0].get('value', 0),
                    'away': away_offense[0].get('value', 0)
                },
                'total_yards': {
                    'home': home_offense[1].get('value', 0),
                    'away': away_offense[1].get('value', 0)
                },
                'passing_yards': {
                    'home': home_offense[2].get('value', 0),
                    'away': away_offense[2].get('value', 0)
                },
                'rushing_yards': {
                    'home': home_offense[3].get('value', 0),
                    'away': away_offense[3].get('value', 0)
                }
            }
            
            return comparison
        except Exception as e:
            print(f"Error in offensive comparison: {str(e)}")
            return "Error comparing offense"

    def _compare_defense(self, home_stats, away_stats):
        """Compare defensive stats between teams"""
        try:
            return "Defensive comparison not available yet"
        except Exception as e:
            return "Error comparing defense"

    def _compare_special_teams(self, home_stats, away_stats):
        """Compare special teams stats"""
        try:
            return "Special teams comparison not available yet"
        except Exception as e:
            return "Error comparing special teams"

    def _assess_weather_impact(self, weather):
        """Assess weather impact on game"""
        try:
            return "Weather impact assessment not available yet"
        except Exception as e:
            return "Error assessing weather"

    def _process_injury_report(self, injury_data):
        """Process injury report data"""
        try:
            return "Injury report not available yet"
        except Exception as e:
            return "Error processing injury report"

    def _filter_h2h_games(self, schedule, opponent):
        """Filter head-to-head games"""
        try:
            return "H2H games not available yet"
        except Exception as e:
            return "Error filtering H2H games"

    def _analyze_h2h_trends(self, games):
        """Analyze head-to-head trends"""
        try:
            return "H2H trends not available yet"
        except Exception as e:
            return "Error analyzing H2H trends"

    def _calculate_dvoa(self, stats):
        """Calculate DVOA"""
        try:
            return "DVOA calculation not available yet"
        except Exception as e:
            return "Error calculating DVOA"

    def _calculate_epa(self, stats):
        """Calculate EPA"""
        try:
            return "EPA calculation not available yet"
        except Exception as e:
            return "Error calculating EPA"

    def _calculate_success_rate(self, stats):
        """Calculate success rate"""
        try:
            return "Success rate calculation not available yet"
        except Exception as e:
            return "Error calculating success rate"

    def get_matchup_analysis(self, home_team, away_team):
        """Analyze team matchups based on recent performance"""
        try:
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{home_team}/statistics"
            home_stats = requests.get(url, headers=self.headers).json()
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{away_team}/statistics"
            away_stats = requests.get(url, headers=self.headers).json()
            
            return {
                'offense_comparison': self._compare_offense(home_stats, away_stats),
                'defense_comparison': self._compare_defense(home_stats, away_stats),
                'special_teams': self._compare_special_teams(home_stats, away_stats)
            }
        except Exception as e:
            return f"Error getting matchup analysis: {str(e)}"

    def get_weather_impact(self, game_id):
        """Get weather data and its potential impact"""
        try:
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/games/{game_id}"
            game_data = requests.get(url, headers=self.headers).json()
            
            if 'weather' in game_data:
                weather = game_data['weather']
                return {
                    'temperature': weather.get('temperature'),
                    'conditions': weather.get('conditions'),
                    'wind_speed': weather.get('windSpeed'),
                    'impact_assessment': self._assess_weather_impact(weather)
                }
            return "Weather data not available"
        except Exception as e:
            return f"Error getting weather data: {str(e)}"

    def get_player_availability(self, team_id):
        """Get injury reports and key player status"""
        try:
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/injuries"
            injury_data = requests.get(url, headers=self.headers).json()
            return self._process_injury_report(injury_data)
        except Exception as e:
            return f"Error getting injury data: {str(e)}"

    def get_historical_matchup(self, home_team, away_team):
        """Get historical head-to-head data"""
        try:
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{home_team}/schedule"
            schedule = requests.get(url, headers=self.headers).json()
            h2h_games = self._filter_h2h_games(schedule, away_team)
            return self._analyze_h2h_trends(h2h_games)
        except Exception as e:
            return f"Error getting historical data: {str(e)}"

    def get_advanced_metrics(self, team_id):
        """Calculate advanced metrics"""
        try:
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"
            stats = requests.get(url, headers=self.headers).json()
            return {
                'dvoa': self._calculate_dvoa(stats),
                'epa': self._calculate_epa(stats),
                'success_rate': self._calculate_success_rate(stats)
            }
        except Exception as e:
            return f"Error calculating metrics: {str(e)}"

def main():
    print("\n=== TODAY'S NFL GAMES & PREDICTIONS ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}")
    print("=" * 60)

    collector = NFLDataCollector()
    games = collector.get_odds()

    for game in games:
        print(f"\n{game['away_team']} @ {game['home_team']}")
        print(f"Start Time: {game['start_time']} ET")
        print(f"Venue: {game['venue']}")
        
        print("\nODDS:")
        print(f"Spread: {game['spread']}")
        print(f"Total: {game['total']}")
        print(f"Moneyline: {game['away_team']} {game['away_ml']} | {game['home_team']} {game['home_ml']}")
        
        print("\nPREDICTIONS:")
        # Spread prediction with confidence
        if game['spread'] != 'N/A':
            spread_value = float(game['spread'])
            spread_confidence = 70 if abs(spread_value) <= 3 else (60 if abs(spread_value) <= 7 else 50)
            pick = game['home_team'] if spread_value < 0 else game['away_team']
            print(f"Spread Pick: {pick} ({spread_confidence}% confidence)")
        
        # Total prediction with confidence
        if game['total'] != 'N/A':
            total = float(game['total'])
            if total > 47:
                print(f"Total Pick: UNDER {game['total']} (65% confidence)")
            elif total < 42:
                print(f"Total Pick: OVER {game['total']} (65% confidence)")
            else:
                print(f"Total Pick: {'OVER' if total < 44.5 else 'UNDER'} {game['total']} (55% confidence)")
        
        # Moneyline prediction with confidence based on spread
        if game['home_ml'] != 'N/A' and game['away_ml'] != 'N/A':
            home_ml = float(game['home_ml'])
            away_ml = float(game['away_ml'])
            spread_value = abs(float(game['spread']))
            
            # Calculate confidence based on spread
            if spread_value <= 3:
                ml_confidence = 65
            elif spread_value <= 7:
                ml_confidence = 55
            else:
                ml_confidence = 45
            
            pick = game['home_team'] if home_ml > away_ml else game['away_team']
            print(f"Moneyline Pick: {pick} ({ml_confidence}% confidence)")
        
        print("-" * 60)

if __name__ == "__main__":
    main()
