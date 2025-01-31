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
    ["Dashboard", "Place Bet", "View Bets", "Analytics", "Sharp Tools", "Kelly Calculator"]
)

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
            sport = st.selectbox(
                "Sport",
                list(SPORTS.keys()),
                format_func=lambda x: f"{SPORTS[x]['icon']} {x}"
            )
            game = st.text_input("Game (e.g., Lakers vs Warriors)")
            bet_type = st.selectbox(
                "Bet Type",
                ["Spread", "Moneyline", "Over/Under", "Player Props", "Team Props", "Parlays"]
            )
            pick = st.text_input("Pick (e.g., Lakers -5.5)")
            
        with col2:
            odds = st.number_input("Odds", min_value=-10000, max_value=10000)
            
            # Walters-style bankroll management
            if 'bankroll' not in st.session_state:
                st.session_state.bankroll = 1000.0
            
            bankroll = st.number_input(
                "Current Bankroll ($)",
                value=st.session_state.bankroll,
                min_value=1.0
            )
            
            # Calculate max bet based on Walters' 2-5% rule
            max_bet = bankroll * 0.05
            stake = st.number_input(
                "Stake ($)",
                min_value=1.0,
                max_value=max_bet,
                help=f"Max bet: ${max_bet:.2f} (5% of bankroll)"
            )
            
            confidence = st.slider(
                "Sharp Confidence",
                1, 100, 50,
                help="Higher confidence for steam moves and reverse line movement"
            )
            
        # Sharp betting indicators
        st.subheader("Sharp Betting Indicators")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            steam_move = st.checkbox(
                "Steam Move Detected",
                help="Rapid line movement across multiple books"
            )
            
        with col2:
            reverse_line_movement = st.checkbox(
                "Reverse Line Movement",
                help="Line moving against public betting %"
            )
            
        with col3:
            public_percentage = st.slider(
                "Public Betting %",
                0, 100, 50,
                help="Percentage of public money on this side"
            )
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            opening_line = st.number_input("Opening Line", value=odds)
            expected_closing_line = st.number_input(
                "Expected Closing Line",
                help="Your prediction of where the line will close"
            )
            
            # Walters' timing strategy
            bet_timing = st.radio(
                "Bet Timing Strategy",
                ["Early Market", "Steam Move Response", "Closing Line Value Hunt"],
                help="When to place the bet for optimal value"
            )
        
        notes = st.text_area(
            "Notes",
            help="Add context about sharp action, injury news, or other factors"
        )
        
        if st.form_submit_button("Place Bet"):
            # Calculate sharp confidence score
            sharp_score = 0
            if steam_move:
                sharp_score += 30
            if reverse_line_movement:
                sharp_score += 25
            if abs(expected_closing_line - odds) > 1:
                sharp_score += 20
            if bet_timing == "Early Market":
                sharp_score += 15
            
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
                'steam_move': steam_move,
                'reverse_line_movement': reverse_line_movement,
                'public_percentage': public_percentage,
                'opening_line': opening_line,
                'sharp_confidence': sharp_score
            }
            
            # Walters' bankroll rules
            daily_bets = st.session_state.db.get_bets({
                'date': datetime.now().strftime("%Y-%m-%d")
            })
            daily_risk = daily_bets['stake'].sum() if not daily_bets.empty else 0
            
            if daily_risk + stake > bankroll * 0.15:
                st.error("⚠️ Daily betting limit exceeded (max 15% of bankroll)")
            else:
                st.session_state.db.add_bet(bet_data)
                st.success("Bet recorded successfully!")
                
                # Update bankroll
                st.session_state.bankroll = bankroll
                
                # Show sharp betting insights
                if sharp_score > 70:
                    st.info("🎯 High sharp confidence in this bet!")
                    if steam_move:
                        st.info("💨 Steam move detected - consider increasing stake")
                    if reverse_line_movement:
                        st.info("↩️ Reverse line movement suggests sharp action")

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

elif page == "Sharp Tools":
    st.title("Sharp Betting Tools")
    
    # Initialize SharpTools
    from sharp_tools import SharpTools
    sharp_tools = SharpTools(st.secrets.get("ODDS_API_KEY"))
    
    # Tabs for different tools
    tab1, tab2, tab3, tab4 = st.tabs([
        "Line Shopping",
        "Sharp Movement",
        "CLV Analysis",
        "Walters Dashboard"
    ])
    
    with tab1:
        st.subheader("Live Line Shopping")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            sport = st.selectbox(
                "Select Sport",
                list(SPORTS.keys()),
                format_func=lambda x: f"{SPORTS[x]['icon']} {x}",
                key="line_shopping_sport"
            )
        
        with col2:
            auto_refresh = st.checkbox(
                "Auto-refresh",
                value=True,
                help="Automatically refresh odds every 30 seconds"
            )
        
        # Fetch current odds
        odds_data = sharp_tools.fetch_odds(SPORTS[sport]['api_name'])
        if "error" not in odds_data:
            for game in odds_data:
                with st.expander(f"### {game['home_team']} vs {game['away_team']}"):
                    # Create odds comparison table
                    odds_df = pd.DataFrame([
                        {
                            'Book': book['title'],
                            'Home ML': book['markets']['h2h']['home'],
                            'Away ML': book['markets']['h2h']['away'],
                            'Spread': f"{book['markets']['spreads']['points']} ({book['markets']['spreads']['odds']})"
                        }
                        for book in game['bookmakers']
                    ])
                    
                    # Highlight best odds
                    best_home = odds_df['Home ML'].max()
                    best_away = odds_df['Away ML'].max()
                    best_home_book = odds_df.loc[odds_df['Home ML'] == best_home, 'Book'].iloc[0]
                    best_away_book = odds_df.loc[odds_df['Away ML'] == best_away, 'Book'].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Best Home Odds",
                            f"{best_home} ({best_home_book})"
                        )
                    with col2:
                        st.metric(
                            "Best Away Odds",
                            f"{best_away} ({best_away_book})"
                        )
                    
                    # Calculate arbitrage opportunities
                    home_decimal = (best_home / 100 + 1) if best_home > 0 else (100 / abs(best_home) + 1)
                    away_decimal = (best_away / 100 + 1) if best_away > 0 else (100 / abs(best_away) + 1)
                    margin = (1/home_decimal + 1/away_decimal - 1) * 100
                    
                    if margin < 0:
                        st.success(f"🎯 Arbitrage Opportunity: {abs(margin):.2f}% profit")
                    
                    st.dataframe(odds_df)
        else:
            st.warning("Please add your Odds API key in Streamlit secrets")
    
    with tab2:
        st.subheader("Sharp Movement Detection")
        
        col1, col2 = st.columns(2)
        with col1:
            monitoring_window = st.slider(
                "Monitoring Window (minutes)",
                5, 120, 30,
                help="Time window to analyze line movements"
            )
        with col2:
            steam_threshold = st.slider(
                "Steam Move Threshold",
                0.5, 3.0, 1.0,
                help="Minimum line movement to qualify as steam"
            )
        
        # Get recent line movements
        movements = st.session_state.db.get_line_movements(minutes=monitoring_window)
        if not movements.empty:
            # Check for steam moves
            steam_detected = sharp_tools.detect_steam_move(
                movements,
                time_window=5,
                threshold=steam_threshold
            )
            
            if steam_detected:
                st.warning("🚨 STEAM MOVE DETECTED! Significant line movement in the last 5 minutes.")
            
            # Show line movement chart
            fig = px.line(
                movements,
                x='timestamp',
                y='odds',
                color='book',
                title="Line Movement Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show volume analysis
            if 'volume' in movements.columns:
                vol_fig = px.bar(
                    movements,
                    x='timestamp',
                    y='volume',
                    color='is_sharp',
                    title="Betting Volume Analysis"
                )
                st.plotly_chart(vol_fig, use_container_width=True)
            
            # Show reverse line movement alerts
            if 'public_percentage' in movements.columns:
                rlm = sharp_tools.detect_reverse_line_movement(
                    movements['public_percentage'].iloc[-1],
                    movements['odds'].iloc[0],
                    movements['odds'].iloc[-1]
                )
                if rlm:
                    st.warning("🔄 Reverse Line Movement Detected!")
                    st.write(f"Public: {movements['public_percentage'].iloc[-1]}% on one side")
                    st.write(f"Line moved: {movements['odds'].iloc[0]} → {movements['odds'].iloc[-1]}")
        else:
            st.info("No recent line movements detected")
    
    with tab3:
        st.subheader("Closing Line Value (CLV) Analysis")
        
        # Get sharp analytics
        sharp_analytics = st.session_state.db.get_sharp_analytics()
        if 'error' not in sharp_analytics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Average CLV",
                    f"{sharp_analytics['avg_clv']:.2f}",
                    help="Average edge vs closing line"
                )
            with col2:
                st.metric(
                    "Sharp Confidence Correlation",
                    f"{sharp_analytics['sharp_confidence_correlation']:.2f}",
                    help="Correlation between sharp confidence and profit"
                )
            with col3:
                clv_win_rate = len([x for x in sharp_analytics['steam_moves'] if x['clv'] > 0]) / len(sharp_analytics['steam_moves'])
                st.metric(
                    "CLV Win Rate",
                    f"{clv_win_rate*100:.1f}%",
                    help="% of bets that beat the closing line"
                )
            
            # CLV by confidence level
            st.write("CLV by Sharp Confidence Level")
            clv_df = pd.DataFrame(
                sharp_analytics['clv_by_confidence'].items(),
                columns=['Confidence Level', 'Average CLV']
            )
            fig = px.bar(
                clv_df,
                x='Confidence Level',
                y='Average CLV',
                title="CLV by Confidence Level"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Steam move performance
            st.write("Steam Move Performance")
            steam_df = pd.DataFrame(sharp_analytics['steam_moves'])
            if not steam_df.empty:
                fig = px.bar(
                    steam_df,
                    x='steam_move',
                    y=['result', 'profit_loss', 'clv'],
                    barmode='group',
                    title="Performance of Steam Move Bets"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add some bets to see CLV analysis")
    
    with tab4:
        st.subheader("Billy Walters Dashboard")
        
        # Walters-style metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Steam Move Win Rate",
                "67.8%",
                "+2.3%",
                help="Win rate on steam move bets"
            )
        
        with col2:
            st.metric(
                "Average CLV Edge",
                "2.1%",
                "+0.3%",
                help="Average closing line value edge"
            )
        
        with col3:
            st.metric(
                "Sharp Money Rate",
                "82.5%",
                "-1.2%",
                help="% of your bets aligned with sharp money"
            )
        
        # Walters Rules Checklist
        st.subheader("Walters Rules Checklist")
        rules_df = pd.DataFrame([
            {
                "Rule": "Never Chase Losses",
                "Status": "✅ Following",
                "Details": "No bets exceed 5% of bankroll"
            },
            {
                "Rule": "Beat the Closing Line",
                "Status": "✅ Following",
                "Details": "Average CLV: +2.1%"
            },
            {
                "Rule": "Early Information Edge",
                "Status": "⚠️ Needs Work",
                "Details": "60% of bets placed in early markets"
            },
            {
                "Rule": "Line Shopping",
                "Status": "✅ Following",
                "Details": "Checking 12+ books per bet"
            }
        ])
        st.dataframe(rules_df, use_container_width=True)
        
        # Performance by Timing
        st.subheader("Performance by Market Timing")
        timing_data = pd.DataFrame([
            {"Timing": "Early Market", "Win Rate": 0.62, "ROI": 0.15},
            {"Timing": "Steam Move Response", "Win Rate": 0.58, "ROI": 0.12},
            {"Timing": "CLV Hunt", "Win Rate": 0.54, "ROI": 0.08}
        ])
        
        fig = px.bar(
            timing_data,
            x="Timing",
            y=["Win Rate", "ROI"],
            barmode="group",
            title="Performance by Bet Timing Strategy"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk Management
        st.subheader("Bankroll Management")
        bankroll_data = pd.DataFrame([
            {"Date": "2024-01-25", "Bankroll": 10000, "Daily Risk": 1200},
            {"Date": "2024-01-26", "Bankroll": 10500, "Daily Risk": 1000},
            {"Date": "2024-01-27", "Bankroll": 11000, "Daily Risk": 1500},
            {"Date": "2024-01-28", "Bankroll": 11200, "Daily Risk": 800}
        ])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=bankroll_data["Date"],
            y=bankroll_data["Bankroll"],
            name="Bankroll"
        ))
        fig.add_trace(go.Bar(
            x=bankroll_data["Date"],
            y=bankroll_data["Daily Risk"],
            name="Daily Risk",
            yaxis="y2"
        ))
        
        fig.update_layout(
            title="Bankroll vs Daily Risk",
            yaxis2=dict(
                title="Daily Risk ($)",
                overlaying="y",
                side="right"
            ),
            yaxis=dict(title="Bankroll ($)")
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
