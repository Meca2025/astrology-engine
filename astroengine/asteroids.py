"""Asteroids: Chiron and the grain-mother's kin.

Positions come only from the Swiss Ephemeris asteroid files
(se00001s.se1 …). This environment does not ship them, and the
Moshier fallback knows no asteroids at all — so when the files are
absent the module says so plainly, naming the missing file, instead
of inventing positions. Honesty over completeness.
"""

import swisseph as swe

from .models import CalculationError

ASTEROIDS = (
    ("Chiron", 2060, "the wound that teaches; the maverick healer"),
    ("Ceres", 1, "the grain-mother; nurture, sustenance, loss"),
    ("Pallas", 2, "the strategist; wisdom, craft, pattern-mind"),
    ("Juno", 3, "the partner; covenant, marriage, right relation"),
    ("Vesta", 4, "the hearth-keeper; devotion, focus, the sacred flame"),
)


def asteroid_positions(jd_ut: float) -> dict:
    """{"positions": {name: {longitude, latitude, speed, retrograde,
    meaning}}, "unavailable": {name: reason}} for the five asteroids.

    Raises CalculationError naming the missing .se1 files when none of
    the five resolve — never invented positions.
    """
    positions: dict[str, dict] = {}
    unavailable: dict[str, str] = {}
    for name, num, meaning in ASTEROIDS:
        try:
            xx, _flags = swe.calc_ut(jd_ut, swe.AST_OFFSET + num,
                                     swe.FLG_SWIEPH)
        except swe.Error as exc:
            unavailable[name] = str(exc)
            continue
        positions[name] = {
            "longitude": xx[0] % 360.0,
            "latitude": xx[1],
            "speed": xx[3],
            "retrograde": xx[3] < 0,
            "meaning": meaning,
        }
    if not positions and unavailable:
        raise CalculationError(
            "no asteroid ephemeris available: "
            + "; ".join(f"{n} ({r})" for n, r in unavailable.items()))
    return {"positions": positions, "unavailable": unavailable}


__all__ = ["ASTEROIDS", "asteroid_positions"]
