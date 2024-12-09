import pandas as pd
from sports_betting.analysis.advanced_ml_optimization import AdvancedMLOptimization
import asyncio

def load_pattern_data():
    """Load historical betting patterns"""
    return pd.read_csv('data/betting_patterns.csv')

def load_performance_data():
    """Load performance history"""
    return pd.read_csv('data/performance_history.csv')

def load_risk_data():
    """Load risk metrics"""
    return pd.read_csv('data/risk_metrics.csv')

async def main():
    # Initialize optimizer
    optimizer = AdvancedMLOptimization()

    # Load data
    data = {
        'patterns': load_pattern_data(),
        'performance': load_performance_data(),
        'risk': load_risk_data()
    }

    # Run optimization
    results = await optimizer.optimize_all(data)

    # Print GAN results
    print("\nGAN Pattern Generation:")
    print(f"Discriminator Accuracy: {results['gan']['performance']['accuracy']:.2%}")
    print(f"Generator Loss: {results['gan']['performance']['loss']:.4f}")

    # Print AutoML results
    print("\nAutoML Optimization:")
    print(f"Best Model: {results['automl']['best_params']['model_type']}")
    print(f"Validation Score: {results['automl']['performance']['val_score']:.4f}")

    # Print Risk Analysis
    print("\nRisk Analysis:")
    print(f"Current Exposure: {results['risk']['risk_metrics']['exposure']:.2%}")
    print(f"Recommended Adjustments: {results['risk']['adjustments']}")

    # Print Performance Attribution
    print("\nPerformance Attribution:")
    for factor, contribution in results['performance']['attribution'].items():
        print(f"{factor}: {contribution:.2%}")

    # Print Recommendations
    print("\nRecommendations:")
    for rec in results['performance']['recommendations']:
        print(f"- {rec}")

if __name__ == "__main__":
    asyncio.run(main()) 