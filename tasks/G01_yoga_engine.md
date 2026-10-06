# G01 — Yoga engine

First slice of ROADMAP_GAMBHIRA.md.

## Skald
The chart is a sky; the yogas are its constellations — the
patterns the seers named when planets stood together in
counsel. Time to teach the engine to see them.

## Rúnhild
- `data/yogas.json`: definitions of the great yogas — name,
  classical source (BPHS / Phaladeepika chapter-verse where
  known), rule in words, signification, known variants.
- `astroengine/yogas.py`: `detect_yogas(request)` computing
  from D1 (whole-sign houses from Lagna; sign lords from
  vedic.json):
  - Pancha Mahapurusha (Ruchaka/Bhadra/Hamsa/Malavya/Shasha):
    Mars/Mercury/Jupiter/Venus/Saturn in own or exaltation sign
    in a kendra from Lagna.
  - Gaja Kesari: Jupiter in kendra (1/4/7/10) from the Moon.
  - Budha-Aditya: Sun and Mercury in the same rashi.
  - Dhana yogas: lords of 2/5/9/11 in mutual kendra/trikona or
    in each other's signs (documented subset, classical).
  - Raja yoga (basic): a kendra lord and a trikona lord in
    mutual kendra/trikona or conjoined; the 9th+10th lord
    combination flagged as the premier form.
  - Kemadruma: no planets in 2nd/12th from Moon (Sun excluded
    per BPHS); bhanga (cancellation) conditions reported, not
    silently applied.
  - Sakata: Jupiter in 6th/8th/12th from the Moon.
- Each detection returns `{yoga, present, planets, details,
  source, variant_notes}`. Classical definitions cited;
  interpretive weight labeled as traditional, not computed fact.
- `yogas` CLI: birth-data flags, `--load` aware, text + `--json`.

## Eldra
Data file first, then module, then CLI.

## Sólrún (subagent verification)
`tests/test_yogas.py`: offline fixtures — Volmarr's chart (expect
Gaja Kesari? verify by hand — do NOT assume); synthetic charts
via constructed longitudes if the module allows injection, else
hand-verified expectations from real ephemeris dates; each yoga
has a positive and a negative case; suite green.

## Védis
INTERFACE.md, COMMANDS.md entries.

## Scribe
DEVLOG.md, TODO.md.

## Acceptance gate
`yogas` on Volmarr's chart matches hand computation; suite green;
pushed with verified remote HEAD.
