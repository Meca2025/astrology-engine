# O06 — Tibetan astrology

Sixth and final slice of ROADMAP_ORACLES.md.

## Skald
From the Kalachakra tantra the Tibetans wove Chinese stems and
Indian stars into one cloth: the element-animal year, the nine
mewa circling, the eight parkha turning, and the five life-forces
that ride with a person from birth.

## Rúnhild
- `astroengine/tibetan.py`: pure typed module (no legacy import).
  `tibetan(iso_date)` ->
  {year: {element, animal, ganzhi-ish year name, rabjung cycle/year},
   mewa: {number, color, element} of the year,
   parkha: {name} of the year,
   forces: {srog, lus, dbang_thang, bla, rlung_ta} each with
   element/animal for the birth year}.
- Year boundary: Losar. Use lunardate CNY as the boundary with an
  explicit DISCLOSED approximation (Losar usually coincides with
  CNY but occasionally differs — boundary-day results flagged).
  Verify against a published Losar table for sample years.
- Mewa/parkha cycles: formulas cross-checked against published
  yearly tables (2023, 2024, 2025 spot years), not recalled loosely.
- Five forces: table-driven from the birth year's element/animal
  per the standard almanac method; method and provenance labeled.
  Where traditions disagree, say so.
- CLI: `tibetan 1972-09-01 [--json]`.

## Eldra
Research first (mewa/parkha/year tables from published sources),
then build module + CLI.

## Sólrún (subagent verification)
`tests/test_tibetan.py`: spot years verified against published
tables (2024 Wood Dragon; mewa/parkha of 2024/2025 from a real
almanac); rabjung math; Losar-boundary flag; suite green.

## Védis
COMMANDS.md + INTERFACE.md; capabilities/tool_schemas if the
pattern requires (check how chinese/bazi were registered).

## Scribe
DEVLOG.md, TODO.md, README row; close out ROADMAP_ORACLES.md.

## Acceptance gate
Every number traceable to a published table; suite green; pushed
with verified remote HEAD; Oracles program complete.
