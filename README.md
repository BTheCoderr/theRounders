# The Rounders - Sports Betting Analytics Platform

A comprehensive sports betting analytics platform inspired by Bill Walters' systematic approach to sports betting. Built with Python and Streamlit, this platform combines advanced statistical analysis, real-time odds tracking, and professional betting principles to provide a powerful toolkit for data-driven sports betting.

## Key Features

### 📊 Line Shopping
- Real-time odds comparison across major sportsbooks
- Automated arbitrage opportunity detection
- Line movement tracking and visualization
- Steam move alerts and sharp money indicators
- Best line recommendations with calculated edges

### 📈 Sharp Movement Tracker
- Track professional betting patterns and steam moves
- Reverse line movement detection
- Sharp money percentage analysis
- Real-time alerts for significant line movements
- Historical sharp action analysis

### 🏆 Power Rankings
- Advanced team rating systems (Massey, Elo, custom algorithms)
- Predictive modeling for game outcomes
- Strength of schedule analysis
- Home/away performance adjustments
- Conference and division strength metrics

### 📊 Analytics Dashboard
- Comprehensive betting performance metrics
- ROI analysis by sport and bet type
- Closing line value (CLV) tracking
- Bankroll management tools
- Advanced visualization of betting patterns

### 📝 Bet Tracking
- Detailed bet logging and management
- Performance analytics and trend analysis
- Kelly Criterion-based bet sizing
- Automated record keeping
- Historical performance review

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python, SQLite
- **Data Analysis**: Pandas, NumPy, Plotly
- **APIs**: The Odds API, Sports Data APIs
- **ML/Stats**: Scikit-learn, SciPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/theRounders.git
cd theRounders
```

2. Create a virtual environment and activate it:
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
cp .env.template .env
```
Edit `.env` with your API keys and configuration.

## Configuration

The application requires the following environment variables:

- `ODDS_API_KEY`: Your API key for odds data
- `SPORTS_API_KEY`: Your API key for sports data
- `DB_PATH`: Path to the SQLite database file
- `PAPER_TRADING`: Set to true for paper trading mode
- `DEFAULT_STAKE`: Default stake amount for bets
- `UPDATE_INTERVAL`: Data update interval in seconds
- `ENABLED_BOOKS`: List of enabled sportsbooks

## Usage

1. Start the Streamlit application:
```bash
streamlit run streamlit_app.py
```

2. Open your browser and navigate to `http://localhost:8501`

## Project Structure

```
theRounders/
├── streamlit_app.py        # Main application file
├── pages/                  # Streamlit pages
│   ├── 1_📊_Line_Shopping.py
│   ├── 2_📈_Sharp_Movement.py
│   ├── 3_🏆_Power_Rankings.py
│   ├── 4_📊_Analytics.py
│   └── 5_📝_Bet_Tracking.py
├── data/                   # Data directory
│   └── betting.db         # SQLite database
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
└── README.md              # Project documentation
```

## Features in Detail

### Line Shopping
- Real-time odds tracking from multiple sportsbooks
- Automated arbitrage detection
- Line movement visualization
- Best line recommendations
- Sharp money tracking

### Sharp Movement Tracker
- Professional betting pattern analysis
- Steam move detection
- Reverse line movement alerts
- Sharp money percentage tracking
- Historical sharp action analysis

### Power Rankings
- Multiple rating systems
- Predictive modeling
- Strength of schedule analysis
- Team performance metrics
- Conference strength analysis

### Analytics
- Comprehensive performance tracking
- ROI analysis
- CLV monitoring
- Bankroll management
- Advanced visualizations

### Bet Tracking
- Detailed record keeping
- Performance analytics
- Kelly Criterion calculator
- Historical analysis
- Trend visualization

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is for educational and entertainment purposes only. Please gamble responsibly and be aware of the laws and regulations in your jurisdiction regarding sports betting.

## Acknowledgments

- Inspired by Bill Walters' systematic approach to sports betting
- Built with principles from professional sports bettors
- Uses various open-source sports data APIs
- Community contributions and feedback
