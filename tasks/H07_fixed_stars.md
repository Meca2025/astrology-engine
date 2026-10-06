# H07 — Fixed stars

Seventh slice of ROADMAP_HORIZONS.md.

## Skald
Beyond the wandering seven, the bright ones hold their stations —
Regulus the heart, Spica the ear of wheat, Antares the heart of the
Scorpion. Their whispers on the planets and angles.

## Rúnhild
- `data/fixed_stars.json`: ~25 bright stars — name, constellation,
  J2000 longitude/latitude, magnitude, traditional nature
  (e.g. "Mars/Jupiter"), one-line meaning. Sources labeled
  (Robson/Vivian Robson *The Fixed Stars and Constellations in
  Astrology*, 1923; nature per Ptolemaic tradition).
- `astroengine/stars.py` (typed path):
  `star_longitude(star, jd_ut)` — precess J2000 → date.
  `star_hits(natal_jd_ut, lat, lon, orb=1.0)` → conjunctions of stars
  to natal planets/ASC/MC (+ paran: star on an angle).
  Precession: swe precession via `swe.precess` or manual; simplest:
  use `swe.fixstar` with a custom star list? pyswisseph ships
  `swe.fixstar_ut` reading its own star catalog — but names/orbs need
  our data file anyway. Cleanest: store J2000 ecliptic lon/lat in our
  JSON, precess with `swe.precess(jd_j2000, jd_target, ...)`.
- CLI: `stars --load NAME --orb 1.0 --json` — lists star contacts;
  also `--date` for the stars' current positions.

## Eldra
Build data file (verify each star's J2000 longitude against a second
source or swe.fixstar), module, CLI.

## Sólrún (subagent verification)
`tests/test_stars.py`: Regulus longitude ~149.8° for J2026 (precessed
from 139.8° J1900-ish — verify numerically); Volmarr's Pluto conjunct
ASC — any star within 1°?; star count and JSON schema valid; suite green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row.

## Acceptance gate
`stars --load volmarr` lists contacts; suite green; pushed with
verified remote HEAD.
