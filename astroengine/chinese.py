"""Chinese zodiac astrology: stem-branch year, NaYin, allies, clashes.

The year's ganzhi (heavenly stem + earthly branch) is deterministic
calendar math: stem = (lunar_year - 4) mod 10, branch =
(lunar_year - 4) mod 12, anchored so 1984 = Jia-Zi. The zodiac year
begins at Lunar New Year (via the lunardate package, cross-checked
against published dates), not January 1. NaYin follows the
traditional Sixty Jiazi verse in ganzhi order. Animal keywords are
interpretive; everything else is computation.
"""

import datetime as _datetime
import json as _json
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError

try:
    from lunardate import LunarDate as _LunarDate
    _from_solar = _LunarDate.from_solar_date
    _to_solar = _LunarDate.to_solar_date
except ImportError:  # pragma: no cover
    _LunarDate = None


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "chinese_zodiac.json").read_text(encoding="utf-8"))


def _lunar_year(greg: _datetime.date) -> int:
    """The Chinese lunar year a Gregorian date falls in."""
    if _LunarDate is None:
        raise CalculationError("lunardate is required for Chinese zodiac "
                               "dates; pip install lunardate")
    try:
        lunar = _from_solar(greg.year, greg.month, greg.day)
    except ValueError as exc:
        raise CalculationError(
            f"date {greg.isoformat()} is outside the supported Chinese "
            f"calendar range (1900-2100): {exc}") from exc
    # lunardate clamps out-of-range dates instead of raising; verify
    # the round trip so a clamped date can never pass silently
    try:
        back = _LunarDate(lunar.year, lunar.month, lunar.day,
                          lunar.is_leap_month).to_solar_date()
    except ValueError as exc:
        raise CalculationError(
            f"date {greg.isoformat()} is outside the supported Chinese "
            f"calendar range (1900-2100)") from exc
    if back != greg:
        raise CalculationError(
            f"date {greg.isoformat()} is outside the supported Chinese "
            f"calendar range (1900-2100)")
    return lunar.year


def year_pillar(lunar_year: int) -> dict:
    """Stem/branch/NaYin for a lunar year. 1984 -> Jia-Zi by anchor."""
    doc = _corpus()
    stem_idx = (lunar_year - 4) % 10
    branch_idx = (lunar_year - 4) % 12
    ganzhi_idx = (lunar_year - 4) % 60
    stem = doc["stems"][stem_idx]
    branch = doc["branches"][branch_idx]
    animal = branch["animal"]
    trine = next(t for t in doc["trines"] if animal in t)
    return {
        "lunar_year": lunar_year,
        "stem": stem["name"],
        "stem_pinyin": stem["pinyin"],
        "stem_element": stem["element"],
        "branch": branch["name"],
        "animal": animal,
        "animal_element": branch["element"],
        "yin_yang": branch["yin_yang"],
        "ganzhi": f"{stem['name']}-{branch['name']}",
        "nayin": doc["nayin"][ganzhi_idx // 2],
        "trine_allies": [a for a in trine if a != animal],
        "secret_friend": doc["secret_friends"][animal],
        "clash": doc["clashes"][animal],
        "animal_keywords": branch["keywords"],
    }


def zodiac(iso_date: str) -> dict:
    """Full Chinese zodiac reading for a Gregorian ISO date."""
    try:
        greg = _datetime.date.fromisoformat(iso_date)
    except ValueError as exc:
        raise CalculationError(
            f"bad date '{iso_date}'; use ISO YYYY-MM-DD") from exc
    ly = _lunar_year(greg)
    cny = _LunarDate(ly, 1, 1).to_solar_date()
    pillar = year_pillar(ly)
    pillar.update({
        "date": iso_date,
        "year_starts": cny.isoformat(),  # Lunar New Year opening this year
        "kind": "computed",
        "note": ("Animal keywords are interpretive; stem/branch/NaYin/"
                 "allies/clash are deterministic calendar math."),
    })
    return pillar


__all__ = ["zodiac", "year_pillar"]
