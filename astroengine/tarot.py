"""Tarot: the 78-card deck, ten spreads, reversals, seeded draws."""

import json as _json
import random as _random
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError

SPREADS = {
    "single": ["The Card"],
    "three": ["Past", "Present", "Future"],
    "five-cross": ["Present", "Challenge", "Past", "Future", "Outcome"],
    "celtic-cross": [
        "Present", "Challenge", "Past", "Future", "Above (goal)",
        "Below (foundation)", "Self", "Others", "Hopes & Fears", "Outcome",
    ],
    "horseshoe": [
        "Past", "Present", "Hidden Influences", "Obstacles",
        "Others' View", "Action to Take", "Outcome",
    ],
    "relationship": [
        "You", "The Other", "The Bond", "Strengths",
        "Challenges", "Advice", "Outcome",
    ],
    "career": [
        "Current Path", "Strengths", "Challenges",
        "Opportunity", "Outcome",
    ],
    "choice": [
        "The Question", "Path A — Promise", "Path A — Cost",
        "Path B — Promise", "Path B — Cost", "Guidance", "Outcome",
    ],
    "year-ahead": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ],
    "chakra": [
        "Root", "Sacral", "Solar Plexus", "Heart",
        "Throat", "Third Eye", "Crown",
    ],
}


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "tarot.json").read_text(encoding="utf-8"))


def deck() -> list[dict]:
    """The full 78-card deck in order."""
    c = _corpus()
    cards = [{"arcana": "major", **m} for m in c["major_arcana"]]
    cards += [{"arcana": "minor", **m} for m in c["minor_arcana"]]
    return cards


def spreads() -> dict[str, list[str]]:
    """All spread names mapped to their position names."""
    return {k: list(v) for k, v in SPREADS.items()}


def draw(spread: str = "three", seed: int | None = None,
         reversals: bool = True, question: str | None = None) -> dict:
    """Draw cards for a spread. Same seed -> same draw (reproducible)."""
    key = spread.strip().lower().replace(" ", "-").replace("_", "-")
    if key not in SPREADS:
        raise CalculationError(
            f"unknown spread '{spread}'; available: {sorted(SPREADS)}")
    rng = _random.Random(seed)
    cards = deck()
    rng.shuffle(cards)
    positions = SPREADS[key]
    drawn = []
    for i, position in enumerate(positions):
        card = cards[i]
        reversed_ = reversals and rng.random() < 0.5
        face = card["reversed"] if reversed_ else card["upright"]
        drawn.append({
            "position": position,
            "card": card["name"],
            "arcana": card["arcana"],
            "reversed": reversed_,
            "keywords": face["keywords"],
            "meaning": face["meaning"],
        })
    return {
        "spread": key,
        "positions": positions,
        "cards": drawn,
        "reversals": reversals,
        "seed": seed,
        "question": question,
        "kind": "interpretive",
        "source": "Rider-Waite-Smith lineage",
        "historical_claim": "modern synthesis",
    }


__all__ = ["SPREADS", "deck", "spreads", "draw"]
