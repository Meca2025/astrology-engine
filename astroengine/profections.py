"""Annual profections: the Hellenistic wheel of years.

Each year of life the Ascendant profects one whole sign; that sign's
traditional domicile lord becomes lord of the year. Whole-sign houses
are assumed throughout (stated, not hidden). Pure computation.
"""

import datetime as _datetime

from .models import CalculationError

_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
          "Pisces"]

# Traditional domicile rulers.
_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Traditional exaltations.
_EXALTED = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
    "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer",
    "Saturn": "Libra",
}


def _sign_of(longitude: float) -> str:
    return _SIGNS[int(longitude % 360.0 // 30)]


def _parse(iso: str) -> _datetime.date:
    try:
        return _datetime.date.fromisoformat(iso)
    except ValueError:
        raise CalculationError(f"invalid date '{iso}': use YYYY-MM-DD")


def essential_dignity(planet: str, sign: str) -> str:
    """Traditional essential dignity of a planet in a sign.

    Scores domicile, exaltation, detriment, and fall only; terms and
    faces are not scored, so some "peregrine" verdicts are partial.
    """
    if _RULERS.get(sign) == planet:
        return "domicile"
    if _EXALTED.get(planet) == sign:
        return "exaltation"
    # detriment: opposite the domicile signs; fall: opposite exaltation
    for s, ruler in _RULERS.items():
        if ruler == planet and _SIGNS[( _SIGNS.index(s) + 6) % 12] == sign:
            return "detriment"
    ex = _EXALTED.get(planet)
    if ex and _SIGNS[(_SIGNS.index(ex) + 6) % 12] == sign:
        return "fall"
    return "peregrine"


def profection(asc_longitude: float, birth_iso: str, target_iso: str,
               lord_longitude: float | None = None) -> dict:
    """Profect the Ascendant to the target date.

    Returns {age, profected_sign, profected_house, time_lord,
    lord_sign, lord_dignity}. Whole-sign houses assumed.
    """
    birth = _parse(birth_iso)
    target = _parse(target_iso)
    if target < birth:
        raise CalculationError("target date precedes the birth date")
    age = target.year - birth.year - (
        (target.month, target.day) < (birth.month, birth.day))
    asc_sign_idx = int(asc_longitude % 360.0 // 30)
    prof_idx = (asc_sign_idx + age) % 12
    prof_sign = _SIGNS[prof_idx]
    lord = _RULERS[prof_sign]
    lord_sign = _sign_of(lord_longitude) if lord_longitude is not None else None
    return {
        "age": age,
        "profected_sign": prof_sign,
        "profected_house": (age % 12) + 1,
        "time_lord": lord,
        "lord_sign": lord_sign,
        "lord_dignity": (essential_dignity(lord, lord_sign)
                         if lord_sign else None),
        "method": "annual profection, whole-sign houses assumed",
    }


__all__ = ["profection", "essential_dignity"]
