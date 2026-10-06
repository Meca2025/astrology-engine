"""Sólrún's scrutiny of the Tibetan astrology engine."""

import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.tibetan import forces, tibetan, year_name  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_year_element_animal():
    assert year_name(2024)["name"] == "Wood Dragon"
    assert year_name(2025)["name"] == "Wood Snake"
    assert year_name(2026)["name"] == "Fire Horse"
    assert year_name(1972)["name"] == "Water Mouse"
    assert year_name(2000)["name"] == "Iron Dragon"


def test_rabjung():
    y = year_name(2024)
    assert (y["rabjung_cycle"], y["rabjung_year"]) == (17, 38)


def test_mewa_cycle():
    # verified against two independent published mewa tables
    assert year_name(2024)["mewa"] == {"number": 3, "color": "Indigo",
                                      "element": "Water"}
    assert year_name(2026)["mewa"]["number"] == 1
    assert year_name(1972)["mewa"] == {"number": 1, "color": "White",
                                      "element": "Metal"}
    assert year_name(2027)["mewa"]["number"] == 9


def test_parkha_cycle():
    # verified against the published 2025-2039 parkha table
    assert year_name(2025)["parkha"]["name"] == "Gin"
    assert year_name(2026)["parkha"]["name"] == "Zin"
    assert year_name(2028)["parkha"]["name"] == "Li"
    assert year_name(2030)["parkha"]["name"] == "Dha"
    assert year_name(2032)["parkha"]["name"] == "Kham"
    assert year_name(2039)["parkha"]["name"] == "Khen"


def test_five_forces():
    f = forces(1972)  # Water Mouse
    assert f["srog"]["element"] == "Water"
    assert f["lus"]["element"] == "Water"
    assert f["dbang_thang"]["element"] == "Water"
    assert f["rlung_ta"]["element"] == "Wood"
    assert f["bla"]["element"] == "Iron"  # mother of Water
    f = forces(2024)  # Wood Dragon
    assert f["srog"]["element"] == "Earth"
    assert f["rlung_ta"]["element"] == "Wood"
    assert f["bla"]["element"] == "Fire"  # mother of Earth
    f = forces(2026)  # Fire Horse
    assert f["srog"]["element"] == "Fire"
    assert f["rlung_ta"]["element"] == "Iron"
    assert f["bla"]["element"] == "Wood"  # mother of Fire


def test_boundary_flag():
    assert tibetan("2023-02-01")["boundary_uncertain"] is True
    assert tibetan("2023-06-01")["boundary_uncertain"] is False
    assert "Losar" in tibetan("2023-02-01")["losar_note"]


def test_bad_date():
    with pytest.raises(CalculationError, match="bad date"):
        tibetan("someday")
