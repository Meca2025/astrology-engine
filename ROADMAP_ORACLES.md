# Oracles Roadmap — more divination arts for the engine

A second divination program, built with the Mythic Engineering rites:
task scroll before code, six roles per slice (Skald → Rúnhild →
Eldra → Sólrún → Védis → Scribe), independent Sólrún verification
subagent, full suite green, push after every slice with the standing
rule honored (fetch, diff, never overwrite Volmarr's edits, never
force-push).

Provenance discipline: every corpus labels its sources and its
historical claim. Rune-poem meanings are historical; tree-lore and
blank runes are flagged modern; Chinese/Tibetan computations follow
the standard sexagenary and elemental algorithms with the anchors
verified, not remembered.

## Slices

- **O01 — Younger Futhark**: `data/runes_younger.json` (16 runes;
  meanings from the Norwegian & Icelandic rune poems; long-branch and
  short-twig glyph variants); `runecast --system younger`.
- **O02 — Anglo-Saxon futhorc**: `data/runes_futhorc.json` (33 runes;
  meanings from the Old English Rune Poem); `runecast --system futhorc`.
- **O03 — Ogham**: `data/ogham.json` (20 + 5 forfeda; kennings from
  Auraicept na n-Éces, tree lore labeled traditional-late); new
  `ogham` CLI with five ogham layouts.
- **O04 — Chinese zodiac**: `astroengine/chinese.py` + `chinese` CLI
  (year animal, element, stem-branch, yin/yang, trine allies, secret
  friend, clash, NaYin).
- **O05 — Four Pillars (BaZi)**: solar terms via Swiss Ephemeris;
  year/month/day/hour pillars with verified ganzhi anchors.
- **O06 — Tibetan astrology**: `astroengine/tibetan.py` + `tibetan`
  CLI (element-animal year, mewa, parkha, five personal elements —
  srog, lus, dbang-thang, bla, rlung-ta).

Each slice: task doc in `tasks/`, corpus/module, CLI, tests,
COMMANDS.md + INTERFACE.md + README + DEVLOG + TODO, capability/tool
schema entries, Sólrún subagent verification, push with verified
remote HEAD, local sync. Then the next slice, without being asked.
