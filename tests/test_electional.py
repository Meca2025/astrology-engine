"""Sólrún's scrutiny of electional astrology."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.electional import (find_windows, moon_void_of_course,  # noqa: E402
                                    planetary_hour, score_moment)
from astroengine.models import CalculationError  # noqa: E402

LAT, LON = 42.81, -73.94


def test_moon_phase_known():
    # new moon was 2026-10-14; on the 23rd the Moon waxes
    s = score_moment(swe.julday(2026, 10, 23, 12), LAT, LON)
    assert s["moon_waxing"] is True
    s2 = score_moment(swe.julday(2026, 10, 10, 12), LAT, LON)
    assert s2["moon_waxing"] is False


def test_mercury_rx_station():
    assert score_moment(swe.julday(2026, 10, 23, 12), LAT, LON)[
        "mercury_retrograde"] is False
    assert score_moment(swe.julday(2026, 10, 25, 12), LAT, LON)[
        "mercury_retrograde"] is True


def test_void_detection_runs():
    void, aspects = moon_void_of_course(swe.julday(2026, 10, 23, 12))
    assert isinstance(void, bool)
    assert all(set(a) == {"planet", "aspect", "orb"} for a in aspects)


def test_planetary_hour_known():
    # 2026-10-23 is a Friday -> day ruler Venus; noon is a day hour
    h = planetary_hour(swe.julday(2026, 10, 23, 16), LAT, LON)
    assert h is not None
    assert h["day_ruler"] == "Venus"
    assert h["sect"] == "day"
    assert h["hour_ruler"] in ("Saturn", "Jupiter", "Mars", "Sun",
                              "Venus", "Mercury", "Moon")


def test_windows_sorted_best_first():
    w = find_windows(swe.julday(2026, 10, 20), swe.julday(2026, 10, 27),
                     LAT, LON, timezone="America/New_York")
    scores = [x["score"] for x in w]
    assert scores == sorted(scores, reverse=True)
    assert len(w) > 0
    assert all(set(x) >= {"datetime", "score", "verdict", "notes"}
               for x in w)


def test_bad_window_raises():
    with pytest.raises(CalculationError):
        find_windows(swe.julday(2026, 10, 27), swe.julday(2026, 10, 20),
                     LAT, LON)


def test_bad_timezone_raises():
    with pytest.raises(CalculationError):
        find_windows(swe.julday(2026, 10, 20), swe.julday(2026, 10, 21),
                     LAT, LON, timezone="Not/AZone")


def test_day_ruler_follows_local_date():
    # Sólrún D1: 2026-10-24 02:00 UT is still Friday night in New York
    h = planetary_hour(swe.julday(2026, 10, 24, 2), LAT, LON,
                       "America/New_York")
    assert h["day_ruler"] == "Venus"
    h_utc = planetary_hour(swe.julday(2026, 10, 24, 2), LAT, LON, "UTC")
    assert h_utc["day_ruler"] == "Saturn"


def test_bad_timezone_in_hour_raises():
    with pytest.raises(CalculationError):
        planetary_hour(swe.julday(2026, 10, 23, 16), LAT, LON, "Not/AZone")
