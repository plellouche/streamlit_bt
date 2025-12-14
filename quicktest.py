from backend.services import log_beers, get_all_events

log_beers(
    user_name="Test",
    beer_count=1,
    beer_type="IPA",
    city="Ann Arbor",
    state="MI",
    bar_name="Skeeps",
)

print(get_all_events())
