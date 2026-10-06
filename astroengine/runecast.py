"""Rune casting: the 24 Elder Futhark runes in a variety of layouts.

Merkstave (murk-stave) readings apply only to the asymmetric runes; the
nine symmetric runes traditionally read the same face-up or face-down.
The optional blank rune is a modern invention (Blum, 1980s) and is
flagged as such — off by default.
"""

import json as _json
import random as _random
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError

LAYOUTS = {
    "single": ["The Rune"],
    "norns": ["Urd — What Was", "Verdandi — What Is Becoming",
              "Skuld — What Shall Be"],
    "elements": ["Fire — spirit and will", "Earth — body and resources",
                 "Air — mind and word", "Water — heart and dream"],
    "cross": ["Present", "Challenge", "Past", "Future", "Outcome"],
    "hammer": ["Past", "Present", "Future", "Above — the gods' will",
               "Below — the roots", "Self", "Outcome"],
    "nine-worlds": ["Asgard — the gods' counsel",
                    "Vanaheim — what flourishes",
                    "Alfheim — light and inspiration",
                    "Midgard — your worldly situation",
                    "Jotunheim — disruptive forces",
                    "Svartalfheim — hidden craft",
                    "Niflheim — stillness and rest",
                    "Muspelheim — fire and transformation",
                    "Helheim — endings and release"],
    "wheel": ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November",
              "December"],
}

_BLANK = {
    "name": "The Blank Rune",
    "glyph": "·",
    "transliteration": "(blank)",
    "upright": {
        "keywords": ["the unknown", "wyrd", "the uncarved"],
        "meaning": "The uncarved rune — wyrd not yet woven; the answer is still being written.",
    },
    "merkstave": None,
    "modern_invention": True,
}


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "runes.json").read_text(encoding="utf-8"))


def runes(include_blank: bool = False) -> list[dict]:
    """The 24 Elder Futhark runes in traditional order."""
    rs = list(_corpus()["runes"])
    if include_blank:
        rs = rs + [_BLANK]
    return rs


def layouts() -> dict[str, list[str]]:
    """All layout names mapped to their position names."""
    return {k: list(v) for k, v in LAYOUTS.items()}


def cast(layout: str = "norns", seed: int | None = None,
         merkstave: bool = True, blank: bool = False,
         question: str | None = None) -> dict:
    """Cast runes for a layout. Same seed -> same cast (reproducible)."""
    key = layout.strip().lower().replace(" ", "-").replace("_", "-")
    if key not in LAYOUTS:
        raise CalculationError(
            f"unknown layout '{layout}'; available: {sorted(LAYOUTS)}")
    rng = _random.Random(seed)
    pouch = runes(include_blank=blank)
    rng.shuffle(pouch)
    positions = LAYOUTS[key]
    if len(positions) > len(pouch):
        raise CalculationError(
            f"layout '{key}' needs {len(positions)} runes but the pouch "
            f"holds {len(pouch)}")
    drawn = []
    for i, position in enumerate(positions):
        rune = pouch[i]
        murk = (merkstave and rune.get("merkstave") is not None
                and rng.random() < 0.5)
        face = rune["merkstave"] if murk else rune["upright"]
        drawn.append({
            "position": position,
            "rune": rune["name"],
            "glyph": rune["glyph"],
            "transliteration": rune["transliteration"],
            "merkstave": murk,
            "keywords": face["keywords"],
            "meaning": face["meaning"],
            "modern_invention": bool(rune.get("modern_invention", False)),
        })
    return {
        "layout": key,
        "positions": positions,
        "runes": drawn,
        "merkstave": merkstave,
        "blank_included": blank,
        "seed": seed,
        "question": question,
        "kind": "interpretive",
        "source": "Elder Futhark",
        "historical_claim": "modern synthesis",
    }


__all__ = ["LAYOUTS", "runes", "layouts", "cast"]
