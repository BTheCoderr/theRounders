import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="betting.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create bets table
        c.execute('''
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                sport TEXT,
                game TEXT,
                bet_type TEXT,
                pick TEXT,
                odds REAL,
                stake REAL,
                confidence INTEGER,
                notes TEXT,
                status TEXT,
                result TEXT,
                profit_loss REAL,
                closing_line REAL,
                steam_move BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create line_movements table
        c.execute('''
            CREATE TABLE IF NOT EXISTS line_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bet_id INTEGER,
                timestamp TIMESTAMP,
                odds REAL,
                book TEXT,
                FOREIGN KEY (bet_id) REFERENCES bets (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_bet(self, bet_data):
        """Add a new bet to the database."""
        conn = sqlite3.connect(self.db_path)
        
        # Convert dict to DataFrame for easier handling
        df = pd.DataFrame([bet_data])
        df.to_sql('bets', conn, if_exists='append', index=False)
        
        conn.close()
        return True
    
    def get_bets(self, filters=None):
        """Get all bets with optional filters."""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM bets"
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = '{value}'")
            query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def update_bet(self, bet_id, update_data):
        """Update an existing bet."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [bet_id]
        
        c.execute(f"UPDATE bets SET {set_clause} WHERE id = ?", values)
        
        conn.commit()
        conn.close()
        return True
    
    def add_line_movement(self, bet_id, odds, book):
        """Record a line movement for a bet."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO line_movements (bet_id, timestamp, odds, book)
            VALUES (?, ?, ?, ?)
        ''', (bet_id, datetime.now(), odds, book))
        
        conn.commit()
        conn.close()
        return True
    
    def get_analytics(self):
        """Get comprehensive betting analytics."""
        conn = sqlite3.connect(self.db_path)
        
        # Get all completed bets
        df = pd.read_sql_query(
            "SELECT * FROM bets WHERE result IS NOT NULL",
            conn
        )
        
        if df.empty:
            conn.close()
            return {"error": "No completed bets found"}
        
        # Calculate overall metrics
        total_bets = len(df)
        wins = len(df[df['result'] == 'Won'])
        win_rate = wins / total_bets
        total_profit = df['profit_loss'].sum()
        total_wagered = df['stake'].sum()
        roi = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0
        
        # Performance by sport
        sport_performance = df.groupby('sport').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum',
            'stake': 'sum'
        }).reset_index()
        sport_performance['roi'] = (sport_performance['profit_loss'] / sport_performance['stake']) * 100
        
        # Performance by bet type
        type_performance = df.groupby('bet_type').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum',
            'stake': 'sum'
        }).reset_index()
        type_performance['roi'] = (type_performance['profit_loss'] / type_performance['stake']) * 100
        
        # Trends over time
        time_performance = df.sort_values('date').set_index('date')
        time_performance['cumulative_pl'] = time_performance['profit_loss'].cumsum()
        time_performance['cumulative_roi'] = (
            time_performance['cumulative_pl'] / 
            time_performance['stake'].cumsum()
        ) * 100
        
        # Steam move analysis
        steam_performance = df.groupby('steam_move').agg({
            'id': 'count',
            'result': lambda x: (x == 'Won').mean(),
            'profit_loss': 'sum'
        }).reset_index()
        
        # Closing line value analysis
        df['clv'] = df.apply(
            lambda x: x['closing_line'] - x['odds'] if x['result'] == 'Won'
            else x['odds'] - x['closing_line'],
            axis=1
        )
        
        analytics = {
            'overall': {
                'total_bets': total_bets,
                'win_rate': win_rate,
                'profit_loss': total_profit,
                'roi': roi
            },
            'by_sport': sport_performance.to_dict('records'),
            'by_type': type_performance.to_dict('records'),
            'trends': {
                'dates': time_performance.index.tolist(),
                'cumulative_pl': time_performance['cumulative_pl'].tolist(),
                'cumulative_roi': time_performance['cumulative_roi'].tolist()
            },
            'steam_moves': steam_performance.to_dict('records'),
            'clv_analysis': {
                'average_clv': df['clv'].mean(),
                'clv_correlation': df['clv'].corr(df['profit_loss'])
            }
        }
        
        conn.close()
        return analytics
    
    def calculate_kelly_criterion(self, odds, win_probability):
        """Calculate Kelly Criterion bet size."""
        if odds <= 0:  # Convert American odds to decimal
            decimal_odds = 1 - (100 / odds)
        else:
            decimal_odds = (odds / 100) + 1
        
        q = 1 - win_probability
        b = decimal_odds - 1
        
        kelly = (b * win_probability - q) / b
        return max(0, kelly)  # Kelly can't be negative for betting purposes 