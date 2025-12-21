import streamlit as st
from backend.services import log_beers


USER_OPTIONS = [
    "Ian 'the jester' Greene",
    "Vishwaz Nathan",
    "Ryan Eschelbach, esquire",
    "Varoon Argawal",
    "Max Furlani",
    "Sonaal 'the fowler' Verma",
    "Paul 'irontooth' Lellouche",
    "Sammy Sug",
    "Derin ~leather neck ~ Alev",
    "Matteo Adriano Ravelli Di Lorenzo Chiellini Ciabattoni",
    "Crundo :)",
    "Jack Kaffeine-Burger",
    "Logan ~CTE~ Brinks",
    "Danny Heibel",
    "Ryan 'Tomahawk' Wu'",
    "Kyra ~Chase~ Heibel",
    "Joe Heibel",
    "Samurai Rei",
    "Grant 'yellow feev' Barry",
    "Andrew 'sugar baby' Tebeau"
]

BEER_TYPES = [
    "Lager",
    "IPA",
    "Pilsner",
    "Seltzer",
    "Stout",
    "Sour",
    "Wheat",
    "Fruity?",
    "Cocktail",
    "Shot",
    "Wine",
    "Other",
]

COUNTRY_OPTIONS = [
    "United States",
    "Canada",
    "Mexico",
    "United Kingdom",
    "Ireland",
    "France",
    "Germany",
    "Spain",
    "Italy",
    "Netherlands",
    "Belgium",
    "Sweden",
    "Norway",
    "Denmark",
    "Poland",
    "Czechia",
    "Austria",
    "Switzerland",
    "Portugal",
    "Greece",
    "Turkey",
    "Israel",
    "United Arab Emirates",
    "India",
    "China",
    "Japan",
    "South Korea",
    "Singapore",
    "Australia",
    "New Zealand",
    "Brazil",
    "Argentina",
    "Chile",
    "Colombia",
    "Peru",
    "South Africa",
    "Other (type manually)",
]


st.title("Log Beers")

with st.expander("Beer Tracker 9000 Rules", expanded=True):
    st.markdown(
        """
        ## Ground Rules

        1. Thou shalt log thy beers truthfully. Deceit corrupts the ledger, and thy honor with it.
        2. Please don't blow up my database (ie. no spam)
        3. One log per drinking session (use the count field). Let the count speak plainly; do not scatter thy sins.
        4. If drink at home leave bar name empty
        5. Location should reflect where the beers were consumed.
        6. Feature suggestions welcomed.
        """
    )

st.divider()

if "user_name" not in st.session_state:
    st.session_state.user_name = USER_OPTIONS[0]
if "city" not in st.session_state:
    st.session_state.city = ""
if "state" not in st.session_state:
    st.session_state.state = ""
if "country" not in st.session_state:
    st.session_state.country = "United States"
if "country_manual" not in st.session_state:
    st.session_state.country_manual = ""

with st.form("log_beers_form"):
    st.subheader("Who and how many")

    user_name = st.selectbox(
        "Name",
        USER_OPTIONS,
        index=USER_OPTIONS.index(st.session_state.user_name),
    )

    beer_count = st.number_input(
        "Number of beers",
        min_value=1,
        step=1,
        value=1,
    )

    beer_type = st.selectbox(
        "Beer type",
        BEER_TYPES,
        index=0,
    )

    st.divider()
    st.subheader("Where")

    city = st.text_input(
        "City",
        value=st.session_state.city,
        placeholder="e.g. Ann Arbor",
    )

    country_choice = st.selectbox(
        "Country",
        COUNTRY_OPTIONS,
        index=COUNTRY_OPTIONS.index(st.session_state.country)
        if st.session_state.country in COUNTRY_OPTIONS
        else 0,
    )

    country_manual = None
    if country_choice == "Other (type manually)":
        country_manual = st.text_input(
            "Country (manual)",
            value=st.session_state.country_manual,
            placeholder="e.g. Thailand",
        ).strip()
        country = country_manual
    else:
        country = country_choice

    state = None
    if country == "United States":
        state = st.text_input(
            "State (US only, 2 letters)",
            value=st.session_state.state,
            placeholder="e.g. MI",
        ).strip()

    bar_name = st.text_input(
        "Bar name (optional)",
        placeholder="e.g. Skeeps",
    )

    submitted = st.form_submit_button("Log beers")

    if submitted:
        if int(beer_count) > 20:
            st.error(f"{int(beer_count)}? Cap.")
        elif not city or not country:
            st.error("City and country are required.")
        elif country == "United States" and (not state):
            st.error("State is required when country is United States.")
        else:
            log_beers(
                user_name=user_name,
                beer_count=int(beer_count),
                beer_type=beer_type,
                bar_name=bar_name or None,
                city=city.strip(),
                state=(state.strip() if state else None),
                country=country.strip(),
            )

            st.session_state.user_name = user_name
            st.session_state.city = city.strip()
            st.session_state.country = country_choice
            st.session_state.country_manual = country_manual or ""
            if country == "United States":
                st.session_state.state = state.strip()

            bc = int(beer_count)
            if 1 <= bc <= 3:
                st.success(f"{user_name}, {bc}? why even bother")
            elif 3 < bc <= 10:
                if country == "United States":
                    st.success(f"{user_name} had {bc} in {city.strip()}, {state.strip()}.")
                else:
                    st.success(f"{user_name} had {bc} in {city.strip()}, {country.strip()}.")
            else:
                st.success(f"{bc}? well done lad")
