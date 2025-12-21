import sqlite3
from pathlib import Path
from typing import Optional
import pandas as pd

from backend.models import DrinkEvent


DB_PATH = Path("data/beer_tracker.db")


class SQLiteStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS drink_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp_utc TEXT NOT NULL,
                    user_name TEXT NOT NULL,
                    beer_count INTEGER NOT NULL,
                    beer_type TEXT,
                    bar_name TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    latitude REAL,
                    longitude REAL
                )
                """
            )
            conn.commit()

            try:
                conn.execute("ALTER TABLE drink_events ADD COLUMN country TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                # Column likely already exists.
                pass

            # Backfill: if 'country' is NULL but 'state' exists, treat as US legacy data.
            try:
                conn.execute(
                    """
                    UPDATE drink_events
                    SET country = 'United States'
                    WHERE country IS NULL AND state IS NOT NULL AND TRIM(state) <> ''
                    """
                )
                conn.commit()
            except sqlite3.OperationalError:
                pass

    def insert_event(self, event: DrinkEvent) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO drink_events (
                    event_id,
                    timestamp_utc,
                    user_name,
                    beer_count,
                    beer_type,
                    bar_name,
                    city,
                    state,
                    country,
                    latitude,
                    longitude
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.timestamp_utc.isoformat(),
                    event.user_name,
                    event.beer_count,
                    event.beer_type,
                    event.bar_name,
                    event.city,
                    event.state,
                    event.country,
                    event.latitude,
                    event.longitude,
                ),
            )
            conn.commit()

    def fetch_events(
        self,
        start_timestamp_utc: Optional[str] = None,
        end_timestamp_utc: Optional[str] = None,
    ) -> pd.DataFrame:
        query = "SELECT * FROM drink_events"
        params = []

        conditions = []
        if start_timestamp_utc:
            conditions.append("timestamp_utc >= ?")
            params.append(start_timestamp_utc)
        if end_timestamp_utc:
            conditions.append("timestamp_utc <= ?")
            params.append(end_timestamp_utc)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)

        return df
