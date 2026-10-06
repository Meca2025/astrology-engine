"""Tibetan astrology (nag rtsis elemental tradition).

For a birth date: the element-animal year (Losar boundary approximated
by Chinese New Year — disclosed), the rabjung 60-year cycle position,
the year's mewa (nine magic-square numbers), the year's parkha (eight
trigrams), and the five personal forces: srog (life force), lus
(body), dbang-thang (power), rlung-ta (windhorse/luck), bla (soul).

Rules (see data/tibetan.json `method` for provenance):
- srog = the birth animal's fixed element
- lus = the year's element
- dbang-thang = the year's element (explicit textual rule)
- rlung-ta = fixed animal table (four independent sources agree)
- bla = the mother element of srog
Lineage variation is disclosed, not hidden.
"""

import datetime as _datetime
import json as _json
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError

_YEAR_ELEMENTS = ["Wood", "Fire", "Earth", "Iron", "Water"]
_RABJUNG_EPOCH = 1027  # first rabjung began in 1027 CE


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "tibetan.json").read_text(encoding="utf-8"))


def _lunar_year(greg: _datetime.date) -> tuple[int, str]:
    """Tibetan year number and its opening (CNY-approximated) date.

    Losar usually coincides with Chinese New Year but occasionally
    differs by days or weeks; callers flag the boundary window.
    """
    try:
        from lunardate import LunarDate
    except ImportError as exc:
        raise CalculationError(
            "lunardate is required for Tibetan year boundaries") from exc
    try:
        lunar = LunarDate.from_solar_date(greg.year, greg.month, greg.day)
        back = LunarDate(lunar.year, lunar.month, lunar.day,
                         lunar.is_leap_month).to_solar_date()
    except ValueError as exc:
        raise CalculationError(
            f"date {greg.isoformat()} is outside the supported range "
            f"(1900-2100)") from exc
    if back != greg:
        raise CalculationError(
            f"date {greg.isoformat()} is outside the supported range "
            f"(1900-2100)")
    cny = LunarDate(lunar.year, 1, 1).to_solar_date()
    return lunar.year, cny.isoformat()


def year_name(lunar_year: int) -> dict:
    """Element-animal year, rabjung position, mewa, parkha."""
    doc = _corpus()
    element = _YEAR_ELEMENTS[((lunar_year - 4) // 2) % 5]
    animal = doc["animals"][(lunar_year - 4) % 12]["tibetan"]
    mewa = doc["mewa"][((1 - lunar_year) % 9)]
    parkha_name = doc["parkha_year_order"][(lunar_year - 2025) % 8]
    parkha = next(p for p in doc["parkha"] if p["name"] == parkha_name)
    return {
        "tibetan_year": lunar_year,
        "element": element,
        "animal": animal,
        "name": f"{element} {animal}",
        "rabjung_cycle": (lunar_year - _RABJUNG_EPOCH) // 60 + 1,
        "rabjung_year": (lunar_year - _RABJUNG_EPOCH) % 60 + 1,
        "mewa": {"number": mewa["number"], "color": mewa["color"],
                 "element": mewa["element"]},
        "parkha": {"name": parkha["name"],
                   "direction": parkha["direction"],
                   "element": parkha["element"]},
    }


def forces(lunar_year: int) -> dict:
    """The five personal forces for a birth year."""
    doc = _corpus()
    yn = year_name(lunar_year)
    animal = yn["animal"]
    year_element = yn["element"]
    animal_element = doc["animals"][(lunar_year - 4) % 12]["element"]
    srog = animal_element
    return {
        "srog": {"element": srog,
                 "note": "life force — the birth animal's element"},
        "lus": {"element": year_element,
                "note": "body/health — the year's element"},
        "dbang_thang": {"element": year_element,
                        "note": "power — the element ruling the year"},
        "rlung_ta": {"element": doc["rlung_ta"][animal],
                     "note": "windhorse/luck — fixed by birth animal"},
        "bla": {"element": doc["mothers"][srog],
                "note": "soul — the mother element of srog"},
    }


def tibetan(iso_date: str) -> dict:
    """Full Tibetan astrology reading for a Gregorian ISO date."""
    try:
        greg = _datetime.date.fromisoformat(iso_date)
    except ValueError as exc:
        raise CalculationError(
            f"bad date '{iso_date}'; use ISO YYYY-MM-DD") from exc
    ly, year_starts = _lunar_year(greg)
    yn = year_name(ly)
    # Losar/CNY can diverge Jan-Mar; flag the uncertain window.
    uncertain = (greg.month, greg.day) >= (1, 21) and (greg.month, greg.day) <= (3, 15)
    yn.update({
        "date": iso_date,
        "year_starts": year_starts,
        "boundary_uncertain": uncertain,
        "losar_note": ("Year opens at Losar, approximated here by Chinese "
                       "New Year; Losar occasionally differs by days or "
                       "weeks (e.g., 2022, 2023) — boundary births should "
                       "be checked against a Tibetan almanac."),
        "forces": forces(ly),
        "method": _corpus()["method"],
        "kind": "computed",
    })
    return yn


__all__ = ["tibetan", "year_name", "forces"]
