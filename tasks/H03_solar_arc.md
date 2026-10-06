# H03 — Solar arc directions

Third slice of ROADMAP_HORIZONS.md.

## Skald
A degree a year — the arc of the Sun carried across the whole chart.
The great modern predictive art, nearly trivial to compute, profound
to read.

## Rúnhild
- `astroengine/directions.py` (typed path): `solar_arc(natal_jd_ut,
  target_jd_ut)` → `{arc: float, directed: {body: longitude}}`.
  Arc = secondary-progressed Sun's longitude at target minus natal
  Sun's longitude (day-for-a-year); every natal longitude += arc.
  Reuse the engine's existing progression computation — no duplicated
  ephemeris logic.
- CLI: `solar-arc --load NAME --target-date YYYY-MM-DD` (or birth
  data), listing directed-to-natal aspects within 1° orb, tightest
  first, with applying/separating and exact-hit flag (orb < 0.1°).
  `--json` for machine readers.

## Eldra
Build module + CLI. Directed ASC/MC too (angles direct like planets).

## Sólrún (subagent verification)
`tests/test_directions.py`: arc equals progressed-Sun minus natal-Sun
on a fixture; directed Sun at target ≈ natal Sun + arc; Volmarr:
directed Sun conjunct natal Mercury near 2026-10-23 found within 1°
orb; applying/separating flags sane. Full suite green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row.

## Acceptance gate
`solar-arc --load volmarr --target-date 2026-10-23` lists the
directed Sun–natal Mercury conjunction; suite green; pushed with
verified remote HEAD.
