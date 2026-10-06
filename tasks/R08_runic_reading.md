# R08 — Interpretation of Runic Cycles (Ch. 8)

Slice R08 of ROADMAP_RUNIC.md. Standing law: six roles in order, push via
the PAT tool. Merge-first: `git fetch` + diff before every push; never
overwrite Volmarr's edits; never force-push.

## Skald — vision and naming

Add the interpretive synthesis layer (Ch. 8 "Chronomantic Methods"):

- `runic_reading(iso_datetime, longitude, timezone, age_years=None,
  moon_sidereal_longitude=None)` — one structured reading object with a
  `computation` section (raw layer results) and an `interpretation`
  section (symbolic statements, every one tagged `interpretive`).

## Rúnhild — architecture

- Corpus addition (`data/runic.json` v1.1 → v1.2), transcribed verbatim
  from Ch. 8, used ONLY for labeled interpretive synthesis:
  - `interpretation.planetary_qualities`: Sól=self-expression,
    Odin=mentality, Frigg=harmony, Tyr=energy, Thor=expansion,
    Loki=limitation, Urd=change, Aegir=uncertainty, Máni=response,
    Vili/Vé=elimination.
  - `interpretation.rune_adverbs`: the 24 Elder Futhark adverbs
    (Feoh=richly … Dag=changingly).
- `runic_reading` computes layers with existing R02–R07 functions:
  half-month, hour (+planetary hour, sele), tide, year station, weekday,
  life period (if age given), lunar mansion (if longitude given),
  runic-name pair.
- Interpretive statements (deterministic, book-grounded only):
  - Per rune-bearing layer: "{Layer} rune {R} — {deity} — expressed
    {adverb}"; the planetary-quality clause "{deity} ({quality})" is added
    ONLY when a Ch. 8 quality key matches the rune's App. 1 deity string
    (accent/case-insensitive, parenthetical aliases honored); otherwise
    the clause is omitted — never invented.
  - Runes outside the 24 (Anglo-Saxon extras like Os) get no adverb
    clause — the Ch. 8 list covers Elder Futhark only.
  - Sele: "especially powerful" coincidence note (Ch. 4) when true.
  - Station: its book symbolic event, quoted.
  - Name: the pair, with the literary-rendering note (R04).
- Computation functions remain importable without the interpretive layer
  (runic_reading is additive; nothing else changes).

## Eldra — build

- Corpus v1.2 addition + `runic_reading` + `_deity_quality` helper +
  `__all__` in `astroengine/runic.py`.

## Sólrún — verification

New `tests/test_runic_reading.py`:

- Golden reading fixture: fixed moment (e.g. 2026-05-16T16:45 UTC, lon 0,
  age 54) — assert the full statement list equals the expected strings
  EXACTLY (golden output).
- Anti-fabrication: across several moments, collect every adverb and
  quality appearing in statements; assert each is in the corpus tables.
- Structure: `computation` has no `interpretive` tags;
  `interpretation.statements` all carry kind=interpretive +
  source="Pennick (2023)".
- Full suite green.

## Védis — cartography

- `astroengine/INTERFACE.md`: "Runic reading (R08)" — the
  computation/interpretation split, stated plainly.
- COMPONENT_INDEX.md: extend runic.py line.

## Scribe — memory

- DEVLOG.md entry; TODO.md R08 checkbox; this task file as work order.
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

Golden-output fixture green; anti-fabrication check green; the split is
explicit in code and docs; pushed with verified remote HEAD. Then R09.
