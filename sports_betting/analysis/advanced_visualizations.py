import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

class AdvancedVisualizations:
    def create_betting_dashboard(self, data):
        """Create interactive betting dashboard"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'ATS Performance', 'Line Movement',
                'Score Distribution', 'Value Opportunities',
                'Trend Analysis', 'ROI Analysis'
            )
        )

        # ATS Performance
        fig.add_trace(
            go.Bar(x=data['teams'], y=data['ats_record']),
            row=1, col=1
        )

        # Line Movement
        fig.add_trace(
            go.Scatter(x=data['time'], y=data['line_movement']),
            row=1, col=2
        )

        # Score Distribution
        fig.add_trace(
            go.Histogram(x=data['scores']),
            row=2, col=1
        )

        # Value Opportunities
        fig.add_trace(
            go.Scatter(x=data['predicted'], y=data['actual'],
                      mode='markers'),
            row=2, col=2
        )

        fig.update_layout(height=1000, showlegend=False)
        return fig

    def create_trend_analysis(self, data):
        """Create trend analysis visualizations"""
        fig = plt.figure(figsize=(15, 10))
        
        # Trend subplot 1: Moving Averages
        ax1 = plt.subplot(221)
        sns.lineplot(data=data['moving_avgs'], ax=ax1)
        
        # Trend subplot 2: Win Rate by Situation
        ax2 = plt.subplot(222)
        sns.barplot(data=data['situation_wins'], ax=ax2)
        
        # Trend subplot 3: ROI Heatmap
        ax3 = plt.subplot(223)
        sns.heatmap(data['roi_matrix'], ax=ax3)
        
        # Trend subplot 4: Performance Distribution
        ax4 = plt.subplot(224)
        sns.kdeplot(data=data['performance_dist'], ax=ax4)
        
        plt.tight_layout()
        return fig

    def create_metric_comparison(self, data):
        """Create interactive metric comparison plots"""
        fig = go.Figure()
        
        # Add scatter plot with size based on confidence
        fig.add_trace(go.Scatter(
            x=data['predicted_value'],
            y=data['actual_value'],
            mode='markers',
            marker=dict(
                size=data['confidence']*20,
                color=data['roi'],
                colorscale='RdYlGn',
                showscale=True
            ),
            text=data['description'],
            hoverinfo='text'
        ))
        
        fig.update_layout(
            title='Betting Value Analysis',
            xaxis_title='Predicted Value',
            yaxis_title='Actual Value'
        )
        
        return fig
