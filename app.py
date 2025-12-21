import streamlit as st

from backend.bootstrap import bootstrap_db_from_csv

bootstrap_db_from_csv()

st.set_page_config(
    page_title="Beer Tracker 9000",
    page_icon="🍺",
    layout="wide",
)

st.title("Beer Tracker 9000")

st.markdown(
    """
    Welcome to **Beer Tracker 9000**.

    Use the pages on the left to:
    - Log beers
    - View leaderboards
    - Explore stats, maps

    """
)
