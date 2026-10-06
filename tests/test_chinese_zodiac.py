"""Sólrún's scrutiny of the Chinese zodiac engine."""

import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.chinese import year_pillar, zodiac  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_anchor_1984_jia_zi():
    p = year_pillar(1984)
    assert (p["stem"], p["branch"]) == ("Jia", "Zi")
    assert p["animal"] == "Rat"
    assert p["stem_element"] == "Wood"
    assert p["yin_yang"] == "yang"
    assert p["nayin"] == "Sea Gold"


def test_known_years():
    assert year_pillar(2024)["ganzhi"] == "Jia-Chen"
    assert year_pillar(2025)["ganzhi"] == "Yi-Si"
    assert year_pillar(2026)["ganzhi"] == "Bing-Wu"
    assert year_pillar(2000)["ganzhi"] == "Geng-Chen"
    assert year_pillar(2000)["nayin"] == "White Wax Gold"
    assert year_pillar(1972)["ganzhi"] == "Ren-Zi"
    assert year_pillar(1972)["nayin"] == "Mulberry Wood"


def test_lunar_new_year_boundary():
    # the animal changes at Lunar New Year, not January 1
    assert zodiac("2024-02-09")["animal"] == "Rabbit"
    assert zodiac("2024-02-09")["ganzhi"] == "Gui-Mao"
    assert zodiac("2024-02-10")["animal"] == "Dragon"
    assert zodiac("2024-02-10")["ganzhi"] == "Jia-Chen"
    assert zodiac("2026-02-16")["animal"] == "Snake"
    assert zodiac("2026-02-17")["animal"] == "Horse"
    assert zodiac("2024-02-10")["year_starts"] == "2024-02-10"


def test_allies_and_clashes():
    r = zodiac("1972-09-01")  # Water Rat
    assert r["animal"] == "Rat"
    assert sorted(r["trine_allies"]) == ["Dragon", "Monkey"]
    assert r["secret_friend"] == "Ox"
    assert r["clash"] == "Horse"
    d = zodiac("2024-05-05")  # Wood Dragon
    assert sorted(d["trine_allies"]) == ["Monkey", "Rat"]
    assert d["secret_friend"] == "Rooster"
    assert d["clash"] == "Dog"


def test_bad_date_is_calculation_error():
    with pytest.raises(CalculationError, match="bad date"):
        zodiac("not-a-date")
    with pytest.raises(CalculationError, match="outside the supported"):
        zodiac("1850-01-01")
