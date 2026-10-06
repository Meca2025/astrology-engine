# H09 — Draconic charts

Ninth slice of ROADMAP_HORIZONS.md.

## Skald
Beneath the tropical chart lies the draconic — the soul-chart,
reckoned from the Moon's north node instead of the spring equinox.
Where the two charts touch, the soul's intent shows through the
personality.

## Rúnhild
- `astroengine/draconic.py` (typed path):
  `draconic_longitude(tropical_lon, node_lon)` = (tropical_lon -
  node_lon) mod 360 — the draconic zodiac sets 0° Aries at the natal
  north node.
  `draconic_chart(natal_jd_ut, lat, lon)` → {body: draconic lon} for
  Sun..Pluto + draconic ASC/MC (recompute houses from draconic ASC?
  Traditional: draconic angles derived by rotating the whole chart —
  simplest honest: draconic ASC = draconic_longitude(tropical ASC)).
  `draconic_contacts(natal_jd_ut, orb=1.0)` → conjunctions between
  draconic and natal positions ("the soul touching the personality").
- CLI: `draconic --load NAME --json` — prints the draconic wheel
  positions and the tightest natal-draconic contacts.

## Eldra
Build module + CLI.

## Sólrún (subagent verification)
`tests/test_draconic.py`: natal north node maps to 0° Aries draconic
by definition; a planet conjunct the node natally sits at 0° Aries
draconic; contacts sorted; suite green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row.

## Acceptance gate
`draconic --load volmarr` runs; suite green; pushed with verified
remote HEAD.
