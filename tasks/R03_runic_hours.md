# R03 — Runic Hours and Planetary Hours

Slice R03 of ROADMAP_RUNIC.md. Parent standing law applies: six Mythic
Engineering roles in order, push after the slice, no force pushes, no
unrelated edits, computation separate from interpretation.

## Skald — vision and naming

Extend `astroengine/runic.py`: the wheel of the day. Two hour-systems from
Pennick Ch. 4 / App. 3, plus their meeting-point:

- `runic_hour(local_apparent_time)` — the rune ruling a solar hour
  (Feoh 12:30–13:30 … Dag 11:30–12:30, Ch. 4 wheel from R01).
- `to_local_apparent_time(iso_datetime, longitude, timezone)` — convert
  civil clock time to Local Apparent Time (the book's "real time": sundial
  time, midday = sun due south). Longitude correction + equation-of-time
  approximation, method declared in the docstring.
- `planetary_hour(weekday, clock_hour)` — Northern Tradition planetary hour
  deity from the App. 3 grid (hour-to-hour divisions, clock time).
- `sele(iso_datetime, longitude, timezone)` — "when appropriate runic hours
  coincide with their planetary equivalents, these are especially powerful":
  the runic hour-rune and the planetary-hour deity share a deity (rune's
  deity field contains the planetary deity). Returns both halves + boolean.

## Rúnhild — architecture

- All new functions pure and JSON-safe; reuse `RunicDateRequest`-style
  frozen dataclass `RunicHourRequest(iso_datetime, longitude, timezone)`.
- `iso_datetime`: ISO `YYYY-MM-DDTHH:MM`; `longitude` decimal degrees
  [-180, 180]; `timezone` IANA/UTC required (civil → LAT needs it).
- LAT method (declared): LAT = UTC + longitude/15h + EoT, with the standard
  low-precision equation-of-time approximation; labeled `method:
  "longitude+eot-approx"`. No ephemeris dependency.
- Planetary hours use CLOCK hour in the given zone (book: hour-to-hour).
- Sele rule: planetary deity D is "appropriate" to runic hour-rune R iff D
  appears in R's deity correspondence (split on "/"). E.g. runic hour Tyr
  (deity "Tyr") + planetary hour Tyr → sele.
- Errors: bad datetime/longitude/zone → CalculationError.

## Eldra — build

- Extend `astroengine/runic.py`. Keep stdlib-only (datetime, zoneinfo, math).

## Sólrún — verification

New `tests/test_runic_hours.py`:

- Wheel fixtures (LAT direct): 12:30→Feoh, 13:30→Ur, 16:45→Rad (Ingrid's
  hour, Ch. 5: born 16 May 4:45pm → Rad — wheel-consistent), 22:45→Is,
  11:45→Dag, 00:15→Jera.
- Kenneth example NOT used as fixture: the book's "Odal 22:30" conflicts
  with the encoded wheel (documented in R01); a test pins the wheel value
  (22:45→Is) and references the note.
- LAT conversion: 2026-06-21T12:00 at longitude 0, UTC → LAT ≈ 12:00 ± 4 min
  (EoT bound); longitude +15° → LAT ≈ civil +1h ± 4 min.
- Planetary grid: Sunday 00:00→Thor; Monday 12:00→Máni; Friday 19:00→Frigg.
- Sele: construct a case — e.g. find an hour where runic rune deity matches
  planetary deity (Tuesday=Tyr day: planetary Tyr hours; runic Tyr hour is
  04:30–05:30 LAT; on a Tuesday at LAT 05:00 with planetary hour 04:00–05:00
  = Odin → not sele; test both true and false paths via direct function
  calls rather than wall-clock).
- Full suite stays green.

## Védis — cartography

- `astroengine/INTERFACE.md`: "Runic hours (R03)" section.
- COMPONENT_INDEX.md: extend the runic.py line.
- No CLI surface yet (R09).

## Scribe — memory

- DEVLOG.md entry; TODO.md R03 checkbox; this task file as work order.
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

Wheel, LAT, planetary grid and sele all reproduce book fixtures; errors
explicit; docs updated; pushed with verified remote HEAD. Then R04.
