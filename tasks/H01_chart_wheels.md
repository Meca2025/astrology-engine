# H01 — Chart wheels (SVG natal wheels)

First slice of ROADMAP_HORIZONS.md.

## Skald
Every astrologer expects to *see* the sky. A beautiful dark wheel —
gold zodiac ring, planet glyphs, colored aspect lines, the native's
name at the heart — rendered as dependency-free SVG.

## Rúnhild
- `astroengine/wheel.py`: `wheel_svg(planets, cusps, aspects, meta)` →
  SVG string. Pure data in, SVG out. **No import of the legacy
  monolith** (house rule); the CLI layer computes and passes plain
  data.
  - `planets`: [{name, glyph, longitude}]
  - `cusps`: [12 floats]; `aspects`: [{a, b, kind}]
  - `meta`: {title, subtitle, asc, mc}
  - Geometry: 0° Aries at 9 o'clock, counterclockwise; planet
    collision-spreading; aspect chords colored by kind.
- CLI: `wheel --load NAME -o chart.svg` or fresh birth data
  (`--date/--time/--lat/--lon/--timezone`, `--city/--nation`).
  Computes via legacy boundary functions in the CLI layer only.

## Eldra
Build renderer + CLI wiring. Planet glyphs: ☉☽☿♀♂♃♄♅♆♇☊.
Aspect colors: conjunction white, opposition red, square orange,
trine blue, sextile green, other gray. XML-escape all meta text.

## Sólrún (subagent verification)
`tests/test_wheel.py`: valid XML; every planet glyph present;
aspect-line count matches input; deterministic output; empty aspects
still valid; meta escaping. Independent visual sanity via a rendered
fixture. Full suite green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry;
capability/tool schemas if they enumerate commands; GOALS.md.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README feature-table row.

## Acceptance gate
`wheel --load volmarr -o /tmp/volmarr.svg` produces a valid,
beautiful SVG; suite green; pushed with verified remote HEAD.
