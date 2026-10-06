"""Transit watch: a calendar of coming transits to natal points.

Daily scan for orb minima between the outer transiting planets and
the natal planets + angles, refined to the exact day. Pure
computation — the calendar reminders themselves are a separate,
user-confirmed step.
"""

from .houses import house_cusps
from .legacy_astronomy import legacy_positions
from .models import CalculationError

# The slow movers whose transits mark the years.
TRANSIT_BODIES = ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
_NATAL_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
                 "Saturn", "Uranus", "Neptune", "Pluto")

_ASPECTS = (
    ("conjunction", 0.0),
    ("opposition", 180.0),
    ("square", 90.0),
    ("trine", 120.0),
)


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _lon_at(jd_ut: float, body: str) -> float:
    return legacy_positions(jd_ut, True)[body]["longitude"] % 360.0


def _refine(tbody: str, nlon: float, target: float,
            lo: float, hi: float) -> tuple[float, float]:
    """Ternary search for the orb minimum on [lo, hi]; returns (jd, orb)."""
    for _ in range(40):
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        o1 = abs(_sep(_lon_at(m1, tbody), nlon) - target)
        o2 = abs(_sep(_lon_at(m2, tbody), nlon) - target)
        if o1 < o2:
            hi = m2
        else:
            lo = m1
    jd = (lo + hi) / 2.0
    return jd, abs(_sep(_lon_at(jd, tbody), nlon) - target)


def _julian_to_ymd(jd_ut: float) -> tuple[int, int, int]:
    import swisseph as _swe
    y, m, d, _h = _swe.revjul(jd_ut, _swe.GREG_CAL)
    return y, m, int(d)


def upcoming_transits(natal_jd_ut: float, from_jd_ut: float,
                      to_jd_ut: float, lat: float | None = None,
                      lon: float | None = None,
                      orb: float = 1.0) -> list[dict]:
    """Scan [from_jd_ut, to_jd_ut] for outer-planet transits to the
    natal chart. Returns [{date, transit_body, aspect, natal_point,
    orb}] sorted by date. Retrograde triple hits are each reported."""
    if to_jd_ut < from_jd_ut:
        raise CalculationError("the watch window ends before it begins")
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

    start_day = int(from_jd_ut)
    end_day = int(to_jd_ut) + 1
    # orb series per (tbody, point, aspect)
    series: dict[tuple[str, str, str], list[float]] = {}
    for day in range(start_day, end_day + 1):
        jd = day + 0.5  # noon UT
        tpos = legacy_positions(jd, True)
        for tbody in TRANSIT_BODIES:
            tlon = (tpos.get(tbody) or {}).get("longitude")
            if tlon is None:
                continue
            tlon %= 360.0
            for pname, plon in points.items():
                # same-body pairs are headline transits (e.g. Saturn return)
                sep = _sep(tlon, plon)
                for aname, target in _ASPECTS:
                    key = (tbody, pname, aname)
                    series.setdefault(key, []).append(
                        abs(sep - target))

    hits: list[dict] = []
    ndays = end_day - start_day + 1
    for (tbody, pname, aname), orbs in series.items():
        target = dict(_ASPECTS)[aname]
        nlon = points[pname]
        for i in range(1, ndays - 1):
            if (orbs[i] <= orb and orbs[i] <= orbs[i - 1]
                    and orbs[i] <= orbs[i + 1]
                    and (orbs[i] < orbs[i - 1] or orbs[i] < orbs[i + 1])):
                jd, orb_min = _refine(tbody, nlon, target,
                                      start_day + i - 1.5,
                                      start_day + i + 1.5)
                if from_jd_ut - 1 <= jd <= to_jd_ut + 1 and orb_min <= orb:
                    y, m, d = _julian_to_ymd(jd)
                    hits.append({
                        "date": f"{y:04d}-{m:02d}-{d:02d}",
                        "transit_body": tbody,
                        "aspect": aname,
                        "natal_point": pname,
                        "orb": round(orb_min, 3),
                    })
    # dedupe near-identical refinements, keep the tightest
    deduped: dict[tuple[str, str, str, str], dict] = {}
    for h in hits:
        key = (h["date"], h["transit_body"], h["aspect"], h["natal_point"])
        if key not in deduped or h["orb"] < deduped[key]["orb"]:
            deduped[key] = h
    return sorted(deduped.values(), key=lambda h: h["date"])


__all__ = ["TRANSIT_BODIES", "upcoming_transits"]
