from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd
from geopy.geocoders import Nominatim
import time

LITERS_PER_BEER = 0.33
LITERS_PER_GALLON = 3.78541


def filter_last_n_days(events: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    Filters events to only those with timestamp_utc >= (now - days).
    Assumes timestamp_utc is stored as ISO string in UTC.
    """
    if events.empty:
        return events

    df = events.copy()
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], errors="coerce", utc=True)
    cutoff = pd.Timestamp(datetime.utcnow(), tz="UTC") - pd.Timedelta(days=days)
    return df[df["timestamp_utc"] >= cutoff]


def daily_beer_counts(events: pd.DataFrame, days: int = 365) -> pd.DataFrame:
    """
    Returns daily totals for the last `days` days.
    Output columns: date (datetime64[ns]), beer_count (int).
    """
    if events.empty:
        return pd.DataFrame(columns=["date", "beer_count"])

    df = events.copy()
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], errors="coerce", utc=True)
    df = df.dropna(subset=["timestamp_utc"])

    cutoff = pd.Timestamp(datetime.utcnow(), tz="UTC") - pd.Timedelta(days=days)

    df = df[df["timestamp_utc"] >= cutoff]
    if df.empty:
        return pd.DataFrame(columns=["date", "beer_count"])

    df["date"] = df["timestamp_utc"].dt.floor("D")

    daily = (
        df.groupby("date", as_index=False)["beer_count"]
        .sum()
        .sort_values("date", ascending=True)
    )
    return daily


def _add_volume_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expects df to have column total_beers.
    Adds total_gallons.
    """
    out = df.copy()
    out["total_gallons"] = (
        out["total_beers"] * LITERS_PER_BEER / LITERS_PER_GALLON
    ).round(2)
    return out


def user_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["user_name", "total_beers", "total_gallons"])

    df = (
        events.groupby("user_name", as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
    )
    return _add_volume_column(df)


def city_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    df0 = events.dropna(subset=["city", "state"])
    if df0.empty:
        return pd.DataFrame(columns=["city", "state", "total_beers", "total_gallons"])

    df = (
        df0.groupby(["city", "state"], as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
    )
    return _add_volume_column(df)


def beer_type_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    df0 = events.dropna(subset=["beer_type"])
    if df0.empty:
        return pd.DataFrame(columns=["beer_type", "total_beers", "total_gallons"])

    df = (
        df0.groupby("beer_type", as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
    )
    return _add_volume_column(df)


def bar_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    df0 = events.dropna(subset=["bar_name", "city", "state"])
    if df0.empty:
        return pd.DataFrame(
            columns=["bar_name", "city", "state", "total_beers", "total_gallons"]
        )

    df = (
        df0.groupby(["bar_name", "city", "state"], as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
    )
    return _add_volume_column(df)


def dominance_stats(events: pd.DataFrame) -> dict:
    """
    Dominance tiers based on total beers (not gallons).
    Returns percentages for top 1, top 3, and everyone else.
    """
    lb = user_leaderboard(events)
    total_beers = float(lb["total_beers"].sum()) if not lb.empty else 0.0

    if total_beers <= 0:
        return {"top_1_pct": 0.0, "top_3_pct": 0.0, "everyone_else_pct": 0.0}

    top_1 = float(lb.head(1)["total_beers"].sum())
    top_3 = float(lb.head(3)["total_beers"].sum())

    return {
        "top_1_pct": round(100.0 * top_1 / total_beers, 1),
        "top_3_pct": round(100.0 * top_3 / total_beers, 1),
        "everyone_else_pct": round(100.0 * (total_beers - top_3) / total_beers, 1),
    }


def bender_stats(events: pd.DataFrame, threshold: int = 7) -> pd.DataFrame:
    """
    Counts number of log events per user where beer_count >= threshold.
    """
    if events.empty:
        return pd.DataFrame(columns=["user_name", "benders"])

    benders = events[events["beer_count"] >= threshold]
    if benders.empty:
        return pd.DataFrame(columns=["user_name", "benders"])

    return (
        benders.groupby("user_name", as_index=False)
        .size()
        .rename(columns={"size": "benders"})
        .sort_values("benders", ascending=False)
    )


def fun_benchmarks(events: pd.DataFrame) -> dict:
    total_beers = int(events["beer_count"].sum()) if not events.empty else 0

    # Explicit assumptions
    ounces_per_beer = 12
    pounds_per_ounce = 1 / 16
    calories_per_beer = 100
    dollars_per_beer = 6

    horse_weight_lb = 1000
    labradoodle_weight_lb = 60

    total_ounces = total_beers * ounces_per_beer
    total_pounds = total_ounces * pounds_per_ounce

    return {
        "total_beers": total_beers,
        "total_pounds": round(total_pounds, 1),
        "total_calories": total_beers * calories_per_beer,
        "horses_equivalent": round(total_pounds / horse_weight_lb, 2)
        if horse_weight_lb > 0
        else 0.0,
        "labradoodles_equivalent": round(total_pounds / labradoodle_weight_lb, 1)
        if labradoodle_weight_lb > 0
        else 0.0,
        "total_spent_usd": total_beers * dollars_per_beer,
    }


def city_heatmap_points(events: pd.DataFrame) -> pd.DataFrame:
    """
    Returns DataFrame with columns:
    city, state, total_beers, latitude, longitude

    Geocodes city/state using Nominatim.
    """
    if events.empty:
        return pd.DataFrame(
            columns=["city", "state", "total_beers", "latitude", "longitude"]
        )

    cities = (
        events.dropna(subset=["city", "state"])
        .groupby(["city", "state"], as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
    )

    geolocator = Nominatim(user_agent="beer-tracker")
    lats = []
    lons = []

    for _, row in cities.iterrows():
        query = f"{row['city']}, {row['state']}"
        try:
            location = geolocator.geocode(query, timeout=10)
            if location:
                lats.append(location.latitude)
                lons.append(location.longitude)
            else:
                lats.append(None)
                lons.append(None)
        except Exception:
            lats.append(None)
            lons.append(None)

        time.sleep(1)

    cities["latitude"] = lats
    cities["longitude"] = lons

    return cities.dropna(subset=["latitude", "longitude"])