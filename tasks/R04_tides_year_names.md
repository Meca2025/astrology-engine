# R04 — Tides of Day, Eightfold Year, Runic Names

Slice R04 of ROADMAP_RUNIC.md. Parent standing law applies: six Mythic
Engineering roles in order, push after the slice, no force pushes, no
unrelated edits, computation separate from interpretation.

## Skald — vision and naming

Extend `astroengine/runic.py` with the day's tides, the year's stations,
and the name-craft:

- `tide(clock_time)` — the tide (App. 6) ruling a clock HH:MM.
- `year_station(iso_date)` — the Station of the Mystic Year (Ch. 5) ruling
  a civil date: station number, rune, festival, day-hour, symbolic event.
- `runic_name(iso_datetime, longitude, timezone)` — the name-craft pair:
  birth half-month rune + birth hour-rune (LAT), per Ch. 5.

## Rúnhild — architecture

- `tide`: pure on HH:MM; 8 windows from the corpus (Midnight wraps
  22:30–01:30). Returns English/OE/ON names + window.
- `year_station`: the book defines the 8 stations (order, rune, festival,
  day-hour, symbolic event) but NOT exact date boundaries — so boundaries
  are a DECLARED engine convention, labeled `method: "festival-span"`:
  each station spans [festival, next festival) in cycle order
  (Fourth→Fifth→Sixth→Seventh→Eighth→First→Second→Third→Fourth),
  festivals at conventional dates: Yule Dec 21, Spring Equinox Mar 20,
  Beltane May 1, Midsummer Jun 21, Lammas Aug 1, Autumn Equinox Sep 22,
  Samhain Oct 31. The First station has no festival in the book; it is
  anchored at **Aug 13** (start of the As half-month — the first of its
  "As/Rad" runes), declared as convention. Result carries the station
  table row + span + method + source + historical_claim.
- `runic_name`: composes `half_month_rune` (date part) + `runic_hour`
  (via `to_local_apparent_time`). Returns the rune pair and each half's
  correspondences. The book's rendered names (Kenneth, Ingrid, Darwin) are
  literary English wordplay on the pairs, NOT mechanical output — the
  docstring says so; the Kenneth/Odal wheel conflict (R01) is referenced.
- All JSON-safe; CalculationError on bad inputs (reuse helpers).

## Eldra — build

- Extend `astroengine/runic.py`. New corpus section NOT needed: tides
  already in `data/runic.json`; the station table is small — add it to
  `data/runic.json` as `stations` (8 rows: number, rune, festival,
  day_hour, symbolic_event, festival_date, span note). Data change +
  code in one slice is fine (R01's corpus anticipated it; keep the JSON
  edit minimal and sourced).
- Wait — R01's corpus is pushed and tested. Adding `stations` to
  runic.json: allowed (additive, version bump 1.0→1.1, tests extended).

## Sólrún — verification

New `tests/test_runic_tides.py`:

- Tide fixtures: 04:30→Morntide, 07:30→Daytide, 12:00→Midday,
  16:30→Eventide, 19:30→Nighttide, 22:30→Midnight, 00:15→Midnight (wrap),
  01:30→Uht, 04:29→Uht.
- Station fixtures: 2026-12-25→Fourth/Jera/Yule; 2026-03-25→Fifth/Beorc;
  2026-06-25→Seventh/Dag; 2026-10-06→Second/Ken (Autumn Eq span);
  2026-11-05→Third/Hagal; 2026-08-20→First/As-Rad (convention span).
- Station table integrity: 8 stations, runes match the book's table
  (As/Rad, Ken, Hagal, Jera, Beorc, Lagu, Dag, Thorn), festivals match.
- `runic_name("2026-05-16T16:45", 0.0, "UTC")` → ("Ing", "Rad") — Ingrid's
  pair, wheel-consistent. Darwin probe documents ("Wyn","Wyn") vs the
  book's literary "Darwin".
- Corpus version 1.1; full suite green.

## Védis — cartography

- `astroengine/INTERFACE.md`: "Tides, stations, names (R04)" section.
- COMPONENT_INDEX.md: extend runic.py line.

## Scribe — memory

- DEVLOG.md entry; TODO.md R04 checkbox; this task file as work order.
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

Tides, stations (with declared boundaries), and name-craft reproduce book
fixtures; errors explicit; docs updated; pushed with verified remote HEAD.
Then R05.
