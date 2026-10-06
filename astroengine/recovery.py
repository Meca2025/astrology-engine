"""Self-healing and error correction.

The mending toolkit: typo-tolerant dates, times and timezones,
did-you-mean suggestions for every closed vocabulary, and a
degradation wrapper so composite readings survive a failing
section. Healing is always logged (a note), never silent;
guesses that could mislead (ambiguous abbreviations, DD/MM vs
MM/DD) are suggested, not assumed.
"""

from __future__ import annotations

import difflib
import re
from datetime import date as _date
from typing import Any, Callable
from zoneinfo import ZoneInfo, available_timezones

from .models import CalculationError

_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def suggest(word: str, candidates: list[str], n: int = 3,
            cutoff: float = 0.6) -> list[str]:
    """Did-you-mean suggestions, best first."""
    return difflib.get_close_matches(word, candidates, n=n, cutoff=cutoff)


def correct_timezone(zone: str | None) -> tuple[str | None, str | None]:
    """Return (corrected_zone, note). Raises CalculationError with
    suggestions when the zone is unknown. None passes through."""
    if zone is None:
        return None, None
    try:
        ZoneInfo(zone)
        return zone, None
    except Exception:
        pass
    fixed = zone.strip().replace(" ", "_")
    try:
        ZoneInfo(fixed)
        return fixed, f"timezone '{zone}' healed to '{fixed}'"
    except Exception:
        pass
    lowered = {z.lower(): z for z in available_timezones()}
    if fixed.lower() in lowered:
        hit = lowered[fixed.lower()]
        return hit, f"timezone '{zone}' healed to '{hit}'"
    hints = suggest(fixed, sorted(available_timezones()))[:3]
    hint = f"; did you mean {', '.join(hints)}?" if hints else ""
    raise CalculationError(f"unknown timezone '{zone}'{hint}")


def _iso_or_raise(year: int, month: int, day: int,
                  original: str) -> tuple[str, str | None]:
    try:
        iso = _date(year, month, day).isoformat()
    except ValueError as exc:
        raise CalculationError(
            f"Invalid date '{original}': {exc}") from exc
    note = None if iso == original.strip() else \
        f"date '{original.strip()}' read as {iso}"
    return iso, note


def heal_date(date_str: str) -> tuple[str, str | None]:
    """Return (YYYY-MM-DD, note). Strict ISO first, then human forms.

    Accepted human forms: 'Oct 7 2026', '7 Oct 2026', MM/DD/YYYY
    (documented US convention), '2026.10.07'. Anything else raises
    a clean CalculationError.
    """
    s = date_str.strip()
    try:
        _date.fromisoformat(s)
        return s, None
    except ValueError:
        pass
    m = re.fullmatch(r"([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})", s)
    if m and m.group(1)[:3].lower() in _MONTHS:
        return _iso_or_raise(int(m.group(3)), _MONTHS[m.group(1)[:3].lower()],
                             int(m.group(2)), date_str)
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3,9}),?\s+(\d{4})", s)
    if m and m.group(2)[:3].lower() in _MONTHS:
        return _iso_or_raise(int(m.group(3)), _MONTHS[m.group(2)[:3].lower()],
                             int(m.group(1)), date_str)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return _iso_or_raise(int(m.group(3)), int(m.group(1)),
                             int(m.group(2)), date_str)
    m = re.fullmatch(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", s)
    if m:
        return _iso_or_raise(int(m.group(1)), int(m.group(2)),
                             int(m.group(3)), date_str)
    raise CalculationError(
        f"Invalid date '{date_str}': supply YYYY-MM-DD "
        f"(also read: 'Oct 7 2026', '7 Oct 2026', MM/DD/YYYY)")


def heal_time(time_str: str | None) -> tuple[str | None, str | None]:
    """Return (HH:MM, note). Strict first, then '8:18am', '8pm', '0818'.
    None (unknown time) passes through."""
    if time_str is None:
        return None, None
    s = time_str.strip()
    if re.fullmatch(r"\d{2}:\d{2}(:\d{2})?", s):
        return s, None
    m = re.fullmatch(r"(\d{1,2}):(\d{2})\s*([AaPp])\.?[Mm]\.?", s)
    if m:
        hour = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "p" else 0)
        return f"{hour:02d}:{m.group(2)}", f"time '{s}' read as {hour:02d}:{m.group(2)}"
    m = re.fullmatch(r"(\d{1,2})\s*([AaPp])\.?[Mm]\.?", s)
    if m:
        hour = int(m.group(1)) % 12 + (12 if m.group(2).lower() == "p" else 0)
        return f"{hour:02d}:00", f"time '{s}' read as {hour:02d}:00"
    m = re.fullmatch(r"(\d{2})(\d{2})", s)
    if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
        return f"{m.group(1)}:{m.group(2)}", f"time '{s}' read as {m.group(1)}:{m.group(2)}"
    raise CalculationError(
        f"Invalid time '{time_str}': supply HH:MM "
        f"(also read: '8:18am', '8pm', '0818')")


def graceful(label: str, fn: Callable, *args: Any,
             **kwargs: Any) -> tuple[bool, Any, str | None]:
    """Run fn; return (True, result, None) or (False, None, error).

    Composite readings use this so one failing optional section
    degrades to an 'unavailable' note instead of killing the report.
    """
    try:
        return True, fn(*args, **kwargs), None
    except CalculationError as exc:
        return False, None, str(exc)
    except Exception as exc:  # noqa: BLE001 — degradation must not raise
        return False, None, f"{type(exc).__name__}: {exc}"


def chart_suggestions(name: str, directory: str | None = None) -> list[str]:
    """Close matches among saved chart names."""
    from .charts import list_charts
    names = [c["name"] for c in list_charts(directory)]
    return suggest(name, names)
