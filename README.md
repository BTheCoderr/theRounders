# The Rounders - Sports Betting Analytics Platform

A comprehensive sports betting analytics platform built with Streamlit, providing tools for line shopping, sharp movement tracking, power rankings, analytics, and bet tracking.

## Features

- **Line Shopping**: Compare odds across different sportsbooks and find the best lines
- **Sharp Movement Tracker**: Track sharp money movements and line changes
- **Power Rankings**: View comprehensive team ratings and matchup predictions
- **Analytics**: Analyze betting performance with detailed metrics and visualizations
- **Bet Tracking**: Log and track bets with detailed record keeping

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
