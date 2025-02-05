import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Line Shopping - The Rounders", page_icon="📊", layout="wide")

# Access shared session state
if 'odds_api' not in st.session_state:
    st.error("Please initialize the app from the home page")
    st.stop()

# Title and description
st.title("Line Shopping")
st.markdown("""
Compare odds across different sportsbooks to find the best value for your bets.
This tool helps you identify arbitrage opportunities and get the best possible lines.
""")

# Show current mode
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

# Filters section
col1, col2 = st.columns(2)

with col1:
    sport = st.selectbox(
        "Sport",
        ["NBA", "NFL", "MLB", "NHL", "UFC/MMA", "Soccer - EPL", "Soccer - Champions League"]
    )
    market = st.selectbox(
        "Market",
        ["Spread", "Moneyline", "Total Points", "Player Props"]
    )

with col2:
    min_edge = st.slider(
        "Minimum Edge (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
        help="Minimum edge required to display an opportunity"
    )
    books = st.multiselect(
        "Sportsbooks",
        ["DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"],
        default=["DraftKings", "FanDuel", "BetMGM"]
    )

# Get odds data
if st.button("Find Best Lines"):
    with st.spinner("Fetching latest odds..."):
        try:
            # Use the shared OddsAPI instance
            odds_data = st.session_state.odds_api.get_odds(sport)
            if odds_data:
                # Convert API data to DataFrame
                odds_df = pd.DataFrame({
                    'Game': [game['teams'][0] + ' vs ' + game['teams'][1] for game in odds_data],
                    'Best Line': [f"{game['best_line']['line']} ({game['best_line']['odds']})" for game in odds_data],
                    'Best Book': [game['best_line']['book'] for game in odds_data],
                    'Market Edge': [f"{game['edge']:.1f}%" for game in odds_data],
                    'Sharp Action': [f"{game['sharp_percentage']}% {game['sharp_side']}" for game in odds_data]
                })
                
                # Display odds comparison
                st.subheader("Best Available Lines")
                st.dataframe(
                    odds_df.style.highlight_max(subset=['Market Edge'])
                )
                
                # Find arbitrage opportunities
                arb_opps = st.session_state.betting_system.find_arbitrage(odds_data)
                
                if arb_opps:
                    st.subheader("Arbitrage Opportunities")
                    arb_df = pd.DataFrame(arb_opps)
                    st.success("Arbitrage opportunities found!")
                    st.dataframe(arb_df)
                else:
                    st.info("No arbitrage opportunities found at this time.")
                
                # Line movement chart
                st.subheader("Line Movement History")
                movement_data = st.session_state.betting_system.get_line_movements(
                    sport=sport,
                    game=odds_df['Game'].iloc[0],  # Use first game as example
                    books=books
                )
                
                if movement_data:
                    fig = px.line(movement_data, 
                                x='Time', 
                                y=books,
                                title='Line Movement Over Time')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No odds data available for the selected sport")
        except Exception as e:
            st.error(f"Error fetching odds: {str(e)}")

# Tips section
with st.expander("Line Shopping Tips"):
    st.markdown("""
    ### Best Practices for Line Shopping
    1. **Compare Multiple Books**: Always check at least 3-4 sportsbooks before placing a bet
    2. **Track Line Movement**: Watch for significant line moves that might indicate sharp action
    3. **Consider the Vig**: Look at the total vig across different books
    4. **Time Your Bets**: Lines are often sharpest right before game time
    5. **Use Multiple Accounts**: Having accounts at multiple books gives you more options
    """)

# Footer
st.markdown("---")
st.caption("Data updates every 60 seconds. Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")) 