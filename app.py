import streamlit as st
import pandas as pd
import numpy as np
from nba_massey_ratings import NBAMasseyRatings
from betting_system import BettingSystem, CLVAnalyzer
import plotly.express as px
import plotly.graph_objects as go

# Initialize session state for betting system
if 'betting_system' not in st.session_state:
    st.session_state.betting_system = None
if 'clv_analyzer' not in st.session_state:
    st.session_state.clv_analyzer = CLVAnalyzer()

def nba_massey_page():
    st.header("NBA Massey Ratings")
    
    # Initialize NBA Massey Ratings
    nba = NBAMasseyRatings()
    
    try:
        # Load season games and calculate ratings
        nba.load_season_games()
        ratings = nba.calculate_ratings()
        
        if ratings and len(ratings) > 0:
            # Initialize betting system with ratings
            st.session_state.betting_system = BettingSystem(ratings)
            
            # Convert ratings dictionary to DataFrame
            df = pd.DataFrame(list(ratings.items()), columns=['Team', 'Rating'])
            
            # Calculate z-scores
            df['Z-Score'] = (df['Rating'] - df['Rating'].mean()) / df['Rating'].std()
            
            # Calculate tiers (1-5 based on z-scores)
            df['Tier'] = pd.qcut(df['Z-Score'], q=5, labels=['5', '4', '3', '2', '1'])
            
            # Calculate win probability vs average team
            df['Win Prob vs Avg'] = 1 / (1 + 10**(-df['Rating']/10))
            
            # Sort by rating descending
            df = df.sort_values('Rating', ascending=False).reset_index(drop=True)
            
            # Format the display
            df.index = df.index + 1  # Start index at 1
            df['Rating'] = df['Rating'].round(3)
            df['Z-Score'] = df['Z-Score'].round(3)
            df['Win Prob vs Avg'] = (df['Win Prob vs Avg'] * 100).round(1).astype(str) + '%'
            
            # Display the ratings table
            st.dataframe(df)
            
            # Add visualization
            st.subheader("Team Ratings Distribution")
            fig = px.bar(df, x='Team', y='Rating',
                        title='NBA Team Ratings',
                        labels={'Rating': 'Massey Rating'})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
            
            # Add backtest results
            st.subheader("Backtest Results")
            if st.button("Run Backtest"):
                accuracy, results = st.session_state.betting_system.backtest_massey()
                if accuracy is not None:
                    st.metric("Prediction Accuracy", f"{accuracy:.1%}")
                    st.dataframe(results)
            
        else:
            st.warning("No ratings data available. Please check if games have been loaded correctly.")
            
    except Exception as e:
        st.error(f"Error calculating ratings: {str(e)}")

def line_shopping_page():
    st.header("Line Shopping")
    
    if st.session_state.betting_system is None:
        st.warning("Please visit the NBA Massey Ratings page first to initialize the betting system.")
        return
    
    # Add sportsbook comparison tool
    st.subheader("Sportsbook Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sport = st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
        game_date = st.date_input("Date")
        
    with col2:
        market = st.selectbox("Market Type", ["Spread", "Moneyline", "Totals"])
        sportsbook = st.selectbox("Sportsbooks", ["All", "DraftKings", "FanDuel", "BetMGM", "Caesars"])
    
    if st.button("Find Best Lines"):
        # Example implementation for NBA
        if sport == "NBA":
            st.info("Fetching best available odds...")
            # Add odds comparison table here
            odds_data = {
                'Game': ['BOS vs NYK', 'LAL vs GSW'],
                'Best Spread': ['-5.5', '+3.5'],
                'Best Odds': ['-110', '-105'],
                'Book': ['DraftKings', 'FanDuel']
            }
            st.dataframe(pd.DataFrame(odds_data))

def sharp_movement_page():
    st.header("Sharp Movement Tracker")
    
    if st.session_state.betting_system is None:
        st.warning("Please visit the NBA Massey Ratings page first to initialize the betting system.")
        return
    
    # Add sharp betting movement analysis
    st.subheader("Line Movement Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sport = st.selectbox("Track Movement For", ["NBA", "NFL", "MLB", "NHL"])
        threshold = st.number_input("Movement Threshold (%)", min_value=1, max_value=10, value=2)
        
    with col2:
        window = st.selectbox("Time Window", ["Last Hour", "Last 3 Hours", "Last 6 Hours", "Last 12 Hours", "Last 24 Hours"])
        movement_type = st.selectbox("Movement Type", ["All", "Sharp", "Public"])
    
    if st.button("Track Movement"):
        st.info("Tracking line movement...")
        # Add movement tracking visualization
        movement_data = pd.DataFrame({
            'Time': pd.date_range(start='now', periods=10, freq='15min'),
            'Line': [-5.5, -5.5, -5, -4.5, -4.5, -4, -4, -3.5, -3.5, -3]
        })
        fig = px.line(movement_data, x='Time', y='Line',
                     title='Line Movement Over Time')
        st.plotly_chart(fig)

def clv_analysis_page():
    st.header("Closing Line Value Analysis")
    
    if st.session_state.betting_system is None:
        st.warning("Please visit the NBA Massey Ratings page first to initialize the betting system.")
        return
    
    # Add CLV analysis tools
    st.subheader("CLV Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        opening = st.number_input("Opening Line", value=0.0, step=0.5)
        your_line = st.number_input("Your Line", value=0.0, step=0.5)
        
    with col2:
        closing = st.number_input("Closing Line", value=0.0, step=0.5)
        bet_type = st.selectbox("Bet Type", ["Spread", "Moneyline", "Total"])
    
    if st.button("Calculate CLV"):
        st.session_state.clv_analyzer.add_bet(your_line, closing)
        stats = st.session_state.clv_analyzer.get_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average CLV", f"{stats['avg_clv']:.2f}")
        with col2:
            st.metric("Positive CLV Rate", f"{stats['positive_clv_rate']:.1%}")
        with col3:
            st.metric("Total Bets Tracked", stats['total_bets'])

def walters_dashboard_page():
    st.header("Billy Walters Dashboard")
    
    if st.session_state.betting_system is None:
        st.warning("Please visit the NBA Massey Ratings page first to initialize the betting system.")
        return
    
    # Add key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Steam Move Win Rate", "67.8%", "+2.3%")
    with col2:
        st.metric("Average CLV Edge", "2.1%", "+0.3%")
    with col3:
        st.metric("Sharp Money Rate", "82.5%", "-1.2%")
    
    # Add Walters Rules checklist
    st.subheader("Walters Rules Checklist")
    
    rules = {
        "Never Chase Losses": True,
        "Beat the Closing Line": True,
        "Early Information Edge": False,
        "Line Shopping": True
    }
    
    for rule, status in rules.items():
        st.checkbox(rule, value=status, disabled=True)
    
    # Add performance chart
    st.subheader("Performance by Market Timing")
    chart_data = pd.DataFrame({
        'Market Timing': ['Early', 'Middle', 'Late'],
        'Win Rate': [0.68, 0.62, 0.58]
    })
    
    fig = px.bar(chart_data, x='Market Timing', y='Win Rate',
                 range_y=[0, 1],
                 labels={'Win Rate': 'Win Rate %'},
                 title='Performance by Market Timing')
    fig.update_traces(texttemplate='%{y:.1%}', textposition='outside')
    st.plotly_chart(fig)
    
    # Add bankroll management
    st.subheader("Bankroll Management")
    edge = st.slider("Edge (%)", 1, 10, 3)
    bankroll = st.number_input("Current Bankroll ($)", value=10000.0, step=1000.0)
    
    recommended_bet = (edge / 100) * bankroll
    st.metric("Recommended Bet Size", f"${recommended_bet:,.2f}")

def main():
    st.title("Sharp Betting Tools")
    
    # Create sidebar navigation
    st.sidebar.title("Mode Selection")
    mode = st.sidebar.radio("Select Mode", ["Paper Trading", "Real Money"])
    st.sidebar.info(f"Currently in {mode} mode")
    
    # Navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page", 
        ["Line Shopping", "Sharp Movement", "CLV Analysis", "Walters Dashboard", "NBA Massey Ratings"])
    
    # Display selected page
    if page == "Line Shopping":
        line_shopping_page()
    elif page == "Sharp Movement":
        sharp_movement_page()
    elif page == "CLV Analysis":
        clv_analysis_page()
    elif page == "Walters Dashboard":
        walters_dashboard_page()
    elif page == "NBA Massey Ratings":
        nba_massey_page()

if __name__ == "__main__":
    main() 