from __future__ import annotations

from typing import Dict
import pandas as pd


LITERS_PER_BEER = 0.33
LITERS_PER_GALLON = 3.78541


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _add_volume_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["total_liters"] = df["beer_count"] * LITERS_PER_BEER
    df["total_gallons"] = df["total_liters"] / LITERS_PER_GALLON
    return df


def filter_last_n_days(events: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    Return events from the last N days based on timestamp_utc.
    Safe for pandas >= 2.0.
    """
    if events.empty or "timestamp_utc" not in events.columns:
        return events.iloc[0:0]

    df = events.copy()
    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"], utc=True, errors="coerce"
    )
    df = df.dropna(subset=["timestamp_utc"])

    cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
    return df[df["timestamp_utc"] >= cutoff]


# ---------------------------------------------------------------------
# Time series
# ---------------------------------------------------------------------

def daily_beer_counts(events: pd.DataFrame, days: int = 365) -> pd.DataFrame:
    df = filter_last_n_days(events, days=days)
    if df.empty:
        return pd.DataFrame(columns=["date", "beer_count"])

    df = df.copy()
    df["date"] = df["timestamp_utc"].dt.normalize()

    return (
        df.groupby("date", as_index=False)["beer_count"]
        .sum()
        .sort_values("date")
    )


# ---------------------------------------------------------------------
# Leaderboards
# ---------------------------------------------------------------------

def user_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty or "user_name" not in events.columns:
        return pd.DataFrame(columns=["user_name", "total_beers", "total_gallons"])

    df = (
        events.groupby("user_name", as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
        .reset_index(drop=True)
    )

    df = _add_volume_columns(df.rename(columns={"total_beers": "beer_count"}))
    df = df.rename(columns={"beer_count": "total_beers"})

    return df[["user_name", "total_beers", "total_gallons"]]


def city_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(
            columns=["city", "state", "country", "total_beers", "total_gallons"]
        )

    required = {"city", "country", "beer_count"}
    if not required.issubset(events.columns):
        return pd.DataFrame(
            columns=["city", "state", "country", "total_beers", "total_gallons"]
        )

    df = events.dropna(subset=["city", "country"]).copy()
    df["state"] = df["state"].fillna("")

    out = (
        df.groupby(["city", "state", "country"], as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
        .reset_index(drop=True)
    )

    out = _add_volume_columns(out.rename(columns={"total_beers": "beer_count"}))
    out = out.rename(columns={"beer_count": "total_beers"})

    return out[["city", "state", "country", "total_beers", "total_gallons"]]


def beer_type_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty or "beer_type" not in events.columns:
        return pd.DataFrame(columns=["beer_type", "total_beers", "total_gallons"])

    df = events.dropna(subset=["beer_type"]).copy()

    out = (
        df.groupby("beer_type", as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
        .reset_index(drop=True)
    )

    out = _add_volume_columns(out.rename(columns={"total_beers": "beer_count"}))
    out = out.rename(columns={"beer_count": "total_beers"})

    return out[["beer_type", "total_beers", "total_gallons"]]


def bar_leaderboard(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty or "bar_name" not in events.columns:
        return pd.DataFrame(columns=["bar_name", "total_beers", "total_gallons"])

    df = events.dropna(subset=["bar_name"]).copy()

    out = (
        df.groupby("bar_name", as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
        .reset_index(drop=True)
    )

    out = _add_volume_columns(out.rename(columns={"total_beers": "beer_count"}))
    out = out.rename(columns={"beer_count": "total_beers"})

    return out[["bar_name", "total_beers", "total_gallons"]]


# ---------------------------------------------------------------------
# Fun / derived stats
# ---------------------------------------------------------------------

def fun_benchmarks(events: pd.DataFrame) -> Dict[str, float]:
    total_beers = int(events["beer_count"].sum()) if not events.empty else 0

    calories = total_beers * 150
    pounds = calories / 3500 if calories else 0
    horses = pounds / 1000 if pounds else 0
    labradoodles = pounds / 65 if pounds else 0
    spent = total_beers * 8

    return {
        "total_beers": total_beers,
        "total_calories": int(calories),
        "total_pounds": round(pounds, 2),
        "horses_equivalent": round(horses, 3),
        "labradoodles_equivalent": round(labradoodles, 2),
        "total_spent_usd": int(spent),
    }


def dominance_stats(events: pd.DataFrame) -> Dict[str, float]:
    if events.empty or "user_name" not in events.columns:
        return {"top_1_pct": 0.0, "top_3_pct": 0.0, "everyone_else_pct": 0.0}

    totals = (
        events.groupby("user_name")["beer_count"]
        .sum()
        .sort_values(ascending=False)
    )

    total = totals.sum()
    if total <= 0:
        return {"top_1_pct": 0.0, "top_3_pct": 0.0, "everyone_else_pct": 0.0}

    top1 = totals.iloc[:1].sum()
    top3 = totals.iloc[:3].sum()

    return {
        "top_1_pct": round(top1 / total * 100, 2),
        "top_3_pct": round(top3 / total * 100, 2),
        "everyone_else_pct": round((total - top3) / total * 100, 2),
    }


def bender_stats(events: pd.DataFrame, threshold: int = 7) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(
            columns=["timestamp_utc", "user_name", "beer_count", "city", "state", "country"]
        )

    df = events.copy()
    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"], utc=True, errors="coerce"
    )
    df = df.dropna(subset=["timestamp_utc"])

    out = df[df["beer_count"] >= threshold].copy()
    return out.sort_values("timestamp_utc", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------
# City heatmap
# ---------------------------------------------------------------------

def city_heatmap_points(events: pd.DataFrame) -> pd.DataFrame:
    """
    Returns latitude / longitude points for Folium heatmap.
    """
    if events.empty:
        return pd.DataFrame(columns=["latitude", "longitude", "total_beers"])

    required = {"latitude", "longitude", "beer_count"}
    if not required.issubset(events.columns):
        return pd.DataFrame(columns=["latitude", "longitude", "total_beers"])

    df = events.dropna(subset=["latitude", "longitude"]).copy()

    return (
        df.groupby(["latitude", "longitude"], as_index=False)["beer_count"]
        .sum()
        .rename(columns={"beer_count": "total_beers"})
        .sort_values("total_beers", ascending=False)
        .reset_index(drop=True)
    )
