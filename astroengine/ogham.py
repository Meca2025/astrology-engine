"""Ogham readings: the Irish tree-staves in grove layouts.

Twenty feda in four aicmí plus the five forfeda, with kennings from
the Auraicept na n-Éces (Bríatharogam Morainn mac Moín, McManus
1988). Divinatory meanings are modern synthesis, labeled as such.
Ogham reads by position — no reversed meanings.
"""

import json as _json
import random as _random
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError

LAYOUTS = {
    "single": ["The Stave"],
    "triad": ["Root — what grounds it",
              "Trunk — what stands",
              "Crown — what grows"],
    "aicme": ["Aicme Beith — the body",
              "Aicme Huath — the trial",
              "Aicme Muin — the craft",
              "Aicme Ailm — the spirit",
              "Forfeda — the mystery beyond"],
    "wheel": ["East — dawn and beginnings",
              "Southeast — green growth",
              "South — full light",
              "Southwest — harvest",
              "West — dusk and release",
              "Northwest — shadow work",
              "North — stillness",
              "Northeast — return"],
    "grove": ["The situation",
              "The root",
              "The obstacle",
              "The ally",
              "The past",
              "The heart",
              "The near future",
              "The self",
              "The kin",
              "The hope",
              "The warning",
              "The outcome"],
}


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "ogham.json").read_text(encoding="utf-8"))


def oghams(include_forfeda: bool = True) -> list[dict]:
    """The ogham staves in aicme order."""
    staves = list(_corpus()["staves"])
    if not include_forfeda:
        staves = [s for s in staves if s["aicme"] != "Forfeda"]
    return staves


def layouts() -> dict[str, list[str]]:
    """All layout names mapped to their position names."""
    return {k: list(v) for k, v in LAYOUTS.items()}


def cast(layout: str = "triad", seed: int | None = None,
         question: str | None = None,
         forfeda: bool = True) -> dict:
    """Cast ogham staves for a layout. Same seed -> same cast."""
    key = layout.strip().lower().replace(" ", "-").replace("_", "-")
    if key not in LAYOUTS:
        raise CalculationError(
            f"unknown layout '{layout}'; available: {sorted(LAYOUTS)}")
    rng = _random.Random(seed)
    pouch = oghams(include_forfeda=forfeda)
    rng.shuffle(pouch)
    positions = LAYOUTS[key]
    if len(positions) > len(pouch):
        raise CalculationError(
            f"layout '{key}' needs {len(positions)} staves but the grove "
            f"holds {len(pouch)}")
    # The aicme layout is a true census: each position draws from its
    # own aicme. With forfeda excluded, the fifth position (the mystery
    # beyond) draws wild from the whole grove.
    aicme_of_position = (["Beith", "Huath", "Muin", "Ailm", "Forfeda"]
                         if key == "aicme" else [None] * len(positions))
    drawn = []
    used: set[str] = set()
    for i, position in enumerate(positions):
        family = aicme_of_position[i]
        if family is not None:
            pool = [s for s in pouch if s["aicme"] == family
                    and s["name"] not in used] or [s for s in pouch
                                                   if s["name"] not in used]
        else:
            pool = [s for s in pouch if s["name"] not in used]
        if not pool:
            raise CalculationError(
                f"layout '{key}' needs more staves than the grove holds")
        stave = rng.choice(pool)
        used.add(stave["name"])
        drawn.append({
            "position": position,
            "stave": stave["name"],
            "glyph": stave["glyph"],
            "transliteration": stave["transliteration"],
            "aicme": stave["aicme"],
            "kenning": stave["kenning"],
            "tree": stave["tree"],
            "keywords": stave["keywords"],
            "meaning": stave["meaning"],
        })
    return {
        "layout": key,
        "positions": positions,
        "staves": drawn,
        "forfeda_included": forfeda,
        "seed": seed,
        "question": question,
        "kind": "interpretive",
        "source": "Ogham",
        "historical_claim": _corpus().get("historical_claim",
                                          "traditional with modern synthesis"),
    }


__all__ = ["LAYOUTS", "oghams", "layouts", "cast"]
