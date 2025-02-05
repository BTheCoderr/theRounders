from sports_betting.analysis.advanced_ml_execution import AdvancedMLExecution
import asyncio

async def main():
    # Initialize system
    ml_execution = AdvancedMLExecution()

    # Sample orders
    orders = [
        {
            'id': 1,
            'asset': 'NFL_SPREAD',
            'size': 1000,
            'side': 'BUY',
            'type': 'LIMIT',
            'price': 110,
            'urgency': 'HIGH',
            'constraints': {
                'max_impact': 0.02,
                'min_execution_rate': 0.3
            }
        },
        {
            'id': 2,
            'asset': 'NBA_TOTAL',
            'size': 500,
            'side': 'SELL',
            'type': 'MARKET',
            'urgency': 'MEDIUM',
            'constraints': {
                'max_impact': 0.015,
                'min_execution_rate': 0.4
            }
        }
    ]

    # Execute with ML models
    results = await ml_execution.execute_with_ml(orders)

    # Print results
    print("\nML Predictions:")
    for order_id, preds in results['predictions'].items():
        print(f"\nOrder {order_id} Predictions:")
        print(f"Impact: {preds['impact']:.4f}")
        print(f"Optimal Size: {preds['optimal_size']}")
        print(f"Timing Score: {preds['timing_score']:.2f}")

    print("\nRisk Metrics:")
    for metric, value in results['risk_metrics'].items():
        print(f"{metric}: {value:.4f}")

    print("\nPerformance Analytics:")
    for metric, value in results['analytics'].items():
        print(f"{metric}: {value:.4f}")

    print("\nExecution Results:")
    for order_id, result in results['execution_results'].items():
        print(f"\nOrder {order_id}:")
        print(f"Average Price: {result['avg_price']}")
        print(f"Market Impact: {result['impact']:.4f}")
        print(f"Execution Quality: {result['quality_score']:.2f}")

if __name__ == "__main__":
    asyncio.run(main()) 