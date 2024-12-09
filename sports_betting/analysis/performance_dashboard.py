import matplotlib.pyplot as plt
import json

def plot_performance():
    with open('picks_history.json', 'r') as f:
        picks = json.load(f)
    
    # Calculate performance metrics
    total_picks = len(picks)
    won = sum(1 for pick in picks if pick['result'] == 'Won')
    lost = sum(1 for pick in picks if pick['result'] == 'Lost')
    win_rate = (won / total_picks) * 100 if total_picks > 0 else 0
    
    # Plot results
    labels = ['Won', 'Lost']
    sizes = [won, lost]
    colors = ['#4CAF50', '#F44336']
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title(f'Performance Dashboard\nTotal Picks: {total_picks} | Win Rate: {win_rate:.1f}%')
    plt.show()

if __name__ == "__main__":
    plot_performance() 