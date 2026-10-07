"""Cartomancy: fortune-telling with the standard 52-card French deck.

Old European folk cartomancy. Each suit rules a traditional domain --
Hearts love and home, Diamonds money and enterprise, Clubs work and
action, Spades challenges and transformation. Like Lenormand, this
tradition reads in *combination*: pairs and chains carry the sentence,
so this module foregrounds pair fusion. No reversals in the folk
tradition.

All interpretation is symbolic counsel, never computed fact.
"""

import json as _json
import random as _random
from collections import Counter as _Counter
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError
from .recovery import suggest as _suggest

# Spread name -> position names.
SPREADS = {
    "single": ["The Card"],
    "line3": ["Past", "Present", "Future"],
    "line5": ["Past", "Present", "Bridge", "Near Future", "Outcome"],
    "line7": ["Distant Past", "Past", "Present", "Near Future",
              "Outcome", "Advice", "Long-term Result"],
    "nine": ["Past Roots", "Past", "Past Crown",
             "Present Roots", "Focus — the heart of the matter",
             "Present Crown",
             "Future Roots", "Future", "Future Crown"],
    "fifteen": ([f"Past — {i}" for i in range(1, 6)] +
                [f"Present — {i}" for i in range(1, 6)] +
                [f"Future — {i}" for i in range(1, 6)]),
}

_COURTS = ("jack", "queen", "king")


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "playing_cards.json").read_text(encoding="utf-8"))


def cards() -> list[dict]:
    """The full 52-card deck, suit-major order."""
    return [dict(c) for c in _corpus()["cards"]]


def suits() -> dict[str, list[str]]:
    """The four suits mapped to their traditional domain keywords."""
    return {k: list(v) for k, v in _corpus()["suit_domains"].items()}


def spreads() -> dict[str, list[str]]:
    """All spread names mapped to their position names."""
    return {k: list(v) for k, v in SPREADS.items()}


def suit_of(card: dict) -> str:
    """The suit of a card dict."""
    return card["suit"]


def is_court(card: dict) -> bool:
    """True for jacks, queens, and kings."""
    return card["rank"] in _COURTS


def dominant_suit(drawn: list[dict]) -> dict:
    """The most frequent suit in a draw, with its traditional domain."""
    counts = _Counter(d["card"]["suit"] for d in drawn)
    suit, n = counts.most_common(1)[0]
    return {"suit": suit, "count": n, "domain": suits()[suit]}


def _resolve_spread(spread: str) -> str:
    key = spread.strip().lower().replace(" ", "-").replace("_", "-")
    if key in SPREADS:
        return key
    hints = _suggest(key, sorted(SPREADS))
    hint = f" did you mean: {', '.join(hints)}?" if hints else ""
    raise CalculationError(
        f"unknown cartomancy spread '{spread}'; available: "
        f"{sorted(SPREADS)}.{hint}")


def pair_reading(a: dict, b: dict) -> str:
    """Fuse two cards into one interpretive sentence (mechanical, labeled).

    Takes the first keyword of each card and joins them; a deterministic
    fusion aid, not channeled lore.
    """
    ka = a["keywords"][0] if a["keywords"] else a["name"].lower()
    kb = b["keywords"][0] if b["keywords"] else b["name"].lower()
    return (f"{a['name']} + {b['name']}: {ka} meeting {kb} — "
            f"{a['meaning']} Seen through {b['name'].lower()}, "
            f"it speaks of {kb}.")


def chain(drawn: list[dict]) -> list[str]:
    """Pair-wise chain readings across a spread (card 1+2, 2+3, ...)."""
    cards_only = [d["card"] for d in drawn]
    return [pair_reading(cards_only[i], cards_only[i + 1])
            for i in range(len(cards_only) - 1)]


def draw(spread: str = "line3", seed: int | None = None,
         question: str | None = None) -> dict:
    """Draw cards for a spread. Same seed -> same draw (reproducible)."""
    key = _resolve_spread(spread)
    rng = _random.Random(seed)
    deck = cards()
    rng.shuffle(deck)
    drawn = []
    for i, position in enumerate(SPREADS[key]):
        card = deck[i]
        drawn.append({
            "position": position,
            "card": card,
            "keywords": list(card["keywords"]),
            "meaning": card["meaning"],
        })
    result = {
        "system": "Playing-card cartomancy",
        "spread": key,
        "seed": seed,
        "question": question,
        "cards": drawn,
        "dominant_suit": dominant_suit(drawn),
        "courts": [d["card"]["name"] for d in drawn if is_court(d["card"])],
        "interpretive": True,
    }
    if len(drawn) > 1:
        result["chain"] = chain(drawn)
    return result
