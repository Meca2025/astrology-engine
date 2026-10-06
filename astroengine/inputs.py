"""Civil-time and location validation without geocoding or guessed zones."""

import math
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import CalculationError, ChartRequest
from .rules import load_rules


def validate_coordinates(latitude: float, longitude: float) -> None:
    for value, limit, label in ((latitude, 90, "latitude"),
                                (longitude, 180, "longitude")):
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise CalculationError(f"{label} must be a finite number")
        if not math.isfinite(value) or abs(value) > limit:
            raise CalculationError(f"{label} must be within [-{limit}, {limit}]")


def validate_profile(request: ChartRequest) -> None:
    rules = load_rules("profiles.json")
    selections = ((request.zodiac, ("tropical", "sidereal"), "zodiac"),
                  (request.ayanamsa, rules["ayanamsas"], "ayanamsa"),
                  (request.house_system, rules["houses"], "house system"),
                  (request.node_type, rules["nodes"], "node type"))
    for selection, choices, label in selections:
        if selection not in choices:
            raise CalculationError(f"Unknown {label}: {selection}")


def resolve_utc(request: ChartRequest) -> datetime:
    validate_coordinates(request.latitude, request.longitude)
    validate_profile(request)
    try:
        local_date = date.fromisoformat(request.date)
        local_time = time.fromisoformat(request.time or "12:00")
        if local_time.tzinfo is not None:
            raise CalculationError("Supply a civil time and separate IANA timezone")
        zone = ZoneInfo(request.timezone)
    except (ValueError, TypeError, ZoneInfoNotFoundError) as exc:
        raise CalculationError(f"Invalid date, time or timezone: {exc}") from exc
    naive = datetime.combine(local_date, local_time)
    candidates = {naive.replace(tzinfo=zone, fold=fold).astimezone(UTC)
                  for fold in (0, 1)
                  if naive.replace(tzinfo=zone, fold=fold).astimezone(UTC)
                  .astimezone(zone).replace(tzinfo=None) == naive}
    if len(candidates) != 1:
        label = "ambiguous" if candidates else "nonexistent"
        raise CalculationError(f"Civil time is {label}; provide the known UTC instant")
    return candidates.pop()
