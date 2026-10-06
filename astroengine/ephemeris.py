"""Single owner of mutable Swiss Ephemeris settings for new calculations."""

import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import swisseph as swe

from .models import CalculationError, ChartRequest
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
    return {**zodiac_position(values[0]), "latitude": values[1],
            "distance_au": values[2], "speed": values[3],
            "retrograde": values[3] < 0, "backend": backend_name(actual),
            "returned_flags": actual}


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
