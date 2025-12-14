import os
import streamlit as st
import pandas as pd
import altair as alt
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

from backend.services import (
    get_all_events,
    export_events_to_csv,
)
from backend.stats import (
    user_leaderboard,
    city_leaderboard,
    bar_leaderboard,
    beer_type_leaderboard,
    fun_benchmarks,
    dominance_stats,
    bender_stats,
    daily_beer_counts,
    city_heatmap_points,
)

st.title("Stats & Leaderboards")

# ---- Load data ----

events = get_all_events()

if events.empty:
    st.info("No beers logged yet. Fix that.")
    st.stop()

# ---- Calendar Heatmap (Last 365 Days) ----

st.header("Beer Logging Activity (Last 365 Days)")

daily = daily_beer_counts(events, days=365)

if not daily.empty:
    cal = daily.copy()
    cal["weekday"] = cal["date"].dt.weekday  # Mon=0 .. Sun=6

    iso = cal["date"].dt.isocalendar()
    cal["iso_year"] = iso.year.astype(int)
    cal["iso_week"] = iso.week.astype(int)

    cal["week_index"] = (
        (cal["iso_year"] - cal["iso_year"].min()) * 53 + cal["iso_week"]
    )

    heatmap = (
        alt.Chart(cal)
        .mark_rect()
        .encode(
            x=alt.X(
                "week_index:O",
                title=None,
                axis=alt.Axis(labels=False, ticks=False),
            ),
            y=alt.Y(
                "weekday:O",
                title=None,
                axis=alt.Axis(
                    labels=True,
                    ticks=False,
                    labelExpr="['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][datum.value]",
                ),
            ),
            color=alt.Color(
                "beer_count:Q",
                scale=alt.Scale(scheme="greens"),
                legend=alt.Legend(title="Beers"),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("beer_count:Q", title="Beers"),
            ],
        )
        .properties(height=160)
    )

    st.altair_chart(heatmap, use_container_width=True)
else:
    st.info("No activity in the last year.")

st.divider()

# ---- City Folium Heatmap ----

st.header("Beer Consumption Heatmap (by City)")

@st.cache_data(show_spinner=True)
def load_city_heatmap(events_df: pd.DataFrame) -> pd.DataFrame:
    return city_heatmap_points(events_df)

city_points = load_city_heatmap(events)

if city_points.empty:
    st.info("Not enough location data to render heatmap.")
else:
    center_lat = city_points["latitude"].mean()
    center_lon = city_points["longitude"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=4)

    heat_data = city_points[
        ["latitude", "longitude", "total_beers"]
    ].values.tolist()

    HeatMap(
        heat_data,
        radius=25,
        blur=15,
        min_opacity=0.3,
    ).add_to(m)

    st_folium(m, width=700, height=500)



st.divider()

# ---- Leaderboards ----

st.header("Leaderboards")

st.subheader("By Person")
st.dataframe(user_leaderboard(events), use_container_width=True)

st.subheader("By City")
st.dataframe(city_leaderboard(events), use_container_width=True)

st.subheader("By Beer Type")
st.dataframe(beer_type_leaderboard(events), use_container_width=True)

st.subheader("By Bar")
bar_lb = bar_leaderboard(events)
if bar_lb.empty:
    st.info("No bars logged yet.")
else:
    st.dataframe(bar_lb, use_container_width=True)

st.divider()

# ---- Fun Stats ----

st.header("Fun Stats")

benchmarks = fun_benchmarks(events)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Beers", benchmarks["total_beers"])
with col2:
    st.metric("Calories", benchmarks["total_calories"])
with col3:
    st.metric("Total Weight (lbs)", benchmarks["total_pounds"])
with col4:
    st.metric("Horse Equivalents", benchmarks["horses_equivalent"])
with col5:
    st.metric("Labradoodle Equivalents", benchmarks["labradoodles_equivalent"])
with col6:
    st.metric("Total Spent ($)", benchmarks["total_spent_usd"])

st.divider()

# ---- Dominance ----

st.header("Dominance")

dom = dominance_stats(events)

d1, d2, d3 = st.columns(3)

with d1:
    st.metric("Top 1 (%)", dom["top_1_pct"])
with d2:
    st.metric("Top 3 (%)", dom["top_3_pct"])
with d3:
    st.metric("Everyone Else (%)", dom["everyone_else_pct"])

st.divider()

# ---- Bender Detection ----

st.header("Bender Detection (7+ beers in one log)")

benders = bender_stats(events, threshold=7)

if benders.empty:
    st.info("No benders logged yet. Hard to believe.")
else:
    st.dataframe(benders, use_container_width=True)

st.divider()

# ---- CSV Export ----

st.subheader("Secondary cache - disregard")

CSV_PATH = "data/beer_events.csv"

if st.button("Backup"):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    export_events_to_csv(CSV_PATH)
    st.success(f"Exported data to {CSV_PATH}")
