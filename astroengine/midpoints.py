"""Midpoints: the secret chords between every two planets.

A midpoint is the shorter-arc center of a planetary pair; a third
planet or angle standing on that midpoint (either end of its axis)
activates the pair's combined meaning. Pure arithmetic on longitudes.
"""

from .houses import house_cusps
from .legacy_astronomy import legacy_positions
from .models import CalculationError

_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
           "Saturn", "Uranus", "Neptune", "Pluto")


def midpoint(lon_a: float, lon_b: float) -> float:
    """Shorter-arc midpoint of two longitudes, in degrees."""
    diff = (lon_b - lon_a) % 360.0
    mid = (lon_a + diff / 2.0) % 360.0
    if diff > 180.0:
        mid = (mid + 180.0) % 360.0
    return mid


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def all_midpoints(positions: dict[str, float]) -> list[dict]:
    """Every pair's midpoint, sorted by longitude."""
    names = [b for b in _BODIES if b in positions]
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            out.append({"pair": f"{a}/{b}",
                        "longitude": round(midpoint(positions[a],
                                                    positions[b]), 3)})
    return sorted(out, key=lambda m: m["longitude"])


def midpoint_hits(natal_jd_ut: float, lat: float | None = None,
                  lon: float | None = None, orb: float = 1.0) -> list[dict]:
    """Planets and angles standing on natal midpoints (either axis end)."""
    if orb <= 0:
        raise CalculationError("orb must be positive")
    natal = legacy_positions(natal_jd_ut, True)
    points: dict[str, float] = {}
    for body in _BODIES:
        p = natal.get(body) or {}
        if p.get("longitude") is not None:
            points[body] = p["longitude"] % 360.0
    if lat is not None and lon is not None:
        _, asc, mc = house_cusps(natal_jd_ut, lat, lon, "placidus")
        points["ASC"] = asc % 360.0
        points["MC"] = mc % 360.0
    lons = {k: v for k, v in points.items()}
    hits = []
    for m in all_midpoints(lons):
        a, b = m["pair"].split("/")
        for pname, plon in points.items():
            if pname in (a, b):
                continue
            d = min(_sep(plon, m["longitude"]),
                    _sep(plon, (m["longitude"] + 180.0) % 360.0))
            if d <= orb:
                hits.append({"pair": m["pair"],
                             "midpoint": m["longitude"],
                             "activated_by": pname,
                             "orb": round(d, 3)})
    return sorted(hits, key=lambda h: h["orb"])


__all__ = ["midpoint", "all_midpoints", "midpoint_hits"]
