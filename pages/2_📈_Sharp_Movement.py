import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Sharp Movement Tracker - The Rounders", page_icon="📈", layout="wide")

# Access shared session state
if 'betting_system' not in st.session_state:
    st.error("Please initialize the app from the home page")
    st.stop()

# Title and description
st.title("Sharp Movement Tracker")
st.markdown("""
Track sharp money movements and line changes across different sportsbooks.
This tool helps you identify where the smart money is going and potential value opportunities.
""")

# Show current mode
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

# Filters section
col1, col2 = st.columns(2)

with col1:
    timeframe = st.selectbox(
        "Timeframe",
        ["Last Hour", "Last 3 Hours", "Last 6 Hours", "Last 12 Hours", "Last 24 Hours"]
    )
    movement_type = st.selectbox(
        "Movement Type",
        ["All", "Steam Moves", "Reverse Line Movement", "Sharp Action"]
    )

with col2:
    threshold = st.slider(
        "Movement Threshold (%)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Minimum line movement percentage to trigger an alert"
    )
    books = st.multiselect(
        "Track Sportsbooks",
        ["DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"],
        default=["DraftKings", "FanDuel", "BetMGM"]
    )

# Track movements
if st.button("Track Movements"):
    with st.spinner("Analyzing line movements..."):
        try:
            # Get sharp movements from betting system
            movements = st.session_state.betting_system.get_sharp_movements(
                timeframe=timeframe,
                movement_type=movement_type,
                threshold=threshold,
                books=books
            )
            
            if movements:
                # Display movements
                st.subheader("Recent Line Movements")
                st.dataframe(
                    pd.DataFrame(movements).style.highlight_max(subset=['Sharp %'])
                )
                
                # Steam move analysis
                st.subheader("Steam Move Analysis")
                steam_data = st.session_state.betting_system.get_steam_move_analysis(
                    game=movements[0]['Game']  # Analyze first game
                )
                
                if steam_data:
                    # Create a figure with two y-axes
                    fig = go.Figure()
                    
                    # Add line movement trace
                    fig.add_trace(
                        go.Scatter(x=steam_data['Time'], y=steam_data['Line'],
                                  name='Line', yaxis='y')
                    )
                    
                    # Add sharp money percentage trace
                    fig.add_trace(
                        go.Scatter(x=steam_data['Time'], y=steam_data['Sharp Money %'],
                                  name='Sharp Money %', yaxis='y2')
                    )
                    
                    # Update layout for dual axes
                    fig.update_layout(
                        title='Steam Move Analysis - ' + movements[0]['Game'],
                        yaxis=dict(title='Line', side='left'),
                        yaxis2=dict(title='Sharp Money %', side='right', overlaying='y'),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Sharp money distribution
                    st.subheader("Sharp Money Distribution")
                    sharp_dist = st.session_state.betting_system.get_sharp_money_distribution(
                        game=movements[0]['Game']
                    )
                    
                    if sharp_dist:
                        fig = px.pie(sharp_dist, 
                                   values='Sharp Money %', 
                                   names='Book',
                                   title='Sharp Money Distribution Across Books')
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No significant movements found for the selected criteria")
        except Exception as e:
            st.error(f"Error analyzing movements: {str(e)}")

# Tips section
with st.expander("Sharp Movement Analysis Tips"):
    st.markdown("""
    ### Understanding Sharp Money Movements
    1. **Steam Moves**: Sudden, coordinated line movements across multiple books
    2. **Reverse Line Movement**: When the line moves opposite to the public betting percentage
    3. **Sharp Action**: Heavy betting from accounts marked as sharp by sportsbooks
    4. **Line Origination**: Pay attention to which books move first
    5. **Timing**: Sharp money often comes in early or very late in the market
    """)

# Active alerts
st.subheader("Active Sharp Money Alerts")
try:
    alerts = st.session_state.betting_system.get_active_alerts()
    if alerts:
        for alert in alerts:
            st.info(f"🔔 **{alert['game']}**: {alert['alert']}")
    else:
        st.info("No active alerts at this time")
except Exception as e:
    st.error(f"Error fetching alerts: {str(e)}")

# Footer
st.markdown("---")
st.caption("Data updates every 30 seconds. Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")) 