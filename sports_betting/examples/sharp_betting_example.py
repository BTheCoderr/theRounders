from datetime import datetime, timedelta
from sports_betting.analysis.sharp_betting_analytics import SharpBettingAnalytics
import asyncio

async def main():
    # Initialize analytics
    sharp_analytics = SharpBettingAnalytics()

    # Analyze prop
    prop = {
        'id': 'NBA_PROP_123',
        'player': 'LeBron James',
        'prop_type': 'points',
        'line': 28.5,
        'game_time': datetime.now() + timedelta(hours=3)
    }

    # Get sharp analysis
    analysis = await sharp_analytics.analyze_market(prop)

    # Print results
    print("\nSharp Money Analysis:")
    print(f"Sharp Side: {analysis['analysis']['sharp_money']['sharp_side']}")
    print(f"Sharp Money %: {analysis['analysis']['sharp_money']['sharp_money_pct']:.1%}")
    print(f"Confidence: {analysis['analysis']['sharp_money']['confidence']:.1%}")

    print("\nSteam Move Detection:")
    for move in analysis['analysis']['steam_moves']['steam_moves']:
        print(f"Time: {move['timestamp']}")
        print(f"Direction: {move['direction']}")
        print(f"Magnitude: {move['magnitude']}")
        print(f"Books: {', '.join(move['books'])}")

    print("\nCLV Analysis:")
    print(f"Average CLV: {analysis['analysis']['clv_data']['average_clv']:.2%}")
    print(f"CLV Win Rate: {analysis['analysis']['clv_data']['clv_win_rate']:.1%}")

if __name__ == "__main__":
    asyncio.run(main()) 