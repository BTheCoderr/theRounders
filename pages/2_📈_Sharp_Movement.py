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
col1, col2, col3 = st.columns(3)

with col1:
    sport = st.selectbox(
        "Sport",
        ["NBA", "NFL", "MLB", "NHL", "NCAAB", "NCAAF"],
        help="Select the sport to track"
    )
    
    timeframe = st.selectbox(
        "Timeframe",
        ["Last Hour", "Last 3 Hours", "Last 6 Hours", "Last 12 Hours", "Last 24 Hours"]
    )

with col2:
    movement_type = st.selectbox(
        "Movement Type",
        ["All", "Steam Moves", "Reverse Line Movement", "Sharp Action", "Value Opportunities"]
    )
    
    threshold = st.slider(
        "Movement Threshold (%)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Minimum line movement percentage to trigger an alert"
    )

with col3:
    books = st.multiselect(
        "Track Sportsbooks",
        ["Pinnacle", "Circa", "Bookmaker", "DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"],
        default=["Pinnacle", "Circa", "Bookmaker"],
        help="Select sportsbooks to track. Sharp books are listed first."
    )
    
    min_books = st.number_input(
        "Minimum Books Moving",
        min_value=2,
        max_value=len(books),
        value=3,
        help="Minimum number of books that must move together for steam move detection"
    )

# Track movements
if st.button("Track Movements"):
    with st.spinner("Analyzing line movements..."):
        try:
            # Get sharp movements from betting system
            movements = st.session_state.betting_system.get_sharp_movements(
                sport=sport,
                timeframe=timeframe,
                movement_type=movement_type,
                threshold=threshold,
                books=books,
                min_books=min_books
            )
            
            if movements:
                # Display movements in tabs
                tab1, tab2, tab3 = st.tabs(["Recent Movements", "Analysis", "Opportunities"])
                
                with tab1:
                    st.subheader("Recent Line Movements")
                    movements_df = pd.DataFrame(movements['movements'])
                    st.dataframe(
                        movements_df.style.highlight_max(subset=['Sharp %'])
                                      .highlight_min(subset=['Public %'])
                    )
                    
                    # Line movement chart
                    st.subheader("Line Movement Visualization")
                    fig = go.Figure()
                    
                    # Add line for each book
                    for book in books:
                        if book in movements['book_lines']:
                            fig.add_trace(
                                go.Scatter(
                                    x=movements['book_lines'][book]['time'],
                                    y=movements['book_lines'][book]['line'],
                                    name=book,
                                    line=dict(
                                        width=3 if book in ["Pinnacle", "Circa", "Bookmaker"] else 1
                                    )
                                )
                            )
                    
                    fig.update_layout(
                        title='Line Movement by Sportsbook',
                        xaxis_title='Time',
                        yaxis_title='Line',
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Sharp vs. Public Analysis
                        st.subheader("Sharp vs. Public Analysis")
                        sharp_public_df = pd.DataFrame({
                            'Book': movements['sharp_public']['books'],
                            'Sharp %': movements['sharp_public']['sharp_pct'],
                            'Public %': movements['sharp_public']['public_pct'],
                            'Line': movements['sharp_public']['lines']
                        })
                        st.dataframe(sharp_public_df)
                        
                        # Visualize sharp vs public money
                        fig = go.Figure()
                        fig.add_trace(
                            go.Bar(
                                name='Sharp Money',
                                x=sharp_public_df['Book'],
                                y=sharp_public_df['Sharp %']
                            )
                        )
                        fig.add_trace(
                            go.Bar(
                                name='Public Money',
                                x=sharp_public_df['Book'],
                                y=sharp_public_df['Public %']
                            )
                        )
                        fig.update_layout(
                            title='Sharp vs. Public Money Distribution',
                            barmode='group'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Steam Move Analysis
                        st.subheader("Steam Move Analysis")
                        if movements['steam_moves']:
                            steam_df = pd.DataFrame(movements['steam_moves'])
                            st.dataframe(steam_df)
                            
                            # Visualize steam moves
                            fig = px.scatter(
                                steam_df,
                                x='timestamp',
                                y='line_diff',
                                size='books_moving',
                                hover_data=['books_involved'],
                                title='Steam Moves Detection'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No steam moves detected in the selected timeframe")
                
                with tab3:
                    # Value Opportunities
                    st.subheader("Value Betting Opportunities")
                    if movements['value_opportunities']:
                        value_df = pd.DataFrame(movements['value_opportunities'])
                        st.dataframe(
                            value_df.style.highlight_max(subset=['edge'])
                        )
                        
                        # Visualize value opportunities
                        fig = px.bar(
                            value_df,
                            x='book',
                            y='edge',
                            color='type',
                            title='Value Betting Edges by Book'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No significant value opportunities found")
            else:
                st.info("No significant movements found for the selected criteria")
        except Exception as e:
            st.error(f"Error analyzing movements: {str(e)}")

# Tips section
with st.expander("Sharp Movement Analysis Tips"):
    st.markdown("""
    ### Understanding Sharp Money Movements
    1. **Steam Moves**: Sudden, coordinated line movements across multiple books
       - Look for quick movements across 3+ books
       - Pay attention to the order of books moving
       - Sharp books usually move first
       
    2. **Reverse Line Movement**: When the line moves opposite to the public betting percentage
       - High public percentage but line moves the other way
       - Often indicates sharp money taking the other side
       - Most reliable when seen at sharp books
       
    3. **Sharp Action**: Heavy betting from accounts marked as sharp by sportsbooks
       - Focus on movements at Pinnacle, Circa, and Bookmaker
       - Look for significant line moves with low public interest
       - Pay attention to early morning movements
       
    4. **Line Origination**: Which books move first matters
       - Sharp books (Pinnacle, Circa, Bookmaker) are market leaders
       - Retail books (DraftKings, FanDuel, etc.) usually follow
       - Pay attention to books that consistently lead movements
       
    5. **Timing Patterns**: When moves happen is important
       - Sharp money often comes early in the market
       - Late sharp moves can be very significant
       - Be cautious of mid-day retail-led movements
    """)

# Active alerts
st.subheader("Active Sharp Money Alerts")
try:
    alerts = st.session_state.betting_system.get_active_alerts()
    if alerts:
        for alert in alerts:
            severity = "🔴" if alert['confidence'] > 0.8 else "🟡" if alert['confidence'] > 0.5 else "🟢"
            st.info(f"{severity} **{alert['game']}**: {alert['alert']} (Confidence: {alert['confidence']:.2f})")
    else:
        st.info("No active alerts at this time")
except Exception as e:
    st.error(f"Error fetching alerts: {str(e)}")

# Footer with auto-refresh
st.markdown("---")
auto_refresh = st.checkbox("Auto-refresh data (30s)", value=True)
if auto_refresh:
    st.empty()
    time_placeholder = st.empty()
    time_placeholder.caption(f"Data updates every 30 seconds. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 