import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def analyze_historical_data(picks_history):
    # Check if we have enough data
    if not picks_history or len(picks_history) < 2:
        print("Not enough historical data for analysis")
        return None
        
    # Prepare data for training
    X = [pick['features'] for pick in picks_history]
    y = [1 if pick['result'] == 'Won' else 0 for pick in picks_history]
    
    # Ensure we have enough samples for splitting
    if len(X) < 5:  # Minimum samples needed for meaningful split
        print("Need at least 5 samples for analysis")
        return None
        
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    return model

def monitor_real_time_odds():
    # Example API call to get real-time odds
    response = requests.get("https://api.sportsdata.io/v3/odds")
    if response.status_code == 200:
        odds_data = response.json()
        # Process and return the odds data
        return odds_data
    else:
        print("Failed to fetch real-time odds")
        return []

def manage_bankroll(bet_amount, bankroll, probability, odds):
    # Kelly Criterion formula
    kelly_fraction = (probability * (odds - 1) - (1 - probability)) / (odds - 1)
    bet_size = bankroll * kelly_fraction
    return min(bet_amount, bet_size)