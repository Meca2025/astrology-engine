"""Sólrún's scrutiny of the ogham grove."""

import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.ogham import cast, oghams, layouts  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_twenty_five_staves_in_aicme_order():
    staves = oghams()
    assert len(staves) == 25
    assert staves[0]["name"] == "Beith"
    assert staves[19]["name"] == "Idhadh"
    assert [s["name"] for s in staves[20:]] == [
        "Eabhadh", "Ór", "Uilleann", "Ifin", "Phagos"]
    aicmí = [s["aicme"] for s in staves]
    assert aicmí == (["Beith"] * 5 + ["Huath"] * 5 + ["Muin"] * 5
                    + ["Ailm"] * 5 + ["Forfeda"] * 5)


def test_glyph_codepoints_sequential():
    staves = oghams()
    cps = [ord(s["glyph"]) for s in staves]
    assert cps == list(range(0x1681, 0x169A))


def test_kennings_grounded():
    staves = {s["name"]: s for s in oghams()}
    assert staves["Beith"]["kenning"] == "withered foot with fine hair"
    assert staves["Dair"]["kenning"] == "highest tree"
    assert staves["Coll"]["kenning"] == "fairest tree"


def test_tree_lore_honest():
    staves = {s["name"]: s for s in oghams()}
    # Luis's true name is Flame/Herb; the rowan is gloss tradition
    assert "flame" in staves["Luis"]["tree"]
    assert staves["Eabhadh"]["tree"] is None


def test_five_layouts():
    ls = layouts()
    assert set(ls) == {"single", "triad", "aicme", "wheel", "grove"}
    assert len(ls["grove"]) == 12


def test_no_forfeda_option():
    assert len(oghams(include_forfeda=False)) == 20
    r = cast(layout="grove", seed=3, forfeda=False)
    assert all(s["aicme"] != "Forfeda" for s in r["staves"])


def test_deterministic():
    a = cast(layout="wheel", seed=7)
    b = cast(layout="wheel", seed=7)
    assert [s["stave"] for s in a["staves"]] == [s["stave"] for s in b["staves"]]


def test_unknown_layout_is_calculation_error():
    with pytest.raises(CalculationError, match="unknown layout"):
        cast(layout="bog")


def test_aicme_layout_draws_true_aicmí():
    # Sólrún O03-D1: positions must not lie about their contents
    for seed in range(10):
        r = cast(layout="aicme", seed=seed)
        got = {s["position"].split(" — ")[0]: s["aicme"] for s in r["staves"]}
        assert got == {"Aicme Beith": "Beith", "Aicme Huath": "Huath",
                       "Aicme Muin": "Muin", "Aicme Ailm": "Ailm",
                       "Forfeda": "Forfeda"}


def test_aicme_layout_no_forfeda_draws_wild_fifth():
    for seed in range(10):
        r = cast(layout="aicme", seed=seed, forfeda=False)
        aicmí = [s["aicme"] for s in r["staves"][:4]]
        assert aicmí == ["Beith", "Huath", "Muin", "Ailm"]
        assert r["staves"][4]["aicme"] != "Forfeda"
