"""Draconic charts: the soul-chart beneath the tropical one.

The draconic zodiac sets 0° Aries at the natal north node, so the
whole chart is rotated by the node's longitude. Here the zero-point
is the engine's N.Node (true node) — disclosed, since classical
draconic work often prefers the mean node. Contacts between the two
zodiacs show where the soul's intent touches the personality.
"""

from .houses import house_cusps
from .legacy_astronomy import legacy_positions
from .models import CalculationError

_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
           "Saturn", "Uranus", "Neptune", "Pluto")


def draconic_longitude(tropical_lon: float, node_lon: float) -> float:
    """Rotate one longitude into the draconic zodiac."""
    return (tropical_lon - node_lon) % 360.0


def draconic_chart(natal_jd_ut: float, lat: float | None = None,
                   lon: float | None = None) -> dict:
    """{body: draconic longitude} plus draconic ASC/MC (the tropical
    angles rotated by the node offset) and the node longitude used."""
    natal = legacy_positions(natal_jd_ut, True)
    node_entry = natal.get("N.Node") or {}
    if node_entry.get("longitude") is None:
        raise CalculationError("north node unavailable for draconic work")
    node_lon = node_entry["longitude"] % 360.0
    out: dict[str, float] = {}
    for body in _BODIES:
        p = natal.get(body) or {}
        if p.get("longitude") is not None:
            out[body] = round(draconic_longitude(p["longitude"] % 360.0,
                                                 node_lon), 3)
    angles: dict[str, float] = {}
    if lat is not None and lon is not None:
        _, asc, mc = house_cusps(natal_jd_ut, lat, lon, "placidus")
        angles["ASC"] = round(draconic_longitude(asc % 360.0, node_lon), 3)
        angles["MC"] = round(draconic_longitude(mc % 360.0, node_lon), 3)
    return {"positions": out, "angles": angles, "node_longitude": round(node_lon, 3),
            "node_kind": "true node (engine N.Node)"}


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def draconic_contacts(natal_jd_ut: float, lat: float | None = None,
                      lon: float | None = None, orb: float = 1.0) -> list[dict]:
    """Conjunctions between draconic positions and natal positions —
    the soul touching the personality. Sorted tightest first."""
    if orb <= 0:
        raise CalculationError("orb must be positive")
    chart = draconic_chart(natal_jd_ut, lat, lon)
    natal = legacy_positions(natal_jd_ut, True)
    tropical: dict[str, float] = {}
    for body in _BODIES:
        p = natal.get(body) or {}
        if p.get("longitude") is not None:
            tropical[body] = p["longitude"] % 360.0
    if lat is not None and lon is not None:
        _, asc, mc = house_cusps(natal_jd_ut, lat, lon, "placidus")
        tropical["ASC"] = asc % 360.0
        tropical["MC"] = mc % 360.0
    draconic_points = dict(chart["positions"])
    draconic_points.update(chart["angles"])
    hits = []
    for dname, dlon in draconic_points.items():
        for tname, tlon in tropical.items():
            d = _sep(dlon, tlon)
            if d <= orb:
                hits.append({"draconic": dname, "natal": tname,
                             "orb": round(d, 3)})
    return sorted(hits, key=lambda h: h["orb"])


__all__ = ["draconic_longitude", "draconic_chart", "draconic_contacts"]
