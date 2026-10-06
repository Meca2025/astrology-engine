# H08 — Asteroids and midpoints

Eighth slice of ROADMAP_HORIZONS.md.

## Skald
The small wanderers carry the subtle stories — Chiron the wound that
teaches, Ceres the grain-mother, Pallas the strategist — and between
every two planets a midpoint hums its secret chord.

## Rúnhild
- `astroengine/asteroids.py` (typed path):
  `asteroid_positions(jd_ut)` → {Chiron, Ceres, Pallas, Juno, Vesta:
  lon/lat/speed}. Via `swe.calc_ut` with the asteroid body numbers
  (Chiron 2060 + 10000 offset scheme; main-belt via their numbers).
  HONEST: the environment lacks `seas_18.se1`; if the ephemeris call
  fails, raise CalculationError naming the missing file — never
  silently substitute Moshier for asteroids.
- `astroengine/midpoints.py` (typed path):
  `midpoints(positions)` → all 45 direct midpoints of Sun..Pluto
  (shorter-arc), sorted; `midpoint_hits(natal_jd, lat, lon)` →
  planets/angles on midpoints within 1°.
- CLI: `asteroids --load NAME --json`; `midpoints --load NAME --json`.

## Eldra
Build both modules + CLIs. Probe which asteroid bodies actually
resolve in this environment first; disclose.

## Sólrún (subagent verification)
`tests/test_asteroids_midpoints.py`: midpoint math hand-verified
(e.g. Sun 0°/Moon 90° → 45°); asteroid availability honestly
reported (skip-if-missing, not fake); suite green.

## Védis
COMMANDS.md sections; `astroengine/INTERFACE.md` entries.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README rows.

## Acceptance gate
Both commands run on Volmarr's chart; suite green; pushed with
verified remote HEAD.
