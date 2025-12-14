from backend.services import log_beers, get_all_events

log_beers(
    user_name="Derin ~leather neck ~ A",
    beer_count=2,
    beer_type="Lager",
    city="San Francisco",
    state="CA",
    bar_name="",
)

print(get_all_events())
