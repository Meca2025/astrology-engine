"""Sólrún's scrutiny of the Anglo-Saxon futhorc."""

import json
import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runecast import cast, runes  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_thirty_three_in_order():
    rs = runes(system="futhorc")
    assert len(rs) == 33
    names = [r["name"] for r in rs]
    assert names[0] == "Feoh"
    assert names[-1] == "Gar"
    # the island's own additions follow the old twenty-four
    assert names[23] == "Daeg"
    assert names[24:29] == ["Ac", "Aesc", "Yr", "Ior", "Ear"]
    assert names[29:] == ["Cweorth", "Calc", "Stan", "Gar"]
    assert "Wynn" in names  # the joy-rune, not to be forgotten


def test_oe_poem_fidelity():
    rs = {r["name"]: r for r in runes(system="futhorc")}
    assert "grave" in rs["Ear"]["upright"]["meaning"]
    assert "horrible" in rs["Ear"]["upright"]["meaning"]
    assert "river" in rs["Ior"]["upright"]["meaning"]
    assert "oak" in rs["Ac"]["upright"]["meaning"].lower()


def test_northumbrian_labeled():
    doc = json.load(open(
        "/home/hatch/workspace/astrology-engine/data/runes_futhorc.json"))
    assert "Northumbrian" in doc["source"]
    rs = {r["name"]: r for r in runes(system="futhorc")}
    assert "No rune-poem stanza" in rs["Gar"]["upright"]["meaning"]


def test_symmetric_have_no_merkstave():
    rs = {r["name"]: r for r in runes(system="futhorc")}
    for name in ("Gyfu", "Haegl", "Is", "Eoh", "Sigel", "Ing",
                 "Ethel", "Daeg"):
        assert rs[name]["merkstave"] is None, name
    assert rs["Feoh"]["merkstave"] is not None
    assert rs["Ear"]["merkstave"] is not None


def test_cast_futhorc():
    r = cast(layout="cross", seed=11, system="futhorc")
    assert r["source"] == "Anglo-Saxon Futhorc"
    assert len(r["runes"]) == 5


def test_all_layouts_fit_thirty_three():
    from astroengine.runecast import layouts
    for name in layouts():
        r = cast(layout=name, seed=2, system="futhorc")
        assert len(r["runes"]) == len(layouts()[name])


def test_deterministic():
    a = cast(layout="norns", seed=99, system="futhorc")
    b = cast(layout="norns", seed=99, system="futhorc")
    assert [x["rune"] for x in a["runes"]] == [x["rune"] for x in b["runes"]]
