"""Sólrún's scrutiny of R05: zodiac, weekday, life-periods, Metonic cycle.

Fixtures from Pennick App. 4/5 and Ch. 6. The Metonic gate is verified two
ways: the 19-year periodicity property, and a real ephemeris check that
full moons recur on nearly the same calendar date 19 years apart.
"""

import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runic import (  # noqa: E402
    zodiac_rune, weekday_rune, life_period, metonic_cycle)
from astroengine.models import CalculationError  # noqa: E402


def test_zodiac_aries_classical():
    z = zodiac_rune("Aries")
    assert (z["rune"], z["deity"]) == ("Eh", "Tyr")
    assert z["variant"] == "classical"


def test_zodiac_pisces_variants():
    assert zodiac_rune("Pisces")["deity"] == "Thor"
    assert zodiac_rune("Pisces", "modern alternative")["deity"] == "Aegir"
    with pytest.raises(CalculationError):
        zodiac_rune("Pisces", "norse")
    with pytest.raises(CalculationError):
        zodiac_rune("Ophiuchus")


def test_zodiac_case_insensitive():
    assert zodiac_rune("leo")["sign"] == "Leo"


def test_weekday_wednesday():
    w = weekday_rune("Wednesday")
    assert (w["deity"], w["planet"]) == ("Odin", "Mercury")
    assert all(k in w for k in ("tree", "herb", "element",
                               "esoteric_number", "magic_square"))
    with pytest.raises(CalculationError):
        weekday_rune("Funday")


def test_life_period_boundaries():
    assert life_period(22)["deity"] == "Sól"
    assert life_period(22)["years_elapsed"] == 0
    assert life_period(68)["deity"] == "Loki"
    assert life_period(0)["deity"] == "Máni"
    p = life_period(54.5)
    assert p["deity"] == "Tyr" and p["years_elapsed"] == 13.5
    assert p["years_remaining"] == 1.5


def test_life_period_outside_wheel():
    with pytest.raises(CalculationError):
        life_period(98)
    with pytest.raises(CalculationError):
        life_period(-1)


def test_metonic_golden_numbers():
    assert metonic_cycle(2000)["golden_number"] == 6  # known reference
    assert metonic_cycle(2026)["golden_number"] == 13
    # 19-year periodicity property
    for y in (1900, 2000, 2026):
        assert (metonic_cycle(y)["golden_number"] ==
                metonic_cycle(y + 19)["golden_number"])


def _full_moon_near(year, month, day):
    """Julian day of the full moon nearest the given date (pyswisseph)."""
    import swisseph as swe
    swe.set_ephe_path("")
    start = swe.julday(year, month, day, 0.0)
    best, best_elong = None, -1.0
    for d in range(-16, 17):
        jd = start + d
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        elong = abs((moon - sun + 180) % 360 - 180)
        if elong > best_elong:
            best, best_elong = jd, elong
    y, m, d, _ = swe.revjul(best)
    return y, m, d


def test_metonic_ephemeris_cross_check():
    # The book (Ch. 6): after 19 solar years the moon's phases fall on
    # nearly the same calendar date. Full moons 19 years apart should
    # land within ~2 days of each other in month-day.
    y1, m1, d1 = _full_moon_near(2007, 1, 15)
    y2, m2, d2 = _full_moon_near(2026, 1, 15)
    assert (m1, m2) == (1, 1)
    assert abs(d1 - d2) <= 2, f"{d1} vs {d2}"
