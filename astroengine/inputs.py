"""Civil-time and location validation without geocoding or guessed zones."""

import math
import re
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import CalculationError, ChartRequest
from .rules import load_rules


def validate_coordinates(latitude: float, longitude: float) -> None:
    for value, limit, label in ((latitude, 90, "latitude"),
                                (longitude, 180, "longitude")):
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise CalculationError(f"{label} must be a finite number")
        if abs(value) > limit or not math.isfinite(value):
            raise CalculationError(f"{label} must be within [-{limit}, {limit}]")


def validate_profile(request: ChartRequest) -> None:
    from .recovery import suggest
    rules = load_rules("profiles.json")
    selections = ((request.zodiac, ("tropical", "sidereal"), "zodiac"),
                  (request.ayanamsa, rules["ayanamsas"], "ayanamsa"),
                  (request.house_system, rules["houses"], "house system"),
                  (request.node_type, rules["nodes"], "node type"))
    for selection, choices, label in selections:
        if selection not in choices:
            hints = suggest(str(selection), list(choices))
            hint = f"; did you mean {', '.join(hints)}?" if hints else ""
            raise CalculationError(f"Unknown {label}: {selection}{hint}")


def parse_civil(date_string: str, time_string: str | None = None) -> datetime:
    """Validate a civil date/clock; only an omitted clock selects local noon."""
    formats = load_rules("profiles.json")["input_formats"]
    clock = formats["unknown_time_surrogate"] if time_string is None else time_string
    if not isinstance(date_string, str) or not re.fullmatch(formats["date"], date_string):
        raise CalculationError("Invalid date: supply YYYY-MM-DD")
    if not isinstance(clock, str) or not re.fullmatch(formats["time"], clock):
        raise CalculationError("Invalid time: supply HH:MM or HH:MM:SS, without a timezone offset")
    try:
        return datetime.combine(date.fromisoformat(date_string), time.fromisoformat(clock))
    except ValueError as exc:
        raise CalculationError(f"Invalid date or time: {exc}") from exc


def resolve_utc(request: ChartRequest) -> datetime:
    validate_coordinates(request.latitude, request.longitude)
    validate_profile(request)
    naive = parse_civil(request.date, request.time)
    from .recovery import correct_timezone
    zone_name, _note = correct_timezone(request.timezone)
    try:
        zone = ZoneInfo(zone_name)
    except (ValueError, TypeError, ZoneInfoNotFoundError) as exc:
        raise CalculationError(f"Invalid date, time or timezone: {exc}") from exc
    try:
        candidates = {naive.replace(tzinfo=zone, fold=fold).astimezone(UTC)
                      for fold in (0, 1)
                      if naive.replace(tzinfo=zone, fold=fold).astimezone(UTC)
                      .astimezone(zone).replace(tzinfo=None) == naive}
    except (ValueError, OverflowError) as exc:
        raise CalculationError("UTC conversion is outside the supported civil calendar") from exc
    if len(candidates) != 1:
        label = "ambiguous" if candidates else "nonexistent"
        raise CalculationError(f"Civil time is {label}; provide the known UTC instant")
    return candidates.pop()
