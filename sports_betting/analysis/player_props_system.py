import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from loguru import logger
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

class PlayerPropsAnalyzer:
    def __init__(self):
        logger.info("Initializing Player Props Analysis System")
        self.models = {
            'passing_yards': None,
            'rushing_yards': None,
            'receiving_yards': None,
            'receptions': None,
            'touchdowns': None,
            'completions': None
        }
        self.player_history = {}
        self.matchup_factors = {}
        
    def analyze_player_prop(self, 
                          player_id: str,
                          prop_type: str,
                          line: float,
                          game_info: Dict) -> Dict:
        """Analyze a specific player prop"""
        try:
            # Get player historical data
            player_data = self._get_player_history(player_id)
            
            # Calculate key metrics
            metrics = {
                'recent_average': self._calculate_recent_average(player_data, prop_type),
                'matchup_factor': self._analyze_matchup(game_info, prop_type),
                'weather_impact': self._analyze_weather_impact(game_info),
                'rest_factor': self._analyze_rest_factor(game_info),
                'usage_trend': self._analyze_usage_trend(player_data),
                'prop_line_value': self._analyze_line_value(line, player_data, prop_type)
            }
            
            # Make prediction
            prediction = self._predict_prop_value(player_data, game_info, prop_type)
            
            # Calculate edge
            edge = self._calculate_edge(prediction, line)
            
            # Generate recommendation
            recommendation = self._generate_prop_recommendation(edge, metrics)
            
            return {
                'prediction': prediction,
                'edge': edge,
                'metrics': metrics,
                'recommendation': recommendation,
                'confidence': self._calculate_confidence(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing player prop: {str(e)}")
            raise
            
    def _analyze_matchup(self, game_info: Dict, prop_type: str) -> float:
        """Analyze matchup-specific factors"""
        opponent_id = game_info['opponent']
        defense_stats = self._get_defense_stats(opponent_id)
        
        factors = {
            'passing_yards': defense_stats['pass_yards_allowed_per_game'],
            'rushing_yards': defense_stats['rush_yards_allowed_per_game'],
            'receiving_yards': defense_stats['pass_yards_allowed_per_game'],
            'receptions': defense_stats['completions_allowed_per_game']
        }
        
        return factors.get(prop_type, 1.0)
        
    def visualize_prop_analysis(self, analysis: Dict) -> go.Figure:
        """Create interactive visualization of prop analysis"""
        fig = go.Figure()
        
        # Historical performance
        fig.add_trace(go.Scatter(
            x=analysis['metrics']['historical_dates'],
            y=analysis['metrics']['historical_values'],
            name='Historical Performance'
        ))
        
        # Prop line
        fig.add_hline(y=analysis['prop_line'], 
                     line_dash="dash", 
                     annotation_text="Prop Line")
        
        # Prediction
        fig.add_hline(y=analysis['prediction'],
                     line_color="green",
                     annotation_text="Prediction")
        
        fig.update_layout(
            title=f"Player Prop Analysis - {analysis['prop_type']}",
            xaxis_title="Date",
            yaxis_title="Value"
        )
        
        return fig
        
    def _calculate_edge(self, prediction: float, line: float) -> float:
        """Calculate betting edge"""
        return ((prediction - line) / line) * 100
        
    def _generate_prop_recommendation(self, edge: float, metrics: Dict) -> Dict:
        """Generate betting recommendation"""
        confidence = self._calculate_confidence(metrics)
        
        if abs(edge) < 5:
            return {
                'recommendation': 'PASS',
                'reason': 'Insufficient edge',
                'confidence': confidence
            }
            
        return {
            'recommendation': 'OVER' if edge > 0 else 'UNDER',
            'edge': edge,
            'confidence': confidence,
            'bet_size': self._calculate_bet_size(edge, confidence)
        }
        
    def _calculate_bet_size(self, edge: float, confidence: float) -> float:
        """Calculate recommended bet size using Kelly Criterion"""
        # Modified Kelly for props
        kelly = (edge * confidence) / 100
        
        # Conservative Kelly (quarter-Kelly)
        return min(kelly * 0.25, 0.05)  # Max 5% of bankroll
        
    def track_prop_result(self, 
                         prop_id: str, 
                         prediction: Dict, 
                         actual_result: float):
        """Track prop betting results"""
        try:
            result = {
                'date': datetime.now(),
                'prop_type': prediction['prop_type'],
                'line': prediction['prop_line'],
                'prediction': prediction['prediction'],
                'actual': actual_result,
                'edge': prediction['edge'],
                'confidence': prediction['confidence'],
                'result': 'WIN' if (
                    (prediction['recommendation'] == 'OVER' and actual_result > prediction['prop_line']) or
                    (prediction['recommendation'] == 'UNDER' and actual_result < prediction['prop_line'])
                ) else 'LOSS'
            }
            
            # Store result
            self._store_result(prop_id, result)
            
            # Update models
            self._update_models(result)
            
            logger.info(f"Tracked result for prop {prop_id}: {result['result']}")
            
        except Exception as e:
            logger.error(f"Error tracking prop result: {str(e)}") 

# Initialize the system
props_analyzer = PlayerPropsAnalyzer()

# Analyze a specific prop
analysis = props_analyzer.analyze_player_prop(
    player_id="PatrickMahomes",
    prop_type="passing_yards",
    line=285.5,
    game_info={
        'opponent': 'LV',
        'weather': {'temp': 72, 'wind': 5},
        'rest_days': 7,
        'home_away': 'home'
    }
)

# Get recommendation
if analysis['recommendation']['recommendation'] != 'PASS':
    print(f"Bet {analysis['recommendation']['bet_size']*100}% of bankroll on "
          f"{analysis['recommendation']['recommendation']}")
    print(f"Edge: {analysis['edge']:.1f}%")
    print(f"Confidence: {analysis['recommendation']['confidence']:.1f}%")

# Visualize analysis
fig = props_analyzer.visualize_prop_analysis(analysis)
fig.show()