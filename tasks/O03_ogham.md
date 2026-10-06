# O03 — Ogham readings

Third slice of ROADMAP_ORACLES.md.

## Skald
Not runes but staves — the Irish trees cut along the stem-line.
Twenty feda in four aicmí, plus the five forfeda the later scribes
added. The Auraicept's kennings remember them.

## Rúnhild
- `data/ogham.json`: 25 staves — name, ogham glyph (U+1681–U+1699),
  transliteration, aicme, kenning (Bríatharogam Morainn mac Moín per
  McManus 1988), tree gloss (Auraicept; only ~8 names are truly
  trees — disclosed), keywords + divinatory meaning (modern
  synthesis, labeled). Source: "Auraicept na n-Éces; kennings per
  McManus, Ériu 39 (1988)".
- `astroengine/ogham.py`: LAYOUTS = single(1), triad(3), aicme(5),
  wheel(8), grove(12); `oghams(include_forfeda)`, `layouts()`,
  `cast(layout, seed, question, forfeda)` — seeded, reproducible.
  No reversed meanings (ogham reads by position).
- CLI: `ogham --layout triad --seed N --question ... --json`,
  `--list-layouts`, `--no-forfeda`.

## Eldra
Build corpus + module + CLI.

## Sólrún (subagent verification)
`tests/test_ogham.py`: 25 staves, aicme order, glyph codepoints
U+1681–U+1699 in sequence; kenning spot-checks (Beith "withered
foot with fine hair", Dair "highest tree"); all 5 layouts castable;
determinism; suite green.

## Védis
COMMANDS.md section; INTERFACE.md entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row.

## Acceptance gate
`ogham --layout aicme` reads true; suite green; pushed with
verified remote HEAD.
