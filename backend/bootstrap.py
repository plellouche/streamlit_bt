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

    Backwards compatible:
    - If CSV does not contain 'country', defaults to 'United States'
    """
    if os.path.exists(DB_PATH):
        return

    if not os.path.exists(CSV_PATH):
        return

    store = SQLiteStore()

    df = pd.read_csv(CSV_PATH)

    if "country" not in df.columns:
        df["country"] = "United States"

    for _, row in df.iterrows():
        timestamp = pd.to_datetime(row["timestamp_utc"], utc=True, errors="coerce")
        if pd.isna(timestamp):
            continue

        event = DrinkEvent(
            event_id=str(row["event_id"]),
            timestamp_utc=timestamp.to_pydatetime(),
            user_name=str(row["user_name"]),
            beer_count=int(row["beer_count"]),
            beer_type=(row["beer_type"] if "beer_type" in df.columns and pd.notna(row["beer_type"]) else None),
            bar_name=(row["bar_name"] if "bar_name" in df.columns and pd.notna(row["bar_name"]) else None),
            city=(row["city"] if "city" in df.columns and pd.notna(row["city"]) else None),
            state=(row["state"] if "state" in df.columns and pd.notna(row["state"]) else None),
            country=(row["country"] if pd.notna(row["country"]) else "United States"),
            latitude=(float(row["latitude"]) if "latitude" in df.columns and pd.notna(row["latitude"]) else None),
            longitude=(float(row["longitude"]) if "longitude" in df.columns and pd.notna(row["longitude"]) else None),
        )

        store.insert_event(event)
