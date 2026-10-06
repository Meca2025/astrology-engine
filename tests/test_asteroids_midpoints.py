"""Sólrún's scrutiny of asteroids and midpoints."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.asteroids import ASTEROIDS, asteroid_positions  # noqa: E402
from astroengine.midpoints import (all_midpoints, midpoint,  # noqa: E402
                                   midpoint_hits)
from astroengine.models import CalculationError  # noqa: E402

JD_NATAL = swe.julday(1972, 9, 1, 12.3)
LAT, LON = 42.81, -73.94


def test_midpoint_basic():
    assert midpoint(0.0, 90.0) == pytest.approx(45.0)
    assert midpoint(90.0, 0.0) == pytest.approx(45.0)


def test_midpoint_wraps():
    assert midpoint(350.0, 10.0) == pytest.approx(0.0)
    assert midpoint(10.0, 350.0) == pytest.approx(0.0)


def test_midpoint_opposite():
    # 180° apart: either end is a valid shorter-arc midpoint
    assert midpoint(0.0, 180.0) in (pytest.approx(90.0), pytest.approx(270.0))


def test_all_midpoints_count():
    pos = {b: float(i * 36) for i, b in enumerate(
        ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
         "Saturn", "Uranus", "Neptune", "Pluto"])}
    mps = all_midpoints(pos)
    assert len(mps) == 45  # C(10,2)
    assert mps == sorted(mps, key=lambda m: m["longitude"])


def test_volmarr_mars_on_saturn_neptune():
    hits = midpoint_hits(JD_NATAL, LAT, LON)
    hit = next(h for h in hits if h["pair"] == "Saturn/Neptune"
               and h["activated_by"] == "Mars")
    assert hit["orb"] < 0.1


def test_midpoint_hits_sorted():
    hits = midpoint_hits(JD_NATAL, LAT, LON)
    orbs = [h["orb"] for h in hits]
    assert orbs == sorted(orbs)
    assert all(h["orb"] <= 1.0 for h in hits)


def test_bad_orb_raises():
    with pytest.raises(CalculationError):
        midpoint_hits(JD_NATAL, LAT, LON, orb=0)


def test_asteroid_table_has_five():
    assert [a[0] for a in ASTEROIDS] == ["Chiron", "Ceres", "Pallas",
                                         "Juno", "Vesta"]


def test_asteroids_honest_about_missing_files():
    # this environment ships no asteroid ephemeris: the module must say
    # so plainly, never invent positions
    with pytest.raises(CalculationError) as exc:
        asteroid_positions(swe.julday(2026, 10, 23))
    msg = str(exc.value)
    assert ".se1" in msg and "Chiron" in msg
