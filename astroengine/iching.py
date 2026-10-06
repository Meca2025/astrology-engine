"""I-Ching: casting by coins or simulated yarrow stalks.

Coin method: three coins tossed per line; heads=3, tails=2.
  6 = old yin (changing), 7 = young yang, 8 = young yin, 9 = old yang (changing).
Yarrow simulation: reproduces the classical 1/16 : 5/16 : 7/16 : 3/16
distribution of 6/7/8/9 via a single 16-sided draw per line.
"""

import json as _json
import random as _random
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "iching.json").read_text(encoding="utf-8"))


def _by_binary() -> dict[str, dict]:
    return {h["binary"]: h for h in _corpus()["hexagrams"]}


def _coin_line(rng: _random.Random) -> int:
    return sum(3 if rng.random() < 0.5 else 2 for _ in range(3))


def _yarrow_line(rng: _random.Random) -> int:
    # classical probabilities: 6:1/16, 7:5/16, 8:7/16, 9:3/16
    roll = rng.randrange(16)
    if roll == 0:
        return 6
    if roll < 6:
        return 7
    if roll < 13:
        return 8
    return 9


def _lines_to_hexagram(values: list[int]) -> dict:
    table = _by_binary()
    binary = "".join("1" if v in (7, 9) else "0" for v in values)
    return table[binary]


def cast(question: str | None = None, method: str = "coins",
         seed: int | None = None) -> dict:
    """Cast a hexagram. Same seed -> same cast (reproducible)."""
    method = (method or "coins").strip().lower()
    if method not in ("coins", "yarrow"):
        raise CalculationError(
            f"unknown casting method '{method}': use coins or yarrow")
    rng = _random.Random(seed)
    toss = _coin_line if method == "coins" else _yarrow_line
    values = [toss(rng) for _ in range(6)]  # bottom line first
    primary = _lines_to_hexagram(values)
    changing = [i + 1 for i, v in enumerate(values) if v in (6, 9)]
    relating = None
    if changing:
        moved = [9 if v == 6 else 6 if v == 9 else v for v in values]
        relating = _lines_to_hexagram(moved)
    return {
        "question": question,
        "method": method,
        "seed": seed,
        "lines": values,
        "primary": _reading_of(primary),
        "changing_lines": changing,
        "relating": _reading_of(relating) if relating else None,
        "kind": "interpretive",
        "source": "Classical I-Ching lineage",
        "historical_claim": "modern synthesis; original renderings",
    }


def _reading_of(hexagram: dict) -> dict:
    return {
        "number": hexagram["number"],
        "name": hexagram["name"],
        "chinese": hexagram["chinese"],
        "judgment": hexagram["judgment"],
        "meaning": hexagram["meaning"],
    }


def hexagrams() -> list[dict]:
    """All 64 hexagrams in King Wen order."""
    return [_reading_of(h) for h in _corpus()["hexagrams"]]


__all__ = ["cast", "hexagrams"]
