# H06 — Electional astrology

Sixth slice of ROADMAP_HORIZONS.md.

## Skald
Not reading the moment — choosing it. The electional art finds the
most fortunate windows for publishing, teaching, launches.

## Rúnhild
- `astroengine/electional.py` (typed path):
  `score_moment(jd_ut, lat, lon)` → `{moon_phase, moon_sign,
  moon_speed, moon_void, moon_applying, mercury_rx,
  benefic_hours?, malefic_aspects, score, verdict}`.
  `find_windows(from_jd, to_jd, lat, lon, step_hours=1)` →
  sorted `[{datetime_iso, score, notes}]`.
  - Moon: sign, waxing/waning, void-of-course (no applying major
    aspect before sign change), applying aspects, speed.
  - Mercury retrograde flag. Hard aspects to Mars/Saturn flagged.
  - Scoring: + for Moon waxing, in domicile/exaltation, applying to
    benefics; − for void-of-course, Moon combust, Mercury rx, Moon
    square/opposition Mars/Saturn.
- CLI: `elect --from-date … --to-date … --lat --lon --timezone`
  (chart-aware `--load` for location), `--json`, `--top N`.
- Fixed, honest rules; no natal chart needed (traditional electional
  stands alone).

## Eldra
Build module + CLI.

## Sólrún (subagent verification)
`tests/test_electional.py`: Moon phase and void-of-course for a known
date; Mercury rx flag on a known retrograde date (e.g. 2026-10-24,
Mercury stations retrograde ~2026-10-24 — verify with engine);
windows sorted by score; full suite green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row.

## Acceptance gate
`elect --from-date 2026-10-20 --to-date 2026-10-27 ...` ranks
windows and flags Mercury rx; suite green; pushed with verified
remote HEAD.
