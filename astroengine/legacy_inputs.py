"""Typed compatibility adapters for legacy input tuples; no legacy imports."""

import math
from calendar import monthrange
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from .inputs import parse_civil, resolve_utc, validate_coordinates
from .models import CalculationError, ChartRequest
from .rules import load_rules

BirthTuple = tuple[int, int, int, float, float, float, str, str, bool, bool]


def coordinate_pair(latitude: float | str | None, longitude: float | str | None,
                    labels: tuple[str, str] = ("--lat", "--lon")
                    ) -> tuple[float, float] | None:
    """Convert legacy numeric flags, admitting only complete, valid pairs."""
    if latitude is None and longitude is None:
        return None
    if latitude is None or longitude is None:
        raise CalculationError(f"Supply both {labels[0]} and {labels[1]} for explicit coordinates")
    if isinstance(latitude, bool) or isinstance(longitude, bool):
        raise CalculationError("Coordinates must be finite numbers, not booleans")
    try:
        lat, lon = float(latitude), float(longitude)
    except (TypeError, ValueError, OverflowError) as exc:
        raise CalculationError("Coordinates must be finite numbers") from exc
    validate_coordinates(lat, lon)
    return lat, lon


def offset_label(utc: datetime, timezone: str) -> str:
    """Retain historical offset seconds when an IANA zone has them."""
    offset = utc.astimezone(ZoneInfo(timezone)).utcoffset()
    seconds = int(offset.total_seconds())
    hours, remainder = divmod(abs(seconds), 3600)
    minutes, seconds_part = divmod(remainder, 60)
    label = f"UTC{'+' if seconds >= 0 else '-'}{hours:02d}:{minutes:02d}"
    return f"{label}:{seconds_part:02d}" if seconds_part else label


def local_hour_to_utc(year: int, month: int, day: int, local_hour: float,
                      timezone: str) -> tuple[float, str]:
    """Keep signed UTC hours relative to civil midnight for Julian-day callers."""
    if isinstance(local_hour, bool) or not isinstance(local_hour, (float, int)):
        raise CalculationError("Local clock hour must be a finite number in [0,24)")
    if not math.isfinite(local_hour) or not 0 <= local_hour < 24:
        raise CalculationError("Local clock hour must be a finite number in [0,24)")
    try:
        civil_day = date(year, month, day)
        midnight = datetime.combine(civil_day, datetime.min.time(), UTC)
        local = midnight.replace(tzinfo=None) + timedelta(hours=local_hour)
    except (ValueError, TypeError, OverflowError) as exc:
        raise CalculationError(f"Invalid civil date or clock: {exc}") from exc
    if local.date() != civil_day:
        raise CalculationError("Local clock hour rounds beyond the civil day")
    request = ChartRequest(civil_day.isoformat(), 0.0, 0.0, timezone, local.time().isoformat())
    utc = resolve_utc(request)
    return (utc - midnight).total_seconds() / 3600, offset_label(utc, timezone)


def clock_label(value: datetime) -> str:
    if value.second or value.microsecond:
        return value.time().replace(tzinfo=None).isoformat()
    return value.strftime("%H:%M")


def return_year(value: str | int | None) -> int:
    """Validate the legacy solar-return target year before astronomy."""
    try:
        if isinstance(value, bool) or (value is not None and not isinstance(value, (str, int))):
            raise ValueError("noninteger year")
        year = datetime.now(UTC).year if value is None else int(value)
        date(year, 1, 1)
    except (TypeError, ValueError, OverflowError) as exc:
        raise CalculationError("Invalid return year: supply an integer in [1,9999]") from exc
    return year


def date_window(start_string: str, end_string: str | None = None) -> tuple[date, date]:
    """Validate ordered civil-date windows; default end clamps leap birthdays."""
    start = parse_civil(start_string).date()
    if end_string is None:
        year = start.year + load_rules("profiles.json")["legacy_defaults"]["prediction_years"]
        if year > date.max.year:
            raise CalculationError("Default prediction end exceeds year 9999; supply --end")
        end = date(year, start.month, min(start.day, monthrange(year, start.month)[1]))
    else:
        end = parse_civil(end_string).date()
    if end <= start:
        raise CalculationError("Prediction --end must be after --start")
    return start, end


def birth_tuple(request: ChartRequest) -> BirthTuple:
    """Normalize a validated request into the unchanged legacy ten-item tuple."""
    utc = resolve_utc(request)
    local = parse_civil(request.date, request.time)
    display = clock_label(utc)
    if utc.date() != local.date():
        display = f"{utc.date().isoformat()} {display}"
    offset = offset_label(utc, request.timezone)
    known = request.time is not None
    if known:
        label = f"{clock_label(local)} LT  →  {display} UTC  ({offset}  {request.timezone})"
    else:
        label = (f"Time unknown — using 12:00 noon  ({request.timezone})  →  "
                 f"{display} UTC  ({offset})")
    utc_hour = (utc - utc.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600
    return (utc.year, utc.month, utc.day, utc_hour, request.latitude, request.longitude,
            request.timezone, label, known, False)
