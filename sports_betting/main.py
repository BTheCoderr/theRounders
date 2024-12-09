from typing import Dict, List
import asyncio
from loguru import logger
import streamlit as st
from datetime import datetime

# Import all our components
from sports_betting.analysis.advanced_betting_patterns import AdvancedBettingPatterns
from sports_betting.analysis.advanced_ml_execution import AdvancedMLExecution
from sports_betting.analysis.advanced_monitoring import AdvancedMonitoringSystem
from sports_betting.analysis.sophisticated_execution import SophisticatedExecutionSystem
from sports_betting.analysis.sharp_betting_analytics import SharpBettingAnalytics

class SportsBettingDashboard:
    def __init__(self):
        self.systems = {
            'betting_patterns': AdvancedBettingPatterns(),
            'ml_execution': AdvancedMLExecution(),
            'monitoring': AdvancedMonitoringSystem(),
            'execution': SophisticatedExecutionSystem(),
            'sharp_analytics': SharpBettingAnalytics()
        }
        
    def run_dashboard(self):
        st.title("Sports Betting Analytics Dashboard")
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Select System",
            ["Betting Patterns", "ML Execution", "Monitoring", "Sharp Analytics", "Settings"]
        )
        
        if page == "Betting Patterns":
            self.show_betting_patterns()
        elif page == "ML Execution":
            self.show_ml_execution()
        elif page == "Monitoring":
            self.show_monitoring()
        elif page == "Sharp Analytics":
            self.show_sharp_analytics()
        elif page == "Settings":
            self.show_settings()

    def show_betting_patterns(self):
        st.header("Betting Patterns Analysis")
        
        # Pattern detection options
        st.subheader("Pattern Detection")
        pattern_types = st.multiselect(
            "Select Pattern Types",
            ["Steam Moves", "Sharp Money", "Line Movements", "Public Betting"]
        )
        
        if st.button("Analyze Patterns"):
            patterns = asyncio.run(self.systems['betting_patterns'].analyze_patterns({
                'types': pattern_types,
                'timestamp': datetime.now()
            }))
            
            # Display results
            self.display_pattern_results(patterns)

    def show_ml_execution(self):
        st.header("ML-Based Execution")
        
        # Order input
        st.subheader("New Order")
        asset = st.text_input("Asset (e.g., NFL_SPREAD)")
        size = st.number_input("Size", min_value=1)
        side = st.selectbox("Side", ["BUY", "SELL"])
        order_type = st.selectbox("Type", ["MARKET", "LIMIT"])
        
        if st.button("Execute Order"):
            order = {
                'asset': asset,
                'size': size,
                'side': side,
                'type': order_type,
                'timestamp': datetime.now()
            }
            
            result = asyncio.run(self.systems['ml_execution'].execute_with_ml([order]))
            self.display_execution_results(result)

    def show_monitoring(self):
        st.header("Real-Time Monitoring")
        
        # Monitoring options
        metrics = st.multiselect(
            "Select Metrics to Monitor",
            ["Execution Quality", "Risk Metrics", "Market Impact", "Performance"]
        )
        
        if st.button("Start Monitoring"):
            monitoring_data = asyncio.Queue()
            asyncio.run(self.systems['monitoring'].monitor(monitoring_data))
            
    def show_sharp_analytics(self):
        st.header("Sharp Betting Analytics")
        
        # Analytics options
        st.subheader("Analysis Options")
        lookback = st.slider("Lookback Period (days)", 1, 30, 7)
        min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.7)
        
        if st.button("Run Analysis"):
            analysis = self.systems['sharp_analytics'].analyze({
                'lookback': lookback,
                'min_confidence': min_confidence
            })
            
            self.display_sharp_analysis(analysis)

    def show_settings(self):
        st.header("System Settings")
        
        # Alert settings
        st.subheader("Alert Settings")
        alert_types = st.multiselect(
            "Enable Alerts",
            ["Email", "Telegram", "SMS", "Dashboard"]
        )
        
        # Risk thresholds
        st.subheader("Risk Thresholds")
        max_risk = st.slider("Maximum Risk Level", 0.0, 1.0, 0.5)
        
        if st.button("Save Settings"):
            self.save_settings({
                'alerts': alert_types,
                'max_risk': max_risk
            })

    def display_pattern_results(self, patterns: Dict):
        st.subheader("Pattern Analysis Results")
        
        for pattern_type, results in patterns.items():
            st.write(f"\n{pattern_type} Patterns:")
            st.write(f"Confidence: {results['confidence']:.2%}")
            st.write(f"Impact: {results['impact']:.4f}")

    def display_execution_results(self, results: Dict):
        st.subheader("Execution Results")
        
        for order_id, result in results['execution_results'].items():
            st.write(f"\nOrder {order_id}:")
            st.write(f"Average Price: {result['avg_price']}")
            st.write(f"Market Impact: {result['impact']:.4f}")
            st.write(f"Quality Score: {result['quality_score']:.2f}")

    def display_sharp_analysis(self, analysis: Dict):
        st.subheader("Sharp Betting Analysis")
        
        st.write("Top Opportunities:")
        for opp in analysis['opportunities']:
            st.write(f"\n{opp['description']}")
            st.write(f"Confidence: {opp['confidence']:.2%}")
            st.write(f"Expected Value: {opp['ev']:.2f}")

    def save_settings(self, settings: Dict):
        st.success("Settings saved successfully!")
        logger.info(f"Updated settings: {settings}")

if __name__ == "__main__":
    dashboard = SportsBettingDashboard()
    dashboard.run_dashboard()
