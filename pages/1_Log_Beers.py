import streamlit as st
from backend.services import log_beers


# ---- Config ----

USER_OPTIONS = [
    "Ian ~the jester~ G",
    "Vishwaz N",
    "Ryan E, esquire",
    "Varoon A",
    "Max Furlani",
    "Sonaal ~the fowler ~ V",
    "Paul ~irontooth~ L",
    "Sammy S",
    "Derin ~leather neck ~ A",
    "Matteo Adriano Ravelli Di Lorenzo Chiellini Ciabattoni",
    "Crundo :)",
    "Jack Kaffeine-Burger",
    "Logan ~CTE~ B",
    "Danny H",
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
    "Other",
]


# ---- Page ----

st.title("Log Beers")

with st.expander("Beer Tracker 9000 Rules", expanded=True):
    st.markdown(
        """
        ## Ground Rules

        1. Thou shalt log thy beers truthfully. Deceit corrupts the ledger, and thy honor with it.
        2. Please don't blow up my database (ie. no spam)
        3. One log per drinking session (use the count field). Let the count speak plainly; do not scatter thy sins.
        4. City and state should reflect where the beers were consumed.
        5. Bar name is optional but encouraged.
        6. Feature suggestions welcomed
        """
    )

st.divider()

# ---- Session defaults ----

if "user_name" not in st.session_state:
    st.session_state.user_name = USER_OPTIONS[0]

if "city" not in st.session_state:
    st.session_state.city = ""

if "state" not in st.session_state:
    st.session_state.state = ""


# ---- Form ----

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

    state = st.text_input(
        "State",
        value=st.session_state.state,
        placeholder="e.g. MI",
    )

    bar_name = st.text_input(
        "Bar name (optional)",
        placeholder="e.g. Skeeps",
    )

    submitted = st.form_submit_button("Log beers")

    if submitted:
        beer_count = int(beer_count)

        if not city or not state:
            st.error("City and state are required.")

        elif beer_count > 20:
            st.error(f"{beer_count}? Cap.")

        else:
            log_beers(
                user_name=user_name,
                beer_count=beer_count,
                beer_type=beer_type,
                bar_name=bar_name or None,
                city=city,
                state=state,
            )

            # Persist defaults
            st.session_state.user_name = user_name
            st.session_state.city = city
            st.session_state.state = state

            if beer_count <= 3:
                st.success(f"{user_name}, {beer_count}? why even bother")

            elif beer_count <= 10:
                st.success(f"{user_name} had {beer_count} in {city}, {state}.")

            else:  # 11–20
                st.success(f"{beer_count}? well done lad")
