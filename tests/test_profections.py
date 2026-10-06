"""Sólrún's scrutiny of annual profections."""

import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.profections import essential_dignity, profection  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_volmarr_age_54():
    r = profection(181.03, "1972-09-01", "2026-10-23")
    assert r["age"] == 54
    assert r["profected_sign"] == "Aries"
    assert r["profected_house"] == 7
    assert r["time_lord"] == "Mars"


def test_birth_year_stays_home():
    r = profection(181.03, "1972-09-01", "1972-09-01")
    assert r["age"] == 0
    assert r["profected_sign"] == "Libra"
    assert r["profected_house"] == 1


def test_twelve_year_return():
    r = profection(181.03, "1972-09-01", "1984-09-01")
    assert r["age"] == 12
    assert r["profected_sign"] == "Libra"


def test_lord_condition():
    r = profection(181.03, "1972-09-01", "2026-10-23",
                   lord_longitude=158.0)  # Mars in Virgo
    assert r["lord_sign"] == "Virgo"
    assert r["lord_dignity"] == "peregrine"


def test_dignity_table():
    assert essential_dignity("Mars", "Scorpio") == "domicile"
    assert essential_dignity("Sun", "Aries") == "exaltation"
    assert essential_dignity("Venus", "Scorpio") == "detriment"
    assert essential_dignity("Sun", "Libra") == "fall"
    assert essential_dignity("Jupiter", "Aries") == "peregrine"


def test_target_before_birth_raises():
    with pytest.raises(CalculationError):
        profection(181.03, "1972-09-01", "1970-01-01")


def test_bad_date_raises():
    with pytest.raises(CalculationError):
        profection(181.03, "not-a-date", "2026-10-23")
