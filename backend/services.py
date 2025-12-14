from typing import Optional
import pandas as pd

from backend.db import SQLiteStore
from backend.models import DrinkEvent


_store = SQLiteStore()


def log_beers(
    user_name: str,
    beer_count: int,
    beer_type: Optional[str] = None,
    bar_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> None:
    event = DrinkEvent.create(
        user_name=user_name,
        beer_count=beer_count,
        beer_type=beer_type,
        bar_name=bar_name,
        city=city,
        state=state,
        latitude=latitude,
        longitude=longitude,
    )
    _store.insert_event(event)


def get_all_events() -> pd.DataFrame:
    return _store.fetch_events()

def export_events_to_csv(path: str):
    import pandas as pd
    events = get_all_events()
    events.to_csv(path, index=False)
