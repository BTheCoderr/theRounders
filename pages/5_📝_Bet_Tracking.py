import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Bet Tracking - The Rounders", page_icon="📝", layout="wide")

# Access shared session state
if 'betting_system' not in st.session_state:
    st.error("Please initialize the app from the home page")
    st.stop()

# Title and description
st.title("Bet Tracking")
st.markdown("""
Log and track your bets with detailed record keeping.
Monitor your betting history, analyze patterns, and maintain proper bankroll management.
""")

# Show current mode
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

try:
    # Get current stats from betting system
    current_stats = st.session_state.betting_system.get_current_stats()
    
    if current_stats:
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Active Bets",
                str(current_stats['active_bets']),
                delta=f"{current_stats['new_bets_today']} new today",
                help="Number of currently active bets"
            )
        with col2:
            st.metric(
                "Today's P/L",
                f"${current_stats['todays_pl']:,.2f}",
                delta=f"{current_stats['todays_pl_pct']:.1%}",
                help="Profit/Loss for today"
            )
        with col3:
            st.metric(
                "Week's P/L",
                f"${current_stats['weeks_pl']:,.2f}",
                delta=f"{current_stats['weeks_pl_pct']:.1%}",
                help="Profit/Loss for this week"
            )
        with col4:
            st.metric(
                "Bankroll",
                f"${current_stats['bankroll']:,.2f}",
                delta=f"${current_stats['bankroll_change']:,.2f}",
                help="Current bankroll"
            )
        
        # Add new bet form
        st.subheader("Add New Bet")
        with st.form("new_bet_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sport = st.selectbox(
                    "Sport",
                    ["NBA", "NFL", "MLB", "NHL", "UFC/MMA", "Soccer"]
                )
                bet_type = st.selectbox(
                    "Bet Type",
                    ["Spread", "Moneyline", "Total", "Player Prop", "Parlay"]
                )
                
            with col2:
                game = st.text_input("Game/Event")
                selection = st.text_input("Selection")
                
            with col3:
                odds = st.number_input("Odds (American)", value=-110)
                stake = st.number_input("Stake ($)", 
                                      value=current_stats.get('recommended_stake', 100.0),
                                      step=10.0)
                
            notes = st.text_area("Notes/Analysis")
            submitted = st.form_submit_button("Add Bet")
            
            if submitted:
                try:
                    # Add bet using betting system
                    bet_data = {
                        'sport': sport,
                        'bet_type': bet_type,
                        'game': game,
                        'selection': selection,
                        'odds': odds,
                        'stake': stake,
                        'notes': notes,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    success = st.session_state.betting_system.add_bet(bet_data)
                    if success:
                        st.success("Bet added successfully!")
                    else:
                        st.error("Failed to add bet")
                except Exception as e:
                    st.error(f"Error adding bet: {str(e)}")
        
        # Active bets
        st.subheader("Active Bets")
        active_bets = st.session_state.betting_system.get_active_bets()
        if active_bets:
            st.dataframe(pd.DataFrame(active_bets))
        else:
            st.info("No active bets")
        
        # Bet history
        st.subheader("Bet History")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now() - timedelta(days=30), datetime.now())
            )
        with col2:
            sport_filter = st.multiselect(
                "Sport",
                ["NBA", "NFL", "MLB", "NHL"],
                default=["NBA", "NFL", "MLB", "NHL"]
            )
        with col3:
            result_filter = st.multiselect(
                "Result",
                ["Win", "Loss", "Push", "Pending"],
                default=["Win", "Loss", "Push", "Pending"]
            )
        
        # Get filtered history
        history = st.session_state.betting_system.get_bet_history(
            start_date=date_range[0],
            end_date=date_range[1],
            sports=sport_filter,
            results=result_filter
        )
        
        if history:
            st.dataframe(
                pd.DataFrame(history).style.apply(
                    lambda x: ['background: #90EE90' if v == 'Win' 
                             else 'background: #FFB6C1' if v == 'Loss'
                             else 'background: #F0F0F0' if v == 'Push'
                             else '' for v in x],
                    subset=['Result']
                )
            )
            
            # Performance visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Cumulative P/L chart
                st.subheader("Cumulative P/L")
                history_df = pd.DataFrame(history)
                history_df['Cumulative P/L'] = history_df['P/L'].cumsum()
                
                fig = px.line(history_df,
                            x='Date',
                            y='Cumulative P/L',
                            title='Cumulative Profit/Loss Over Time')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Win/Loss distribution
                st.subheader("Win/Loss Distribution")
                result_counts = pd.DataFrame(history)['Result'].value_counts()
                
                fig = px.pie(values=result_counts.values,
                            names=result_counts.index,
                            title='Win/Loss Distribution')
                st.plotly_chart(fig, use_container_width=True)
            
            # Bankroll management
            st.subheader("Bankroll Management")
            col1, col2 = st.columns(2)
            
            with col1:
                # Bankroll over time
                bankroll_data = st.session_state.betting_system.get_bankroll_history()
                if bankroll_data:
                    fig = px.line(pd.DataFrame(bankroll_data),
                                x='Date',
                                y='Bankroll',
                                title='Bankroll Over Time')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Stake distribution
                st.subheader("Stake Distribution")
                history_df = pd.DataFrame(history)
                stake_ranges = pd.cut(history_df['Stake'],
                                    bins=[0, 100, 200, 300, 400, float('inf')],
                                    labels=['$0-100', '$101-200', '$201-300', '$301-400', '$400+'])
                stake_dist = stake_ranges.value_counts()
                
                fig = px.bar(x=stake_dist.index,
                            y=stake_dist.values,
                            title='Stake Distribution')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No bet history found for the selected filters")
        
        # Tips section
        with st.expander("Betting Tips"):
            st.markdown("""
            ### Best Practices for Bet Tracking
            1. **Record Everything**: Log all bets immediately after placing them
            2. **Include Notes**: Document your reasoning for each bet
            3. **Track CLV**: Compare your odds to closing lines
            4. **Review Regularly**: Analyze your betting patterns weekly
            5. **Maintain Discipline**: Stick to your predetermined stake sizes
            """)
        
        # Export options
        st.subheader("Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to CSV"):
                if history:
                    csv = pd.DataFrame(history).to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="bet_history.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data to export")
        
        with col2:
            if st.button("Export to Excel"):
                st.info("Excel export functionality coming soon!")
    else:
        st.warning("No betting data available")

except Exception as e:
    st.error(f"Error loading bet tracking data: {str(e)}")

# Footer
st.markdown("---")
st.caption("Data updates in real-time. Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")) 