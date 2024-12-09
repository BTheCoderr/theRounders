import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
# or from sklearn.ensemble import RandomForestRegressor for more complex predictions

def predict_next_ppg(player_data):
    # Assuming player_data is a DataFrame with historical game data
    # Example structure:
    # player_data columns: ['date', 'points', 'minutes_played', 'opponent', etc.]
    
    # Create features (you might want to use last N games)
    X = player_data[['minutes_played', 'field_goal_percentage', 'previous_points']].values
    y = player_data['points'].values
    
    # Fit model
    model = LinearRegression()
    model.fit(X[:-1], y[1:])  # Train on all but last game
    
    # Predict next game
    next_game_prediction = model.predict(X[-1:])
    
    return next_game_prediction[0]

# Example usage:
# prediction = predict_next_ppg(player_historical_data)
# print(f"Predicted points for next game: {prediction:.1f}")
