"""API usage monitoring and alerting."""
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import sqlite3
from dataclasses import dataclass
from utils.api_config import APIConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIUsageStats:
    """API usage statistics."""
    api_name: str
    calls_made: int
    calls_remaining: int
    reset_time: datetime
    errors: int

class APIMonitor:
    """Monitor API usage and alert on potential issues."""
    
    def __init__(self, db_path: str = 'data/api_usage.db'):
        self.db_path = Path(db_path)
        self.api_config = APIConfig()
        self._init_db()
    
    def _init_db(self):
        """Initialize the database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    status_code INTEGER,
                    response_time FLOAT,
                    error TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rate_limits (
                    api_name TEXT PRIMARY KEY,
                    calls_made INTEGER,
                    calls_remaining INTEGER,
                    reset_time DATETIME
                )
            ''')
    
    def log_api_call(self, api_name: str, endpoint: str, status_code: int,
                     response_time: float, error: str = None):
        """Log an API call to the database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute('''
                INSERT INTO api_calls (api_name, endpoint, status_code, response_time, error)
                VALUES (?, ?, ?, ?, ?)
            ''', (api_name, endpoint, status_code, response_time, error))
    
    def update_rate_limits(self, api_name: str, calls_made: int,
                          calls_remaining: int, reset_time: datetime):
        """Update rate limit information."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO rate_limits
                (api_name, calls_made, calls_remaining, reset_time)
                VALUES (?, ?, ?, ?)
            ''', (api_name, calls_made, calls_remaining, reset_time))
    
    def get_usage_stats(self, api_name: str = None,
                       time_window: timedelta = timedelta(hours=24)) -> List[APIUsageStats]:
        """Get API usage statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get API calls within time window
            query = '''
                SELECT api_name,
                       COUNT(*) as total_calls,
                       SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as errors
                FROM api_calls
                WHERE timestamp > datetime('now', ?)
            '''
            
            params = [f'-{time_window.total_seconds()} seconds']
            if api_name:
                query += ' AND api_name = ?'
                params.append(api_name)
            
            query += ' GROUP BY api_name'
            
            calls = conn.execute(query, params).fetchall()
            
            # Get current rate limits
            limits = conn.execute('''
                SELECT * FROM rate_limits
                WHERE api_name = ? OR ? IS NULL
            ''', (api_name, api_name)).fetchall()
            
            stats = []
            for call in calls:
                limit = next((l for l in limits if l['api_name'] == call['api_name']), None)
                if limit:
                    stats.append(APIUsageStats(
                        api_name=call['api_name'],
                        calls_made=call['total_calls'],
                        calls_remaining=limit['calls_remaining'],
                        reset_time=datetime.fromisoformat(limit['reset_time']),
                        errors=call['errors']
                    ))
            
            return stats
    
    def check_rate_limit_alerts(self) -> List[str]:
        """Check for rate limit alerts."""
        alerts = []
        stats = self.get_usage_stats()
        
        for stat in stats:
            # Alert if we're close to the limit
            usage_percent = (stat.calls_made / (stat.calls_made + stat.calls_remaining)) * 100
            if usage_percent >= 80:
                alerts.append(
                    f"WARNING: {stat.api_name} API usage at {usage_percent:.1f}% "
                    f"({stat.calls_remaining} calls remaining)"
                )
            
            # Alert if error rate is high
            error_rate = (stat.errors / stat.calls_made) * 100 if stat.calls_made > 0 else 0
            if error_rate >= 10:
                alerts.append(
                    f"WARNING: {stat.api_name} API error rate at {error_rate:.1f}%"
                )
        
        return alerts
    
    def get_endpoint_performance(self, days: int = 7) -> Dict:
        """Get endpoint performance statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            
            return conn.execute('''
                SELECT api_name,
                       endpoint,
                       COUNT(*) as calls,
                       AVG(response_time) as avg_response_time,
                       MIN(response_time) as min_response_time,
                       MAX(response_time) as max_response_time,
                       SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as errors
                FROM api_calls
                WHERE timestamp > datetime('now', '-' || ? || ' days')
                GROUP BY api_name, endpoint
                ORDER BY calls DESC
            ''', (days,)).fetchall()
    
    def export_usage_report(self, output_path: Path):
        """Export API usage report."""
        stats = self.get_usage_stats()
        performance = self.get_endpoint_performance()
        alerts = self.check_rate_limit_alerts()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'usage_stats': [vars(stat) for stat in stats],
            'endpoint_performance': [dict(p) for p in performance],
            'alerts': alerts
        }
        
        output_path.write_text(json.dumps(report, indent=2))
        logger.info(f"API usage report exported to {output_path}")

if __name__ == '__main__':
    # Example usage
    monitor = APIMonitor()
    alerts = monitor.check_rate_limit_alerts()
    for alert in alerts:
        logger.warning(alert)
    
    # Export daily report
    report_path = Path('reports/api_usage_report.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    monitor.export_usage_report(report_path) 