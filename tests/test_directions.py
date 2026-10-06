"""Sólrún's scrutiny of solar arc directions."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.directions import directed_aspects, solar_arc  # noqa: E402
from astroengine.legacy_astronomy import legacy_positions  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402

# Volmarr's sky: 1972-09-01 12:18 UTC.
JD_NATAL = swe.julday(1972, 9, 1, 12.3)
JD_TARGET = swe.julday(2026, 10, 23, 12.0)


def test_arc_is_progressed_sun_motion():
    natal = legacy_positions(JD_NATAL, True)
    years = (JD_TARGET - JD_NATAL) / 365.25
    prog = legacy_positions(JD_NATAL + years, True)
    expected = ((prog["Sun"]["longitude"] - natal["Sun"]["longitude"])
                % 360.0)
    r = solar_arc(JD_NATAL, JD_TARGET)
    assert r["arc"] == pytest.approx(expected)
    assert r["years"] == pytest.approx(years)


def test_directed_sun_advances_by_arc():
    natal = legacy_positions(JD_NATAL, True)
    r = solar_arc(JD_NATAL, JD_TARGET)
    assert r["directed"]["Sun"] == pytest.approx(
        (natal["Sun"]["longitude"] + r["arc"]) % 360.0)


def test_volmarr_directed_mercury_conjunct_uranus():
    natal = legacy_positions(JD_NATAL, True)
    r = solar_arc(JD_NATAL, JD_TARGET)
    natal_lon = {b: natal[b]["longitude"] for b in r["directed"]}
    hits = directed_aspects(r["directed"], natal_lon)
    hit = next(h for h in hits
               if h["directed"] == "Mercury" and h["natal"] == "Uranus"
               and h["aspect"] == "conjunction")
    assert hit["orb"] < 0.15
    assert hit["exact"]


def test_target_before_birth_raises():
    with pytest.raises(CalculationError):
        solar_arc(JD_TARGET, JD_NATAL)


def test_applying_flag():
    # directed body 0.5° before exact conjunction, moving forward
    hits = directed_aspects({"Mars": 10.0}, {"Venus": 10.5}, orb=1.0)
    assert hits[0]["applying"] is True
    hits = directed_aspects({"Mars": 10.6}, {"Venus": 10.5}, orb=1.0)
    assert hits[0]["applying"] is False


def test_sorted_tightest_first():
    hits = directed_aspects({"Mars": 10.0, "Sun": 50.0},
                            {"Venus": 10.5, "Moon": 50.2}, orb=1.0)
    orbs = [h["orb"] for h in hits]
    assert orbs == sorted(orbs)


def test_same_body_square_reported():
    # arc 90°: directed Sun square natal Sun is a genuine direction
    hits = directed_aspects({"Sun": 90.0}, {"Sun": 0.0}, orb=1.0, arc=90.0)
    assert any(h["aspect"] == "square" and h["directed"] == "Sun"
               and h["natal"] == "Sun" for h in hits)


def test_trivial_identity_suppressed():
    # arc 0.3°: directed Sun conjunct natal Sun is nothing moving yet
    hits = directed_aspects({"Sun": 0.3}, {"Sun": 0.0}, orb=1.0, arc=0.3)
    assert not any(h["directed"] == "Sun" and h["natal"] == "Sun"
                   for h in hits)
