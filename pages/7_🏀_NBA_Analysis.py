import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="NBA Analysis - The Rounders", page_icon="🏀", layout="wide")

# Access shared session state
if 'betting_system' not in st.session_state:
    st.error("Please initialize the app from the home page")
    st.stop()

# Title and description
st.title("NBA Betting Analysis")
st.markdown("""
Advanced NBA betting analysis including line predictions, injury impacts, situational spots, and arbitrage opportunities.
This tool combines machine learning predictions with sharp money tracking to find the best betting opportunities.
""")

# Show current mode
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

# Filters section
col1, col2, col3 = st.columns(3)

with col1:
    games = st.multiselect(
        "Select Games",
        st.session_state.betting_system.get_nba_games(),
        help="Select NBA games to analyze"
    )
    
    market_type = st.selectbox(
        "Market Type",
        ["Full Game", "1st Quarter", "1st Half", "Player Props"],
        help="Select the type of market to analyze"
    )

with col2:
    books = st.multiselect(
        "Sportsbooks",
        ["Pinnacle", "Circa", "Bookmaker", "DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"],
        default=["Pinnacle", "Circa", "Bookmaker", "DraftKings", "FanDuel"],
        help="Select sportsbooks to compare"
    )
    
    min_edge = st.slider(
        "Minimum Edge (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Minimum edge percentage to highlight opportunities"
    )

with col3:
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
    
    show_analysis = st.checkbox(
        "Show Advanced Analysis",
        value=True,
        help="Display additional analysis like injury impacts and situational spots"
    )

# Main analysis section
if st.button("Analyze Games") or auto_refresh:
    with st.spinner("Analyzing NBA games..."):
        try:
            for game in games:
                st.subheader(f"Analysis for {game}")
                
                # Get comprehensive game analysis
                analysis = st.session_state.betting_system.analyze_nba_game(game)
                
                if analysis:
                    # Display analysis in tabs
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "Line Prediction",
                        "Situational Analysis",
                        "Value Opportunities",
                        "Live Betting"
                    ])
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Model prediction
                            st.subheader("Line Prediction")
                            prediction = analysis['line_prediction']
                            if prediction:
                                st.metric(
                                    "Predicted Line",
                                    f"{prediction['predicted_line']:.1f}",
                                    f"{prediction['predicted_line'] - prediction['sharp_consensus']:.1f}"
                                )
                                st.metric(
                                    "Model Confidence",
                                    f"{prediction['model_confidence']:.2%}"
                                )
                                
                                # Visualization of line prediction vs market
                                fig = go.Figure()
                                fig.add_trace(
                                    go.Scatter(
                                        x=['Model', 'Sharp', 'Market'],
                                        y=[
                                            prediction['predicted_line'],
                                            prediction['sharp_consensus'],
                                            analysis['current_market_line']
                                        ],
                                        mode='lines+markers',
                                        name='Lines'
                                    )
                                )
                                fig.update_layout(
                                    title='Line Comparison',
                                    yaxis_title='Spread'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Market analysis
                            st.subheader("Market Analysis")
                            st.write("Sharp vs. Public Money")
                            fig = go.Figure()
                            fig.add_trace(
                                go.Bar(
                                    x=['Sharp', 'Public'],
                                    y=[
                                        analysis['sharp_money_percentage'],
                                        analysis['public_money_percentage']
                                    ],
                                    name='Betting Percentages'
                                )
                            )
                            fig.update_layout(
                                title='Money Distribution',
                                yaxis_title='Percentage'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Injury impact
                            st.subheader("Injury Impact")
                            injuries = analysis['injury_impact']
                            if injuries:
                                st.dataframe(pd.DataFrame(injuries))
                                st.metric(
                                    "Total Injury Impact",
                                    f"{injuries['total_impact']:.1f} points"
                                )
                        
                        with col2:
                            # Situational spots
                            st.subheader("Situational Analysis")
                            spots = analysis['situational_spots']
                            
                            # Rest advantage
                            st.write("Rest Advantage")
                            rest = spots['rest_advantage']
                            st.metric(
                                "Rest Differential",
                                f"{rest['rest_advantage']} days",
                                f"{rest['line_impact']:.1f} points"
                            )
                            
                            # Back-to-back
                            st.write("Back-to-Back Situations")
                            b2b = spots['back_to_back']
                            if b2b['home_b2b'] or b2b['away_b2b']:
                                st.warning(
                                    f"{'Home' if b2b['home_b2b'] else 'Away'} team on back-to-back"
                                )
                                st.metric(
                                    "B2B Impact",
                                    f"{b2b['line_impact']:.1f} points"
                                )
                    
                    with tab3:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Value opportunities
                            st.subheader("Value Betting Opportunities")
                            value_bets = analysis['value_bets']
                            if value_bets:
                                st.dataframe(
                                    pd.DataFrame(value_bets)
                                    .style.highlight_max(subset=['edge'])
                                )
                                
                                # Visualize edges
                                fig = px.bar(
                                    pd.DataFrame(value_bets),
                                    x='market',
                                    y='edge',
                                    color='confidence',
                                    title='Value Betting Edges'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No significant value opportunities found")
                        
                        with col2:
                            # Arbitrage opportunities
                            st.subheader("Arbitrage Opportunities")
                            arb_opps = analysis['arbitrage_opportunities']
                            if arb_opps:
                                st.dataframe(
                                    pd.DataFrame(arb_opps)
                                    .style.highlight_max(subset=['profit_percentage'])
                                )
                                
                                # Display optimal bet sizing
                                st.subheader("Optimal Arbitrage Bets")
                                for arb in arb_opps:
                                    st.write(f"**{arb['type']} Arbitrage**")
                                    st.write(f"Profit: {arb['profit_percentage']:.2f}%")
                                    st.write("Bet Distribution:")
                                    st.write(f"- Bet 1: {arb['optimal_bets']['stake1_percentage']:.1f}%")
                                    st.write(f"- Bet 2: {arb['optimal_bets']['stake2_percentage']:.1f}%")
                            else:
                                st.info("No arbitrage opportunities found")
                    
                    with tab4:
                        # Live betting analysis
                        st.subheader("Live Betting Analysis")
                        live = analysis['live_betting_opportunities']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Key numbers
                            st.write("Key Numbers to Watch")
                            st.write(f"Current margin targets: {', '.join(map(str, live['key_numbers']))}")
                            
                            # Momentum analysis
                            st.write("Momentum Analysis")
                            if live['momentum_shifts']:
                                st.dataframe(pd.DataFrame(live['momentum_shifts']))
                        
                        with col2:
                            # Live betting triggers
                            st.write("Live Betting Triggers")
                            if live['live_betting_triggers']:
                                for trigger in live['live_betting_triggers']:
                                    st.info(f"🎯 {trigger['description']}")
                                    st.write(f"Edge: {trigger['edge']:.1f}%")
                            else:
                                st.info("No active live betting triggers")
                else:
                    st.warning("Unable to analyze game at this time")
        except Exception as e:
            st.error(f"Error analyzing games: {str(e)}")

# Tips section
with st.expander("NBA Betting Tips"):
    st.markdown("""
    ### NBA Betting Strategy
    1. **Line Shopping**
       - Focus on sharp books for market prices
       - Look for stale lines in retail books
       - Pay attention to early morning lines
       
    2. **Injury Impact**
       - Monitor late scratches and rest days
       - Consider rotation changes
       - Factor in back-to-back games
       
    3. **Situational Spots**
       - Look for rest advantages
       - Consider travel and time zones
       - Watch for letdown and look-ahead spots
       
    4. **Live Betting**
       - Wait for key momentum shifts
       - Target specific point margins
       - Consider pace and matchup factors
       
    5. **Props and Derivatives**
       - Compare to season averages
       - Consider matchup history
       - Watch for role changes
    """)

# Footer with auto-refresh status
st.markdown("---")
if auto_refresh:
    time_placeholder = st.empty()
    time_placeholder.caption(f"Data updates every 30 seconds. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 