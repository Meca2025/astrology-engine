"""Lenormand: the 36-card Petit Lenormand, classic spreads, Grand Tableau.

The Petit Lenormand is 19th-century European folk cartomancy. It is read in
*combination* -- pairs and chains carry the sentence -- so this module
foregrounds pair fusion alongside single-card keywords. There are no
reversals in the Lenormand tradition.

The Grand Tableau lays all 36 cards in a 4x9 grid. Traditional techniques
implemented here as documented geometric rules:
- Houses: position N sits in the house of card N (position 24 = House of
  the Heart); the house flavors the card that lands in it.
- Knighting: cards a chess-knight's move from the significator.
- Mirroring: positions equidistant from the center mirror each other
  (position i mirrors position 37 - i).
- Corners: the four corner cards summarize the reading's theme.
- Fate line: the row holding the significator.

All interpretation is symbolic counsel, never computed fact.
"""

import json as _json
import random as _random
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError
from .recovery import suggest as _suggest

# Spread name -> position names. Tableau is handled by tableau().
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
}

_TABLEAU_ROWS, _TABLEAU_COLS = 4, 9

_SIGNIFICATORS = {"man": 28, "woman": 29}


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "lenormand.json").read_text(encoding="utf-8"))


def cards() -> list[dict]:
    """The full 36-card deck in traditional order."""
    return [dict(c) for c in _corpus()["cards"]]


def spreads() -> dict[str, list[str]]:
    """All spread names mapped to their position names (tableau listed too)."""
    out = {k: list(v) for k, v in SPREADS.items()}
    out["tableau"] = ["Grand Tableau — 36 cards, 4 rows x 9"]
    return out


def _by_number(number: int) -> dict:
    for c in cards():
        if c["number"] == number:
            return c
    raise CalculationError(f"no Lenormand card numbered {number}")


def _resolve_spread(spread: str) -> str:
    key = spread.strip().lower().replace(" ", "-").replace("_", "-")
    if key in SPREADS:
        return key
    hints = _suggest(key, sorted(SPREADS) + ["tableau"])
    hint = f" did you mean: {', '.join(hints)}?" if hints else ""
    raise CalculationError(
        f"unknown Lenormand spread '{spread}'; available: "
        f"{sorted(SPREADS) + ['tableau']}.{hint}")


def pair_reading(a: dict, b: dict) -> str:
    """Fuse two cards into one interpretive sentence (mechanical, labeled).

    Takes the first keyword of each card and joins them; this is a
    deterministic fusion aid, not channeled lore.
    """
    ka = a["keywords"][0] if a["keywords"] else a["name"].lower()
    kb = b["keywords"][0] if b["keywords"] else b["name"].lower()
    return (f"{a['name']} + {b['name']}: {ka} meeting {kb} — "
            f"{a['meaning']} Seen through {b['name'].lower()}, "
            f"it speaks of {kb}.")


def chain(drawn: list[dict]) -> list[str]:
    """Pair-wise chain readings across a line spread (card 1+2, 2+3, ...)."""
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
    positions = SPREADS[key]
    drawn = []
    for i, position in enumerate(positions):
        card = deck[i]
        drawn.append({
            "position": position,
            "card": card,
            "keywords": list(card["keywords"]),
            "meaning": card["meaning"],
            "timing": card["timing"],
            "playing_card": card["playing_card"],
        })
    result = {
        "system": "Petit Lenormand",
        "spread": key,
        "seed": seed,
        "question": question,
        "cards": drawn,
        "interpretive": True,
    }
    if len(drawn) > 1:
        result["chain"] = chain(drawn)
    return result


def _pos_to_rc(position: int) -> tuple[int, int]:
    """1-based position -> (row, col), both 0-based, row-major 4x9."""
    return (position - 1) // _TABLEAU_COLS, (position - 1) % _TABLEAU_COLS


def _rc_to_pos(row: int, col: int) -> int:
    return row * _TABLEAU_COLS + col + 1


def knight_positions(position: int) -> list[int]:
    """Positions a chess-knight's move away from `position` on the 4x9 grid."""
    row, col = _pos_to_rc(position)
    out = []
    for dr, dc in ((2, 1), (2, -1), (-2, 1), (-2, -1),
                   (1, 2), (1, -2), (-1, 2), (-1, -2)):
        r, c = row + dr, col + dc
        if 0 <= r < _TABLEAU_ROWS and 0 <= c < _TABLEAU_COLS:
            out.append(_rc_to_pos(r, c))
    return sorted(out)


def mirror_of(position: int) -> int:
    """The position mirroring `position` across the tableau center."""
    return 37 - position


def tableau(seed: int | None = None, question: str | None = None,
            significator: str = "woman") -> dict:
    """Lay the Grand Tableau: all 36 cards with houses and techniques."""
    sig_key = significator.strip().lower()
    if sig_key not in _SIGNIFICATORS:
        hints = _suggest(sig_key, sorted(_SIGNIFICATORS))
        hint = f" did you mean: {', '.join(hints)}?" if hints else ""
        raise CalculationError(
            f"unknown significator '{significator}'; choose "
            f"{sorted(_SIGNIFICATORS)}.{hint}")
    sig_number = _SIGNIFICATORS[sig_key]

    rng = _random.Random(seed)
    deck = cards()
    rng.shuffle(deck)

    grid = []
    sig_pos = None
    for position in range(1, 37):
        card = deck[position - 1]
        house_card = _by_number(position)
        row, col = _pos_to_rc(position)
        if card["number"] == sig_number:
            sig_pos = position
        grid.append({
            "position": position,
            "row": row + 1,
            "col": col + 1,
            "card": card,
            "house": {
                "card": house_card["name"],
                "number": house_card["number"],
                "domain": list(house_card["keywords"]),
            },
        })

    knights = knight_positions(sig_pos)
    knight_cards = [{"position": p,
                     "card": grid[p - 1]["card"]["name"]}
                    for p in knights]
    mirrors = [{"positions": (i, mirror_of(i)),
                "cards": (grid[i - 1]["card"]["name"],
                          grid[mirror_of(i) - 1]["card"]["name"])}
               for i in range(1, 19)]
    corners = [grid[p - 1]["card"]["name"] for p in (1, 9, 28, 36)]
    sig_row = _pos_to_rc(sig_pos)[0] + 1
    fate_line = [grid[p - 1]["card"]["name"]
                 for p in range(1, 37) if _pos_to_rc(p)[0] + 1 == sig_row]

    return {
        "system": "Petit Lenormand",
        "spread": "tableau",
        "seed": seed,
        "question": question,
        "significator": {
            "card": _by_number(sig_number)["name"],
            "number": sig_number,
            "position": sig_pos,
            "row": _pos_to_rc(sig_pos)[0] + 1,
            "col": _pos_to_rc(sig_pos)[1] + 1,
        },
        "grid": grid,
        "knighting": knight_cards,
        "mirroring": mirrors,
        "corners": corners,
        "fate_line": fate_line,
        "interpretive": True,
    }
