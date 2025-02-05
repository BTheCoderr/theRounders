import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Power Rankings - The Rounders", page_icon="🏆", layout="wide")

# Access shared session state
if 'nba_ratings' not in st.session_state or 'mlb_ratings' not in st.session_state:
    st.error("Please initialize the app from the home page")
    st.stop()

# Title and description
st.title("Power Rankings & Ratings")
st.markdown("""
View comprehensive power rankings and ratings for teams across different sports.
These ratings incorporate various factors including offense, defense, and recent performance.
""")

# Show current mode
mode_status = "🟢" if st.session_state.betting_mode == "paper" else "🔴"
st.sidebar.info(f"{mode_status} Currently in {'Paper Trading' if st.session_state.betting_mode == 'paper' else 'Real Money'} mode")

# Sport selection
SPORTS = {
    "NBA": {"icon": "🏀", "ratings": st.session_state.nba_ratings},
    "MLB": {"icon": "⚾", "ratings": st.session_state.mlb_ratings},
    "NFL": {"icon": "🏈", "ratings": None},
    "NHL": {"icon": "🏒", "ratings": None}
}

selected_sport = st.selectbox(
    "Select Sport",
    list(SPORTS.keys()),
    format_func=lambda x: f"{SPORTS[x]['icon']} {x}"
)

# Create tabs for different rating views
tab1, tab2, tab3, tab4 = st.tabs(["Team Ratings", "Offensive Ratings", "Defensive Ratings", "Matchup Predictor"])

with tab1:
    st.subheader("Team Power Ratings")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        timeframe = st.selectbox(
            "Timeframe",
            ["Last Week", "Last Month", "Last 3 Months", "Season to Date"]
        )
    with col2:
        rating_type = st.selectbox(
            "Rating Type",
            ["Overall", "Home", "Away", "vs. Winning Teams", "vs. Losing Teams"]
        )
    
    # Get ratings from the appropriate system
    if SPORTS[selected_sport]["ratings"]:
        try:
            ratings = SPORTS[selected_sport]["ratings"].get_power_ratings(
                timeframe=timeframe,
                rating_type=rating_type
            )
            
            if ratings:
                # Display rankings table
                st.dataframe(
                    ratings.style
                    .background_gradient(subset=['Rating'])
                    .bar(subset=['Off Rating', 'Def Rating'], color=['#90EE90', '#FFB6C1'])
                    .format({
                        'Rating': '{:.1f}',
                        'Off Rating': '{:.1f}',
                        'Def Rating': '{:.1f}',
                        'SOS': '{:.3f}'
                    })
                )
                
                # Rating distribution visualization
                fig = px.scatter(ratings,
                               x='Off Rating',
                               y='Def Rating',
                               text='Team',
                               title='Offensive vs Defensive Ratings',
                               labels={'Off Rating': 'Offensive Rating',
                                      'Def Rating': 'Defensive Rating'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No ratings data available for the selected criteria")
        except Exception as e:
            st.error(f"Error getting ratings: {str(e)}")
    else:
        st.warning(f"Ratings not yet available for {selected_sport}")

with tab2:
    st.subheader("Offensive Ratings Breakdown")
    
    if SPORTS[selected_sport]["ratings"]:
        try:
            # Get offensive metrics from rating system
            off_metrics = SPORTS[selected_sport]["ratings"].get_offensive_metrics()
            
            if off_metrics:
                # Team selection for detailed analysis
                selected_team = st.selectbox("Select Team for Detailed Analysis", off_metrics['Team'].unique())
                team_metrics = off_metrics[off_metrics['Team'] == selected_team].iloc[0]
                
                # Get metric names excluding 'Team'
                metrics = [col for col in off_metrics.columns if col != 'Team']
                
                # Radar chart
                fig = go.Figure(data=go.Scatterpolar(
                    r=[team_metrics[m] for m in metrics],
                    theta=metrics,
                    fill='toself'
                ))
                fig.update_layout(title=f"{selected_team} Offensive Profile")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No offensive metrics available")
        except Exception as e:
            st.error(f"Error getting offensive metrics: {str(e)}")
    else:
        st.warning(f"Ratings not yet available for {selected_sport}")

with tab3:
    st.subheader("Defensive Ratings Breakdown")
    
    if SPORTS[selected_sport]["ratings"]:
        try:
            # Get defensive metrics from rating system
            def_metrics = SPORTS[selected_sport]["ratings"].get_defensive_metrics()
            
            if def_metrics:
                # Team selection for detailed analysis
                selected_team_def = st.selectbox("Select Team", def_metrics['Team'].unique(), key='def_team')
                team_metrics_def = def_metrics[def_metrics['Team'] == selected_team_def].iloc[0]
                
                # Get metric names excluding 'Team'
                metrics = [col for col in def_metrics.columns if col != 'Team']
                
                # Radar chart
                fig = go.Figure(data=go.Scatterpolar(
                    r=[team_metrics_def[m] for m in metrics],
                    theta=metrics,
                    fill='toself'
                ))
                fig.update_layout(title=f"{selected_team_def} Defensive Profile")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No defensive metrics available")
        except Exception as e:
            st.error(f"Error getting defensive metrics: {str(e)}")
    else:
        st.warning(f"Ratings not yet available for {selected_sport}")

with tab4:
    st.subheader("Matchup Predictor")
    
    if SPORTS[selected_sport]["ratings"]:
        try:
            # Get all teams
            teams = SPORTS[selected_sport]["ratings"].get_teams()
            
            if teams:
                # Team selection
                col1, col2 = st.columns(2)
                with col1:
                    team1 = st.selectbox("Home Team", teams)
                with col2:
                    team2 = st.selectbox("Away Team", teams)
                
                if st.button("Analyze Matchup"):
                    # Get prediction from rating system
                    prediction = SPORTS[selected_sport]["ratings"].predict_matchup(
                        home_team=team1,
                        away_team=team2
                    )
                    
                    if prediction:
                        # Predicted score
                        st.markdown("### Predicted Score")
                        score_col1, score_col2 = st.columns(2)
                        with score_col1:
                            st.metric(team1, prediction['home_score'], prediction['home_trend'])
                        with score_col2:
                            st.metric(team2, prediction['away_score'], prediction['away_trend'])
                        
                        # Win probability gauge
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=prediction['home_win_prob'] * 100,
                            title={'text': f"{team1} Win Probability"},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 100], 'color': "gray"}
                                ]
                            }
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Key matchup factors
                        st.markdown("### Key Matchup Factors")
                        for factor in prediction['factors']:
                            st.markdown(
                                f"**{factor['name']}**: Advantage {factor['advantage']} "
                                f"({factor['strength']:.0%} confidence)"
                            )
            else:
                st.warning("No teams available for matchup prediction")
        except Exception as e:
            st.error(f"Error analyzing matchup: {str(e)}")
    else:
        st.warning(f"Ratings not yet available for {selected_sport}")

# Footer with methodology explanation
with st.expander("Rating Methodology"):
    if SPORTS[selected_sport]["ratings"]:
        try:
            methodology = SPORTS[selected_sport]["ratings"].get_methodology_description()
            st.markdown(methodology)
        except Exception as e:
            st.error(f"Error getting methodology: {str(e)}")
    else:
        st.markdown("""
        ### Rating System Methodology
        
        Our power ratings are calculated using a combination of:
        1. **Massey Ratings**: Based on point differentials and strength of schedule
        2. **Advanced Analytics**: Incorporating offensive and defensive efficiency metrics
        3. **Recent Form**: Weighted more heavily towards recent performance
        4. **Home/Away Splits**: Accounting for home court/field advantage
        5. **Injury Adjustments**: Ratings are adjusted based on player availability
        
        The system is updated daily and includes adjustments for:
        - Strength of schedule
        - Margin of victory
        - Game location
        - Rest days
        - Travel distance
        """)

# Footer
st.markdown("---")
st.caption("Ratings update daily after games complete. Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")) 