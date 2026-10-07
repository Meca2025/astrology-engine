"""Sólrún's scrutiny of the Lenormand line."""

import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.lenormand import (  # noqa: E402
    cards, spreads, draw, tableau, pair_reading, chain,
    knight_positions, mirror_of, _pos_to_rc, _rc_to_pos)
from astroengine.models import CalculationError  # noqa: E402


# --- corpus ---
def test_deck_complete():
    deck = cards()
    assert len(deck) == 36
    assert [c["number"] for c in deck] == list(range(1, 37))
    for c in deck:
        for field in ("number", "name", "playing_card", "keywords",
                      "meaning", "timing"):
            assert c[field], (c["number"], field)
        assert len(c["keywords"]) >= 3


def test_significators():
    by_num = {c["number"]: c for c in cards()}
    assert by_num[28]["name"] == "Man"
    assert by_num[29]["name"] == "Woman"


def test_traditional_playing_cards():
    by_num = {c["number"]: c["playing_card"] for c in cards()}
    assert by_num[1] == "9 of Hearts"
    assert by_num[25] == "Ace of Clubs"
    assert by_num[31] == "Ace of Diamonds"
    assert by_num[36] == "6 of Clubs"


# --- spreads ---
def test_spread_counts():
    s = spreads()
    assert len(s["single"]) == 1
    assert len(s["line3"]) == 3
    assert len(s["line5"]) == 5
    assert len(s["line7"]) == 7
    assert len(s["nine"]) == 9


def test_seeded_draw_reproducible():
    a = draw("line5", seed=7)
    b = draw("line5", seed=7)
    assert ([c["card"]["name"] for c in a["cards"]] ==
            [c["card"]["name"] for c in b["cards"]])
    assert a["chain"] == b["chain"]


def test_no_duplicate_cards_in_draw():
    for name in ("single", "line3", "line5", "line7", "nine"):
        d = draw(name, seed=3)
        names = [c["card"]["name"] for c in d["cards"]]
        assert len(set(names)) == len(names), name


def test_chain_links_pairs():
    d = draw("line3", seed=7)
    assert len(d["chain"]) == 2
    first_two = [c["card"]["name"] for c in d["cards"][:2]]
    assert first_two[0] in d["chain"][0] and first_two[1] in d["chain"][0]


def test_unknown_spread_suggests():
    with pytest.raises(CalculationError) as exc:
        draw("tableu")  # near-miss of tableau
    assert "tableau" in str(exc.value)


# --- tableau geometry ---
def test_position_roundtrip():
    for p in range(1, 37):
        r, c = _pos_to_rc(p)
        assert _rc_to_pos(r, c) == p
        assert 0 <= r < 4 and 0 <= c < 9


def test_tableau_has_all_36_once():
    t = tableau(seed=11)
    names = [cell["card"]["name"] for cell in t["grid"]]
    assert len(names) == 36 and len(set(names)) == 36


def test_houses_follow_card_numbers():
    t = tableau(seed=11)
    for cell in t["grid"]:
        assert cell["house"]["number"] == cell["position"]
    # position 24 sits in the House of the Heart
    assert t["grid"][23]["house"]["card"] == "Heart"


def test_knighting_hand_verified():
    # Position 1 (corner): knight moves land on 12 and 20 only.
    assert knight_positions(1) == [12, 20]
    # Position 11 (row 2, col 2): hand-checked L-moves.
    assert knight_positions(11) == [4, 22, 28, 30]


def test_knighting_in_tableau_agrees():
    t = tableau(seed=7, significator="woman")
    sig_pos = t["significator"]["position"]
    expect = knight_positions(sig_pos)
    assert [k["position"] for k in t["knighting"]] == expect
    # knighted cards really are those positions' cards
    by_pos = {c["position"]: c["card"]["name"] for c in t["grid"]}
    for k in t["knighting"]:
        assert k["card"] == by_pos[k["position"]]


def test_mirroring_pairs():
    assert mirror_of(1) == 36
    assert mirror_of(18) == 19
    t = tableau(seed=7)
    assert len(t["mirroring"]) == 18
    for m in t["mirroring"]:
        a, b = m["positions"]
        assert b == 37 - a


def test_corners_and_fate_line():
    t = tableau(seed=7)
    assert len(t["corners"]) == 4
    by_pos = {c["position"]: c["card"]["name"] for c in t["grid"]}
    assert t["corners"] == [by_pos[p] for p in (1, 9, 28, 36)]
    sig_row = t["significator"]["row"]
    assert len(t["fate_line"]) == 9
    assert t["significator"]["card"] in t["fate_line"]
    row_cards = [c["card"]["name"] for c in t["grid"] if c["row"] == sig_row]
    assert t["fate_line"] == row_cards


def test_significator_choice():
    man = tableau(seed=7, significator="man")
    woman = tableau(seed=7, significator="woman")
    assert man["significator"]["number"] == 28
    assert woman["significator"]["number"] == 29
    with pytest.raises(CalculationError):
        tableau(significator="child")


def test_pair_reading_fuses():
    deck = cards()
    text = pair_reading(deck[0], deck[1])
    assert "Rider" in text and "Clover" in text
    assert deck[0]["keywords"][0] in text
