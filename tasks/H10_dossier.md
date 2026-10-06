# H10 — Written natal dossiers

Tenth and final slice of ROADMAP_HORIZONS.md.

## Skald
All the engine's arts — wheels, houses, stars, midpoints, the
draconic deep, the year-lord, the coming sky — gathered into one
written dossier, the whole chart speaking as a single story.

## Rúnhild
- `astroengine/dossier.py` (typed path):
  `natal_dossier(natal_jd_ut, lat, lon, name, target_date)` →
  structured dict + rendered text with sections:
  1. The Pillars (Sun, Moon, ASC)
  2. The Wanderers (planets: sign, house, dignity, rx)
  3. The Chords (tightest natal aspects)
  4. The Bright Ones (fixed star contacts)
  5. The Secret Chords (midpoint activations)
  6. The Soul Beneath (draconic contacts)
  7. The Year-Lord (profection for the target year)
  8. The Coming Sky (3 months of transit watch)
  Draws only on typed modules: houses, aspects, profections,
  watch, stars, midpoints, draconic, directions (solar arc hits?).
  Descriptive synthesis from computed facts; traditional lore
  labeled; symbolic framing, never causal claims.
- CLI: `dossier --load NAME --target-date YYYY-MM-DD --json`
  (+ `--out FILE` to write the text).

## Eldra
Build module + CLI.

## Sólrún (subagent verification)
`tests/test_dossier.py`: all eight sections present; Volmarr's
dossier names his Sun/Moon/ASC correctly and includes the Oct 23
transit in the Coming Sky; suite green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry; capabilities/
tool schemas if the command registry needs them.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row; close the Horizons
roadmap (ROADMAP_HORIZONS.md completion note).

## Acceptance gate
`dossier --load volmarr` writes the full story; suite green; pushed
with verified remote HEAD. The Horizons program is complete.
