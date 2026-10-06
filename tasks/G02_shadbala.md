# G02 — Shadbala: the sixfold strength

Second slice of ROADMAP_GAMBHIRA.md.

## Skald
How strong is a planet, truly? The seers weighed each wanderer
six ways and counted the total in virupas. Time to teach the
engine the scales.

## Rúnhild
- `data/shadbala.json`: the constant tables — exaltation points,
  natural strengths (naisargika), directional peaks (dig),
  Kala-bala components, Chesta-bala speed states, minimum
  required virupas per planet, all with source notes.
- `astroengine/shadbala.py`: `shadbala(request)` for Sun..Saturn:
  1. Sthana: Uchcha (0–60 by distance from debilitation point),
     Saptavargaja (7 vargas × dignity scores), Ojhayugma,
     Kendradi, Drekkana.
  2. Dig: directional strength peaking in 1st/4th/7th/10th per
     planet, proportional by house distance.
  3. Kala: Natonnata (day/night), Paksha, Hora-lord, Ayana;
     Tribhaga/Varsha/Masa/Dina where computable, else disclosed
     as omitted.
  4. Chesta: 8 motional states from daily speed, honestly
     simplified and labeled.
  5. Naisargika: fixed table.
  6. Drik: special Vedic aspects (Mars 4/8, Jupiter 5/9,
     Saturn 3/10, all 7th); benefic drishti adds, malefic
     subtracts.
  Totals in virupas + rupas, compared against the classical
  minima. Every approximation disclosed in `limitations`.
- `shadbala` CLI: birth-data flags, `--load` aware, text +
  `--json`.
- Cross-check spot values against an independent implementation
  where available; record the comparison.

## Eldra
Data first, then module, then CLI.

## Sólrún (subagent verification)
`tests/test_shadbala.py`: totals for Volmarr's chart in sane
ranges (Jupiter strong — Hamsa); each bala component non-negative
and bounded; minima comparison present; unknown-time path
explicit; suite green.

## Védis
INTERFACE.md, COMMANDS.md entries.

## Scribe
DEVLOG.md.

## Acceptance gate
Spot cross-check recorded; suite green; pushed with verified
remote HEAD.
