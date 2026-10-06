"""Rune casting: Elder Futhark, Younger Futhark, or Anglo-Saxon futhorc
in a variety of layouts.

Merkstave (murk-stave) readings apply only to the asymmetric runes;
symmetric runes traditionally read the same face-up or face-down.
The optional blank rune is a modern invention (Blum, 1980s) and is
flagged as such — off by default, Elder Futhark only.
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


_SYSTEM_FILES = {
    "elder": "runes.json",
    "younger": "runes_younger.json",
    "futhorc": "runes_futhorc.json",
}
_SYSTEM_NAMES = {
    "elder": "Elder Futhark",
    "younger": "Younger Futhark",
    "futhorc": "Anglo-Saxon Futhorc",
}


@_lru_cache(maxsize=3)
def _load_corpus(key: str) -> dict:
    path = _Path(__file__).parent.parent / "data" / _SYSTEM_FILES[key]
    if not path.exists():
        raise CalculationError(
            f"the {_SYSTEM_NAMES[key]} corpus is not yet forged "
            f"(expected at data/{_SYSTEM_FILES[key]})")
    return _json.loads(path.read_text(encoding="utf-8"))


def _corpus(system: str = "elder") -> dict:
    key = system.strip().lower()
    if key not in _SYSTEM_FILES:
        raise CalculationError(
            f"unknown rune system '{system}'; "
            f"available: {sorted(_SYSTEM_FILES)}")
    return _load_corpus(key)


def runes(include_blank: bool = False, system: str = "elder") -> list[dict]:
    """The runes of a system in traditional order."""
    rs = list(_corpus(system)["runes"])
    if include_blank:
        if system.strip().lower() != "elder":
            raise CalculationError(
                "the blank rune is an Elder Futhark modernism only")
        rs = rs + [_BLANK]
    return rs


def systems() -> dict[str, str]:
    """Available rune systems mapped to their display names."""
    return dict(_SYSTEM_NAMES)


def layouts() -> dict[str, list[str]]:
    """All layout names mapped to their position names."""
    return {k: list(v) for k, v in LAYOUTS.items()}


def cast(layout: str = "norns", seed: int | None = None,
         merkstave: bool = True, blank: bool = False,
         question: str | None = None, system: str = "elder") -> dict:
    """Cast runes for a layout. Same seed -> same cast (reproducible)."""
    sys_key = system.strip().lower()
    if sys_key not in _SYSTEM_FILES:
        raise CalculationError(
            f"unknown rune system '{system}'; "
            f"available: {sorted(_SYSTEM_FILES)}")
    key = layout.strip().lower().replace(" ", "-").replace("_", "-")
    if key not in LAYOUTS:
        raise CalculationError(
            f"unknown layout '{layout}'; available: {sorted(LAYOUTS)}")
    rng = _random.Random(seed)
    pouch = runes(include_blank=blank, system=sys_key)
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
        "source": _SYSTEM_NAMES[sys_key],
        "historical_claim": _corpus(sys_key).get("historical_claim",
                                                 "modern synthesis"),
    }


__all__ = ["LAYOUTS", "runes", "layouts", "cast", "systems"]
