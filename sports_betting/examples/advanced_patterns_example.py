from datetime import datetime, timedelta
from sports_betting.analysis.advanced_betting_patterns import AdvancedBettingPatterns
import asyncio

async def main():
    # Initialize pattern analyzer
    pattern_analyzer = AdvancedBettingPatterns()

    # Analyze patterns
    prop = {
        'id': 'NBA_PROP_123',
        'player': 'Stephen Curry',
        'prop_type': 'threes',
        'line': 4.5,
        'game_time': datetime.now() + timedelta(hours=2)
    }

    patterns = await pattern_analyzer.analyze_patterns(prop)

    # Print results
    print("\nSteam Patterns:")
    for pattern_type, pattern in patterns['steam']['patterns'].items():
        print(f"\nPattern Type: {pattern_type}")
        print(f"Confidence: {pattern.confidence:.2f}")
        print(f"Impact: {pattern.impact:.2f}")
        print(f"Books: {', '.join(pattern.books_involved)}")

    print("\nSharp Reversals:")
    for reversal in patterns['reversals']['reversals']:
        print(f"\nTime: {reversal['timestamp']}")
        print(f"Size: {reversal['size']}")
        print(f"Confidence: {reversal['confidence']:.2f}")

    print("\nML Pattern Recognition:")
    print(f"RF Confidence: {patterns['ml_patterns']['rf_confidence']:.2f}")
    print(f"Anomaly Score: {patterns['ml_patterns']['anomalies']}")
    print(f"Combined Score: {patterns['ml_patterns']['combined_score']:.2f}")

if __name__ == "__main__":
    asyncio.run(main()) 