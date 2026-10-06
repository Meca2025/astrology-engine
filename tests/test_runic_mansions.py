"""Sólrún's scrutiny of R06: the 28 lunar mansions (Pennick Ch. 7).

Alcyone anchor, mansion boundaries, the wrap into mansion 28, longitude
normalization, and exact tiling of the 28 segments.
"""

import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runic import (  # noqa: E402
    lunar_mansion, lunar_mansions, MANSION_ANCHOR_DEG, MANSION_WIDTH_DEG)
from astroengine.models import CalculationError  # noqa: E402


def test_alcyone_anchor_is_mansion_one():
    m = lunar_mansion(MANSION_ANCHOR_DEG)
    assert m["mansion"] == 1
    assert m["rune"] == "Feoh"
    assert m["northern_name"] == "Boars' Throng"
    assert m["star"] == "Alcyone"
    assert "declared modern convention" in m["method"]


def test_mansion_two_boundary():
    m = lunar_mansion(MANSION_ANCHOR_DEG + MANSION_WIDTH_DEG)
    assert m["mansion"] == 2
    assert m["rune"] == "Ur"
    assert m["northern_name"] == "The Follower"
    assert m["star"] == "Aldebaran"


def test_wrap_into_mansion_28():
    m = lunar_mansion(MANSION_ANCHOR_DEG - 0.1)
    assert m["mansion"] == 28
    assert m["rune"] == "Ear"
    assert m["northern_name"] == "The Last Ones"


def test_normalization():
    assert (lunar_mansion(370.0)["mansion"] ==
            lunar_mansion(10.0)["mansion"])


def test_segments_tile_exactly():
    rows = lunar_mansions()
    assert len(rows) == 28
    for i, row in enumerate(rows):
        start, end = row["segment"]
        # segments are stored rounded to 4 decimals; allow for that
        assert abs(start - round((MANSION_ANCHOR_DEG + i * MANSION_WIDTH_DEG)
                                 % 360.0, 4)) < 1e-9
        assert abs((end - start) % 360.0 - MANSION_WIDTH_DEG) < 1e-3
    assert rows[0]["rune"] == "Feoh" and rows[27]["rune"] == "Ear"


def test_bad_longitude():
    with pytest.raises(CalculationError):
        lunar_mansion("full")
