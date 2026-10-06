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


# ---------------------------------------------------------------------------
# R04 — Tides of day (App. 6), Stations of the year (Ch. 5), runic names
# ---------------------------------------------------------------------------

def tide(clock_time: str) -> dict:
    """Return the tide (Pennick App. 6) ruling a clock ``HH:MM`` time.

    The eight tides are fixed clock divisions (04:30–07:30 etc.); they use
    civil clock time, not local apparent time.
    """
    hh, mm = _parse_time(clock_time)
    corpus = _corpus()
    tides = corpus["tides"]["tides"]

    def _mins(value: str) -> int:
        h, m = (int(x) for x in value.split(":"))
        return h * 60 + m

    now = hh * 60 + mm
    for entry in tides:
        start, end = _mins(entry["start"]), _mins(entry["end"])
        if start <= end:
            hit = start <= now < end
        else:  # wraps midnight, e.g. Midnight 22:30–01:30
            hit = now >= start or now < end
        if hit:
            return {
                "clock_time": clock_time,
                "english": entry["english"],
                "old_english": entry["old_english"],
                "old_norse": entry["old_norse"],
                "window": f"{entry['start']}–{entry['end']}",
                "source": "Pennick (2023)",
                "historical_claim": "modern synthesis",
            }
    raise CalculationError(
        f"no tide covers '{clock_time}' (corpus tides cover the full day)")


def year_station(iso_date: str) -> dict:
    """Return the Station of the Mystic Year (Pennick Ch. 5) for a date.

    Boundary method (declared convention, not book text): each station spans
    [festival_date, next festival_date) in cycle order
    Fourth→Fifth→Sixth→Seventh→Eighth→First→Second→Third→Fourth. The First
    station has no festival in the book; it is conventionally anchored at
    Aug 13, the start of the As half-month (first of its "As/Rad" runes).
    """
    day = _parse_date(iso_date)
    corpus = _corpus()
    stations = corpus["stations"]["stations"]
    # Latest festival anchor on or before the date (wrap: before the first
    # anchor of the year, the year began with the Fourth station / Yule).
    anchors = sorted(
        stations,
        key=lambda s: (int(s["festival_date"][0:2]),
                       int(s["festival_date"][3:5])))
    day_key = (day.month, day.day)
    chosen = anchors[-1]
    for station in anchors:
        mm, dd = (int(x) for x in station["festival_date"].split("-"))
        if (mm, dd) <= day_key:
            chosen = station
    return {
        "date": iso_date,
        "station": chosen["number"],
        "name": chosen["name"],
        "runes": chosen["runes"],
        "festival": chosen["festival"],
        "day_hour": chosen["day_hour"],
        "symbolic_event": chosen["symbolic_event"],
        "method": "festival-span (declared engine convention; "
                  "boundaries are not in the book)",
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    }


def runic_name(iso_datetime: str, longitude: float, timezone: str) -> dict:
    """Compose the runic-name pair for a birth/name-taking moment (Ch. 5).

    Returns the half-month rune (the person's "name" rune) and the
    local-apparent hour-rune. The book's rendered names (Kenneth, Ingrid,
    Darwin) are literary English wordplay on these pairs, not mechanical
    output — e.g. the printed Kenneth example (Odal hour) conflicts with
    the systematic wheel (Is hour); see R01 notes. The engine reports the
    wheel-faithful pair.
    """
    lon = _check_longitude(longitude)
    zone = _zone(timezone)
    if zone is None:
        raise CalculationError("timezone is required for runic-name work")
    naive = _parse_iso_datetime(iso_datetime)
    if naive.tzinfo is not None:
        raise CalculationError(
            f"invalid datetime '{iso_datetime}': must be wall time without "
            "offset; pass the zone separately")
    lat = to_local_apparent_time(iso_datetime, lon, timezone)
    month_rune = half_month_rune(naive.date().isoformat())
    hour_rune = runic_hour(lat["local_apparent_time"])
    return {
        "datetime": iso_datetime,
        "half_month_rune": month_rune["rune"],
        "hour_rune": hour_rune["rune"],
        "pair": f"{month_rune['rune']}-{hour_rune['rune']}",
        "local_apparent_time": lat["local_apparent_time"],
        "method": lat["method"],
        "note": "Book names (Kenneth, Ingrid, Darwin) are literary "
                "renderings of such pairs, not mechanical output.",
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    }


__all__ += ["tide", "year_station", "runic_name"]


# ---------------------------------------------------------------------------
# R05 — Zodiacal (App. 5), weekday (App. 4), and life-period (Ch. 6) layers
# ---------------------------------------------------------------------------

def zodiac_rune(sign: str, variant: str = "classical") -> dict:
    """Return the App. 5 correspondences for a zodiac sign.

    Capricorn, Aquarius and Pisces each have two rows in the book:
    "classical" and "modern alternative". Every other sign has one row.
    """
    corpus = _corpus()
    rows = [r for r in corpus["zodiac"]
            if r["sign"].lower() == sign.strip().lower()]
    if not rows:
        raise CalculationError(
            f"unknown zodiac sign '{sign}'")
    variants = {r["variant"] for r in rows}
    if variant not in variants:
        raise CalculationError(
            f"unknown variant '{variant}' for {rows[0]['sign']}; "
            f"available: {sorted(variants)}")
    row = next(r for r in rows if r["variant"] == variant)
    return {
        "sign": row["sign"],
        "variant": row["variant"],
        "rune": row["rune"],
        "deity": row["deity"],
        "planet": row["planet"],
        "day": row["day"],
        "stone": row["stone"],
        "animal": row["animal"],
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    }


def weekday_rune(weekday: str) -> dict:
    """Return the App. 4 correspondences for an English weekday."""
    corpus = _corpus()
    for row in corpus["weekdays"]:
        if row["day"].lower() == weekday.strip().lower():
            return {
                "weekday": row["day"],
                "deity": row["deity"],
                "planet": row["planet"],
                "rune": row["rune"],
                "tree": row["tree"],
                "herb": row["herb"],
                "element": row["element"],
                "esoteric_number": row["esoteric_number"],
                "magic_square": row["magic_square"],
                "source": "Pennick (2023)",
                "historical_claim": "modern synthesis",
            }
    raise CalculationError(f"unknown weekday '{weekday}'")


def life_period(age_years: float) -> dict:
    """Return the Ch. 6 planetary life-period ruling an age in years.

    The book's wheel: Máni 0–4, Odin 4–14, Frigg 14–22, Sól 22–41,
    Tyr 41–56, Thor 56–68, Loki 68–98 (98 years total).
    """
    try:
        age = float(age_years)
    except (TypeError, ValueError):
        raise CalculationError(
            f"invalid age '{age_years}': must be a number of years")
    corpus = _corpus()
    for idx, period in enumerate(corpus["life_periods"]):
        if period["start_age"] <= age < period["end_age"]:
            return {
                "age": age,
                "period": idx + 1,
                "deity": period["deity"],
                "planet": period["planet"],
                "years_elapsed": round(age - period["start_age"], 6),
                "years_remaining": round(period["end_age"] - age, 6),
                "period_span": [period["start_age"], period["end_age"]],
                "source": "Pennick (2023)",
                "historical_claim": "modern synthesis",
            }
    raise CalculationError(
        f"age {age} is outside the book's 0–98 year life-period wheel")


def metonic_cycle(year: int) -> dict:
    """Return the year's place in the 19-year Metonic cycle (Ch. 6).

    Golden Number = (year mod 19) + 1, the calendrical count the book
    describes (golden characters on the Athenian monuments; the Church's
    later Easter reckoning is derivative). Pure calendrical computation —
    runic.py stays ephemeris-free by design.
    """
    try:
        y = int(year)
    except (TypeError, ValueError):
        raise CalculationError(
            f"invalid year '{year}': must be an integer")
    golden = (y % 19) + 1
    return {
        "year": y,
        "golden_number": golden,
        "year_in_cycle": golden,
        "years_until_cycle_restart": 19 - golden,
        "cycle_length_years": 19,
        "note": "After 310 Julian years the moon takes a step backward — "
                "the Aun cycle, requiring recalibration of the Metonic "
                "count (Ch. 6).",
        "method": "calendrical Golden Number per Pennick Ch. 6",
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    }


__all__ += ["zodiac_rune", "weekday_rune", "life_period", "metonic_cycle"]


# ---------------------------------------------------------------------------
# R06 — The 28 lunar mansions (Ch. 7)
# ---------------------------------------------------------------------------

# Declared modern convention (not historical fact): 28 equal sidereal
# segments of 360/28 degrees; mansion 1 (Feoh, "Boars' Throng") begins at
# Alcyone's J2000 sidereal longitude, per the book's "mansions began with
# the star Alcyone (eta Tauri)". Derived: Alcyone J2000 RA 3h47m24.3s Dec
# +24d06'18" -> tropical 59.9746 deg; minus Lahiri ayanamsa 23.8571 deg.
MANSION_ANCHOR_DEG = 36.1175
MANSION_WIDTH_DEG = 360.0 / 28.0


def _mansion_row(corpus: dict, number: int) -> dict:
    return next(m for m in corpus["mansions"]["mansions"]
                if m["number"] == number)


def lunar_mansion(sidereal_longitude_deg: float) -> dict:
    """Return the lunar mansion (Ch. 7) for a sidereal longitude in degrees.

    The caller supplies the Moon's sidereal longitude (runic.py stays
    ephemeris-free); this function maps it onto the 28 equal mansion
    segments anchored at Alcyone (see MANSION_ANCHOR_DEG).
    """
    try:
        lon = float(sidereal_longitude_deg) % 360.0
    except (TypeError, ValueError):
        raise CalculationError(
            f"invalid longitude '{sidereal_longitude_deg}': must be a "
            "number of sidereal degrees")
    corpus = _corpus()
    # epsilon keeps exact-boundary longitudes in the mansion they open
    # (float dust would otherwise drop them into the previous segment)
    index = int(((lon - MANSION_ANCHOR_DEG) % 360.0 + 1e-9)
                // MANSION_WIDTH_DEG)
    row = _mansion_row(corpus, index + 1)
    start = (MANSION_ANCHOR_DEG + index * MANSION_WIDTH_DEG) % 360.0
    end = (start + MANSION_WIDTH_DEG) % 360.0
    return {
        "sidereal_longitude": round(lon, 6),
        "mansion": row["number"],
        "rune": row["rune"],
        "northern_name": row["northern_name"],
        "star": row["star"],
        "designation": row["designation"],
        "segment": [round(start, 4), round(end, 4)],
        "method": "28 equal sidereal segments anchored at Alcyone "
                  "(declared modern convention)",
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    }


def lunar_mansions() -> list[dict]:
    """Return all 28 lunar mansions with their computed segment bounds."""
    corpus = _corpus()
    out = []
    for i in range(28):
        row = _mansion_row(corpus, i + 1)
        start = (MANSION_ANCHOR_DEG + i * MANSION_WIDTH_DEG) % 360.0
        end = (start + MANSION_WIDTH_DEG) % 360.0
        out.append({
            "mansion": row["number"],
            "rune": row["rune"],
            "northern_name": row["northern_name"],
            "star": row["star"],
            "designation": row["designation"],
            "segment": [round(start, 4), round(end, 4)],
        })
    return out


__all__ += ["MANSION_ANCHOR_DEG", "MANSION_WIDTH_DEG",
            "lunar_mansion", "lunar_mansions"]


# ---------------------------------------------------------------------------
# R07 — Twelve Palaces (App. 7) and Nine Worlds (Ch. 6): correspondence
# overlays (fixed tables, not computed quantities)
# ---------------------------------------------------------------------------

_OVERLAY = {
    "kind": "correspondence overlay",
    "source": "Pennick (2023)",
    "historical_claim": "modern synthesis",
}


def grimnismal_palace(sign: str) -> dict:
    """Return the Grímnismál palace (App. 7) for a zodiac sign.

    Fixed correspondence overlay: sign → palace, meaning of its name,
    ruling deity. Not a computed quantity.
    """
    corpus = _corpus()
    for row in corpus["palaces"]["palaces"]:
        if row["sign"].lower() == sign.strip().lower():
            return {"sign": row["sign"], "palace": row["palace"],
                    "meaning": row["meaning"], "deity": row["deity"],
                    **_OVERLAY}
    raise CalculationError(
        f"unknown zodiac sign '{sign}' for the palaces overlay")


def world_rune(world: str) -> dict:
    """Return the rune of a named world (Ch. 6 nine-worlds table)."""
    corpus = _corpus()
    for row in corpus["worlds"]["worlds"]:
        if row["world"].lower() == world.strip().lower():
            return {"world": row["world"], "rune": row["rune"],
                    **_OVERLAY}
    raise CalculationError(
        f"unknown world '{world}' for the nine-worlds overlay")


def nine_worlds() -> list[dict]:
    """Return the ordered Nine Worlds ↔ rune table (Ch. 6)."""
    corpus = _corpus()
    return [{"world": row["world"], "rune": row["rune"], **_OVERLAY}
            for row in corpus["worlds"]["worlds"]]


__all__ += ["grimnismal_palace", "world_rune", "nine_worlds"]


# ---------------------------------------------------------------------------
# R08 — Interpretive synthesis (Ch. 8 "Chronomantic Methods")
# ---------------------------------------------------------------------------

def _deity_quality(corpus: dict, deity_str: str):
    """Match an App. 1 deity string to a Ch. 8 planetary quality.

    Returns (matched_key, quality) or (None, None) when nothing in the
    book's quality table matches — the caller then omits the quality
    clause rather than inventing one.
    """
    import re
    import unicodedata
    qualities = corpus["interpretation"]["planetary_qualities"]

    def norm(s: str) -> str:
        s = unicodedata.normalize("NFKD", s)
        return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()

    tokens = re.findall(r"[A-Za-zÁáÉéÍíÓóÚúÝýÞþÐðÆæÖöÅå]+", deity_str or "")
    for tok in tokens:
        for key, quality in qualities.items():
            if norm(tok) == norm(key):
                return key, quality
    return None, None


def _rune_statement(corpus: dict, layer: str, rune: str,
                    deity_str: str | None) -> dict:
    """Build one interpretive statement for a rune-bearing layer."""
    adverbs = corpus["interpretation"]["rune_adverbs"]
    parts = [f"{layer} rune {rune}"]
    if deity_str:
        key, quality = _deity_quality(corpus, deity_str)
        if quality:
            parts.append(f"{key} ({quality})")
        else:
            parts.append(deity_str)
    adverb = adverbs.get(rune)
    if adverb:
        parts.append(f"expressed {adverb}")
    return {
        "layer": layer,
        "statement": " — ".join(parts) + ".",
        "kind": "interpretive",
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    }


def runic_reading(iso_datetime: str, longitude: float, timezone: str,
                  age_years: float | None = None,
                  moon_sidereal_longitude: float | None = None) -> dict:
    """Compose a structured runic reading for a moment (Ch. 8).

    `computation` holds the raw layer results (no interpretation);
    `interpretation.statements` holds deterministic symbolic statements,
    each tagged interpretive and drawn ONLY from the book's tables —
    anything the tables do not cover is omitted, never invented.
    """
    corpus = _corpus()
    naive = _parse_iso_datetime(iso_datetime)
    zone = _zone(timezone)
    if zone is None:
        raise CalculationError("timezone is required for a runic reading")
    aware = naive.replace(tzinfo=zone)

    comp: dict = {}
    comp["half_month"] = half_month_rune(naive.date().isoformat())
    lat = to_local_apparent_time(iso_datetime, longitude, timezone)
    comp["hour"] = runic_hour(lat["local_apparent_time"])
    comp["planetary_hour"] = planetary_hour(
        aware.strftime("%A"), aware.hour)
    comp["sele"] = sele(iso_datetime, longitude, timezone)["sele"]
    comp["tide"] = tide(f"{aware.hour:02d}:{aware.minute:02d}")
    comp["station"] = year_station(naive.date().isoformat())
    comp["weekday"] = weekday_rune(aware.strftime("%A"))
    comp["name"] = runic_name(iso_datetime, longitude, timezone)
    if age_years is not None:
        comp["life_period"] = life_period(age_years)
    if moon_sidereal_longitude is not None:
        comp["mansion"] = lunar_mansion(moon_sidereal_longitude)

    statements = []
    hm = comp["half_month"]
    statements.append(_rune_statement(
        corpus, "Half-month", hm["rune"],
        hm["correspondences"].get("deity")))
    hr = comp["hour"]
    statements.append(_rune_statement(
        corpus, "Hour", hr["rune"],
        hr["correspondences"].get("deity")))
    if comp["sele"]:
        statements.append({
            "layer": "Sele",
            "statement": "Sele — the hour-rune's deity correspondence "
                         "contains the planetary hour's deity: an "
                         "especially powerful coincidence (Ch. 4).",
            "kind": "interpretive",
            "source": "Pennick (2023)",
            "historical_claim": "modern synthesis",
        })
    st = comp["station"]
    statements.append({
        "layer": "Station",
        "statement": f"Station {st['name']} ({st['runes']}): "
                     f"{st['symbolic_event']}",
        "kind": "interpretive",
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    })
    wd = comp["weekday"]
    statements.append(_rune_statement(
        corpus, "Weekday", wd["rune"], wd["deity"]))
    if "life_period" in comp:
        lp = comp["life_period"]
        key, quality = _deity_quality(corpus, lp["deity"])
        text = f"Life period: {lp['deity']}"
        if quality:
            text += f" ({quality})"
        text += (f" — year {lp['years_elapsed']:.1f} of the reign, "
                 f"{lp['years_remaining']:.1f} years remaining.")
        statements.append({
            "layer": "Life period", "statement": text,
            "kind": "interpretive", "source": "Pennick (2023)",
            "historical_claim": "modern synthesis",
        })
    if "mansion" in comp:
        mn = comp["mansion"]
        adverb = corpus["interpretation"]["rune_adverbs"].get(mn["rune"])
        text = (f"Lunar mansion {mn['mansion']} ({mn['northern_name']}, "
                f"{mn['star']})")
        if adverb:
            # Ch. 8 adverbs cover the Elder Futhark only; other runes
            # are named without an adverb clause, never invented
            text += f" — expressed {adverb}"
        statements.append({
            "layer": "Lunar mansion", "statement": text + ".",
            "kind": "interpretive", "source": "Pennick (2023)",
            "historical_claim": "modern synthesis",
        })
    nm = comp["name"]
    statements.append({
        "layer": "Runic name",
        "statement": f"Runic-name pair {nm['pair']}: the book's rendered "
                     "names (Kenneth, Ingrid, Darwin) are literary "
                     "wordplay on such pairs, not mechanical output.",
        "kind": "interpretive",
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    })

    return {
        "datetime": iso_datetime,
        "computation": comp,
        "interpretation": {
            "kind": "interpretive",
            "statements": statements,
            "source": "Pennick (2023)",
            "historical_claim": "modern synthesis",
        },
        "source": "Pennick (2023)",
        "historical_claim": "modern synthesis",
    }


__all__ += ["runic_reading"]
