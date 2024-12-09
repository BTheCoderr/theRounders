from sports_betting.analysis.advanced_monitoring import AdvancedMonitoringSystem
from datetime import datetime
import asyncio

# Initialize monitoring system
monitoring = AdvancedMonitoringSystem()

# Create data stream
data_stream = asyncio.Queue()

# Sample data generator
async def generate_data():
    while True:
        data = {
            'timestamp': datetime.now(),
            'executions': [
                {
                    'id': 1,
                    'price': 110.5,
                    'size': 100,
                    'impact': 0.002
                }
            ],
            'market_data': {
                'volatility': 0.15,
                'liquidity': 10000,
                'spread': 0.01
            }
        }
        await data_stream.put(data)
        await asyncio.sleep(1)

# Start monitoring
async def main():
    # Start data generator
    asyncio.create_task(generate_data())
    
    # Start monitoring
    await monitoring.monitor(data_stream)

# Run the system
if __name__ == '__main__':
    asyncio.run(main()) 