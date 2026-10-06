"""Sólrún's scrutiny of R07: palaces and nine worlds (fixed overlays)."""

import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runic import (  # noqa: E402
    grimnismal_palace, world_rune, nine_worlds)
from astroengine.models import CalculationError  # noqa: E402

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def test_palace_gate_endpoints():
    a = grimnismal_palace("Aries")
    assert (a["palace"], a["deity"], a["meaning"]) == (
        "Bilskírnir", "Thor", "Lightning")
    p = grimnismal_palace("Pisces")
    assert (p["palace"], p["deity"]) == ("Noatún", "Njord")
    assert a["kind"] == "correspondence overlay"


def test_all_twelve_palaces():
    seen = set()
    for sign in SIGNS:
        r = grimnismal_palace(sign.lower())
        assert r["sign"] == sign
        assert r["palace"] and r["meaning"] and r["deity"]
        seen.add(r["palace"])
    assert len(seen) == 12
    with pytest.raises(CalculationError):
        grimnismal_palace("Ophiuchus")


def test_nine_worlds():
    worlds = nine_worlds()
    assert len(worlds) == 9
    assert (worlds[0]["world"], worlds[0]["rune"]) == ("Asgard", "Gyfu")
    assert (worlds[-1]["world"], worlds[-1]["rune"]) == ("Helheim", "Hagal")
    assert world_rune("asgard")["rune"] == "Gyfu"
    with pytest.raises(CalculationError):
        world_rune("Midgard Express")
