import streamlit as st
from backend.bootstrap import bootstrap_db_from_csv

bootstrap_db_from_csv()

st.set_page_config(
    page_title="Beer Tracker",
    page_icon="🍺",
    layout="centered",
)

st.title("🍺 Beer Tracker")

st.markdown(
    """
    Welcome to the Beer Tracker 9000.

    Use navigation bar on the left to:
    - Log beers
    - View stats
    """
)
