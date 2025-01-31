# The Rounders Sports Betting Analytics Platform 🎯

A comprehensive sports betting analytics platform that provides advanced statistics, predictions, and tracking for NBA, NFL, NHL, and MLB betting. Built with Bill Walters' principles in mind, focusing on data-driven decisions, line shopping, and proper bankroll management.

## Features 🌟

### Core Analytics
- Real-time odds collection from multiple sportsbooks
- Advanced statistical analysis and predictions
- Power rankings and team strength metrics
- Line movement tracking and steam move detection
- Arbitrage opportunity detection
- Kelly Criterion-based bankroll management

### Sports Coverage
- NBA: Spreads, moneylines, totals, player props
- NFL: Game lines, player props, team totals
- MLB: Moneylines, run lines, player props
- NHL: Puck lines, moneylines, totals

### AI/ML Integration
- LSTM models for player prop predictions
- Ensemble models for game predictions
- Power rankings based on multiple factors
- Bayesian optimization for model tuning

### Betting Strategy Tools
- Kelly Criterion calculator
- Hedging calculator
- Arbitrage finder
- Line movement alerts
- Best odds comparison

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/theRounders.git
cd theRounders
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration ⚙️

1. Add your API keys to `.env`:
```
ODDS_API_KEY=your_key_here
SPORTSDATA_API_KEY=your_key_here
BETFAIR_API_KEY=your_key_here
```

2. Configure supported sportsbooks in `sports_betting/config/settings.py`

3. Adjust model parameters and betting strategies in the configuration files

## Usage 📊

### Starting the API Server
```bash
uvicorn sports_betting.web_interface.app:app --reload
```

### Starting the Web Interface
```bash
streamlit run sports_betting.web_interface.streamlit_app.py
```

### Running Tests
```bash
pytest tests/
```

## Features in Detail 📈

### Odds Collection
- Real-time odds from multiple sportsbooks
- Line movement tracking
- Steam move detection
- Best odds comparison

### Predictions
- Game predictions with confidence levels
- Player prop predictions using LSTM
- Power rankings and team strength metrics
- Weather impact analysis

### Bet Tracking
- Detailed bet history
- Performance analytics
- ROI tracking
- Confidence level analysis
- Time-based performance analysis

### Risk Management
- Kelly Criterion implementation
- Bankroll management
- Hedging calculator
- Risk exposure analysis

## API Documentation 📚

The API documentation is available at `http://localhost:8000/docs` when running the server.

### Key Endpoints
- `/api/odds/{sport}`: Get current odds
- `/api/predictions/game`: Get game predictions
- `/api/predictions/props`: Get player prop predictions
- `/api/arbitrage/{sport}`: Get arbitrage opportunities
- `/api/bets/analytics`: Get betting analytics

## Web Interface 🖥️

The Streamlit interface provides:
1. Dashboard with key metrics
2. Live odds monitoring
3. Prediction interface
4. Bet tracking and analysis
5. Settings management

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📝

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- Built with principles from professional sports bettors
- Inspired by Bill Walters' systematic approach
- Uses various open-source sports data APIs

## Disclaimer ⚠️

This software is for educational purposes only. Please be aware of and comply with your local laws and regulations regarding sports betting.
