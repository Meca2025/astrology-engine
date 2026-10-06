"""Solar arc directions: a degree a year, carried across the chart.

The arc is the secondary-progressed Sun's motion (day-for-a-year)
between birth and the target date; every natal longitude advances by
that arc. Pure computation — no interpretation.
"""

from .houses import house_cusps
from .legacy_astronomy import legacy_positions
from .models import CalculationError

_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
           "Saturn", "Uranus", "Neptune", "Pluto")

# (name, target separation); squares and trines count both flanks.
_ASPECTS = (
    ("conjunction", 0.0),
    ("sextile", 60.0),
    ("square", 90.0),
    ("trine", 120.0),
    ("opposition", 180.0),
)


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def solar_arc(natal_jd_ut: float, target_jd_ut: float,
              lat: float | None = None, lon: float | None = None,
              houses: str = "placidus") -> dict:
    """Direct the chart by the solar arc to the target date.

    Returns {arc, years, directed: {body: longitude}, directed_asc,
    directed_mc}. Raises CalculationError if the target precedes birth.
    """
    if target_jd_ut < natal_jd_ut:
        raise CalculationError("target date precedes the birth date")
    natal = legacy_positions(natal_jd_ut, True)
    years = (target_jd_ut - natal_jd_ut) / 365.25
    prog = legacy_positions(natal_jd_ut + years, True)  # day-for-a-year
    arc = ((prog["Sun"]["longitude"] - natal["Sun"]["longitude"])
           % 360.0)
    directed: dict[str, float] = {}
    for body in _BODIES:
        p = natal.get(body) or {}
        if p.get("longitude") is not None:
            directed[body] = (p["longitude"] + arc) % 360.0
    directed_asc = directed_mc = None
    if lat is not None and lon is not None:
        _, asc, mc = house_cusps(natal_jd_ut, lat, lon, houses)
        directed_asc = (asc + arc) % 360.0
        directed_mc = (mc + arc) % 360.0
    return {
        "arc": arc,
        "years": years,
        "directed": directed,
        "directed_asc": directed_asc,
        "directed_mc": directed_mc,
        "natal_jd_ut": natal_jd_ut,
        "target_jd_ut": target_jd_ut,
    }


def directed_aspects(directed: dict[str, float],
                     natal: dict[str, float],
                     orb: float = 1.0,
                     arc: float | None = None) -> list[dict]:
    """Directed-to-natal aspects within orb, tightest first.

    natal: {body: longitude}. Applying = the orb shrinks as the arc
    grows (directions move forward ~1°/year). When arc is given, the
    trivial identity (a body aspecting itself before it has moved) is
    suppressed — but genuine same-body hits (e.g. directed Sun square
    natal Sun at arc 90°) are reported. At exact perfection an aspect
    is labeled separating: the peak is past.
    """
    trivial_sep = _sep(arc, 0.0) if arc is not None else None
    hits: list[dict] = []
    for dbody, dlon in directed.items():
        for nbody, nlon in natal.items():
            sep = _sep(dlon, nlon)
            for name, target in _ASPECTS:
                distance = abs(sep - target)
                if distance <= orb:
                    if (trivial_sep is not None and dbody == nbody
                            and name == "conjunction"
                            and abs(distance - trivial_sep) < 1e-9):
                        continue  # nothing has moved yet
                    # nudge the arc forward: shrinking orb => applying
                    ahead = _sep((dlon + 0.1) % 360.0, nlon)
                    hits.append({
                        "directed": dbody,
                        "natal": nbody,
                        "aspect": name,
                        "orb": round(distance, 3),
                        "applying": abs(ahead - target) < distance,
                        "exact": distance < 0.1,
                    })
    hits.sort(key=lambda h: h["orb"])
    return hits


__all__ = ["solar_arc", "directed_aspects"]
