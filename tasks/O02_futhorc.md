# O02 — Anglo-Saxon futhorc rune readings

Second slice of ROADMAP_ORACLES.md.

## Skald
Thirty-three staves, the English row — the twenty-four old ones plus
the island's own: ac, æsc, yr, ior, ear, and the four Northumbrian
late-comers. The Old English Rune Poem speaks for twenty-nine of
them; the last four carry manuscript tradition honestly labeled.

## Rúnhild
- `data/runes_futhorc.json`: 33 runes in traditional futhorc order —
  name, glyph, transliteration, upright keywords + meaning (OE Rune
  Poem for 1–29), merkstave for asymmetric staves per the engine's
  convention. Source: "Old English Rune Poem (historical); four
  Northumbrian runes per manuscript tradition"; historical_claim
  "traditional with modern synthesis".
- No module changes needed (`runecast --system futhorc` already
  wired; O01's clean missing-corpus error disappears once the file
  lands).

## Eldra
Build the corpus; the engine already knows what to do with it.

## Sólrún (subagent verification)
`tests/test_futhorc.py`: 33 runes, order (feoh first, gar last);
spot-check OE poem fidelity (ear = the grave, ior = the river-beast);
all 7 layouts castable; suite green.

## Védis
COMMANDS.md touch; INTERFACE.md touch.

## Scribe
DEVLOG.md entry; TODO.md checkbox.

## Acceptance gate
`runecast --system futhorc --layout cross` reads true; suite green;
pushed with verified remote HEAD.
