"""Sólrún's scrutiny of the transit watch."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.watch import TRANSIT_BODIES, upcoming_transits  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402

JD_NATAL = swe.julday(1972, 9, 1, 12.3)
LAT, LON = 42.81, -73.94


def test_finds_october_23():
    hits = upcoming_transits(JD_NATAL, swe.julday(2026, 10, 6),
                             swe.julday(2026, 11, 6), LAT, LON)
    hit = next(h for h in hits
               if h["transit_body"] == "Jupiter"
               and h["aspect"] == "conjunction"
               and h["natal_point"] == "Mercury")
    assert hit["date"] == "2026-10-23"
    assert hit["orb"] < 0.5


def test_sorted_by_date():
    hits = upcoming_transits(JD_NATAL, swe.julday(2026, 1, 1),
                             swe.julday(2027, 6, 1), LAT, LON)
    dates = [h["date"] for h in hits]
    assert dates == sorted(dates)
    assert len(hits) > 1


def test_outer_bodies_only():
    hits = upcoming_transits(JD_NATAL, swe.julday(2026, 1, 1),
                             swe.julday(2026, 2, 1), LAT, LON)
    assert all(h["transit_body"] in TRANSIT_BODIES for h in hits)


def test_empty_window():
    hits = upcoming_transits(JD_NATAL, swe.julday(2026, 10, 24),
                             swe.julday(2026, 10, 24), LAT, LON)
    assert hits == []


def test_bad_window_raises():
    with pytest.raises(CalculationError):
        upcoming_transits(JD_NATAL, swe.julday(2026, 11, 6),
                          swe.julday(2026, 10, 6), LAT, LON)


def test_bad_orb_raises():
    with pytest.raises(CalculationError):
        upcoming_transits(JD_NATAL, swe.julday(2026, 10, 6),
                          swe.julday(2026, 11, 6), LAT, LON, orb=0)


def test_dates_are_real():
    import datetime
    hits = upcoming_transits(JD_NATAL, swe.julday(2026, 10, 6),
                             swe.julday(2026, 11, 6), LAT, LON)
    for h in hits:
        datetime.date.fromisoformat(h["date"])  # raises if malformed


def test_saturn_return_reported():
    # Sólrún D1: same-body returns are headline transits, not noise
    hits = upcoming_transits(JD_NATAL, swe.julday(2031, 1, 1),
                             swe.julday(2033, 12, 31), LAT, LON)
    sat = [h for h in hits if h["transit_body"] == "Saturn"
           and h["natal_point"] == "Saturn"
           and h["aspect"] == "conjunction"]
    assert len(sat) >= 1
    assert all(h["orb"] < 1.0 for h in sat)
