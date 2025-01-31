import streamlit as st
import pandas as pd
from datetime import datetime

# Configure the app
st.set_page_config(
    page_title="The Rounders - Sports Betting Analytics",
    page_icon="🎯",
    layout="wide"
)

# Simple in-memory storage for testing
class SimpleStorage:
    def __init__(self):
        self.bets = []
        
    def add_bet(self, bet_data):
        self.bets.append(bet_data)
        
    def get_bets(self):
        return pd.DataFrame(self.bets) if self.bets else pd.DataFrame()

# Initialize storage
if 'storage' not in st.session_state:
    st.session_state.storage = SimpleStorage()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Dashboard", "Place Bet", "View Bets"])

if page == "Dashboard":
    st.title("Sports Betting Dashboard")
    
    # Simple metrics
    bets_df = st.session_state.storage.get_bets()
    if not bets_df.empty:
        col1, col2, col3 = st.columns(3)
        
        # Total bets
        col1.metric("Total Bets", len(bets_df))
        
        # Win rate
        if 'result' in bets_df.columns:
            win_rate = (bets_df['result'] == 'Won').mean() * 100
            col2.metric("Win Rate", f"{win_rate:.1f}%")
        
        # Total profit/loss
        if 'profit_loss' in bets_df.columns:
            total_pl = bets_df['profit_loss'].sum()
            col3.metric("Total P/L", f"${total_pl:.2f}")
    
elif page == "Place Bet":
    st.title("Place New Bet")
    
    with st.form("new_bet"):
        col1, col2 = st.columns(2)
        
        with col1:
            sport = st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"])
            game = st.text_input("Game (e.g., Lakers vs Warriors)")
            bet_type = st.selectbox("Bet Type", ["Spread", "Moneyline", "Over/Under"])
            
        with col2:
            odds = st.number_input("Odds", min_value=-10000, max_value=10000)
            stake = st.number_input("Stake ($)", min_value=1.0, step=1.0)
            confidence = st.slider("Confidence", 1, 100, 50)
        
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Place Bet"):
            bet_data = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'sport': sport,
                'game': game,
                'bet_type': bet_type,
                'odds': odds,
                'stake': stake,
                'confidence': confidence,
                'notes': notes,
                'status': 'Pending'
            }
            
            st.session_state.storage.add_bet(bet_data)
            st.success("Bet recorded successfully!")

elif page == "View Bets":
    st.title("Betting History")
    
    bets_df = st.session_state.storage.get_bets()
    if not bets_df.empty:
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
        st.info("No bets recorded yet. Head to the 'Place Bet' page to add some!")
