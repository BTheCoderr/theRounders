from sports_betting.analysis.advanced_ml_optimization import AdvancedMLOptimization
import pandas as pd
import asyncio

async def main():
    # Initialize system
    optimizer = AdvancedMLOptimization()

    # Load historical betting data
    data = {
        'historical': pd.read_csv('data/historical_bets.csv'),
        'features': [
            'odds', 'line', 'public_money', 'sharp_money',
            'weather', 'rest_days', 'h2h_record'
        ],
        'target': 'result'
    }

    # Run optimization
    results = await optimizer.optimize_all(data)

    # Print Neural Network Results
    print("\nNeural Network Performance:")
    nn_results = results['torch_net']
    print(f"Training Loss: {nn_results['performance']['train_loss']:.4f}")
    print(f"Validation Loss: {nn_results['performance']['val_loss']:.4f}")
    print(f"Accuracy: {nn_results['performance']['accuracy']:.2%}")

    # Print Ensemble Results
    print("\nEnsemble Model Performance:")
    ensemble = results['automl']
    print(f"Best Model: {ensemble['best_params']['model_type']}")
    print(f"Feature Importance:")
    for feat, imp in ensemble['feature_importance'].items():
        print(f"- {feat}: {imp:.3f}")

    # Print Real-time Optimization
    print("\nReal-time Pattern Performance:")
    patterns = results['real_time']
    print(f"Pattern Count: {len(patterns['optimized_patterns'])}")
    print(f"Performance Delta: {patterns['performance_delta']:.2%}")

    # Print Risk Analysis
    print("\nRisk Analysis:")
    risk = results['risk']
    print(f"Current Exposure: {risk['risk_metrics']['exposure']:.2%}")
    print(f"Recommended Position Sizes:")
    for pos in risk['positions'][:3]:
        print(f"- {pos['name']}: ${pos['size']:.2f}")

if __name__ == "__main__":
    asyncio.run(main()) 