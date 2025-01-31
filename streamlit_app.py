import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os

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
        
        # Create bets table
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
                FOREIGN KEY (bet_id) REFERENCES bets (id)
            )
        ''')
        
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
page = st.sidebar.radio(
    "Select a page",
    ["Dashboard", "Place Bet", "View Bets", "Analytics", "Kelly Calculator"]
)

if page == "Dashboard":
    st.title("Sports Betting Dashboard")
    
    # Get analytics
    analytics = st.session_state.db.get_analytics()
    
    if 'error' not in analytics:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Bets", analytics['overall']['total_bets'])
        col2.metric("Win Rate", f"{analytics['overall']['win_rate']*100:.1f}%")
        col3.metric("Total P/L", f"${analytics['overall']['profit_loss']:.2f}")
        col4.metric("ROI", f"{analytics['overall']['roi']:.1f}%")
        
        # Performance charts
        st.subheader("Performance Over Time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=analytics['trends']['dates'],
            y=analytics['trends']['cumulative_pl'],
            name="Profit/Loss ($)"
        ))
        fig.add_trace(go.Scatter(
            x=analytics['trends']['dates'],
            y=analytics['trends']['cumulative_roi'],
            name="ROI (%)",
            yaxis="y2"
        ))
        fig.update_layout(
            yaxis2=dict(overlaying='y', side='right', title="ROI (%)"),
            yaxis=dict(title="Profit/Loss ($)"),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance by sport
        st.subheader("Performance by Sport")
        sport_df = pd.DataFrame(analytics['by_sport'])
        fig = px.bar(
            sport_df,
            x='sport',
            y=['profit_loss', 'roi'],
            barmode='group',
            title="Profit/Loss and ROI by Sport"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # CLV Analysis
        st.subheader("Closing Line Value Analysis")
        st.metric("Average CLV", f"{analytics['clv_analysis']['average_clv']:.2f}")
        st.write(f"Correlation with P/L: {analytics['clv_analysis']['clv_correlation']:.2f}")
        
        # Steam Move Performance
        st.subheader("Steam Move Performance")
        steam_df = pd.DataFrame(analytics['steam_moves'])
        if not steam_df.empty:
            st.dataframe(steam_df)
    else:
        st.info("Add some bets to see your analytics!")

elif page == "Place Bet":
    st.title("Place New Bet")
    
    with st.form("new_bet"):
        col1, col2 = st.columns(2)
        
        with col1:
            sport = st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
            game = st.text_input("Game (e.g., Lakers vs Warriors)")
            bet_type = st.selectbox("Bet Type", ["Spread", "Moneyline", "Over/Under"])
            pick = st.text_input("Pick (e.g., Lakers -5.5)")
            
        with col2:
            odds = st.number_input("Odds", min_value=-10000, max_value=10000)
            stake = st.number_input("Stake ($)", min_value=1.0, step=1.0)
            confidence = st.slider("Confidence", 1, 100, 50)
            steam_move = st.checkbox("Steam Move Detected")
        
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Place Bet"):
            bet_data = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'sport': sport,
                'game': game,
                'bet_type': bet_type,
                'pick': pick,
                'odds': odds,
                'stake': stake,
                'confidence': confidence,
                'notes': notes,
                'status': 'Pending',
                'steam_move': steam_move
            }
            
            st.session_state.db.add_bet(bet_data)
            st.success("Bet recorded successfully!")

elif page == "View Bets":
    st.title("Betting History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        sport_filter = st.selectbox("Sport", ["All"] + ["NBA", "NFL", "MLB", "NHL"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Won", "Lost", "Push"])
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now())
        )
    
    # Get filtered bets
    filters = {}
    if sport_filter != "All":
        filters['sport'] = sport_filter
    if status_filter != "All":
        filters['status'] = status_filter
    
    bets_df = st.session_state.db.get_bets(filters)
    
    if not bets_df.empty:
        # Add result input for pending bets
        for idx, row in bets_df[bets_df['status'] == 'Pending'].iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"{row['game']} - {row['pick']} ({row['odds']})")
            result = col2.selectbox(
                "Result",
                ["Pending", "Won", "Lost", "Push"],
                key=f"result_{row['id']}"
            )
            if result != "Pending":
                closing_line = col3.number_input(
                    "Closing Line",
                    value=float(row['odds']),
                    key=f"closing_{row['id']}"
                )
                if st.button("Update", key=f"update_{row['id']}"):
                    profit = row['stake'] * (row['odds']/100) if result == "Won" else -row['stake']
                    update_data = {
                        'status': result,
                        'result': result,
                        'profit_loss': profit,
                        'closing_line': closing_line
                    }
                    st.session_state.db.update_bet(row['id'], update_data)
                    st.experimental_rerun()
        
        # Display all bets
        st.dataframe(bets_df)
        
        # Download button
        csv = bets_df.to_csv(index=False)
        st.download_button(
            label="Download Betting History",
            data=csv,
            file_name="betting_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No bets found matching the filters.")

elif page == "Analytics":
    st.title("Advanced Analytics")
    
    analytics = st.session_state.db.get_analytics()
    
    if 'error' not in analytics:
        # Performance by bet type
        st.subheader("Performance by Bet Type")
        type_df = pd.DataFrame(analytics['by_type'])
        fig = px.bar(
            type_df,
            x='bet_type',
            y=['profit_loss', 'roi'],
            barmode='group',
            title="Profit/Loss and ROI by Bet Type"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Confidence analysis
        st.subheader("Performance by Confidence Level")
        bets_df = st.session_state.db.get_bets()
        if not bets_df.empty:
            bets_df['confidence_bucket'] = pd.qcut(bets_df['confidence'], 4)
            conf_analysis = bets_df.groupby('confidence_bucket').agg({
                'result': lambda x: (x == 'Won').mean(),
                'profit_loss': 'sum',
                'id': 'count'
            }).reset_index()
            fig = px.scatter(
                conf_analysis,
                x='confidence_bucket',
                y='result',
                size='id',
                title="Win Rate by Confidence Level"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Steam move analysis
        st.subheader("Steam Move Analysis")
        steam_df = pd.DataFrame(analytics['steam_moves'])
        if not steam_df.empty:
            fig = px.bar(
                steam_df,
                x='steam_move',
                y=['result', 'profit_loss'],
                barmode='group',
                title="Performance of Steam Move Bets"
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "Kelly Calculator":
    st.title("Kelly Criterion Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        odds = st.number_input("American Odds", min_value=-10000, max_value=10000)
        bankroll = st.number_input("Bankroll ($)", min_value=1.0, value=1000.0)
        
    with col2:
        win_prob = st.slider("Estimated Win Probability (%)", 1, 99, 50) / 100
        
    if st.button("Calculate Kelly Bet"):
        kelly = st.session_state.db.calculate_kelly_criterion(odds, win_prob)
        suggested_bet = kelly * bankroll
        
        st.metric("Kelly Fraction", f"{kelly:.3f}")
        st.metric("Suggested Bet Size", f"${suggested_bet:.2f}")
        
        st.write("Conservative Kelly Sizes:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Quarter Kelly", f"${suggested_bet * 0.25:.2f}")
        col2.metric("Half Kelly", f"${suggested_bet * 0.5:.2f}")
        col3.metric("Three-Quarter Kelly", f"${suggested_bet * 0.75:.2f}")
        
        st.info("""
        The Kelly Criterion provides the optimal bet size to maximize long-term growth.
        However, it's often recommended to use a fractional Kelly (Quarter or Half)
        to reduce volatility while maintaining most of the benefits.
        """)
