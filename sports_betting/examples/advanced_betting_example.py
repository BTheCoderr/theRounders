from sports_betting.analysis.advanced_betting_system import AdvancedBettingSystem
import asyncio

async def main():
    # Initialize system
    betting_system = AdvancedBettingSystem()

    # Scan for opportunities
    opportunities = await betting_system.scan_all_opportunities()

    # Print results
    print("\nStraight Bet Opportunities:")
    for bet in opportunities['straight_bets']:
        print(f"Prop: {bet['player']} {bet['prop_type']}")
        print(f"Line: {bet['line']} @ {bet['odds']}")
        print(f"Recommended Size: ${bet['bet_sizes']['amount']:.2f}")

    print("\nArbitrage Opportunities:")
    for arb in opportunities['arbitrage']:
        print(f"Profit: {arb['profit_pct']:.2%}")
        print(f"Over: {arb['over']['sportsbook']} @ {arb['over']['odds']}")
        print(f"Under: {arb['under']['sportsbook']} @ {arb['under']['odds']}")

    print("\nCorrelated Parlay Opportunities:")
    for parlay in opportunities['parlays']:
        print(f"Expected Value: {parlay['ev']:.2%}")
        print("Legs:")
        for leg in parlay['legs']:
            print(f"- {leg['player']} {leg['prop_type']} {leg['line']}")

if __name__ == "__main__":
    asyncio.run(main()) 