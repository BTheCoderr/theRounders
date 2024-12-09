from typing import Dict, List, Optional
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass

@dataclass
class BettingPattern:
    pattern_type: str
    confidence: float
    impact: float
    books_involved: List[str]
    timestamp: datetime

class AdvancedBettingPatterns:
    def __init__(self):
        self.steam_analyzer = AdvancedSteamAnalyzer()
        self.sharp_reversal = SharpReversalDetector()
        self.book_patterns = BookPatternAnalyzer()
        self.ml_patterns = MLPatternRecognition()
        self.alerts = RealTimeAlerts()
        
    async def analyze_patterns(self, prop: Dict) -> Dict:
        """Analyze all betting patterns"""
        patterns = {
            'steam': await self.steam_analyzer.analyze(prop),
            'reversals': await self.sharp_reversal.detect(prop),
            'book_patterns': await self.book_patterns.analyze(prop),
            'ml_patterns': await self.ml_patterns.detect_patterns(prop)
        }
        
        # Set up real-time monitoring
        await self.alerts.monitor_patterns(patterns)
        
        return patterns

class AdvancedSteamAnalyzer:
    def __init__(self):
        self.steam_types = {
            'regular': self._detect_regular_steam,
            'reverse': self._detect_reverse_steam
        }
        
    async def analyze(self, prop: Dict) -> Dict:
        """Analyze advanced steam patterns"""
        steam_patterns = {}
        
        for pattern_name, detector in self.steam_types.items():
            pattern = await detector(prop)
            if pattern:
                steam_patterns[pattern_name] = pattern
                
        return {
            'patterns': steam_patterns,
            'strength': self._calculate_steam_strength(steam_patterns),
            'recommendations': self._generate_steam_recommendations(steam_patterns)
        }
        
    async def _detect_cascade_steam(self, prop: Dict) -> Optional[BettingPattern]:
        """Detect cascading steam moves across books"""
        try:
            line_moves = await self._get_line_movement_data(prop)
            cascade = self._analyze_cascade_pattern(line_moves)
            
            if cascade['is_cascade']:
                return BettingPattern(
                    pattern_type='cascade',
                    confidence=cascade['confidence'],
                    impact=cascade['impact'],
                    books_involved=cascade['books'],
                    timestamp=datetime.now()
                )
            return None
            
        except Exception as e:
            logger.error(f"Error detecting cascade steam: {str(e)}")
            return None

    def _detect_reverse_steam(self, data=None):
        # Implement reverse steam detection logic
        # For now, returning a placeholder result
        return {
            'detected': False,
            'confidence': 0.0,
            'impact': 0.0
        }

    def _detect_regular_steam(self, data=None):
        # Assuming this method already exists
        pass

class SharpReversalDetector:
    def __init__(self):
        self.min_reversal_size = 20  # Minimum reversal in cents
        self.min_sharp_volume = 10000  # Minimum sharp volume
        
    async def detect(self, prop: Dict) -> Dict:
        """Detect sharp money reversals"""
        try:
            # Get sharp money flow data
            sharp_data = await self._get_sharp_money_flow(prop)
            
            # Detect reversals
            reversals = self._detect_reversals(sharp_data)
            
            # Analyze reversal impact
            impact = self._analyze_reversal_impact(reversals)
            
            return {
                'reversals': reversals,
                'impact': impact,
                'confidence': self._calculate_reversal_confidence(reversals)
            }
            
        except Exception as e:
            logger.error(f"Error detecting reversals: {str(e)}")
            return None

class BookPatternAnalyzer:
    def __init__(self):
        self.book_profiles = self._load_book_profiles()
        self.ml_model = self._load_pattern_model()
        
    def _load_book_profiles(self) -> Dict:
        """Load book profiles with default values"""
        return {
            'default': {
                'sharp_threshold': 0.7,
                'volume_threshold': 10000,
                'line_sensitivity': 0.5
            }
        }
        
    def _load_pattern_model(self):
        """Load the pattern recognition model"""
        return RandomForestClassifier(n_estimators=100)
        
    async def analyze(self, prop: Dict) -> Dict:
        """Analyze book-specific patterns"""
        try:
            # Get book-specific data
            book_data = await self._get_book_data(prop)
            
            # Analyze patterns for each book
            patterns = {}
            for book, data in book_data.items():
                patterns[book] = {
                    'sharp_tendency': self._analyze_sharp_tendency(data),
                    'line_movement_pattern': self._analyze_line_pattern(data),
                    'volume_pattern': self._analyze_volume_pattern(data)
                }
                
            return {
                'book_patterns': patterns,
                'recommendations': self._generate_book_recommendations(patterns)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing book patterns: {str(e)}")
            return None

class MLPatternRecognition:
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100)
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.scaler = StandardScaler()
        
    async def detect_patterns(self, prop: Dict) -> Dict:
        """Detect patterns using ML"""
        try:
            # Prepare features
            features = await self._prepare_features(prop)
            
            # Random Forest prediction
            rf_prediction = self.rf_model.predict_proba(features)
            
            # Anomaly detection
            anomalies = self.anomaly_detector.predict(features)
            
            return {
                'rf_confidence': rf_prediction,
                'anomalies': anomalies,
                'combined_score': self._combine_predictions(
                    rf_prediction, anomalies
                )
            }
            
        except Exception as e:
            logger.error(f"Error in ML pattern detection: {str(e)}")
            return None

class RealTimeAlerts:
    def __init__(self):
        self.alert_thresholds = {
            'steam': 0.8,
            'reversal': 0.7,
            'pattern': 0.75
        }
        self.alert_channels = ['email', 'telegram', 'app']
        
    async def monitor_patterns(self, patterns: Dict):
        """Monitor patterns and send alerts"""
        try:
            while True:
                # Check for significant patterns
                alerts = self._check_alert_conditions(patterns)
                
                if alerts:
                    # Send alerts through all channels
                    await self._send_alerts(alerts)
                    
                # Update patterns
                patterns = await self._update_patterns(patterns)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in pattern monitoring: {str(e)}")
            
    async def _send_alerts(self, alerts: List[Dict]):
        """Send alerts through configured channels"""
        for alert in alerts:
            for channel in self.alert_channels:
                try:
                    await self._send_alert_to_channel(alert, channel)
                except Exception as e:
                    logger.error(f"Error sending alert to {channel}: {str(e)}") 