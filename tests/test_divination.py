"""Sólrún's scrutiny of the divination quartet."""

import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.tarot import draw, spreads, deck  # noqa: E402
from astroengine.iching import cast, hexagrams  # noqa: E402
from astroengine.numerology import (  # noqa: E402
    life_path, destiny, soul_urge, personality, personal_year,
    full_reading, reduce_number)
from astroengine.readings import reading  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


# --- tarot ---
def test_deck_complete():
    assert len(deck()) == 78
    assert len(spreads()) == 10


def test_seeded_draw_reproducible():
    a = draw("celtic-cross", seed=7)
    b = draw("celtic-cross", seed=7)
    assert [c["card"] for c in a["cards"]] == [c["card"] for c in b["cards"]]
    assert len(a["cards"]) == 10


def test_spread_positions_unique():
    for name, positions in spreads().items():
        assert len(set(positions)) == len(positions), name
        d = draw(name, seed=1, reversals=False)
        assert [c["position"] for c in d["cards"]] == positions
        assert not any(c["reversed"] for c in d["cards"])


def test_unknown_spread():
    with pytest.raises(CalculationError):
        draw("no-such-spread")


# --- numerology ---
def test_volmarr_life_path_master():
    assert life_path("1972-09-01")["number"] == 11
    assert life_path("1972-09-01")["master_number"] is True


def test_masters_held():
    assert reduce_number(29) == 11
    assert reduce_number(38) == 11  # 3+8=11 held
    assert reduce_number(44) == 8  # 44 is not a master hold
    assert reduce_number(29, keep_masters=False) == 2  # 29 -> 11 -> 2


def test_name_numbers():
    assert destiny("Volmarr Goði")["number"] == 8
    assert soul_urge("Volmarr Goði")["number"] == 22
    assert personality("Volmarr Goði")["number"] == 4


def test_personal_year():
    assert personal_year("1972-09-01", for_year=2026)["number"] == 2


def test_bad_inputs():
    with pytest.raises(CalculationError):
        life_path("not-a-date")
    with pytest.raises(CalculationError):
        destiny("123")


# --- i-ching ---
def test_64_hexagrams():
    assert len(hexagrams()) == 64


def test_cast_reproducible():
    a = cast(seed=42)
    b = cast(seed=42)
    assert a["lines"] == b["lines"]
    assert a["primary"]["number"] == b["primary"]["number"]


def test_changing_lines_relate():
    for seed in range(30):
        r = cast(seed=seed)
        if r["changing_lines"]:
            assert r["relating"] is not None
            assert 1 <= r["relating"]["number"] <= 64
            return
    pytest.fail("no changing lines in 30 casts")


def test_yarrow_method():
    r = cast(method="yarrow", seed=3)
    assert r["method"] == "yarrow"
    assert len(r["lines"]) == 6
    with pytest.raises(CalculationError):
        cast(method="bones")


# --- astrology readings ---
def test_reading_labels():
    r = reading("general", {"Sun": {"longitude": 159.0},
                            "Moon": {"longitude": 58.5}})
    assert r["label"].startswith("interpretive")
    assert all(p["type"] == "interpretive" for p in r["paragraphs"])
    assert any("Sun in Virgo" in p["text"] for p in r["paragraphs"])


def test_love_foregrounds_venus():
    r = reading("love", {"Sun": {"longitude": 159.0},
                         "Venus": {"longitude": 89.9}})
    assert any("Venus in Gemini" in p["text"] for p in r["paragraphs"])


def test_career_foregrounds_mc():
    r = reading("career", {"Sun": {"longitude": 159.0},
                           "Saturn": {"longitude": 56.2}},
                mc_sign="Cancer")
    assert any("Midheaven in Cancer" in p["text"] for p in r["paragraphs"])


def test_unknown_kind():
    with pytest.raises(CalculationError):
        reading("past-life", {})
