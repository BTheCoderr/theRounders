import json

def simulate_betting_strategy(picks_history, initial_bankroll):
    bankroll = initial_bankroll
    for pick in picks_history:
        try:
            bet_amount = pick.get('bet_amount', 0)  # Use get() with default value
            odds = pick.get('odds', 0)
            result = pick.get('result', '')
            
            if result == 'Won':
                bankroll += bet_amount * (odds - 1)
            elif result == 'Lost':
                bankroll -= bet_amount
                
        except Exception as e:
            print(f"Error processing pick: {e}")
            continue
            
    return bankroll

def test_strategy():
    try:
        # Load historical picks
        with open('picks_history.json', 'r') as f:
            picks_history = json.load(f)
        
        # Simulate strategy
        final_bankroll = simulate_betting_strategy(picks_history, 10000)
        print(f"Final bankroll after simulation: ${final_bankroll:.2f}")
        
    except FileNotFoundError:
        print("No picks history found. Creating empty history.")
        with open('picks_history.json', 'w') as f:
            json.dump([], f)
        return 0
    except Exception as e:
        print(f"Error in test strategy: {e}")
        return 0

if __name__ == "__main__":
    test_strategy() 