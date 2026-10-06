"""Sólrún's scrutiny of the rune casting."""

import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runecast import cast, layouts, runes  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_24_runes_futhark_order():
    rs = runes()
    assert len(rs) == 24
    assert [r["name"] for r in rs[:8]] == [
        "Fehu", "Uruz", "Thurisaz", "Ansuz", "Raidho", "Kenaz",
        "Gebo", "Wunjo"]
    assert all(r["glyph"] for r in rs)


def test_symmetric_runes_never_merkstave():
    symmetric = {r["name"] for r in runes() if r["merkstave"] is None}
    assert len(symmetric) == 9
    for seed in range(40):
        r = cast("wheel", seed=seed)
        for d in r["runes"]:
            if d["rune"] in symmetric:
                assert d["merkstave"] is False, (seed, d["rune"])


def test_seeded_cast_reproducible():
    a = cast("nine-worlds", seed=7)
    b = cast("nine-worlds", seed=7)
    assert [(d["rune"], d["merkstave"]) for d in a["runes"]] == \
           [(d["rune"], d["merkstave"]) for d in b["runes"]]
    assert len(a["runes"]) == 9


def test_layout_positions_unique():
    for name, positions in layouts().items():
        assert len(set(positions)) == len(positions), name
        d = cast(name, seed=1, merkstave=False)
        assert [x["position"] for x in d["runes"]] == positions
        assert not any(x["merkstave"] for x in d["runes"])


def test_no_duplicate_runes_in_cast():
    r = cast("wheel", seed=3)
    assert len({d["rune"] for d in r["runes"]}) == 12


def test_blank_rune_opt_in():
    r = cast("single", seed=1, blank=True)
    assert len(runes(include_blank=True)) == 25
    blanks = [d for d in r["runes"] if d["modern_invention"]]
    # may or may not be drawn; the flag must be honest either way
    assert all(d["rune"] == "The Blank Rune" for d in blanks)


def test_unknown_layout():
    with pytest.raises(CalculationError):
        cast("no-such-layout")
