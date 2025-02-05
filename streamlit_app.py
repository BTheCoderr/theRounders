import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
import asyncio
from odds_api import OddsAPI
from data_scraper import DataScraper
from api_config import APIConfig
from walters_simulator import WaltersSimulator

class DatabaseManager:
    def __init__(self, db_path="betting.db", mode="real"):
        self.db_path = f"{mode}_{db_path}"
        self._init_db()
    
    # ... existing DatabaseManager methods ...
    # Copy all methods from the original DatabaseManager class here
    def _init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create bets table with additional sharp betting fields
        c.execute('''
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                sport TEXT,
                game TEXT,
                bet_type TEXT,
                pick TEXT,
                odds REAL,
                stake REAL,
                confidence INTEGER,
                notes TEXT,
                status TEXT,
                result TEXT,
                profit_loss REAL,
                closing_line REAL,
                steam_move BOOLEAN,
                reverse_line_movement BOOLEAN,
                sharp_confidence REAL,
                public_percentage REAL,
                opening_line REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create line_movements table
        c.execute('''
            CREATE TABLE IF NOT EXISTS line_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bet_id INTEGER,
                timestamp TIMESTAMP,
                odds REAL,
                book TEXT,
                volume REAL,
                is_sharp BOOLEAN,
                FOREIGN KEY (bet_id) REFERENCES bets (id)
            )
        ''')
        
        # Create books table for line shopping
        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                api_name TEXT,
                is_active BOOLEAN
            )
        ''')
        
        # Insert default sportsbooks
        default_books = [
            ('DraftKings', 'draftkings', 1),
            ('FanDuel', 'fanduel', 1),
            ('BetMGM', 'betmgm', 1),
            ('Caesars', 'caesars', 1),
            ('PointsBet', 'pointsbet', 1)
        ]
        
        c.executemany(
            'INSERT OR IGNORE INTO books (name, api_name, is_active) VALUES (?, ?, ?)',
            default_books
        )
        
        conn.commit()
        conn.close()

    def add_bet(self, bet_data):
        """Add a new bet to the database."""
        conn = sqlite3.connect(self.db_path)
        
        # Convert dict to DataFrame for easier handling
        df = pd.DataFrame([bet_data])
        df.to_sql('bets', conn, if_exists='append', index=False)
        
        conn.close()
        return True
    
    def get_bets(self, filters=None):
        """Get all bets with optional filters."""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM bets"
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = '{value}'")
            query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def update_bet(self, bet_id, update_data):
        """Update an existing bet."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [bet_id]
        
        c.execute(f"UPDATE bets SET {set_clause} WHERE id = ?", values)
        
        conn.commit()
        conn.close()
        return True
    
    def calculate_kelly_criterion(self, odds, win_probability):
        """Calculate Kelly Criterion bet size."""
        if odds <= 0:  # Convert American odds to decimal
            decimal_odds = 1 - (100 / odds)
        else:
            decimal_odds = (odds / 100) + 1
        
        q = 1 - win_probability
        b = decimal_odds - 1
        
        kelly = (b * win_probability - q) / b
        return max(0, kelly)  # Kelly can't be negative for betting purposes

    def get_analytics(self):
        """Get comprehensive betting analytics."""
        conn = sqlite3.connect(self.db_path)
        
        # Get all completed bets
        df = pd.read_sql_query(
            "SELECT * FROM bets WHERE result IS NOT NULL",
            conn
        )
        
        if df.empty:
            conn.close()
            return {"error": "No completed bets found"}
        
        # Calculate overall metrics
        total_bets = len(df)
        wins = len(df[df['result'] == 'Won'])
        win_rate = wins / total_bets
        total_profit = df['profit_loss'].sum()
        total_wagered = df['stake'].sum()
        roi = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0
        
        # Performance by sport
        sport_performance = df.groupby('sport').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum',
            'stake': 'sum'
        }).reset_index()
        sport_performance['roi'] = (sport_performance['profit_loss'] / sport_performance['stake']) * 100
        
        # Performance by bet type
        type_performance = df.groupby('bet_type').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum',
            'stake': 'sum'
        }).reset_index()
        type_performance['roi'] = (type_performance['profit_loss'] / type_performance['stake']) * 100
        
        # Trends over time
        time_performance = df.sort_values('date').set_index('date')
        time_performance['cumulative_pl'] = time_performance['profit_loss'].cumsum()
        time_performance['cumulative_roi'] = (
            time_performance['cumulative_pl'] / 
            time_performance['stake'].cumsum()
        ) * 100
        
        # Steam move analysis
        steam_performance = df.groupby('steam_move').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum'
        }).reset_index()
        
        # Closing line value analysis
        df['clv'] = df.apply(
            lambda x: x['closing_line'] - x['odds'] if x['result'] == 'Won'
            else x['odds'] - x['closing_line'],
            axis=1
        )
        
        analytics = {
            'overall': {
                'total_bets': total_bets,
                'win_rate': win_rate,
                'profit_loss': total_profit,
                'roi': roi
            },
            'by_sport': sport_performance.to_dict('records'),
            'by_type': type_performance.to_dict('records'),
            'trends': {
                'dates': time_performance.index.tolist(),
                'cumulative_pl': time_performance['cumulative_pl'].tolist(),
                'cumulative_roi': time_performance['cumulative_roi'].tolist()
            },
            'steam_moves': steam_performance.to_dict('records'),
            'clv_analysis': {
                'average_clv': df['clv'].mean(),
                'clv_correlation': df['clv'].corr(df['profit_loss'])
            }
        }
        
        conn.close()
        return analytics

    def add_line_movement(self, bet_id, odds, book, volume=None, is_sharp=False):
        """Record a line movement for a bet."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO line_movements (bet_id, timestamp, odds, book, volume, is_sharp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bet_id, datetime.now(), odds, book, volume, is_sharp))
        
        conn.commit()
        conn.close()
        return True
    
    def get_line_movements(self, bet_id=None, minutes=60):
        """Get line movements for analysis."""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT * FROM line_movements 
            WHERE timestamp >= datetime('now', ?) 
        """
        params = [f'-{minutes} minutes']
        
        if bet_id:
            query += " AND bet_id = ?"
            params.append(bet_id)
            
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def get_sharp_analytics(self):
        """Get analytics focused on sharp betting patterns."""
        conn = sqlite3.connect(self.db_path)
        
        # Get all completed bets with sharp indicators
        df = pd.read_sql_query("""
            SELECT 
                b.*,
                COUNT(lm.id) as line_movement_count,
                AVG(CASE WHEN lm.is_sharp THEN 1 ELSE 0 END) as sharp_movement_ratio
            FROM bets b
            LEFT JOIN line_movements lm ON b.id = lm.bet_id
            WHERE b.result IS NOT NULL
            GROUP BY b.id
        """, conn)
        
        if df.empty:
            conn.close()
            return {"error": "No completed bets found"}
        
        # Calculate CLV performance
        df['clv'] = df.apply(
            lambda x: x['closing_line'] - x['odds'] if x['result'] == 'Won'
            else x['odds'] - x['closing_line'],
            axis=1
        )
        
        # Steam move performance
        steam_performance = df.groupby('steam_move').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum',
            'clv': 'mean'
        }).reset_index()
        
        # RLM performance
        rlm_performance = df.groupby('reverse_line_movement').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum',
            'clv': 'mean'
        }).reset_index()
        
        # Sharp confidence correlation
        sharp_corr = df['sharp_confidence'].corr(df['profit_loss'])
        
        analytics = {
            'steam_moves': steam_performance.to_dict('records'),
            'reverse_line_movement': rlm_performance.to_dict('records'),
            'sharp_confidence_correlation': sharp_corr,
            'avg_clv': df['clv'].mean(),
            'clv_by_confidence': df.groupby(pd.qcut(df['sharp_confidence'], 4))['clv'].mean().to_dict()
        }
        
        conn.close()
        return analytics

# Initialize API clients
@st.cache_resource
def init_clients():
    return {
        'odds_api': OddsAPI(),
        'data_scraper': DataScraper(),
        'config': APIConfig(),
        'simulator': WaltersSimulator()
    }

clients = init_clients()

# Configure the app
st.set_page_config(
    page_title="The Rounders - Sports Betting Analytics",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state for mode selection
if 'betting_mode' not in st.session_state:
    st.session_state.betting_mode = "paper"

# Mode selection in sidebar
st.sidebar.title("Mode Selection")
betting_mode = st.sidebar.radio(
    "Select Mode",
    ["Paper Trading", "Real Money"],
    index=0,
    help="Paper Trading lets you practice without real money"
)

# Update the betting mode and database
if betting_mode == "Paper Trading":
    st.session_state.betting_mode = "paper"
else:
    st.session_state.betting_mode = "real"

# Initialize database with selected mode
if 'db' not in st.session_state or st.session_state.get('last_mode') != st.session_state.betting_mode:
    st.session_state.db = DatabaseManager(mode=st.session_state.betting_mode)
    st.session_state.last_mode = st.session_state.betting_mode

# Show current mode
st.sidebar.info(f"Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["Dashboard", "Line Shopping", "Sharp Movement", "Walters Mode", "Support", "Settings"]
)

# Add chatbot toggle in sidebar
show_chatbot = st.sidebar.checkbox("Show Chatbot", value=False)

if show_chatbot:
    st.sidebar.markdown("---")
    with st.sidebar.expander("Chatbot", expanded=True):
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("How can I help you?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Add basic responses based on keywords
            response = "I'll help you with that. Please create a support ticket if you need more detailed assistance."
            if "odds" in prompt.lower():
                response = "I can help you find the latest odds. Check the Line Shopping page for real-time odds across different bookmakers."
            elif "bet" in prompt.lower():
                response = "For betting assistance, check out our Walters Mode page for professional betting strategies."
            
            st.session_state.messages.append({"role": "assistant", "content": response})

# Update sports selection
SPORTS = {
    "NFL": {"api_name": "americanfootball_nfl", "icon": "🏈"},
    "NBA": {"api_name": "basketball_nba", "icon": "🏀"},
    "MLB": {"api_name": "baseball_mlb", "icon": "⚾"},
    "NHL": {"api_name": "icehockey_nhl", "icon": "🏒"},
    "UFC/MMA": {"api_name": "mma_mixed_martial_arts", "icon": "🥊"},
    "Soccer - EPL": {"api_name": "soccer_epl", "icon": "⚽"},
    "Soccer - Champions League": {"api_name": "soccer_uefa_champs_league", "icon": "⚽"},
    "Tennis": {"api_name": "tennis_atp", "icon": "🎾"},
    "Golf": {"api_name": "golf_pga", "icon": "⛳"},
    "NCAAB": {"api_name": "basketball_ncaab", "icon": "🏀"},
    "NCAAF": {"api_name": "americanfootball_ncaaf", "icon": "🏈"}
}

# Settings in sidebar
with st.sidebar.expander("API Settings"):
    st.write("API Status:")
    api_status = clients['config'].validate_api_keys()
    for api, status in api_status.items():
        st.write(f"✅ {api}" if status else f"❌ {api}")

# Main content
if page == "Dashboard":
    st.title("Sports Betting Dashboard")
    
    # Sport selection
    sport = st.selectbox(
        "Select Sport",
        options=list(clients['config'].SUPPORTED_SPORTS.keys())
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Live Odds")
        odds_data = clients['odds_api'].get_odds(sport)
        if odds_data:
            for game, data in odds_data.items():
                with st.expander(game):
                    st.write(f"Start time: {data['commence_time']}")
                    for book, book_data in data['bookmakers'].items():
                        st.write(f"\n{book}:")
                        for market, outcomes in book_data['markets'].items():
                            st.write(f"{market}: {outcomes}")
    
    with col2:
        st.subheader("Recent Scores")
        scores = clients['odds_api'].get_scores(sport)
        if scores:
            for game, data in scores.items():
                st.write(f"{game}: {data['scores']}")

elif page == "Line Shopping":
    st.title("Line Shopping")
    
    sport = st.selectbox(
        "Select Sport",
        options=list(clients['config'].SUPPORTED_SPORTS.keys())
    )
    
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        st.empty()
        while True:
            odds_data = clients['odds_api'].get_odds(sport)
            if odds_data:
                for game, data in odds_data.items():
                    with st.expander(game):
                        best_odds = {}
                        for book, book_data in data['bookmakers'].items():
                            for market, outcomes in book_data['markets'].items():
                                for outcome, odds in outcomes['outcomes'].items():
                                    if outcome not in best_odds or odds['price'] > best_odds[outcome]['price']:
                                        best_odds[outcome] = {
                                            'price': odds['price'],
                                            'book': book
                                        }
                        
                        # Display best odds
                        st.write("Best Odds:")
                        for outcome, odds in best_odds.items():
                            st.write(f"{outcome}: {odds['price']} ({odds['book']})")
            
            st.empty()
            time.sleep(30)

elif page == "Sharp Movement":
    st.title("Sharp Movement Detection")
    
        col1, col2 = st.columns(2)
        
        with col1:
        monitoring_window = st.slider(
            "Monitoring Window (minutes)",
            min_value=1,
            max_value=60,
            value=5
        )
        
        steam_threshold = st.slider(
            "Steam Move Threshold (%)",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.1
        )
    
    with col2:
        st.subheader("Active Alerts")
        # Get alerts from the alert system
        alerts = clients['simulator'].get_alerts()
        if alerts:
            for alert in alerts:
                with st.expander(f"{alert.type.upper()} - {alert.sport}"):
                    st.write(f"Confidence: {alert.confidence:.2%}")
                    st.write(f"Movement: {alert.old_line} → {alert.new_line}")
                    st.write("Details:", alert.details)

elif page == "Walters Mode":
    st.title("Walters Mode")
    
    # Get Walters strategy rules
    rules = clients['simulator'].get_strategy_rules()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Strategy Rules")
        for rule in rules:
            with st.expander(f"{rule['name']} ({rule['importance']})"):
                st.write(f"Description: {rule['description']}")
                st.write(f"Threshold: {rule['threshold']}")
                st.write(f"Weight: {rule['weight']}")
                st.write(f"Category: {rule['category']}")
            
        with col2:
        st.subheader("Performance Metrics")
        # Add performance metrics here
        st.metric("Win Rate", "62.5%")
        st.metric("ROI", "+15.3%")
        st.metric("CLV", "+2.1%")

elif page == "Support":
    st.title("Support Center")
    
    tab1, tab2 = st.tabs(["Create Ticket", "View Tickets"])
    
    with tab1:
        st.subheader("Submit a Support Ticket")
        
        ticket_type = st.selectbox(
            "Issue Type",
            ["Technical Problem", "Account Issue", "Feature Request", "API Integration", "Other"]
        )
        
        priority = st.select_slider(
            "Priority",
            options=["Low", "Medium", "High", "Urgent"],
            value="Medium"
        )
        
        description = st.text_area(
            "Describe your issue",
            height=150
        )
        
        if st.button("Submit Ticket"):
            # Add ticket to database
            conn = sqlite3.connect(st.session_state.db.db_path)
            c = conn.cursor()
            
            # Create tickets table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    priority TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert new ticket
            c.execute('''
                INSERT INTO support_tickets (type, priority, description)
                VALUES (?, ?, ?)
            ''', (ticket_type, priority, description))
            
            conn.commit()
            conn.close()
            
            st.success("Ticket submitted successfully!")
    
    with tab2:
        st.subheader("Your Support Tickets")
        
        # Fetch tickets from database
        conn = sqlite3.connect(st.session_state.db.db_path)
        tickets_df = pd.read_sql_query("SELECT * FROM support_tickets ORDER BY created_at DESC", conn)
        conn.close()
        
        if not tickets_df.empty:
            for _, ticket in tickets_df.iterrows():
                with st.expander(f"{ticket['type']} - {ticket['status']} ({ticket['created_at']})"):
                    st.write(f"Priority: {ticket['priority']}")
                    st.write(f"Description: {ticket['description']}")
    else:
            st.info("No support tickets found.")

elif page == "Settings":
    st.title("Settings")
    
    st.subheader("API Configuration")
    for api, status in api_status.items():
        st.write(f"{api}: {'Connected' if status else 'Not Connected'}")
    
    st.subheader("Rate Limits")
    for api, limits in clients['config'].RATE_LIMITS.items():
        st.write(f"{api}:")
        st.write(f"- Requests per minute: {limits.get('requests_per_minute', 'N/A')}")
        st.write(f"- Minimum interval: {limits.get('min_interval')}s")
