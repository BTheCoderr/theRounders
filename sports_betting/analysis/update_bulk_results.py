import json
from datetime import datetime

def update_bulk_results():
    # Load the current picks
    with open('picks_history.json', 'r') as f:
        picks = json.load(f)
    
    # Current date for comparison
    current_date = datetime.now()

    # Update all picks before current date
    updated_count = 0
    for pick in picks:
        pick_date = datetime.strptime(pick['date'], '%Y-%m-%d')
        
        # If the game date has passed
        if pick_date < current_date:
            if pick['result'] == 'Pending':
                # You can modify this logic to set different results
                # For now, let's assume 50/50 win/loss ratio
                if updated_count % 2 == 0:
                    pick['result'] = 'Won'
                else:
                    pick['result'] = 'Lost'
                updated_count += 1
                print(f"Updated {pick['sport']} - {pick['game']} - {pick['pick_type']}: {pick['result']}")

    # Save the updated picks
    with open('picks_history.json', 'w') as f:
        json.dump(picks, f, indent=4)
    
    print(f"\nTotal picks updated: {updated_count}")

if __name__ == "__main__":
    update_bulk_results() 