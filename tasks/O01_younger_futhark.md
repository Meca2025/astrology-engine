# O01 — Younger Futhark rune readings

First slice of ROADMAP_ORACLES.md.

## Skald
The younger row — sixteen staves, the Viking Age's own hand. The
Norwegian and Icelandic rune poems remember their names; the stones
remember two hands, long-branch and short-twig.

## Rúnhild
- `data/runes_younger.json`: 16 runes in traditional order —
  name, long-branch glyph, short-twig glyph, transliteration,
  upright keywords + meaning (from the Norwegian & Icelandic rune
  poems), merkstave where the rune is asymmetric. Source labeled:
  "Norwegian & Icelandic rune poems (historical)"; historical_claim
  "traditional with modern synthesis".
- `astroengine/runecast.py`: `cast(..., system="elder")` — system
  selects the corpus file (`elder`/`younger`/`futhorc`); the seven
  layouts are shared (all fit a 16-rune pouch). Result carries
  `"source": "Younger Futhark"` and the variant glyphs.
- CLI: `runecast --system younger` (choices: elder, younger, futhorc
  — futhorc corpus lands in O02; unknown system errors clearly).

## Eldra
Build corpus + generalize cast() + CLI flag.

## Sólrún (subagent verification)
`tests/test_younger_futhark.py`: 16 runes, order starts fé; both
glyph variants present; cast --system younger draws 16-pouch (wheel
layout impossible → clear error since 12 ≤ 16 fine — actually all 7
layouts fit); --system bogus errors; suite green.

## Védis
COMMANDS.md note; INTERFACE.md entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row (runecast line).

## Acceptance gate
`runecast --system younger --layout norns` reads true; suite green;
pushed with verified remote HEAD.
