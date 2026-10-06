# O05 — Four Pillars / BaZi

Fifth slice of ROADMAP_ORACLES.md.

## Skald
Four pillars hold the roof of a life: the year of ancestors, the
month of parents, the day of the self, the hour of children. Each
a stem and a branch; the day stem is the Day Master, the lord of
the chart.

## Rúnhild
- `astroengine/bazi.py`: pure typed module (no legacy import).
  `pillars(iso_date, time, timezone)` ->
  {year, month, day, hour} each {stem, branch, ganzhi, nayin},
  plus day_master, solar_term (current jie), lichun moment.
- Year pillar: ganzhi changes at Lichun (not CNY).
- Month pillar: branch from the current jie (12 jie via Swiss
  Ephemeris Sun longitude); stem by the Five Tigers rule from the
  year stem. Month branches: Yin@Lichun … Chou@Xiaohan.
- Day pillar: ganzhi from Julian Day Number; offsets DERIVED from
  the verified anchor 1939-01-17 = Jia-Yin and cross-checked on
  1985-09-12 and 1685-03-28 (all Jia-Yin in published charts).
- Hour pillar: branch from the 12 two-hour periods (Zi 23–1 …);
  stem by the Five Rats rule from the day stem. Convention
  documented: calendar-day boundary at local midnight; local clock
  time used as given (no true-solar-time correction — disclosed).
- Solar terms via pyswisseph (already a dependency): find the jie
  interval containing the moment; Lichun moment for the year
  boundary. Boundary behavior explicitly tested.
- CLI: `bazi --date 1972-09-01 --time 08:18 --timezone
  America/New_York [--json]` following engine conventions.

## Eldra
Build module + CLI.

## Sólrún (subagent verification)
`tests/test_bazi.py`: Volmarr 1972-09-01 08:18 America/New_York —
  year Ren-Zi, month Wu-Shen, day Xin-You (verify independently!),
  hour Ren-Chen; boundary probes (a date just before/after Lichun;
  a date just before/after a jie); day-pillar formula cross-check
  on the three Jia-Yin anchors; suite green.

## Védis
COMMANDS.md + INTERFACE.md.

## Scribe
DEVLOG.md, TODO.md, README row.

## Acceptance gate
`bazi` for Volmarr matches an independent published-style
computation; suite green; pushed with verified remote HEAD.
