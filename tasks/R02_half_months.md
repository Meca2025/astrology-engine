# R02 — Runic Half-Months Engine

Slice R02 of ROADMAP_RUNIC.md. Parent standing law applies: six Mythic
Engineering roles in order, push after the slice, no force pushes, no
unrelated edits, computation separate from interpretation.

## Skald — vision and naming

New module `astroengine/runic.py`: the first living computation of the
runic star-program. Given a civil date, it names the ruling half-month
rune of the Northern year-wheel (App. 2). Pure functions, no ephemeris
needed — the wheel is calendrical. Public entry:

`half_month_rune(date, time=None, timezone=None) -> dict`

## Rúnhild — architecture

- Frozen dataclass `RunicDateRequest(date, time=None, timezone=None)`.
  - `date`: ISO `YYYY-MM-DD`, required.
  - `time`: ISO `HH:MM`, optional; when given on a boundary day, the
    book's local-apparent start time decides the rune.
  - `timezone`: IANA name or `UTC`, optional; only meaningful with `time`.
    Unknown/invalid zones raise `CalculationError` (reuse
    `astroengine.models.CalculationError`).
- Boundary rule (App. 2): 24 half-months in calendar order starting
  Peorth 01-13. A date belongs to the latest-starting half-month whose
  start is <= the date; dates before 01-13 belong to Eoh (started 12-28
  of the prior year). On a start date with a `time` given, the new rune
  begins at the book's start time (local apparent); before that, the
  previous rune still rules.
- Return JSON-safe dict: `rune`, `half_month_start`, `half_month_end`,
  `days_remaining`, `next_rune`, `correspondences` (tree/herb/color/
  polarity/element/deity/symbolic_meaning from the corpus — data, not
  interpretation), `source`, `historical_claim`.
- No interpretation, no predictions. Reads `data/runic.json` via the
  existing `rules.load_rules` helper (check: load_rules("runic.json")).

## Eldra — build

- `astroengine/runic.py` with `_load_corpus()`, `_ordered_half_months()`,
  `half_month_rune(...)`.
- Keep it dependency-light: datetime + zoneinfo only.

## Sólrún — verification

New `tests/test_runic_half_months.py`, book fixtures:

- 2026-01-28 → Peorth; 2026-02-12 → Elhaz (book: Peorth until 12 Feb)
- 2026-09-13 → Ken; 2026-09-28 → Gyfu
- 2026-05-14 → Ing; 2026-06-29 → Feoh
- 2026-01-01 → Eoh (wrap: before Peorth's 01-13)
- 2026-12-31 → Eoh (started 12-28)
- Boundary-time: 2026-01-28 04:00 → Elhaz (start 05:00 not yet);
  2026-01-28 05:00 → Elhaz? No — 05:00 IS the start: Elhaz begins
  01-28 05:00, so 04:59 → Peorth, 05:00 → Elhaz.
- Invalid date / invalid timezone → CalculationError.
- Full suite stays green.

## Védis — cartography

- Document `astroengine/runic.py` in `astroengine/INTERFACE.md`
  (new "Runic cycles (R02)" section) and COMPONENT_INDEX.md.
- No CLI surface yet (the unified `runic` command lands in R09);
  module is importable and independently testable.

## Scribe — memory

- DEVLOG.md entry; TODO.md R02 checkbox; this task file as work order.
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

`half_month_rune` reproduces every book fixture above; errors are
explicit; docs updated; pushed with verified remote HEAD. Then R03.
