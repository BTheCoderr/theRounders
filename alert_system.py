from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import threading
import queue
import logging
from dataclasses import dataclass

@dataclass
class Alert:
    type: str  # "steam" or "rlm"
    sport: str
    event: str
    market: str
    old_line: float
    new_line: float
    timestamp: datetime
    confidence: float
    details: Dict
    source: str

class AlertSystem:
    def __init__(self, min_steam_threshold: float = 0.02,
                 min_rlm_threshold: float = 0.15,
                 monitoring_window: int = 300):
        self.min_steam_threshold = min_steam_threshold
        self.min_rlm_threshold = min_rlm_threshold
        self.monitoring_window = monitoring_window  # seconds
        
        self.alert_queue = queue.Queue()
        self.line_history = {}
        self.public_money = {}
        self.sharp_money = {}
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Start monitoring thread
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_changes)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def track_line_movement(self, sport: str, event: str, market: str,
                          line: float, timestamp: datetime,
                          book: str) -> None:
        """Track line movement for steam move detection."""
        key = (sport, event, market)
        
        if key not in self.line_history:
            self.line_history[key] = []
        
        self.line_history[key].append({
            "line": line,
            "timestamp": timestamp,
            "book": book
        })
        
        # Clean old history
        cutoff = datetime.now() - timedelta(seconds=self.monitoring_window)
        self.line_history[key] = [
            h for h in self.line_history[key]
            if h["timestamp"] > cutoff
        ]
        
        # Check for steam moves
        self._check_steam_move(key)
    
    def track_betting_percentages(self, sport: str, event: str, market: str,
                                public_pct: float, sharp_pct: float,
                                line: float) -> None:
        """Track betting percentages for RLM detection."""
        key = (sport, event, market)
        
        self.public_money[key] = public_pct
        self.sharp_money[key] = sharp_pct
        
        # Check for RLM
        self._check_rlm(key, line)
    
    def _check_steam_move(self, key: tuple) -> None:
        """Check for steam moves in recent line history."""
        if len(self.line_history[key]) < 2:
            return
        
        history = sorted(self.line_history[key], key=lambda x: x["timestamp"])
        start_line = history[0]["line"]
        end_line = history[-1]["line"]
        
        # Calculate line movement
        movement = abs(end_line - start_line)
        time_span = (history[-1]["timestamp"] - history[0]["timestamp"]).total_seconds()
        
        # Check if movement exceeds threshold within window
        if movement >= self.min_steam_threshold and time_span <= self.monitoring_window:
            # Calculate confidence based on number of books and movement size
            books_involved = len(set(h["book"] for h in history))
            confidence = min(1.0, (movement / self.min_steam_threshold) * (books_involved / 3))
            
            alert = Alert(
                type="steam",
                sport=key[0],
                event=key[1],
                market=key[2],
                old_line=start_line,
                new_line=end_line,
                timestamp=datetime.now(),
                confidence=confidence,
                details={
                    "movement": movement,
                    "time_span": time_span,
                    "books_involved": books_involved,
                    "movement_history": [
                        {"book": h["book"], "line": h["line"], 
                         "timestamp": h["timestamp"].isoformat()}
                        for h in history
                    ]
                },
                source="line_monitoring"
            )
            
            self.alert_queue.put(alert)
            self.logger.info(f"Steam move detected: {movement:.3f} points in {time_span:.1f}s")
    
    def _check_rlm(self, key: tuple, current_line: float) -> None:
        """Check for reverse line movement."""
        if key not in self.public_money or key not in self.sharp_money:
            return
        
        public_pct = self.public_money[key]
        sharp_pct = self.sharp_money[key]
        
        # Get previous line if available
        prev_line = None
        if key in self.line_history and len(self.line_history[key]) > 0:
            prev_line = self.line_history[key][0]["line"]
        
        if prev_line is not None:
            line_movement = current_line - prev_line
            
            # Check if line moved against public money
            is_rlm = (
                (public_pct > 70 and line_movement < 0) or
                (public_pct < 30 and line_movement > 0)
            )
            
            if is_rlm and abs(line_movement) >= self.min_rlm_threshold:
                # Calculate confidence based on public % and sharp %
                public_confidence = abs(public_pct - 50) / 50  # How strong is public lean
                sharp_confidence = sharp_pct / 100  # How much sharp money involved
                confidence = (public_confidence + sharp_confidence) / 2
                
                alert = Alert(
                    type="rlm",
                    sport=key[0],
                    event=key[1],
                    market=key[2],
                    old_line=prev_line,
                    new_line=current_line,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    details={
                        "public_pct": public_pct,
                        "sharp_pct": sharp_pct,
                        "line_movement": line_movement,
                        "public_lean": "heavy" if abs(public_pct - 50) > 30 else "moderate"
                    },
                    source="money_tracking"
                )
                
                self.alert_queue.put(alert)
                self.logger.info(
                    f"RLM detected: {line_movement:.3f} points against {public_pct:.1f}% public"
                )
    
    def _monitor_changes(self) -> None:
        """Background thread to monitor for changes and clean up old data."""
        while self.is_running:
            try:
                # Clean up old line history
                cutoff = datetime.now() - timedelta(seconds=self.monitoring_window)
                for key in list(self.line_history.keys()):
                    self.line_history[key] = [
                        h for h in self.line_history[key]
                        if h["timestamp"] > cutoff
                    ]
                    
                    # Remove empty histories
                    if not self.line_history[key]:
                        del self.line_history[key]
                
                # Sleep for a short interval
                time.sleep(1)
            
            except Exception as e:
                self.logger.error(f"Error in monitor thread: {str(e)}")
    
    def get_alerts(self, max_alerts: Optional[int] = None) -> List[Alert]:
        """Get pending alerts from the queue."""
        alerts = []
        try:
            while True:
                if max_alerts and len(alerts) >= max_alerts:
                    break
                    
                alert = self.alert_queue.get_nowait()
                alerts.append(alert)
                self.alert_queue.task_done()
        
        except queue.Empty:
            pass
        
        return alerts
    
    def stop(self) -> None:
        """Stop the monitoring thread."""
        self.is_running = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
    
    def get_monitoring_stats(self) -> Dict:
        """Get current monitoring statistics."""
        return {
            "tracked_events": len(self.line_history),
            "monitoring_window": self.monitoring_window,
            "steam_threshold": self.min_steam_threshold,
            "rlm_threshold": self.min_rlm_threshold,
            "pending_alerts": self.alert_queue.qsize()
        } 