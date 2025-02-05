from sports_betting.analysis.advanced_execution_system import AdvancedExecutionSystem
import asyncio

async def main():
    # Initialize system
    execution_system = AdvancedExecutionSystem()

    # Sample orders
    orders = [
        {
            'id': 1,
            'asset': 'NFL_SPREAD',
            'size': 1000,
            'side': 'BUY',
            'type': 'LIMIT',
            'price': 110
        },
        {
            'id': 2,
            'asset': 'NBA_TOTAL',
            'size': 500,
            'side': 'SELL',
            'type': 'MARKET'
        }
    ]

    # Execute strategy
    results = await execution_system.execute_strategy(orders)

    # Print execution results
    print("\nExecution Results:")
    for order_id, result in results['execution_results'].items():
        print(f"\nOrder {order_id}:")
        print(f"Average Price: {result['avg_price']}")
        print(f"Market Impact: {result['impact']:.4f}")
        print(f"Execution Time: {result['execution_time']:.2f}s")

    # Print hedging results
    print("\nHedging Results:")
    for hedge in results['hedging_results']['hedge_orders']:
        print(f"\nHedge for {hedge['asset']}:")
        print(f"Size: {hedge['size']}")
        print(f"Ratio: {hedge['hedge_ratio']:.2f}")

    # Print risk decomposition
    print("\nRisk Decomposition:")
    for component, risk in results['analysis']['risk_decomposition'].items():
        print(f"\n{component} Risk:")
        print(f"VaR: {risk['var']:.2f}")
        print(f"Expected Shortfall: {risk['es']:.2f}")

if __name__ == "__main__":
    asyncio.run(main()) 