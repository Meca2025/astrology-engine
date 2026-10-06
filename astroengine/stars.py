"""Fixed stars: the bright ones and their contacts to the chart.

J2000 ecliptic positions from data/fixed_stars.json (Swiss Ephemeris
sefstars.txt, Moshier data), precessed to the date with the IAU 1976
theory (Meeus ch. 21). Proper motion and nutation are not applied —
sub-arcminute at these orbs, and disclosed in the data file.
"""

import json
import math
import os
from functools import lru_cache

from .houses import house_cusps
from .legacy_astronomy import legacy_positions
from .models import CalculationError

_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "data", "fixed_stars.json")
_J2000 = 2451545.0
_NATAL_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
                 "Saturn", "Uranus", "Neptune", "Pluto")


@lru_cache(maxsize=1)
def load_stars() -> list[dict]:
    with open(_DATA, encoding="utf-8") as f:
        doc = json.load(f)
    stars = doc["stars"]
    for s in stars:
        for k in ("name", "constellation", "j2000_lon", "j2000_lat",
                  "magnitude", "nature", "meaning"):
            if k not in s:
                raise CalculationError(f"fixed star record missing '{k}'")
    return stars


def _precess_ecliptic(lon_deg: float, lat_deg: float,
                      jd_to: float) -> tuple[float, float]:
    """Precess J2000 mean ecliptic coords to mean ecliptic of jd_to."""
    t = (jd_to - _J2000) / 36525.0
    # ecliptic -> equatorial (J2000 obliquity)
    eps0 = math.radians(23.4392911)
    lon, lat = math.radians(lon_deg), math.radians(lat_deg)
    xq = math.cos(lat) * math.cos(lon)
    yq = math.cos(lat) * math.sin(lon) * math.cos(eps0) - math.sin(lat) * math.sin(eps0)
    zq = math.cos(lat) * math.sin(lon) * math.sin(eps0) + math.sin(lat) * math.cos(eps0)
    ra0, dec0 = math.atan2(yq, xq), math.asin(max(-1.0, min(1.0, zq)))
    # IAU 1976 precession angles, degrees -> radians
    zeta = math.radians((2306.2181 * t + 0.30188 * t * t + 0.017998 * t**3) / 3600.0)
    z = math.radians((2306.2181 * t + 1.09468 * t * t + 0.018203 * t**3) / 3600.0)
    theta = math.radians((2004.3109 * t - 0.42665 * t * t - 0.041833 * t**3) / 3600.0)
    a = math.cos(dec0) * math.sin(ra0 + zeta)
    b = (math.cos(theta) * math.cos(dec0) * math.cos(ra0 + zeta)
         - math.sin(theta) * math.sin(dec0))
    c = (math.sin(theta) * math.cos(dec0) * math.cos(ra0 + zeta)
         + math.cos(theta) * math.sin(dec0))
    ra = math.atan2(a, b) + z
    dec = math.asin(max(-1.0, min(1.0, c)))
    # equatorial -> ecliptic of date
    eps = math.radians(23.4392911 - 0.0130042 * t - 0.00000016 * t * t
                       + 0.000000504 * t**3)
    xe = math.cos(dec) * math.cos(ra)
    ye = math.cos(dec) * math.sin(ra) * math.cos(eps) + math.sin(dec) * math.sin(eps)
    ze = -math.cos(dec) * math.sin(ra) * math.sin(eps) + math.sin(dec) * math.cos(eps)
    return math.degrees(math.atan2(ye, xe)) % 360.0, math.degrees(math.asin(max(-1.0, min(1.0, ze))))


def star_longitude(name: str, jd_ut: float) -> float:
    """Precessed ecliptic longitude of a named star at jd_ut."""
    for s in load_stars():
        if s["name"].lower() == name.lower():
            lon, _lat = _precess_ecliptic(s["j2000_lon"], s["j2000_lat"], jd_ut)
            return lon
    raise CalculationError(f"unknown fixed star '{name}'")


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def star_hits(natal_jd_ut: float, lat: float | None = None,
              lon: float | None = None, orb: float = 1.0) -> list[dict]:
    """Conjunctions of the bright stars to natal planets and angles.

    Stars are precessed to the birth date; only longitude is compared
    (traditional practice). ASC/MC are included as contact points, so a
    star conjunct an angle is reported as a hit on that angle.
    """
    if orb <= 0:
        raise CalculationError("orb must be positive")
    natal = legacy_positions(natal_jd_ut, True)
    points: dict[str, float] = {}
    for body in _NATAL_BODIES:
        p = natal.get(body) or {}
        if p.get("longitude") is not None:
            points[body] = p["longitude"] % 360.0
    if lat is not None and lon is not None:
        _, asc, mc = house_cusps(natal_jd_ut, lat, lon, "placidus")
        points["ASC"] = asc % 360.0
        points["MC"] = mc % 360.0
    hits = []
    for s in load_stars():
        slon, _ = _precess_ecliptic(s["j2000_lon"], s["j2000_lat"], natal_jd_ut)
        for pname, plon in points.items():
            d = _sep(slon, plon)
            if d <= orb:
                hits.append({"star": s["name"],
                             "constellation": s["constellation"],
                             "nature": s["nature"],
                             "meaning": s["meaning"],
                             "magnitude": s.get("magnitude"),
                             "star_longitude": round(slon, 3),
                             "natal_point": pname,
                             "orb": round(d, 3)})
    return sorted(hits, key=lambda h: h["orb"])


__all__ = ["load_stars", "star_longitude", "star_hits"]
