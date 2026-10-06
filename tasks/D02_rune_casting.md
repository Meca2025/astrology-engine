# D02 — Rune casting: rune readings in a variety of layouts

Volmarr's commission (2026-10-06): *"also add rune readings in a verity
of layouts"*.

A fifth divination system: cast the 24 Elder Futhark runes in traditional
and Norse-flavored layouts, with merkstave (reversed) readings and
seeded reproducibility.

## Skald — vision and naming

`runecast` — the rune-pouch oracle.

## Rúnhild — architecture

### Data (`data/runes.json`)
- 24 Elder Futhark runes in traditional order: name, glyph (unicode),
  transliteration, upright {keywords, meaning}, merkstave {keywords,
  meaning} or `null` for the nine symmetric runes (Gebo, Hagalaz,
  Nauthiz, Isa, Jera, Eihwaz, Sowilo, Ingwaz, Dagaz) which traditionally
  read the same face-up or face-down — encoded honestly.
- Optional 25th blank rune, **flagged as a modern invention** (Blum,
  1980s), off by default (`--blank`).
- Meanings: original one-line distillations, `historical_claim:
  "modern synthesis"`.

### Engine (`astroengine/runecast.py`)
- `cast(layout="norns", seed=None, merkstave=True, blank=False,
  question=None)` — seeded `random.Random`, draw without replacement;
  50% merkstave chance for asymmetric runes only.
- Layouts (7):
  - `single` — The Rune (1)
  - `norns` — Urd / Verdandi / Skuld (3)
  - `elements` — Fire, Earth, Air, Water (4)
  - `cross` — Present, Challenge, Past, Future, Outcome (5)
  - `hammer` — seven-rune Mjölnir spread (7)
  - `nine-worlds` — Asgard, Vanaheim, Alfheim, Midgard, Jotunheim,
    Svartalfheim, Niflheim, Muspelheim, Helheim (9)
  - `wheel` — the twelve-month year wheel (12)

### CLI
`runecast --layout nine-worlds --seed 7 --question "..." --json`,
`--list-layouts`, `--no-merkstave`, `--blank`, `--save` (chart library).

## Sólrún — verification

`tests/test_runecast.py`: 24 runes load in Futhark order; symmetric
runes never merkstave; seeded cast reproducible; all layout positions
unique and covered; blank rune adds a 25th flagged modern; unknown
layout raises. Full suite green.

## Védis / Scribe

COMMANDS.md section; INTERFACE.md + COMPONENT_INDEX.md entries; DEVLOG;
TODO checkbox; README quartet row gains `runecast`. Push task doc before
code; push after green; verify remote HEAD; sync local clone.
