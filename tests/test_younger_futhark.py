"""Sólrún's scrutiny of the Younger Futhark."""

import json
import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runecast import cast, runes, systems  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_sixteen_runes_in_order():
    rs = runes(system="younger")
    assert len(rs) == 16
    assert rs[0]["name"] == "Fé"
    assert rs[-1]["name"] == "Ýr"


def test_both_glyph_variants():
    rs = {r["name"]: r for r in runes(system="younger")}
    assert rs["Óss"]["glyph"] == "ᚬ"
    assert rs["Óss"]["glyph_short_twig"] == "ᚭ"
    assert rs["Hagall"]["glyph"] == "ᚼ"
    assert rs["Hagall"]["glyph_short_twig"] == "ᚽ"
    assert rs["Týr"]["glyph_short_twig"] == "ᛐ"


def test_symmetric_runes_have_no_merkstave():
    rs = {r["name"]: r for r in runes(system="younger")}
    for name in ("Hagall", "Íss", "Sól"):
        assert rs[name]["merkstave"] is None, name
    assert rs["Fé"]["merkstave"] is not None


def test_cast_younger():
    r = cast(layout="norns", seed=7, system="younger")
    assert r["source"] == "Younger Futhark"
    assert len(r["runes"]) == 3
    names = {x["name"] for x in runes(system="younger")}
    assert all(x["rune"] in names for x in r["runes"])


def test_all_layouts_fit_sixteen():
    from astroengine.runecast import layouts
    for name, positions in layouts().items():
        assert len(positions) <= 16, name
        r = cast(layout=name, seed=1, system="younger")
        assert len(r["runes"]) == len(positions)


def test_unknown_system_raises():
    with pytest.raises(CalculationError):
        cast(system="bogus")


def test_blank_only_elder():
    with pytest.raises(CalculationError):
        runes(include_blank=True, system="younger")


def test_elder_still_default():
    r = cast(layout="single", seed=3)
    assert r["source"] == "Elder Futhark"
    assert len(runes()) == 24


def test_systems_registry():
    assert systems() == {"elder": "Elder Futhark",
                         "younger": "Younger Futhark",
                         "futhorc": "Anglo-Saxon Futhorc"}


def test_corpus_provenance():
    doc = json.load(open(
        "/home/hatch/workspace/astrology-engine/data/runes_younger.json"))
    assert "Norwegian" in doc["source"] and "Icelandic" in doc["source"]
    assert doc["historical_claim"] == "traditional with modern synthesis"


def test_missing_corpus_is_calculation_error():
    # Sólrún O01-D1: an advertised-but-unforged corpus must fail cleanly
    with pytest.raises(CalculationError, match="not yet forged"):
        cast(system="futhorc")
