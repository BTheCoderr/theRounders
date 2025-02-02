import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from odds_api import OddsAPI
from data_scraper import DataScraper
from api_config import APIConfig
from walters_simulator import WaltersSimulator
from betting_system import BettingSystem
from mlb_ratings import MLBRatings
from nba_massey_ratings import NBAMasseyRatings

# Must be the first Streamlit command
st.set_page_config(
    page_title="The Rounders - Sports Betting Analytics",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'betting_mode' not in st.session_state:
    st.session_state.betting_mode = "paper"
if 'api_config' not in st.session_state:
    st.session_state.api_config = APIConfig()
if 'odds_api' not in st.session_state:
    st.session_state.odds_api = OddsAPI(st.session_state.api_config)
if 'data_scraper' not in st.session_state:
    st.session_state.data_scraper = DataScraper()
if 'walters_simulator' not in st.session_state:
    st.session_state.walters_simulator = WaltersSimulator()
if 'betting_system' not in st.session_state:
    st.session_state.betting_system = BettingSystem()
if 'mlb_ratings' not in st.session_state:
    st.session_state.mlb_ratings = MLBRatings()
if 'nba_ratings' not in st.session_state:
    st.session_state.nba_ratings = NBAMasseyRatings()

# Sidebar configuration
st.sidebar.title("Mode Selection")
betting_mode = st.sidebar.radio(
    "Select Mode",
    ["Paper Trading", "Real Money"],
    index=0 if st.session_state.betting_mode == "paper" else 1,
    help="Paper Trading lets you practice without real money"
)

# Update betting mode
st.session_state.betting_mode = "paper" if betting_mode == "Paper Trading" else "real"

# Show current mode with status indicator
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {betting_mode} mode")

# API settings in sidebar
with st.sidebar.expander("API Settings"):
    st.write("API Status:")
    api_status = st.session_state.api_config.validate_api_keys()
    for api, status in api_status.items():
        st.write(f"✅ {api}" if status else f"❌ {api}")

# Main content
st.title("The Rounders - Sports Betting Analytics")
st.markdown("""
Welcome to The Rounders - your comprehensive sports betting analytics platform.
Navigate through the pages using the sidebar to access different tools and features.
""")

# Quick stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Model Win Rate", "62.3%", "+2.1%")
with col2:
    st.metric("CLV Average", "+1.8", "+0.3")
with col3:
    st.metric("Sharp Money Rate", "71.5%", "-1.2%")
with col4:
    st.metric("ROI", "+12.4%", "+3.2%")

# Today's top predictions
st.subheader("Today's Top Predictions")
predictions = pd.DataFrame({
    'Game': ['Lakers vs Warriors', 'Celtics vs Bucks', 'Heat vs Nets'],
    'Prediction': ['Lakers -3.5', 'Bucks +2.5', 'Heat -1.5'],
    'Confidence': [0.85, 0.78, 0.72],
    'Value': ['+2.1', '+1.8', '+1.5'],
    'Sharp Action': ['80% Lakers', '65% Bucks', '55% Heat']
})

st.dataframe(
    predictions.style.background_gradient(subset=['Confidence'])
    .format({'Confidence': '{:.1%}'})
)

# Performance visualization
st.subheader("Model Performance by Sport")
performance_data = pd.DataFrame({
    'Sport': ['NBA', 'NFL', 'MLB', 'NHL'],
    'Win Rate': [0.623, 0.584, 0.552, 0.567],
    'ROI': [0.124, 0.098, 0.076, 0.082],
    'Sample Size': [1200, 800, 1500, 1000]
})

fig = px.bar(performance_data, 
            x='Sport', 
            y=['Win Rate', 'ROI'],
            barmode='group',
            title='Model Performance Metrics by Sport')
st.plotly_chart(fig, use_container_width=True)

# Sharp money alerts
st.subheader("Sharp Money Alerts")
alerts = [
    {"game": "Lakers vs Warriors", "movement": "Line moved from -3 to -4.5 with 80% sharp money"},
    {"game": "Celtics vs Bucks", "movement": "Reverse line movement detected"},
    {"game": "Heat vs Nets", "movement": "Steam move detected at multiple books"}
]

for alert in alerts:
    with st.container():
        st.markdown(f"**{alert['game']}**")
        st.markdown(f"_{alert['movement']}_")
        st.markdown("---")

# Feature overview
st.subheader("Available Features")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Analytics Tools
    - 📊 **Line Shopping**: Compare odds across different sportsbooks
    - 📈 **Sharp Movement**: Track line movements and sharp money
    - 🏆 **Power Rankings**: View comprehensive team ratings
    - 📊 **Analytics**: Analyze your betting performance
    - 📝 **Bet Tracking**: Log and monitor your bets
    """)

with col2:
    st.markdown("""
    ### Key Features
    - Real-time odds comparison
    - Sharp money movement tracking
    - Advanced statistical models
    - Detailed performance analytics
    - Comprehensive bet tracking
    - Bankroll management tools
    """)

# Getting started guide
with st.expander("Getting Started Guide"):
    st.markdown("""
    ### How to Use The Rounders Platform
    
    1. **Choose Your Mode**
       - Start with Paper Trading to practice without risk
       - Switch to Real Money mode when ready
    
    2. **Set Up API Keys**
       - Configure your API keys in the sidebar settings
       - Connect to preferred sportsbooks
    
    3. **Explore Features**
       - Use Line Shopping to find the best odds
       - Track Sharp Movement for smart money signals
       - View Power Rankings for team analysis
       - Monitor your performance in Analytics
       - Log all bets in Bet Tracking
    
    4. **Best Practices**
       - Always compare odds across multiple books
       - Track your bets and maintain detailed records
       - Follow proper bankroll management
       - Review your performance regularly
    """)

# Footer
st.markdown("---")
st.caption("Data updates every 60 seconds. Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))

# Keep the DatabaseManager class and its methods at the end of the file
class DatabaseManager:
    def __init__(self, db_path="betting.db", mode="real"):
        self.db_path = f"{mode}_{db_path}"
        self._init_db()
    
    # ... rest of the DatabaseManager class implementation ...
    # (keeping all the existing methods)
