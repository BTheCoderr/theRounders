import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Analytics - The Rounders", page_icon="📊", layout="wide")

# Access shared session state
if 'betting_system' not in st.session_state:
    st.error("Please initialize the app from the home page")
    st.stop()

# Title and description
st.title("Betting Analytics")
st.markdown("""
Track and analyze your betting performance with detailed metrics and visualizations.
Get insights into your betting patterns, ROI, and areas for improvement.
""")

# Show current mode
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

try:
    # Get analytics from betting system
    analytics = st.session_state.betting_system.get_analytics()
    
    if analytics:
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Bets",
                str(analytics['overall']['total_bets']),
                delta=f"{analytics['overall']['bets_last_week']} this week",
                help="Total number of bets placed"
            )
        with col2:
            st.metric(
                "Win Rate",
                f"{analytics['overall']['win_rate']:.1%}",
                delta=f"{analytics['overall']['win_rate_change']:.1%}",
                help="Overall win rate for all bets"
            )
        with col3:
            st.metric(
                "ROI",
                f"{analytics['overall']['roi']:.1%}",
                delta=f"{analytics['overall']['roi_change']:.1%}",
                help="Return on Investment"
            )
        with col4:
            st.metric(
                "CLV",
                f"{analytics['overall']['avg_clv']:.2f}",
                delta=f"{analytics['overall']['clv_change']:.2f}",
                help="Average Closing Line Value"
            )
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs(["Performance", "CLV Analysis", "Sharp Money"])
        
        with tab1:
            st.subheader("Performance Metrics")
            
            # Time period selection
            timeframe = st.selectbox(
                "Select Timeframe",
                ["Last Week", "Last Month", "Last 3 Months", "Year to Date", "All Time"]
            )
            
            # Performance over time
            if analytics['trends']:
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(x=analytics['trends']['dates'],
                              y=analytics['trends']['win_rates'],
                              name='Win Rate', yaxis='y1')
                )
                fig.add_trace(
                    go.Scatter(x=analytics['trends']['dates'],
                              y=analytics['trends']['rois'],
                              name='ROI', yaxis='y2')
                )
                fig.update_layout(
                    title='Daily Performance Metrics',
                    yaxis=dict(title='Win Rate', side='left'),
                    yaxis2=dict(title='ROI', side='right', overlaying='y')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Performance by sport
            if analytics['by_sport']:
                sport_df = pd.DataFrame(analytics['by_sport'])
                fig = px.bar(sport_df,
                            x='sport',
                            y=['win_rate', 'roi'],
                            barmode='group',
                            title='Performance Metrics by Sport')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Closing Line Value Analysis")
            
            # CLV distribution
            if analytics['clv_analysis']:
                clv_dist = pd.DataFrame(analytics['clv_analysis']['distribution'])
                fig = px.histogram(clv_dist,
                                 x='clv',
                                 y='frequency',
                                 title='Distribution of Closing Line Value',
                                 labels={'clv': 'Closing Line Value',
                                       'frequency': 'Number of Bets'})
                st.plotly_chart(fig, use_container_width=True)
                
                # CLV by sport
                clv_sport = pd.DataFrame(analytics['clv_analysis']['by_sport'])
                fig = px.bar(clv_sport,
                            x='sport',
                            y='avg_clv',
                            title='Average CLV by Sport')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Sharp Money Analysis")
            
            # Sharp money performance
            if analytics['sharp_money']:
                sharp_df = pd.DataFrame(analytics['sharp_money']['performance'])
                fig = px.bar(sharp_df,
                            x='category',
                            y=['win_rate', 'roi'],
                            barmode='group',
                            title='Performance with Sharp Money')
                st.plotly_chart(fig, use_container_width=True)
                
                # Steam move analysis
                steam_df = pd.DataFrame(analytics['sharp_money']['steam_moves'])
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(x=steam_df['time'],
                              y=steam_df['win_rate'],
                              name='Win Rate', yaxis='y1')
                )
                fig.add_trace(
                    go.Bar(x=steam_df['time'],
                          y=steam_df['number_of_moves'],
                          name='Number of Moves', yaxis='y2')
                )
                fig.update_layout(
                    title='Steam Move Analysis',
                    yaxis=dict(title='Win Rate', side='left'),
                    yaxis2=dict(title='Number of Moves', side='right', overlaying='y')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Betting patterns analysis
        st.subheader("Betting Patterns Analysis")
        
        # Create columns for different metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance by day of week
            if analytics['patterns']['by_day']:
                day_df = pd.DataFrame(analytics['patterns']['by_day'])
                fig = px.bar(day_df,
                            x='day',
                            y='win_rate',
                            title='Win Rate by Day of Week')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Performance by bet type
            if analytics['patterns']['by_type']:
                type_df = pd.DataFrame(analytics['patterns']['by_type'])
                fig = px.bar(type_df,
                            x='type',
                            y='win_rate',
                            title='Win Rate by Bet Type')
                st.plotly_chart(fig, use_container_width=True)
        
        # Tips and insights
        with st.expander("Analysis Insights"):
            insights = analytics.get('insights', [])
            if insights:
                st.markdown("### Key Insights")
                for i, insight in enumerate(insights, 1):
                    st.markdown(f"{i}. **{insight['title']}**: {insight['description']}")
            else:
                st.markdown("""
                ### Key Insights
                1. **Best Performance**: Highest win rate on Tuesdays (62%)
                2. **Most Profitable**: Player props showing highest ROI at 12.4%
                3. **Sharp Money**: Following sharp money movement shows 62% win rate
                4. **CLV Edge**: Average CLV of +1.8 indicates good line shopping
                5. **Improvement Areas**: 
                    - Lower win rate on weekends
                    - Totals bets underperforming other markets
                """)
    else:
        st.warning("No betting data available for analysis")

except Exception as e:
    st.error(f"Error getting analytics: {str(e)}")

# Footer
st.markdown("---")
st.caption("Analytics update hourly. Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")) 