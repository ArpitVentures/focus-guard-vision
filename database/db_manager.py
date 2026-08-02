"""
FocusGuard AI - SQLite Session Telemetry Persistence Engine
"""
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import BASE_DIR
from utils.logger import logger


class DatabaseManager:
    """
    Manages local SQLite database storage for session metrics and historical analytics.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (BASE_DIR / "database" / "focus_guard.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Creates sessions table if it doesn't exist."""
        # noinspection SqlNoDataSourceInspection
        query = """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration_seconds INTEGER NOT NULL,
            avg_focus_score REAL NOT NULL,
            min_focus_score REAL NOT NULL,
            total_blinks INTEGER NOT NULL,
            total_alerts INTEGER NOT NULL,
            primary_distraction TEXT
        );
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query)
                conn.commit()
            logger.info(f"Database initialized successfully at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize SQLite database: {e}")

    def save_session(
        self,
        duration_sec: int,
        avg_score: float,
        min_score: float,
        total_blinks: int,
        total_alerts: int,
        primary_distraction: str = "None"
    ) -> bool:
        """Saves a completed session record to local SQLite storage."""
        # noinspection SqlNoDataSourceInspection
        query = """
        INSERT INTO sessions (
            duration_seconds,
            avg_focus_score,
            min_focus_score,
            total_blinks,
            total_alerts,
            primary_distraction
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query, (
                    duration_sec,
                    round(avg_score, 1),
                    round(min_score, 1),
                    total_blinks,
                    total_alerts,
                    primary_distraction
                ))
                conn.commit()
            logger.info("Session telemetry saved to local SQLite database.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save session record: {e}")
            return False

    def get_historical_summary(self) -> Dict[str, Any]:
        """Fetches historical session stats for the summary dashboard."""
        # noinspection SqlNoDataSourceInspection
        query = """
        SELECT 
            COUNT(id) as total_sessions,
            COALESCE(AVG(avg_focus_score), 0.0) as overall_avg_score,
            COALESCE(SUM(duration_seconds), 0) as total_time_sec,
            COALESCE(SUM(total_alerts), 0) as total_all_alerts
        FROM sessions;
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    return {
                        "total_sessions": int(row["total_sessions"]),
                        "overall_avg_score": float(row["overall_avg_score"]),
                        "total_time_sec": int(row["total_time_sec"]),
                        "total_all_alerts": int(row["total_all_alerts"])
                    }
                return {"total_sessions": 0, "overall_avg_score": 0.0, "total_time_sec": 0, "total_all_alerts": 0}
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch historical summary: {e}")
            return {"total_sessions": 0, "overall_avg_score": 0.0, "total_time_sec": 0, "total_all_alerts": 0}
