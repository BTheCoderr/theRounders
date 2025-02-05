from sports_betting.analysis.advanced_ml_systems import AdvancedMLSystems
import pandas as pd
import asyncio

def load_market_data():
    """Load historical market data"""
    return pd.read_csv('data/market_history.csv')

def load_betting_data():
    """Load historical betting data"""
    return pd.read_csv('data/betting_history.csv')

def load_performance_data():
    """Load performance metrics"""
    return pd.read_csv('data/performance_history.csv')

async def main():
    # Initialize systems
    ml_systems = AdvancedMLSystems()

    # Load data
    data = {
        'market_data': load_market_data(),
        'betting_data': load_betting_data(),
        'performance_data': load_performance_data()
    }

    # Run all systems
    results = await ml_systems.run_all_systems(data)

    # Print GAN results
    print("\nAdvanced GAN Results:")
    for arch, perf in results['gan']['performance'].items():
        print(f"{arch} Accuracy: {perf['accuracy']:.2%}")
        print(f"{arch} Loss: {perf['loss']:.4f}")

    # Print RL results
    print("\nRL Agent Results:")
    for agent, perf in results['rl']['results'].items():
        print(f"{agent} Total Reward: {perf['total_reward']:.2f}")
        print(f"{agent} Win Rate: {perf['win_rate']:.2%}")

    # Print Bayesian Optimization results
    print("\nBayesian Optimization Results:")
    print(f"Best Parameters: {results['bayesian']['best_params']}")
    print(f"Best Score: {results['bayesian']['best_score']:.4f}")

    # Print Risk Scenario results
    print("\nRisk Scenario Analysis:")
    for scenario, result in results['risk']['scenario_results'].items():
        print(f"\n{scenario} Impact:")
        print(f"Max Loss: ${result['max_loss']:,.2f}")
        print(f"Recovery Time: {result['recovery_time']} days")

    # Print Real-time Monitoring
    print("\nReal-time Performance Metrics:")
    for metric, value in results['monitor']['metrics'].items():
        print(f"{metric}: {value:.4f}")

if __name__ == "__main__":
    asyncio.run(main()) 