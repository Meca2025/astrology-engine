"""R03 — tests for runic hours, apparent time, planetary hours, sele.

Book fixtures from Pennick (2023), Ch. 4 (runic hours) and App. 3
(Northern Tradition planetary hours). The Kenneth worked example is NOT
used: its "Odal 22:30" conflicts with the encoded wheel (R01 note).
"""
import pytest

from astroengine.models import CalculationError
from astroengine.runic import (planetary_hour, runic_hour, sele,
                               to_local_apparent_time)


def test_wheel_fixtures():
    assert runic_hour("12:30")["rune"] == "Feoh"
    assert runic_hour("13:30")["rune"] == "Ur"
    assert runic_hour("16:45")["rune"] == "Rad"    # Ingrid's hour (Ch. 5)
    assert runic_hour("22:45")["rune"] == "Is"     # wheel value, not Kenneth's
    assert runic_hour("11:45")["rune"] == "Dag"
    assert runic_hour("00:15")["rune"] == "Jera"
    assert runic_hour("16:45")["window"] == "16:30-17:30"


def test_wheel_result_shape():
    out = runic_hour("16:45")
    assert out["correspondences"]["deity"] == "Ing/Nerthus"
    assert out["source"] == "Pennick (2023)"
    assert out["historical_claim"] == "modern synthesis"


def test_local_apparent_time():
    # solstice noon at Greenwich: LAT within a few minutes of 12:00
    lat = to_local_apparent_time("2026-06-21T12:00", 0.0, "UTC")
    assert lat["local_apparent_time"] in ("11:57", "11:58", "11:59",
                                          "12:00", "12:01", "12:02")
    assert lat["method"] == "longitude+eot-approx"
    # +15 degrees east shifts LAT about an hour forward
    lat2 = to_local_apparent_time("2026-06-21T12:00", 15.0, "UTC")
    h1 = int(lat["local_apparent_time"][:2])
    h2 = int(lat2["local_apparent_time"][:2])
    assert (h2 - h1) % 24 == 1


def test_planetary_hour_grid():
    assert planetary_hour("Sunday", 0)["deity"] == "Thor"
    assert planetary_hour("Monday", 12)["deity"] == "Máni"
    assert planetary_hour("Friday", 19)["deity"] == "Frigg"
    assert planetary_hour("saturday", 23)["deity"] == "Frigg"
    with pytest.raises(CalculationError):
        planetary_hour("Funday", 3)
    with pytest.raises(CalculationError):
        planetary_hour("Sunday", 24)


def test_sele_true():
    # Saturday 2026-11-07 13:05 civil, lon +7.5: LAT 13:51 -> runic Ur
    # (deities Thor/Urd); planetary Saturday 13:00 = Thor -> sele
    out = sele("2026-11-07T13:05", 7.5, "UTC")
    assert out["sele"] is True
    assert out["runic_hour"]["rune"] == "Ur"
    assert out["planetary_hour"]["deity"] == "Thor"
    assert out["method"] == "longitude+eot-approx"


def test_sele_false():
    out = sele("2026-10-06T05:00", -86.15, "America/Indiana/Indianapolis")
    assert out["sele"] is False
    assert out["runic_hour"]["rune"] == "Elhaz"   # LAT 03:28
    assert out["planetary_hour"]["deity"] == "Odin"


def test_sele_invalid():
    with pytest.raises(CalculationError):
        sele("2026-11-07T13:05", 200.0, "UTC")
    with pytest.raises(CalculationError):
        sele("2026-11-07T13:05", 7.5, "Not/AZone")
    with pytest.raises(CalculationError):
        sele("not-a-datetime", 7.5, "UTC")
