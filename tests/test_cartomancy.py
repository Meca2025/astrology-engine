"""Sólrún's scrutiny of the playing-card cartomancy line."""

import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.cartomancy import (  # noqa: E402
    cards, suits, spreads, draw, pair_reading, chain,
    suit_of, is_court, dominant_suit)
from astroengine.models import CalculationError  # noqa: E402


# --- corpus ---
def test_deck_complete():
    deck = cards()
    assert len(deck) == 52
    assert len({c["name"] for c in deck}) == 52


def test_suit_rank_census():
    deck = cards()
    by_suit = {}
    for c in deck:
        by_suit.setdefault(c["suit"], set()).add(c["rank"])
    assert set(by_suit) == {"hearts", "diamonds", "clubs", "spades"}
    expect_ranks = {"ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                    "jack", "queen", "king"}
    for suit, ranks in by_suit.items():
        assert ranks == expect_ranks, suit


def test_card_fields():
    for c in cards():
        for field in ("suit", "rank", "name", "keywords", "meaning"):
            assert c[field], (c["name"], field)
        assert len(c["keywords"]) >= 3


def test_suit_domains():
    s = suits()
    assert set(s) == {"hearts", "diamonds", "clubs", "spades"}
    assert "love" in s["hearts"]
    assert "money" in s["diamonds"]
    assert "work" in s["clubs"]
    assert "challenges" in s["spades"]


def test_court_detection():
    deck = cards()
    courts = [c for c in deck if is_court(c)]
    assert len(courts) == 12
    assert {c["rank"] for c in courts} == {"jack", "queen", "king"}


# --- spreads ---
def test_spread_counts():
    s = spreads()
    assert len(s["single"]) == 1
    assert len(s["line3"]) == 3
    assert len(s["line5"]) == 5
    assert len(s["line7"]) == 7
    assert len(s["nine"]) == 9
    assert len(s["fifteen"]) == 15


def test_seeded_draw_reproducible():
    a = draw("fifteen", seed=7)
    b = draw("fifteen", seed=7)
    assert ([c["card"]["name"] for c in a["cards"]] ==
            [c["card"]["name"] for c in b["cards"]])
    assert a["chain"] == b["chain"]
    assert a["dominant_suit"] == b["dominant_suit"]


def test_no_duplicate_cards_in_draw():
    for name in spreads():
        d = draw(name, seed=3)
        names = [c["card"]["name"] for c in d["cards"]]
        assert len(set(names)) == len(names), name


def test_dominant_suit_counts():
    d = draw("fifteen", seed=7)
    dom = d["dominant_suit"]
    assert dom["suit"] in suits()
    actual = sum(1 for c in d["cards"] if c["card"]["suit"] == dom["suit"])
    assert dom["count"] == actual
    assert dom["domain"] == suits()[dom["suit"]]


def test_chain_links_pairs():
    d = draw("line3", seed=7)
    assert len(d["chain"]) == 2
    first_two = [c["card"]["name"] for c in d["cards"][:2]]
    assert first_two[0] in d["chain"][0] and first_two[1] in d["chain"][0]


def test_suit_of():
    assert suit_of(cards()[0]) == "hearts"
    assert suit_of(cards()[51]) == "spades"


def test_unknown_spread_suggests():
    with pytest.raises(CalculationError) as exc:
        draw("line-3")  # near-miss of line3
    assert "line3" in str(exc.value)


def test_pair_reading_fuses():
    deck = cards()
    text = pair_reading(deck[0], deck[13])
    assert "Ace of Hearts" in text and "Ace of Diamonds" in text
