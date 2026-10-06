"""Single owner of mutable Swiss Ephemeris settings for new calculations."""

import threading
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import swisseph as swe

from .models import CalculationError, ChartRequest, EphemerisRequest
from .rules import load_rules

_LOCK = threading.RLock()


def zodiac_position(longitude: float) -> dict[str, Any]:
    longitude %= 360
    index = int(longitude // 30)
    return {"longitude": longitude, "sign_index": index,
            "sign": load_rules("profiles.json")["signs"][index],
            "degree_in_sign": longitude % 30}


def backend_name(flags: int) -> str:
    if flags & swe.FLG_JPLEPH:
        return "jpl"
    if flags & swe.FLG_SWIEPH:
        return "swiss"
    if flags & swe.FLG_MOSEPH:
        return "moshier"
    return "unspecified"


def _body(jd: float, body_id: int, flags: int) -> dict[str, Any]:
    values, actual = swe.calc_ut(jd, body_id, flags)
    if actual < 0 or not all(math.isfinite(value) for value in values):
        raise CalculationError("Ephemeris returned invalid body coordinates")
    return {**zodiac_position(values[0]), "latitude": values[1],
            "distance_au": values[2], "speed": values[3],
            "retrograde": values[3] < 0, "backend": backend_name(actual),
            "returned_flags": actual, "requested_flags": flags}


def _configure(request: EphemerisRequest) -> int:
    """Call only while the owning ephemeris lock is held."""
    try:
        valid_jd = (not isinstance(request.julian_day, bool)
                    and isinstance(request.julian_day, (float, int))
                    and math.isfinite(request.julian_day))
    except OverflowError:
        valid_jd = False
    if not valid_jd:
        raise CalculationError("Julian day must be a finite UT number")
    rules = load_rules("profiles.json")
    if request.zodiac not in ("tropical", "sidereal"):
        raise CalculationError(f"Unknown zodiac: {request.zodiac}")
    if not isinstance(request.ayanamsa, str) or request.ayanamsa not in rules["ayanamsas"]:
        raise CalculationError(f"Unknown ayanamsa: {request.ayanamsa}")
    path = Path(request.ephemeris_path).expanduser().resolve() if request.ephemeris_path else None
    if path is not None and not path.is_dir():
        raise CalculationError("Ephemeris path must be an existing directory")
    swe.set_ephe_path(str(path) if path else "")
    swe.set_sid_mode(getattr(swe, rules["ayanamsas"][request.ayanamsa]))
    return swe.FLG_SWIEPH | swe.FLG_SPEED | (
        swe.FLG_SIDEREAL if request.zodiac == "sidereal" else 0)


def positions_at_jd(request: EphemerisRequest, required: dict[str, str],
                    optional: dict[str, str] | None = None) -> dict[str, Any]:
    """Calculate a named registry; optional Swiss errors remain explicit."""
    positions: dict[str, Any] = {}
    unavailable: dict[str, str] = {}
    with _LOCK:
        try:
            flags = _configure(request)
            for name, identifier in required.items():
                try:
                    positions[name] = _body(request.julian_day, getattr(swe, identifier), flags)
                except swe.Error as exc:
                    raise CalculationError(f"Required body {name} unavailable: {exc}") from exc
            for name, identifier in (optional or {}).items():
                try:
                    positions[name] = _body(request.julian_day, getattr(swe, identifier), flags)
                except swe.Error as exc:
                    unavailable[name] = str(exc)
        except swe.Error as exc:
            raise CalculationError(f"Swiss Ephemeris settings failed: {exc}") from exc
    return {"positions": positions, "unavailable": unavailable,
            "provenance": {"swiss_ephemeris_version": swe.version,
                           "requested_backend": "swiss", "requested_flags": flags,
                           "backends": sorted({p["backend"] for p in positions.values()}),
                           "zodiac": request.zodiac, "ayanamsa": request.ayanamsa,
                           "julian_day_ut": request.julian_day}}


def houses_at_jd(request: EphemerisRequest, latitude: float, longitude: float,
                 system: bytes = b"P") -> tuple[list[float], float, float]:
    """Twelve requested cusps or an error; never a substitute house system."""
    from .inputs import validate_coordinates
    validate_coordinates(latitude, longitude)
    codes = {code.encode("ascii") for code in load_rules("profiles.json")["houses"].values()}
    codes.update(code.encode("ascii") for code in load_rules("legacy_astronomy.json")["house_aliases"])
    if not isinstance(system, bytes) or system not in codes:
        raise CalculationError("Unknown twelve-house system code")
    with _LOCK:
        try:
            flags = _configure(request) & swe.FLG_SIDEREAL
            cusps, angles = swe.houses_ex(request.julian_day, latitude, longitude, system, flags)
        except swe.Error as exc:
            raise CalculationError(f"House calculation failed ({system.decode('ascii')}): {exc}") from exc
    if len(cusps) != 12 or not all(math.isfinite(value) for value in (*cusps, *angles)):
        raise CalculationError("House calculation returned invalid cusps or angles")
    return list(cusps), angles[0], angles[1]


def solar_day_events(request: EphemerisRequest, latitude: float,
                     longitude: float) -> tuple[float, float, float]:
    """Legacy UT search window with explicit missing-event failures."""
    from .inputs import validate_coordinates
    validate_coordinates(latitude, longitude)
    rules = load_rules("legacy_astronomy.json")["solar_events"]
    events: list[float] = []
    search = request.julian_day
    with _LOCK:
        try:
            _configure(request)
            for label in rules["sequence"]:
                mode = getattr(swe, rules["modes"][label]) | swe.BIT_DISC_CENTER
                status, times = swe.rise_trans(search, swe.SUN, mode, (longitude, latitude, 0),
                                              flags=swe.FLG_SWIEPH)
                if status != 0:
                    raise CalculationError(f"Solar {label} unavailable at this location (status {status})")
                event = times[0]
                if not math.isfinite(event) or event <= search:
                    raise CalculationError(f"Solar {label} returned an invalid event time")
                events.append(event)
                search = event + rules["search_gap_days"]
        except swe.Error as exc:
            raise CalculationError(f"Solar rise/set calculation failed: {exc}") from exc
    return events[0], events[1], events[2]


def _houses(jd: float, request: ChartRequest, flags: int,
            rules: dict[str, Any]) -> dict[str, Any] | None:
    if request.time is None:
        return None
    code = rules["houses"][request.house_system].encode("ascii")
    house_flags = flags & swe.FLG_SIDEREAL
    cusps, angles = swe.houses_ex(jd, request.latitude, request.longitude,
                                code, house_flags)
    return {"system": request.house_system, "cusps": list(cusps),
            "ascendant": angles[0], "midheaven": angles[1]}


def calculate(utc: datetime, request: ChartRequest) -> dict[str, Any]:
    rules = load_rules("profiles.json")
    hour = (utc.hour + utc.minute / 60 + utc.second / 3600
            + utc.microsecond / 3_600_000_000)
    jd = swe.julday(utc.year, utc.month, utc.day, hour)
    path = Path(request.ephemeris_path).expanduser().resolve() if request.ephemeris_path else None
    if path is not None and not path.is_dir():
        raise CalculationError("Ephemeris path must be an existing directory")
    with _LOCK:
        try:
            swe.set_ephe_path(str(path) if path else "")
            swe.set_sid_mode(getattr(swe, rules["ayanamsas"][request.ayanamsa]))
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            if request.zodiac == "sidereal":
                flags |= swe.FLG_SIDEREAL
            positions = {name: _body(jd, getattr(swe, identifier), flags)
                         for name, identifier in rules["bodies"].items()}
            positions["North Node"] = _body(jd, getattr(swe, rules["nodes"][request.node_type]), flags)
            north = positions["North Node"]
            positions["South Node"] = {**north, **zodiac_position(north["longitude"] + 180),
                                       "latitude": -north["latitude"]}
            houses = _houses(jd, request, flags, rules)
            ayanamsa = swe.get_ayanamsa_ex_ut(jd, swe.FLG_SWIEPH)[1] if request.zodiac == "sidereal" else None
        except swe.Error as exc:
            raise CalculationError(f"Swiss Ephemeris calculation failed: {exc}") from exc
    return {"julian_day_ut": jd, "positions": positions, "houses": houses,
            "ayanamsa_degrees": ayanamsa,
            "provenance": {"swiss_ephemeris_version": swe.version,
                           "requested_backend": "swiss", "requested_flags": flags,
                           "backends": sorted({p["backend"] for p in positions.values()}),
                           "rule_version": rules["version"],
                           "time_scale": "UTC supplied as UT; Swiss Ephemeris delta-T model"}}


def equatorial_positions(jd: float, request: ChartRequest) -> dict[str, Any]:
    """Internal location-domain snapshot; equatorial frame is zodiac-independent."""
    rules = load_rules('profiles.json')
    path = Path(request.ephemeris_path).expanduser().resolve() if request.ephemeris_path else None
    with _LOCK:
        try:
            swe.set_ephe_path(str(path) if path else '')
            flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
            positions = {}
            for name, identifier in rules['bodies'].items():
                values, actual = swe.calc_ut(jd, getattr(swe, identifier), flags)
                positions[name] = {'right_ascension': values[0], 'declination': values[1],
                                   'backend': backend_name(actual), 'returned_flags': actual}
            sidereal_time = swe.sidtime(jd) * 15
        except swe.Error as exc:
            raise CalculationError(f'Equatorial calculation failed: {exc}') from exc
    return {'positions': positions, 'greenwich_sidereal_degrees': sidereal_time}
