import os
import pandas as pd

from backend.db import SQLiteStore
from backend.models import DrinkEvent

DB_PATH = "data/beer_tracker.db"
CSV_PATH = "data/beer_events.csv"


def bootstrap_db_from_csv():
    """
    If SQLite DB is missing but CSV backup exists,
    rebuild the DB by replaying events.
    """
    if os.path.exists(DB_PATH):
        return

    if not os.path.exists(CSV_PATH):
        return

    # Instantiate store (this creates DB + tables)
    store = SQLiteStore()

    df = pd.read_csv(CSV_PATH)

    for _, row in df.iterrows():
        event = DrinkEvent(
            event_id=row["event_id"],
            timestamp_utc=pd.to_datetime(row["timestamp_utc"], utc=True),
            user_name=row["user_name"],
            beer_count=int(row["beer_count"]),
            beer_type=row.get("beer_type"),
            bar_name=row.get("bar_name"),
            city=row.get("city"),
            state=row.get("state"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
        )
        store.insert_event(event)
