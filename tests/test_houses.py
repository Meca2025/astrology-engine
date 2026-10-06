"""Sólrún's scrutiny of the house systems."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.houses import SYSTEMS, house_cusps  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402

# Volmarr's sky: 1972-09-01 12:18 UTC, Schenectady NY.
JD = swe.julday(1972, 9, 1, 12.3)
LAT, LON = 42.81, -73.94


def test_five_systems_named():
    assert set(SYSTEMS) == {"placidus", "whole-sign", "equal", "koch",
                            "regiomontanus"}


def test_all_systems_return_twelve_cusps():
    for system in SYSTEMS:
        cusps, asc, mc = house_cusps(JD, LAT, LON, system)
        assert len(cusps) == 12, system
        assert all(0.0 <= c < 360.0 for c in cusps), system


def test_asc_preserved_across_systems():
    ascs = {house_cusps(JD, LAT, LON, s)[1] for s in SYSTEMS}
    assert max(ascs) - min(ascs) < 1.0 / 60.0  # within one arc-minute


def test_volmarr_placidus_asc_unchanged():
    _, asc, _ = house_cusps(JD, LAT, LON, "placidus")
    assert abs(asc - 181.03) < 0.02  # Libra 1°01'


def test_whole_sign_cusps_on_boundaries():
    cusps, asc, _ = house_cusps(JD, LAT, LON, "whole-sign")
    assert asc == pytest.approx(181.03, abs=0.02)
    for c in cusps:
        assert c % 30.0 == pytest.approx(0.0, abs=1e-6)
    assert cusps[0] == pytest.approx(180.0)  # Libra ingress


def test_equal_cusps_thirty_apart_from_asc():
    cusps, asc, _ = house_cusps(JD, LAT, LON, "equal")
    for i, c in enumerate(cusps):
        assert (c - asc) % 360.0 == pytest.approx((i * 30.0) % 360.0,
                                                 abs=1e-6)


def test_unknown_system_raises():
    with pytest.raises(CalculationError):
        house_cusps(JD, LAT, LON, "bogus")


def test_name_normalization():
    a = house_cusps(JD, LAT, LON, "Whole_Sign")
    b = house_cusps(JD, LAT, LON, "whole-sign")
    assert a[0] == b[0]
