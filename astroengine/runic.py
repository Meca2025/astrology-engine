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
