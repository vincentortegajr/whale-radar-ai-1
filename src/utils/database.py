"""Database utilities for WhaleRadar.ai"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import json
from src.utils.logger_setup import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


class Database:
    """SQLite database for storing signals and market data"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path
        self._ensure_directory()
        self._init_database()
        
    def _ensure_directory(self):
        """Ensure database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    signal_strength INTEGER NOT NULL,
                    current_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit_1 REAL,
                    take_profit_2 REAL,
                    take_profit_3 REAL,
                    momentum_score INTEGER,
                    liquidation_direction TEXT,
                    rsi_status TEXT,
                    reasons TEXT,
                    scale_zones TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Market data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price_change_pct REAL,
                    volume_change_pct REAL,
                    oi_change_pct REAL,
                    rsi_1h REAL,
                    rsi_4h REAL,
                    rsi_1d REAL,
                    total_long_liquidations REAL,
                    total_short_liquidations REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Alerts sent table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts_sent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id INTEGER,
                    telegram_message_id TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (signal_id) REFERENCES signals(id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_symbol ON market_data(symbol)")
            
            conn.commit()
            
        logger.info(f"Database initialized at {self.db_path}")
        
    def save_signal(self, signal) -> int:
        """Save a trading signal to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert lists to JSON
            reasons_json = json.dumps(signal.reasons)
            scale_zones_json = json.dumps(signal.scale_in_zones)
            
            # Extract take profits
            tp1 = signal.take_profit_targets[0] if len(signal.take_profit_targets) > 0 else None
            tp2 = signal.take_profit_targets[1] if len(signal.take_profit_targets) > 1 else None
            tp3 = signal.take_profit_targets[2] if len(signal.take_profit_targets) > 2 else None
            
            cursor.execute("""
                INSERT INTO signals (
                    symbol, action, confidence, signal_strength,
                    current_price, stop_loss, take_profit_1, take_profit_2, take_profit_3,
                    momentum_score, liquidation_direction, rsi_status,
                    reasons, scale_zones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.symbol, signal.action, signal.confidence, signal.signal_strength,
                signal.current_price, signal.stop_loss, tp1, tp2, tp3,
                signal.momentum_score, signal.liquidation_direction, signal.rsi_status,
                reasons_json, scale_zones_json
            ))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_recent_signals(self, hours: int = 24, symbol: str = None) -> List[Dict]:
        """Get recent signals from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM signals 
                WHERE created_at > datetime('now', '-{} hours')
            """.format(hours)
            
            if symbol:
                query += f" AND symbol = '{symbol}'"
                
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
            
    def cleanup_old_data(self, days: int = 30):
        """Remove data older than specified days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM signals 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days))
            
            cursor.execute("""
                DELETE FROM market_data 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days))
            
            conn.commit()
            
            logger.info(f"Cleaned up data older than {days} days")


# Global database instance
db = Database()