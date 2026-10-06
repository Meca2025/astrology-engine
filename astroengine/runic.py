"""Northern runic cycles — R02 of ROADMAP_RUNIC.md.

Calendrical computations from Nigel Pennick, 'Runes and Astrology' (2023),
read from data/runic.json. Computation only: no symbolic interpretation,
no predictions. Historical claim of the underlying tables: modern synthesis.
"""

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import CalculationError
from .rules import load_rules


@dataclass(frozen=True)
class RunicDateRequest:
    """A civil date (and optional clock time) on the runic year-wheel."""
    date: str                      # ISO YYYY-MM-DD, required
    time: str | None = None        # ISO HH:MM, optional (boundary refinement)
    timezone: str | None = None    # IANA name or UTC; meaningful with time


def _corpus() -> dict:
    return load_rules("runic.json")


def _ordered_half_months(corpus: dict) -> list[dict]:
    """Half-months sorted by calendar start (MM-DD), Peorth (01-13) first."""
    return sorted(corpus["half_months"], key=lambda h: h["start"])


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CalculationError(f"invalid date '{value}': expected YYYY-MM-DD") \
            from exc


def _parse_time(value: str) -> tuple[int, int]:
    try:
        hh, mm = value.split(":")
        h, m = int(hh), int(mm)
    except (ValueError, AttributeError) as exc:
        raise CalculationError(
            f"invalid time '{value}': expected HH:MM") from exc
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise CalculationError(f"invalid time '{value}': expected HH:MM")
    return h, m


def _zone(name: str | None) -> ZoneInfo | None:
    if name is None:
        return None
    if name == "UTC":
        return ZoneInfo("UTC")
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise CalculationError(f"unknown timezone '{name}'") from exc


def _correspondences(corpus: dict, rune: str) -> dict:
    for r in corpus["runes"]:
        if r["name"] == rune and r["futhark"] == "elder":
            return {k: r[k] for k in ("tree", "herb", "color", "polarity",
                                      "element", "deity", "symbolic_meaning")}
    raise CalculationError(f"rune '{rune}' not found in corpus")


def half_month_rune(iso_date: str, time: str | None = None,
                    timezone: str | None = None) -> dict:
    """Name the ruling half-month rune for a civil date.

    Boundary rule (Pennick App. 2): the date belongs to the latest-starting
    half-month whose start date is on or before it; dates before 01-13 belong
    to Eoh (which began 12-28 of the prior year). When a clock time is given
    on a start date, the new rune begins at the book's local-apparent start
    time; before that hour the previous rune still rules.
    """
    day = _parse_date(iso_date)
    zone = _zone(timezone)
    clock = _parse_time(time) if time is not None else None
    if timezone is not None and time is None:
        raise CalculationError(
            "timezone is only meaningful together with a clock time")

    corpus = _corpus()
    ordered = _ordered_half_months(corpus)
    starts = [(h["start"], h) for h in ordered]  # MM-DD strings sort correctly

    key = day.strftime("%m-%d")
    # latest start <= key; wrap to Eoh for keys before 01-13
    idx = -1
    for i, (s, _) in enumerate(starts):
        if s <= key:
            idx = i
    if idx == -1:
        idx = len(starts) - 1  # Eoh, started 12-28 of the prior year
    current = starts[idx][1]

    if clock is not None and current["start"] == key:
        sh, sm = _parse_time(current["start_time"])
        if (clock[0], clock[1]) < (sh, sm):
            idx = (idx - 1) % len(starts)
            current = starts[idx][1]

    nxt = starts[(idx + 1) % len(starts)][1]
    nm, nd = int(nxt["start"][:2]), int(nxt["start"][3:])
    next_date = date(day.year, nm, nd)
    if next_date <= day:
        # next start lies in the following calendar year (e.g. Eoh -> Peorth)
        next_date = date(day.year + 1, nm, nd)
    days_remaining = (next_date - day).days

    return {
        "rune": current["rune"],
        "half_month_start": current["start"],
        "half_month_start_time": current["start_time"],
        "half_month_end": nxt["start"],
        "days_remaining": days_remaining,
        "next_rune": nxt["rune"],
        "correspondences": _correspondences(corpus, current["rune"]),
        "source": corpus["source"],
        "historical_claim": corpus["historical_claim"],
        "request": {"date": iso_date, "time": time, "timezone": timezone,
                    "zone_resolved": str(zone) if zone else None},
    }


def runic_date_request(iso_date: str, time: str | None = None,
                       timezone: str | None = None) -> RunicDateRequest:
    """Build a validated frozen request (raises CalculationError if invalid)."""
    _parse_date(iso_date)
    if time is not None:
        _parse_time(time)
    _zone(timezone)
    if timezone is not None and time is None:
        raise CalculationError(
            "timezone is only meaningful together with a clock time")
    return RunicDateRequest(date=iso_date, time=time, timezone=timezone)


__all__ = ["RunicDateRequest", "CalculationError", "half_month_rune",
           "runic_date_request"]


# ---------------------------------------------------------------------------
# R03 — runic hours, local apparent time, planetary hours, sele
# ---------------------------------------------------------------------------

import math


@dataclass(frozen=True)
class RunicHourRequest:
    """A civil clock instant plus observer longitude, for hour-wheel work."""
    iso_datetime: str              # ISO YYYY-MM-DDTHH:MM (civil, in `timezone`)
    longitude: float               # decimal degrees, -180..180
    timezone: str                  # IANA name or UTC (required)


def _parse_iso_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise CalculationError(
            f"invalid datetime '{value}': expected YYYY-MM-DDTHH:MM") from exc


def _check_longitude(value: float) -> float:
    try:
        lon = float(value)
    except (TypeError, ValueError) as exc:
        raise CalculationError(
            f"invalid longitude '{value}': expected decimal degrees") from exc
    if not -180.0 <= lon <= 180.0:
        raise CalculationError(
            f"invalid longitude '{value}': expected -180..180")
    return lon


def _equation_of_time_minutes(day_of_year: int) -> float:
    """Low-precision EoT approximation (minutes). Declared, not exact."""
    b = math.radians(360.0 / 365.0 * (day_of_year - 81))
    return (9.87 * math.sin(2 * b) - 7.53 * math.cos(b)
            - 1.5 * math.sin(b))


def to_local_apparent_time(iso_datetime: str, longitude: float,
                           timezone: str) -> dict:
    """Convert civil clock time to Local Apparent Time (the book's real time).

    Method (declared): LAT = UTC + longitude/15h + EoT, with the standard
    low-precision equation-of-time approximation. Midday LAT = sun due south.
    Accuracy is a few minutes; the book itself averages start times "to the
    nearest hour".
    """
    from datetime import timedelta
    naive = _parse_iso_datetime(iso_datetime)
    if naive.tzinfo is not None:
        raise CalculationError(
            f"invalid datetime '{iso_datetime}': must be wall time without "
            "offset; pass the zone separately")
    lon = _check_longitude(longitude)
    zone = _zone(timezone)
    if zone is None:
        raise CalculationError("timezone is required for apparent-time work")
    aware = naive.replace(tzinfo=zone)
    utc = aware.astimezone(ZoneInfo("UTC"))
    eot = _equation_of_time_minutes(aware.timetuple().tm_yday)
    lat = utc + timedelta(hours=lon / 15.0, minutes=eot)
    return {
        "local_apparent_time": lat.strftime("%H:%M"),
        "utc": utc.strftime("%Y-%m-%dT%H:%M"),
        "equation_of_time_minutes": round(eot, 2),
        "longitude": lon,
        "method": "longitude+eot-approx",
    }


def runic_hour(local_apparent_time: str) -> dict:
    """Name the rune ruling a solar hour (HH:MM local apparent time).

    Wheel (Ch. 4): Feoh 12:30-13:30, each futhark rune one solar hour later,
    Dag 11:30-12:30.
    """
    h, m = _parse_time(local_apparent_time)
    t = h * 60 + m
    idx = ((t - (12 * 60 + 30)) % (24 * 60)) // 60
    corpus = _corpus()
    entry = corpus["runic_hours"]["hours"][idx]
    return {
        "rune": entry["rune"],
        "window": f'{entry["start"]}-{entry["end"]}',
        "correspondences": _correspondences(corpus, entry["rune"]),
        "source": corpus["source"],
        "historical_claim": corpus["historical_claim"],
    }


_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday"]


def planetary_hour(weekday: str, clock_hour: int) -> dict:
    """Name the deity of a Northern Tradition planetary hour (App. 3).

    The book divides planetary hours hour-to-hour on CLOCK time (unlike the
    solar runic hours). `weekday`: English name; `clock_hour`: 0-23.
    """
    name = weekday.strip().capitalize()
    if name not in _WEEKDAYS:
        raise CalculationError(
            f"invalid weekday '{weekday}': expected one of "
            + ", ".join(_WEEKDAYS))
    try:
        hh = int(clock_hour)
    except (TypeError, ValueError) as exc:
        raise CalculationError(
            f"invalid clock_hour '{clock_hour}': expected 0-23") from exc
    if not 0 <= hh <= 23:
        raise CalculationError(
            f"invalid clock_hour '{clock_hour}': expected 0-23")
    corpus = _corpus()
    deity = corpus["planetary_hours"]["grid"][name][hh]
    return {
        "weekday": name,
        "clock_hour": hh,
        "deity": deity,
        "note": corpus["planetary_hours"]["note"],
        "source": corpus["source"],
        "historical_claim": corpus["historical_claim"],
    }


def sele(iso_datetime: str, longitude: float, timezone: str) -> dict:
    """Detect sele: runic hour-rune and planetary hour sharing a deity.

    Pennick: "When appropriate runic hours coincide with their planetary
    equivalents, these are especially powerful." Appropriate = the planetary
    deity appears in the hour-rune's deity correspondence (App. 1).
    """
    lon = _check_longitude(longitude)
    zone = _zone(timezone)
    if zone is None:
        raise CalculationError("timezone is required for sele work")
    naive = _parse_iso_datetime(iso_datetime)
    if naive.tzinfo is not None:
        raise CalculationError(
            f"invalid datetime '{iso_datetime}': must be wall time without "
            "offset; pass the zone separately")
    aware = naive.replace(tzinfo=zone)

    lat = to_local_apparent_time(iso_datetime, lon, timezone)
    rh = runic_hour(lat["local_apparent_time"])
    weekday = aware.strftime("%A")
    ph = planetary_hour(weekday, aware.hour)

    rune_deities = {d.strip() for d in
                    rh["correspondences"]["deity"].split("/")}
    is_sele = ph["deity"] in rune_deities
    return {
        "sele": is_sele,
        "runic_hour": {"rune": rh["rune"], "window": rh["window"],
                       "local_apparent_time": lat["local_apparent_time"],
                       "deities": sorted(rune_deities)},
        "planetary_hour": {"weekday": ph["weekday"],
                           "clock_hour": ph["clock_hour"],
                           "deity": ph["deity"]},
        "method": lat["method"],
        "source": rh["source"],
        "historical_claim": rh["historical_claim"],
    }


__all__ += ["RunicHourRequest", "to_local_apparent_time", "runic_hour",
            "planetary_hour", "sele"]
