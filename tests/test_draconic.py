"""Sólrún's scrutiny of the draconic chart."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.draconic import (draconic_chart, draconic_contacts,  # noqa: E402
                                  draconic_longitude)
from astroengine.models import CalculationError  # noqa: E402

JD_NATAL = swe.julday(1972, 9, 1, 12.3)
LAT, LON = 42.81, -73.94


def test_node_maps_to_zero_aries():
    chart = draconic_chart(JD_NATAL, LAT, LON)
    node = chart["node_longitude"]
    assert draconic_longitude(node, node) == pytest.approx(0.0)


def test_rotation_is_consistent():
    chart = draconic_chart(JD_NATAL, LAT, LON)
    node = chart["node_longitude"]
    # draconic Sun + node == tropical Sun (mod 360)
    from astroengine.legacy_astronomy import legacy_positions
    tropical_sun = legacy_positions(JD_NATAL, True)["Sun"]["longitude"] % 360.0
    assert (chart["positions"]["Sun"] + node) % 360.0 == pytest.approx(
        tropical_sun, abs=0.01)


def test_all_ten_bodies_present():
    chart = draconic_chart(JD_NATAL, LAT, LON)
    assert len(chart["positions"]) == 10
    assert set(chart["angles"]) == {"ASC", "MC"}
    assert chart["node_kind"].startswith("true node")


def test_contacts_sorted_and_bounded():
    hits = draconic_contacts(JD_NATAL, LAT, LON, orb=5.0)
    orbs = [h["orb"] for h in hits]
    assert orbs == sorted(orbs)
    assert all(h["orb"] <= 5.0 for h in hits)
    assert len(hits) > 0


def test_tightest_contact_is_saturn_mercury():
    hits = draconic_contacts(JD_NATAL, LAT, LON, orb=2.0)
    assert hits[0]["draconic"] == "Saturn"
    assert hits[0]["natal"] == "Mercury"
    assert hits[0]["orb"] < 2.0


def test_bad_orb_raises():
    with pytest.raises(CalculationError):
        draconic_contacts(JD_NATAL, LAT, LON, orb=0)
