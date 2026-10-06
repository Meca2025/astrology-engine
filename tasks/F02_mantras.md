# F02 — Remedial Vedic mantras

Third slice of ROADMAP_VISTARA.md. Volmarr's words: "and
recommended remedial Vedic mantras".

## Skald
When the sky presses hard, the old way is not to curse the
planets but to sing to them. The forecast names the pressures;
this slice answers with the traditional songs.

## Rúnhild
- `data/mantras.json`: planet → traditional mantras. The
  Navagraha set (Om Suryaya Namaha … Om Ketave Namaha), the
  Gayatri, and the planetary Gayatris (Shani, Rahu, Ketu).
  All ancient, public-domain verses. Each entry: planet, deity,
  transliterated mantra, traditional repetition count (108),
  purpose, source note. No invented mantras, ever.
- `astroengine/mantras.py`: `remedies_for(afflictions)` consuming
  F01's `afflictions` block — mantras for pressured planets and
  dasha lords, deduped, each with a `reason` string ("Saturn
  mahadasha lord", "Mars squares natal Moon", …).
- CLI: `forecast --mantras` appends a REMEDIES section (text +
  JSON `remedies` key); standalone `mantras [--planet NAME]`
  lookup command.
- Framing: devotional practice, symbolic and traditional — never
  medical, never guaranteed remedy. Say so in the text.

## Eldra
Data file first (Sólrún checks every mantra string against the
traditional forms), then module, then CLI wiring.

## Sólrún (subagent verification)
`tests/test_mantras.py`: all nine grahas have ≥1 mantra; no
empty strings; `remedies_for` on the 2026-10-23 afflictions
recommends Saturn (dasha lord) and Neptune/Mars-pressured points
with reasons; unknown planet raises cleanly; suite green.

## Védis
INTERFACE.md, COMMANDS.md entries.

## Scribe
DEVLOG.md, TODO.md.

## Acceptance gate
`forecast --date 1972-09-01 ... --on 2026-10-23 --mantras` shows
Saturn remedies with reasons; suite green; pushed with verified
remote HEAD.
