from datetime import datetime
from sports_betting.analysis.weather_analysis import WeatherAnalysis

def test_weather():
    weather = WeatherAnalysis()
    
    # Test multiple teams
    teams_to_test = [
        ("Buffalo Bills", "NFL"),
        ("Minnesota Vikings", "NFL"),  # Indoor stadium
        ("Michigan", "COLLEGE")
    ]
    
    game_time = datetime.now()
    
    for team, league in teams_to_test:
        print(f"\nTesting Weather for {team} ({league})")
        print("=" * 50)
        
        try:
            weather_data = weather.get_game_weather(team, game_time, league)
            if weather_data:
                print(f"Stadium Type: {'Indoor' if weather_data.get('indoor') else 'Outdoor'}")
                print(f"Temperature: {weather_data['temperature']}°F")
                print(f"Wind Speed: {weather_data['wind_mph']} mph")
                print(f"Precipitation: {weather_data['precipitation_mm']}%")
                print(f"Humidity: {weather_data['humidity']}%")
                
                impact = weather.analyze_weather_impact(weather_data, league)
                print(f"Weather Impact Score: {impact}")
            else:
                print("Error: Could not fetch weather data")
                
        except Exception as e:
            print(f"Error during weather analysis: {e}")

if __name__ == "__main__":
    test_weather()