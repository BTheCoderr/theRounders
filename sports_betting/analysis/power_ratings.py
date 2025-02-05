import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PowerRatings:
    def __init__(self):
        self.ratings = {}
        self.weights = {
            'offense': 0.20,
            'defense': 0.20,
            'recent_form': 0.15,
            'strength_of_schedule': 0.10,
            'home_away_performance': 0.10,
            'rest_advantage': 0.05,
            'injury_impact': 0.05,
            'pace_factor': 0.05,
            'betting_market': 0.05,
            'weather_impact': 0.05
        }
    
    def calculate_offensive_rating(self, team_data):
        """Enhanced offensive rating calculation"""
        return (
            team_data['points_per_game'] * 0.3 +
            team_data['offensive_rating'] * 0.3 +
            team_data['pace'] * 0.2 +
            team_data.get('three_point_percentage', 0) * 0.1 +
            team_data.get('free_throw_percentage', 0) * 0.1
        )
    
    def calculate_defensive_rating(self, team_data):
        """Enhanced defensive rating calculation"""
        return (
            (100 - team_data['opp_points_per_game']) * 0.3 +
            team_data['defensive_rating'] * 0.3 +
            team_data.get('blocks_per_game', 0) * 0.2 +
            team_data.get('steals_per_game', 0) * 0.1 +
            team_data.get('defensive_rebounds', 0) * 0.1
        )
    
    def calculate_rest_advantage(self, team_schedule):
        """Calculate rating based on days of rest and travel"""
        # Implementation would consider:
        # - Days since last game
        # - Travel distance
        # - Time zone changes
        # - Back-to-back games
        return 50  # Placeholder
    
    def calculate_injury_impact(self, team_injuries, team_roster):
        """Calculate impact of current injuries"""
        # Implementation would consider:
        # - Player importance (starter vs bench)
        # - Position scarcity
        # - Injury duration
        # - Replacement player quality
        return 50  # Placeholder
    
    def calculate_pace_factor(self, team_data, opponent_data):
        """Calculate pace matchup factor"""
        # Implementation would consider:
        # - Team's preferred pace
        # - Opponent's preferred pace
        # - Historical pace matchup data
        return 50  # Placeholder
    
    def calculate_betting_market_factor(self, market_data):
        """Calculate factor based on betting market movements"""
        # Implementation would consider:
        # - Line movements
        # - Sharp money indicators
        # - Public betting percentages
        # - Historical betting patterns
        return 50  # Placeholder
    
    def calculate_weather_impact(self, weather_data, venue_data):
        """Calculate weather impact for outdoor sports"""
        # Implementation would consider:
        # - Temperature
        # - Wind speed/direction
        # - Precipitation
        # - Team's historical performance in similar conditions
        return 50  # Placeholder
    
    def calculate_situational_spots(self, team_schedule, opponent_schedule):
        """Calculate situational advantages/disadvantages"""
        # Implementation would consider:
        # - Look-ahead spots
        # - Letdown spots
        # - Revenge games
        # - Division/Conference importance
        return 50  # Placeholder
    
    def calculate_coaching_factor(self, coaching_data):
        """Calculate coaching advantage"""
        # Implementation would consider:
        # - Coach's historical ATS record
        # - In-game adjustments
        # - Player rotation patterns
        return 50  # Placeholder
    
    def calculate(self, sports_data, market_data=None, weather_data=None, injury_data=None):
        """Calculate overall power ratings with all factors"""
        ratings_df = pd.DataFrame()
        
        for _, team_data in sports_data.iterrows():
            team_name = team_data['name']
            
            # Calculate all components
            ratings = {
                'offense': self.calculate_offensive_rating(team_data),
                'defense': self.calculate_defensive_rating(team_data),
                'recent_form': self.calculate_recent_form(team_data),
                'strength_of_schedule': self.calculate_strength_of_schedule(team_data, sports_data),
                'home_away': self.calculate_home_away_performance(team_data),
                'rest_advantage': self.calculate_rest_advantage(team_data),
                'injury_impact': self.calculate_injury_impact(injury_data, team_data),
                'pace_factor': self.calculate_pace_factor(team_data, None),
                'betting_market': self.calculate_betting_market_factor(market_data),
                'weather_impact': self.calculate_weather_impact(weather_data, None)
            }
            
            # Calculate weighted final rating
            final_rating = sum(
                ratings[factor] * weight 
                for factor, weight in self.weights.items()
            )
            
            # Store all ratings
            self.ratings[team_name] = {
                'overall': final_rating,
                **ratings
            }
        
        # Convert to DataFrame and sort
        ratings_df = pd.DataFrame.from_dict(self.ratings, orient='index')
        return ratings_df.sort_values('overall', ascending=False)