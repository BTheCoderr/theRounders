import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# Configure the app
st.set_page_config(
    page_title="Sports Betting Analytics Platform",
    page_icon="🎯",
    layout="wide"
)

# API endpoint
API_BASE_URL = "http://localhost:8000/api"

def fetch_api_data(endpoint: str, method="GET", data=None):
    """Fetch data from the API."""
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}/{endpoint}")
        else:
            response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a page",
    ["Dashboard", "Live Odds", "Predictions", "Bet Tracker", "Analytics", "Settings"]
)

# Dashboard page
if page == "Dashboard":
    st.title("Sports Betting Dashboard")
    
    # Get supported sports
    sports = fetch_api_data("sports")
    
    if sports:
        cols = st.columns(len(sports))
        for i, (sport, config) in enumerate(sports.items()):
            with cols[i]:
                st.subheader(sport)
                st.write(f"Metrics: {', '.join(config['metrics'])}")
    
    # Display recent performance
    st.subheader("Recent Performance")
    analytics = fetch_api_data("bets/analytics")
    
    if analytics and "overall" in analytics:
        cols = st.columns(3)
        cols[0].metric("Win Rate", f"{analytics['overall']['win_rate']*100:.1f}%")
        cols[1].metric("ROI", f"{analytics['overall']['roi']*100:.1f}%")
        cols[2].metric("Total Bets", analytics['overall']['total_bets'])
    
    # Display arbitrage opportunities
    st.subheader("Live Arbitrage Opportunities")
    selected_sport = st.selectbox("Select Sport", list(sports.keys()) if sports else [])
    
    if selected_sport:
        opportunities = fetch_api_data(f"arbitrage/{selected_sport}")
        if opportunities:
            for opp in opportunities:
                st.info(
                    f"💰 {opp['type'].upper()} Arbitrage: "
                    f"{opp['profit_percentage']:.2f}% profit potential\n"
                    f"Bet 1: {opp['home_sportsbook']} @ {opp['home_odds']}\n"
                    f"Bet 2: {opp['away_sportsbook']} @ {opp['away_odds']}"
                )

# Live Odds page
elif page == "Live Odds":
    st.title("Live Betting Odds")
    
    sports = fetch_api_data("sports")
    selected_sport = st.selectbox("Select Sport", list(sports.keys()) if sports else [])
    
    if selected_sport:
        odds = fetch_api_data(f"odds/{selected_sport}")
        if odds:
            st.dataframe(pd.DataFrame(odds))
            
            # Line Movement Chart
            st.subheader("Line Movement")
            event_id = st.selectbox("Select Event", [e['event_id'] for e in odds])
            if event_id:
                movements = fetch_api_data(f"line-movement/{selected_sport}/{event_id}")
                if movements:
                    df_movement = pd.DataFrame(movements['moneyline'])
                    fig = px.line(df_movement, title="Moneyline Movement")
                    st.plotly_chart(fig)

# Predictions page
elif page == "Predictions":
    st.title("Game Predictions")
    
    tab1, tab2 = st.tabs(["Game Predictions", "Player Props"])
    
    with tab1:
        sports = fetch_api_data("sports")
        if sports:
            sport = st.selectbox("Select Sport", list(sports.keys()))
            odds = fetch_api_data(f"odds/{sport}")
            
            if odds:
                game = st.selectbox("Select Game", [f"{e['home_team']} vs {e['away_team']}" for e in odds])
                
                if game:
                    home_team, away_team = game.split(" vs ")
                    prediction = fetch_api_data("predictions/game", method="POST", data={
                        "sport": sport,
                        "game_id": "1",  # Placeholder
                        "home_team": home_team,
                        "away_team": away_team
                    })
                    
                    if prediction:
                        cols = st.columns(2)
                        cols[0].metric("Home Win Probability", f"{prediction['home_win_probability']*100:.1f}%")
                        cols[1].metric("Away Win Probability", f"{prediction['away_win_probability']*100:.1f}%")
                        
                        st.progress(prediction['confidence'])
                        st.caption(f"Confidence: {prediction['confidence']*100:.1f}%")
    
    with tab2:
        if sports:
            sport = st.selectbox("Select Sport (Props)", list(sports.keys()))
            player_id = st.text_input("Player ID")
            prop_type = st.selectbox("Prop Type", ["Points", "Rebounds", "Assists"])
            line = st.number_input("Line", min_value=0.0, step=0.5)
            
            if st.button("Get Prediction"):
                prediction = fetch_api_data("predictions/props", method="POST", data={
                    "sport": sport,
                    "player_id": player_id,
                    "prop_type": prop_type,
                    "line": line
                })
                
                if prediction:
                    st.metric("Predicted Value", f"{prediction['predicted_value']:.1f}")
                    st.progress(prediction['confidence'] / 100)
                    st.caption(f"Confidence: {prediction['confidence']:.1f}%")

# Bet Tracker page
elif page == "Bet Tracker":
    st.title("Bet Tracker")
    
    # Form for adding new bets
    with st.form("new_bet"):
        st.subheader("Add New Bet")
        cols = st.columns(3)
        
        sport = cols[0].selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
        game = cols[1].text_input("Game")
        pick_type = cols[2].selectbox("Pick Type", ["Spread", "Moneyline", "Total", "Prop"])
        
        cols = st.columns(3)
        pick = cols[0].text_input("Pick")
        line = cols[1].number_input("Line", step=0.5)
        odds = cols[2].number_input("Odds", min_value=-1000, max_value=1000, step=5)
        
        cols = st.columns(3)
        bet_amount = cols[0].number_input("Bet Amount", min_value=1.0, step=1.0)
        book = cols[1].selectbox("Sportsbook", ["DraftKings", "FanDuel", "BetMGM"])
        confidence = cols[2].slider("Confidence", 1, 100, 50)
        
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Place Bet"):
            response = fetch_api_data("bets", method="POST", data={
                "sport": sport,
                "game": game,
                "pick_type": pick_type,
                "pick": pick,
                "line": line,
                "odds": odds,
                "bet_amount": bet_amount,
                "book": book,
                "confidence": confidence,
                "notes": notes
            })
            
            if response:
                st.success("Bet recorded successfully!")

# Analytics page
elif page == "Analytics":
    st.title("Betting Analytics")
    
    analytics = fetch_api_data("bets/analytics")
    
    if analytics:
        # Overall performance
        st.subheader("Overall Performance")
        cols = st.columns(4)
        cols[0].metric("Win Rate", f"{analytics['overall']['win_rate']*100:.1f}%")
        cols[1].metric("ROI", f"{analytics['overall']['roi']*100:.1f}%")
        cols[2].metric("Total Bets", analytics['overall']['total_bets'])
        
        # Performance by sport
        st.subheader("Performance by Sport")
        sport_df = pd.DataFrame(analytics['by_sport']).T
        fig = go.Figure(data=[
            go.Bar(name='Win Rate', y=sport_df['win_rate']*100),
            go.Bar(name='ROI', y=sport_df['roi']*100)
        ])
        fig.update_layout(barmode='group')
        st.plotly_chart(fig)
        
        # Confidence analysis
        if 'confidence_analysis' in analytics:
            st.subheader("Performance by Confidence Level")
            conf_df = pd.DataFrame(analytics['confidence_analysis']).T
            fig = px.scatter(conf_df, x='range', y='win_rate', size='total_bets',
                           title="Win Rate vs Confidence Level")
            st.plotly_chart(fig)
        
        # Timing analysis
        if 'timing_analysis' in analytics:
            st.subheader("Performance by Time of Day")
            time_df = pd.DataFrame(analytics['timing_analysis']).T
            fig = px.line(time_df, x='hours', y='win_rate',
                         title="Win Rate by Time of Day")
            st.plotly_chart(fig)

# Settings page
else:
    st.title("Settings")
    
    st.subheader("API Configuration")
    api_key = st.text_input("API Key", type="password")
    
    st.subheader("Notification Settings")
    st.checkbox("Enable Email Notifications")
    st.checkbox("Enable Push Notifications")
    
    st.subheader("Model Settings")
    st.slider("Minimum Confidence Threshold", 0, 100, 65)
    st.number_input("Kelly Criterion Fraction", 0.0, 1.0, 0.25, 0.05)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!") 