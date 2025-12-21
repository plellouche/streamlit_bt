from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True)
class DrinkEvent:
    event_id: str
    timestamp_utc: datetime
    user_name: str
    beer_count: int
    beer_type: Optional[str]
    bar_name: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

    @staticmethod
    def create(
        user_name: str,
        beer_count: int,
        beer_type: Optional[str] = None,
        bar_name: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> "DrinkEvent":
        if not user_name or not user_name.strip():
            raise ValueError("user_name must be a non-empty string")

        if not isinstance(beer_count, int) or beer_count <= 0:
            raise ValueError("beer_count must be a positive integer")

        return DrinkEvent(
            event_id=str(uuid.uuid4()),
            timestamp_utc=datetime.utcnow(),
            user_name=user_name.strip(),
            beer_count=beer_count,
            beer_type=_normalize_str(beer_type),
            bar_name=_normalize_str(bar_name),
            city=_normalize_str(city),
            state=_normalize_str(state),
            country=_normalize_str(country),
            latitude=latitude,
            longitude=longitude,
        )


def _normalize_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None
