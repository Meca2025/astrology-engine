"""Electional astrology: choosing fortunate moments.

Scores candidate moments by the traditional considerations — the
Moon's state above all — and searches a window for the best hours.
Computation only; the choice of what to elect them *for* belongs to
the querent.
"""

import datetime as _dt
from zoneinfo import ZoneInfo

from .ephemeris import solar_day_events
from .legacy_astronomy import legacy_positions, legacy_request
from .models import CalculationError

CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
_DAY_RULERS = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
               4: "Venus", 5: "Saturn", 6: "Sun"}  # date.weekday() Mon=0
_MAJOR = (("conjunction", 0.0), ("sextile", 60.0), ("square", 90.0),
          ("trine", 120.0), ("opposition", 180.0))
_APPLY_ORB = 6.0  # degrees, for void-of-course and applying aspects
_COMBUST_ORB = 8.5
_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
_MOON_DIGNITY = {"Cancer": 3, "Taurus": 3, "Capricorn": -2, "Scorpio": -2}
_BENEFICS = {"Venus", "Jupiter"}
_MALEFICS = {"Mars", "Saturn"}
_CLASSICAL = ("Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _unwrap(delta: float) -> float:
    return (delta + 180.0) % 360.0 - 180.0


def moon_void_of_course(jd_ut: float) -> tuple[bool, list[dict]]:
    """True/False plus the Moon's applying major aspects.

    Samples the Moon's motion until it leaves its sign (classical
    planets as targets, linear interpolation between two ephemerides).
    An aspect counts as applying when its orb shrinks between samples —
    a modern, looser reading than Lilly, who required perfection
    before ingress.
    """
    now = legacy_positions(jd_ut, True)
    moon = now["Moon"]
    mlon = moon["longitude"] % 360.0
    speed = moon["speed"]  # deg/day, always positive for the Moon
    if speed <= 0:
        raise CalculationError("lunar ephemeris returned non-positive speed")
    boundary = (int(mlon // 30) + 1) * 30.0
    t_exit = (boundary - mlon) / speed  # days
    later = legacy_positions(jd_ut + t_exit, True)

    p0 = {b: (now[b]["longitude"] % 360.0) for b in _CLASSICAL}
    p1 = {b: (later[b]["longitude"] % 360.0) for b in _CLASSICAL}
    steps = max(8, int(t_exit * 8))  # ~3-hour sampling
    prev: dict[tuple[str, str], float] = {}
    applying: dict[tuple[str, str], float] = {}
    for i in range(steps + 1):
        f = i / steps
        ml = (mlon + speed * t_exit * f) % 360.0
        for b in _CLASSICAL:
            if b == "Moon":
                continue
            pl = (p0[b] + _unwrap(p1[b] - p0[b]) * f) % 360.0
            sep = _sep(ml, pl)
            for aname, target in _MAJOR:
                orb = abs(sep - target)
                key = (b, aname)
                if orb <= _APPLY_ORB and key in prev and orb < prev[key] - 1e-9:
                    applying[key] = min(applying.get(key, orb), orb)
                prev[key] = orb
    aspects = [{"planet": b, "aspect": a, "orb": round(o, 2)}
               for (b, a), o in sorted(applying.items(), key=lambda kv: kv[1])]
    return (not aspects), aspects


def planetary_hour(jd_ut: float, lat: float, lon: float,
                   timezone: str = "UTC") -> dict | None:
    """Planetary hour and day ruler for a moment, or None near the poles.

    The planetary day follows the LOCAL date — a Friday night in New
    York is still Venus's day even when UTC has turned Saturday.
    """
    try:
        req = legacy_request(jd_ut - 1.0)
        sunrise, sunset, next_sunrise = solar_day_events(req, lat, lon)
    except CalculationError:
        return None
    try:
        tz = ZoneInfo(timezone)
    except Exception as exc:
        raise CalculationError(f"unknown timezone '{timezone}'") from exc
    import swisseph as _swe
    y, mo, d, h, mi, _sec = _swe.jdut1_to_utc(jd_ut, 1)[:6]
    local = _dt.datetime(int(y), int(mo), int(d), int(h), int(mi),
                         tzinfo=_dt.timezone.utc).astimezone(tz)
    ruler_idx = CHALDEAN.index(_DAY_RULERS[local.weekday()])
    if sunrise <= jd_ut < sunset:
        idx = int((jd_ut - sunrise) / ((sunset - sunrise) / 12.0))
        return {"hour_ruler": CHALDEAN[(ruler_idx + idx) % 7],
                "day_ruler": CHALDEAN[ruler_idx], "sect": "day"}
    # night: find which sunset precedes us
    try:
        if jd_ut < sunrise:
            req = legacy_request(jd_ut - 2.0)
            _, sunset, next_sunrise = solar_day_events(req, lat, lon)
    except CalculationError:
        return None
    night_idx = (ruler_idx + 12) % 7
    idx = int((jd_ut - sunset) / ((next_sunrise - sunset) / 12.0))
    idx = max(0, min(11, idx))
    return {"hour_ruler": CHALDEAN[(night_idx + idx) % 7],
            "day_ruler": CHALDEAN[ruler_idx], "sect": "night"}


def _revjul(jd_ut: float) -> tuple[int, int, int]:
    import swisseph as _swe
    y, m, d, _h = _swe.revjul(jd_ut, _swe.GREG_CAL)
    return y, m, int(d)


def score_moment(jd_ut: float, lat: float, lon: float,
                 timezone: str = "UTC") -> dict:
    """Score one moment for electional work. Higher is better."""
    pos = legacy_positions(jd_ut, True)
    moon = pos["Moon"]
    sun = pos["Sun"]
    mlon = moon["longitude"] % 360.0
    slon = sun["longitude"] % 360.0
    moon_sign = _SIGNS[int(mlon // 30)]
    elong = (mlon - slon) % 360.0
    waxing = elong < 180.0
    combust = _sep(mlon, slon) <= _COMBUST_ORB
    void, applying = moon_void_of_course(jd_ut)
    mercury_rx = bool(pos["Mercury"]["retrograde"])

    score = 0
    notes: list[str] = []
    score += 2 if waxing else -1
    notes.append("Moon waxing" if waxing else "Moon waning")
    score += _MOON_DIGNITY.get(moon_sign, 0)
    if moon_sign in ("Cancer", "Taurus"):
        notes.append(f"Moon in {moon_sign} (domicile/exaltation)")
    elif moon_sign in ("Capricorn", "Scorpio"):
        notes.append(f"Moon in {moon_sign} (detriment/fall)")
    if void:
        score -= 4
        notes.append("Moon void of course")
    if combust:
        score -= 3
        notes.append("Moon combust")
    if mercury_rx:
        score -= 3
        notes.append("Mercury retrograde")
    for a in applying:
        if a["planet"] in _BENEFICS and a["aspect"] in (
                "conjunction", "sextile", "trine"):
            score += 2
            notes.append(f"Moon applying {a['aspect']} {a['planet']}")
        elif a["planet"] in _MALEFICS and a["aspect"] in (
                "square", "opposition"):
            score -= 3
            notes.append(f"Moon applying {a['aspect']} {a['planet']} — caution")
    hour = planetary_hour(jd_ut, lat, lon, timezone)
    if hour:
        if hour["hour_ruler"] in _BENEFICS:
            score += 1
            notes.append(f"hour of {hour['hour_ruler']}")
        elif hour["hour_ruler"] in _MALEFICS:
            score -= 1
            notes.append(f"hour of {hour['hour_ruler']} — caution")

    if score >= 4:
        verdict = "favorable"
    elif score >= 0:
        verdict = "mixed"
    else:
        verdict = "unfavorable"
    return {"moon_sign": moon_sign, "moon_waxing": waxing,
            "moon_void": void, "moon_combust": combust,
            "moon_applying": applying, "mercury_retrograde": mercury_rx,
            "planetary_hour": hour, "score": score,
            "verdict": verdict, "notes": notes}


def find_windows(from_jd_ut: float, to_jd_ut: float, lat: float, lon: float,
                 step_hours: float = 6.0, timezone: str = "UTC") -> list[dict]:
    """Score candidate moments across a window; best first."""
    if to_jd_ut < from_jd_ut:
        raise CalculationError("the search window ends before it begins")
    if step_hours <= 0:
        raise CalculationError("step_hours must be positive")
    try:
        tz = ZoneInfo(timezone)
    except Exception as exc:
        raise CalculationError(f"unknown timezone '{timezone}'") from exc
    import swisseph as _swe
    out: list[dict] = []
    jd = from_jd_ut
    while jd <= to_jd_ut:
        s = score_moment(jd, lat, lon, timezone)
        y, mo, d, h, mi, _sec = _swe.jdut1_to_utc(jd, 1)[:6]
        local = _dt.datetime(int(y), int(mo), int(d), int(h), int(mi),
                             tzinfo=_dt.timezone.utc).astimezone(tz)
        out.append({"datetime": local.isoformat(timespec="minutes"),
                    "score": s["score"], "verdict": s["verdict"],
                    "moon_sign": s["moon_sign"],
                    "notes": s["notes"]})
        jd += step_hours / 24.0
    return sorted(out, key=lambda w: (-w["score"], w["datetime"]))


__all__ = ["moon_void_of_course", "planetary_hour", "score_moment",
           "find_windows"]
