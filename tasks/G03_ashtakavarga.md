# G03 — Ashtakavarga: the 337 bindus

Third slice of ROADMAP_GAMBHIRA.md.

## Skald
Every chart ever cast holds exactly 337 points of light — no
more, no less. The seers counted where each planet's blessing
falls. Now the engine counts too.

## Rúnhild
- `data/ashtakavarga.json`: the seven benefic-place tables per
  B.V. Raman (planet → contributor → houses), with the canonical
  totals (48/49/39/54/56/52/39 = 337) and source notes. Lagna is
  the eighth contributor (included; variant disclosed).
- `astroengine/ashtakavarga.py`:
  - `bhinna(signs, lagna_sign)`: pure function — planetary sign
    indices + lagna → the seven Bhinnashtakavarga charts
    (bindus per sign) and the Sarvashtakavarga totals.
  - `compute_ashtakavarga(request)`: wraps the ephemeris (D1
    sidereal signs).
  - Classical reading notes as labeled lore: SAV < 28 weak,
    > 30 strong per sign; transit use documented.
  - Trikona/Ekadhipatya reductions noted as future work, not
    silently omitted.
- `ashtakavarga` CLI: birth-data flags, `--load` aware, text +
  `--json`.

## Eldra
Task doc first (done), then data, module, CLI.

## Sólrún (subagent verification)
`tests/test_ashtakavarga.py`: B.V. Raman's Standard Horoscope
(1918-10-16 Bangalore; sidereal signs Sun Virgo, Moon Aquarius,
Mars Scorpio, Mercury Libra, Jupiter Gemini, Venus Virgo,
Saturn Leo, Lagna Capricorn) — Sun's BAV must equal
[5,3,5,4,4,4,3,5,5,0,5,5] (Aries→Pisces); all seven BAV totals
equal the canonical constants; SAV sums to 337; suite green.

## Védis
INTERFACE.md, COMMANDS.md entries.

## Scribe
DEVLOG.md.

## Acceptance gate
Raman fixture green; suite green; pushed with verified remote
HEAD.
