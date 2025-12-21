import streamlit as st
import pandas as pd
import altair as alt

from backend.services import get_all_events
from backend.stats import (
    filter_last_n_days,
    daily_beer_counts,
    user_leaderboard,
    city_leaderboard,
    bar_leaderboard,
    beer_type_leaderboard,
    fun_benchmarks,
    dominance_stats,
    bender_stats,
)

st.title("Stats (Last 30 Days)")

events = get_all_events()
events_30d = filter_last_n_days(events, days=30)

if events_30d.empty:
    st.info("No beers logged in the last 30 days. Hydration arc?")
    st.stop()

st.header("Beer Logging Activity (Last 30 Days)")

daily = daily_beer_counts(events_30d, days=30)

if daily.empty:
    st.info("No activity in the last 30 days.")
else:
    cal = daily.copy()
    cal["weekday"] = cal["date"].dt.weekday

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

st.divider()

st.header("Leaderboards (Last 30 Days)")

st.subheader("By Person")
st.dataframe(user_leaderboard(events_30d), use_container_width=True)

st.subheader("By City")
st.dataframe(city_leaderboard(events_30d), use_container_width=True)

st.subheader("By Beer Type")
st.dataframe(beer_type_leaderboard(events_30d), use_container_width=True)

st.subheader("By Bar")
bar_lb = bar_leaderboard(events_30d)
if bar_lb.empty:
    st.info("No bars logged yet.")
else:
    st.dataframe(bar_lb, use_container_width=True)

st.divider()

st.header("Fun Stats (Last 30 Days)")

benchmarks = fun_benchmarks(events_30d)
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

st.header("Dominance (Last 30 Days)")
dom = dominance_stats(events_30d)

d1, d2, d3 = st.columns(3)
with d1:
    st.metric("Top 1 (%)", dom["top_1_pct"])
with d2:
    st.metric("Top 3 (%)", dom["top_3_pct"])
with d3:
    st.metric("Everyone Else (%)", dom["everyone_else_pct"])

st.divider()

st.header("Bender Detection (Last 30 Days)")
benders = bender_stats(events_30d, threshold=7)

if benders.empty:
    st.info("No benders logged yet. Hard to believe.")
else:
    st.dataframe(benders, use_container_width=True)
