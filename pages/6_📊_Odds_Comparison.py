import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Odds Comparison - The Rounders", page_icon="📊", layout="wide")

# Access shared session state
if 'betting_system' not in st.session_state:
    st.error("Please initialize the app from the home page")
    st.stop()

# Title and description
st.title("Odds Comparison Dashboard")
st.markdown("""
Compare odds across different sportsbooks in real-time. 
Track line movements, find the best odds, and identify potential arbitrage opportunities.
""")

# Show current mode
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

# Filters section
col1, col2, col3 = st.columns(3)

with col1:
    sport = st.selectbox(
        "Sport",
        ["NBA", "NFL", "MLB", "NHL", "NCAAB", "NCAAF", "UFC", "Tennis", "Golf", "Soccer"],
        help="Select the sport to track"
    )
    
    market_type = st.selectbox(
        "Market Type",
        ["Moneyline", "Spread", "Totals"],
        help="Select the type of market to analyze"
    )

with col2:
    books = st.multiselect(
        "Sportsbooks",
        ["Pinnacle", "Circa", "Bookmaker", "DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"],
        default=["Pinnacle", "Circa", "Bookmaker", "DraftKings", "FanDuel"],
        help="Select sportsbooks to compare. Sharp books are listed first."
    )
    
    min_edge = st.slider(
        "Minimum Edge (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Minimum edge percentage to highlight value opportunities"
    )

with col3:
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
    
    show_analysis = st.checkbox(
        "Show Advanced Analysis",
        value=True,
        help="Display additional analysis like sharp money and steam moves"
    )

# Main odds comparison table
if st.button("Fetch Odds") or auto_refresh:
    with st.spinner("Fetching latest odds..."):
        try:
            # Get current odds from betting system
            odds_data = st.session_state.betting_system.get_current_odds(
                sport=sport,
                market_type=market_type.lower(),
                books=books
            )
            
            if odds_data:
                # Display odds in tabs
                tab1, tab2, tab3 = st.tabs(["Current Odds", "Line Movement", "Opportunities"])
                
                with tab1:
                    st.subheader("Current Odds Comparison")
                    odds_df = pd.DataFrame(odds_data['current_odds'])
                    
                    # Highlight best odds
                    if market_type == "Moneyline":
                        st.dataframe(
                            odds_df.style.highlight_max(subset=['Home Odds', 'Away Odds'])
                        )
                    else:
                        st.dataframe(
                            odds_df.style.highlight_max(subset=['Odds'])
                                   .highlight_min(subset=['Line'])
                        )
                    
                    # Consensus lines chart
                    st.subheader("Market Consensus")
                    fig = go.Figure()
                    
                    # Add sharp books consensus
                    fig.add_trace(
                        go.Scatter(
                            x=odds_data['consensus']['time'],
                            y=odds_data['consensus']['sharp'],
                            name='Sharp Consensus',
                            line=dict(width=3, color='red')
                        )
                    )
                    
                    # Add public books consensus
                    fig.add_trace(
                        go.Scatter(
                            x=odds_data['consensus']['time'],
                            y=odds_data['consensus']['public'],
                            name='Public Consensus',
                            line=dict(width=2, color='blue')
                        )
                    )
                    
                    fig.update_layout(
                        title='Sharp vs. Public Consensus Lines',
                        xaxis_title='Time',
                        yaxis_title='Line',
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Line movement chart
                        st.subheader("Line Movement History")
                        fig = go.Figure()
                        
                        for book in books:
                            if book in odds_data['line_history']:
                                fig.add_trace(
                                    go.Scatter(
                                        x=odds_data['line_history'][book]['time'],
                                        y=odds_data['line_history'][book]['line'],
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
                    
                    with col2:
                        # Steam moves analysis
                        st.subheader("Steam Moves")
                        if odds_data['steam_moves']:
                            steam_df = pd.DataFrame(odds_data['steam_moves'])
                            st.dataframe(steam_df)
                            
                            # Visualize steam moves
                            fig = px.scatter(
                                steam_df,
                                x='timestamp',
                                y='line_diff',
                                size='books_moving',
                                hover_data=['books'],
                                title='Steam Moves Detection'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No steam moves detected in the selected timeframe")
                
                with tab3:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Value opportunities
                        st.subheader("Value Betting Opportunities")
                        if odds_data['value_opportunities']:
                            value_df = pd.DataFrame(odds_data['value_opportunities'])
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
                    
                    with col2:
                        # Arbitrage opportunities
                        st.subheader("Arbitrage Opportunities")
                        if odds_data['arbitrage']:
                            arb_df = pd.DataFrame(odds_data['arbitrage'])
                            st.dataframe(
                                arb_df.style.highlight_max(subset=['profit_percentage'])
                            )
                            
                            # Display optimal bet sizing
                            st.subheader("Optimal Arbitrage Bets")
                            for arb in odds_data['arbitrage']:
                                st.write(f"**{arb['type']} Arbitrage**")
                                st.write(f"Profit: {arb['profit_percentage']:.2f}%")
                                st.write("Bet Distribution:")
                                st.write(f"- Bet 1: {arb['optimal_bets']['stake1_percentage']:.1f}%")
                                st.write(f"- Bet 2: {arb['optimal_bets']['stake2_percentage']:.1f}%")
                        else:
                            st.info("No arbitrage opportunities found")
            else:
                st.warning("No odds data available for the selected criteria")
        except Exception as e:
            st.error(f"Error fetching odds: {str(e)}")

# Tips section
with st.expander("Odds Comparison Tips"):
    st.markdown("""
    ### Best Practices for Line Shopping
    1. **Compare Multiple Books**: Always check at least 3-4 sportsbooks before placing a bet
       - Focus on sharp books for accurate market prices
       - Look for outliers in retail books for value
       
    2. **Track Line Movement**: Watch for significant line moves
       - Sharp books usually move first
       - Quick moves across multiple books indicate steam
       - Pay attention to overnight and early morning movements
       
    3. **Understand the Market**: Different books have different tendencies
       - Sharp books (Pinnacle, Circa, Bookmaker) set the market
       - Retail books often shade lines based on public betting
       - Some books are slow to update, creating opportunities
       
    4. **Look for Value**: Don't just take the best price
       - Compare to sharp consensus lines
       - Consider the timing of your bets
       - Factor in book limits and restrictions
       
    5. **Use Multiple Accounts**: Maintain accounts at several books
       - Helps capture best odds
       - Useful for arbitrage opportunities
       - Reduces exposure to single book limits
    """)

# Footer with auto-refresh status
st.markdown("---")
if auto_refresh:
    time_placeholder = st.empty()
    time_placeholder.caption(f"Data updates every 30 seconds. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 