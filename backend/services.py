from __future__ import annotations

from typing import Optional, Union, IO
import time

import pandas as pd
from geopy.geocoders import Nominatim
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import os

SUPABASE_DATABASE_URL = os.environ["SUPABASE_DATABASE_URL"]


def get_engine() -> Engine:
    return create_engine(
        SUPABASE_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
        connect_args={
            "sslmode": "require"
        },
        future=True,
    )


def ensure_schema() -> None:
    """
    Create table if it does not exist.
    Safe to call multiple times.
    """
    engine = get_engine()
    ddl = text(
        """
        CREATE TABLE IF NOT EXISTS beer_events (
            event_id BIGSERIAL PRIMARY KEY,
            timestamp_utc TIMESTAMPTZ NOT NULL,
            user_name TEXT NOT NULL,
            beer_count INTEGER NOT NULL,
            beer_type TEXT NULL,
            bar_name TEXT NULL,
            city TEXT NULL,
            state TEXT NULL,
            country TEXT NULL,
            latitude DOUBLE PRECISION NULL,
            longitude DOUBLE PRECISION NULL
        );
        """
    )
    with engine.begin() as conn:
        conn.execute(ddl)


# ---------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------

def get_all_events() -> pd.DataFrame:
    """
    Load all beer events into a DataFrame.
    """
    ensure_schema()
    engine = get_engine()

    query = text(
        """
        SELECT
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
        FROM beer_events
        ORDER BY timestamp_utc ASC
        """
    )

    df = pd.read_sql(query, engine, parse_dates=["timestamp_utc"])
    return df


# ---------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------

def insert_event(
    *,
    timestamp_utc,
    user_name: str,
    beer_count: int,
    beer_type: Optional[str] = None,
    bar_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> None:
    """
    Insert a single event row.
    """
    ensure_schema()
    engine = get_engine()

    query = text(
        """
        INSERT INTO beer_events (
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
        VALUES (
            :timestamp_utc,
            :user_name,
            :beer_count,
            :beer_type,
            :bar_name,
            :city,
            :state,
            :country,
            :latitude,
            :longitude
        )
        """
    )

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "timestamp_utc": timestamp_utc,
                "user_name": user_name,
                "beer_count": int(beer_count),
                "beer_type": beer_type,
                "bar_name": bar_name,
                "city": city,
                "state": state,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
            },
        )


# ---------------------------------------------------------------------
# High-level logging API used by the Streamlit form
# ---------------------------------------------------------------------

_geolocator: Optional[Nominatim] = None


def _get_geolocator() -> Nominatim:
    global _geolocator
    if _geolocator is None:
        _geolocator = Nominatim(user_agent="beer_tracker_streamlit")
    return _geolocator


def _geocode_city(
    *,
    city: str,
    state: Optional[str],
    country: str,
) -> tuple[Optional[float], Optional[float]]:
    """
    Best-effort geocoding. Returns (lat, lon) or (None, None).
    """
    parts = [city]
    if state:
        parts.append(state)
    parts.append(country)
    query = ", ".join([p for p in parts if p])

    geolocator = _get_geolocator()

    # Nominatim usage policy expects you to throttle requests.
    # This app is low stakes, so keep it simple.
    time.sleep(1.0)

    try:
        location = geolocator.geocode(query, exactly_one=True, timeout=10)
    except Exception:
        location = None

    if not location:
        return None, None

    return float(location.latitude), float(location.longitude)


def log_beers(
    *,
    user_name: str,
    beer_count: int,
    beer_type: Optional[str] = None,
    bar_name: Optional[str] = None,
    city: str,
    state: Optional[str],
    country: str,
) -> None:
    """
    Called by the Streamlit logging form.
    Adds timestamp_utc automatically and geocodes (best effort).
    """
    # FIX: Timestamp.utcnow() is already tz-aware in recent pandas.
    ts = pd.Timestamp.now(tz="UTC")

    city_clean = (city or "").strip()
    state_clean = (state or "").strip() or None
    country_clean = (country or "").strip()

    lat, lon = _geocode_city(
        city=city_clean,
        state=state_clean,
        country=country_clean,
    )

    insert_event(
        timestamp_utc=ts,
        user_name=user_name,
        beer_count=int(beer_count),
        beer_type=(beer_type or None),
        bar_name=(bar_name or None),
        city=city_clean or None,
        state=state_clean,
        country=country_clean or None,
        latitude=lat,
        longitude=lon,
    )


# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------

TargetType = Union[str, IO[str], IO[bytes]]


def export_events_to_csv(target: TargetType) -> None:
    """
    Export all events to CSV.

    `target` can be:
      - a file path (str)
      - a file-like object (StringIO / BytesIO)
    """
    df = get_all_events()
    df.to_csv(target, index=False)
