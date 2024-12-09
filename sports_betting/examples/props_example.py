from sports_betting.analysis.advanced_props_system import AdvancedPropsSystem
import asyncio

async def main(): 
    # Initialize system
    props_system = AdvancedPropsSystem()

    # Analyze prop
    prop = {
        'sport': 'NBA',
        'player': 'Nikola Jokic',
        'prop_type': 'assists',
        'line': 8.5,
        'game_id': 'DEN_vs_LAL_2024_01_01'
    }

    # Get comprehensive analysis
    analysis = await props_system.analyze_all_factors(prop)

    # Print results
    print(f"\nCorrelation Impact: {analysis['correlations']['impact_scores']}")
    print(f"Injury Impact: {analysis['injury_impact']['total_impact']}")
    print(f"Lineup Impact: {analysis['lineup_impact']['minutes_projection']}")

    if analysis['bet_placed']:
        print(f"\nBet placed at {analysis['bet_placed']['sportsbook']}")
        print(f"Stake: {analysis['bet_placed']['stake']}")
        print(f"Odds: {analysis['bet_placed']['odds']}")

if __name__ == "__main__":
    asyncio.run(main()) 