# H05 — Transit watch

Fifth slice of ROADMAP_HORIZONS.md.

## Skald
The sky keeps moving; the engine should keep watch. A calendar of
coming transits to natal points — including the standing promise of
2026-10-23.

## Rúnhild
- `astroengine/watch.py` (typed path):
  `upcoming_transits(natal_jd_ut, from_jd_ut, to_jd_ut, lat=None,
  lon=None, orb=1.0)` → list of `{date, transit_body, aspect,
  natal_point, orb}`.
  - Transit bodies: Jupiter, Saturn, Uranus, Neptune, Pluto.
  - Natal points: Sun..Pluto + ASC + MC (angles when lat/lon given).
  - Aspects: conjunction, opposition, square, trine.
  - Method: daily scan for orb minima, ternary-refined to the exact
    day; retrograde triple hits each reported.
- CLI: `watch --load NAME --from YYYY-MM-DD --to YYYY-MM-DD`
  (defaults: today → +1 year), `--orb`, `--json`.
- `--remind` is out of scope for this slice (needs user-confirmed
  calendar writes); the October 23 promise lives in the tracked goal.

## Eldra
Build module + CLI. Keep the scan fast enough for a 1-year window.

## Sólrún (subagent verification)
`tests/test_watch.py`: finds Jupiter conjunct natal Mercury on
2026-10-23 for Volmarr (orb < 0.5°); empty window → []; from > to
raises; exact dates are real calendar dates. Full suite green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row.

## Acceptance gate
`watch --load volmarr --from 2026-10-06 --to 2026-11-06` lists the
2026-10-23 Jupiter–Mercury conjunction; suite green; pushed with
verified remote HEAD.
