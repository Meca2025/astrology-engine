# R01 — The Runic Corpus (data)

Slice R01 of ROADMAP_RUNIC.md. Parent standing law applies: six Mythic
Engineering roles in order, push after the slice, no force pushes, no
unrelated edits, computation separate from interpretation.

## Skald — vision and naming

Create `data/runic.json`: the complete machine-readable transcription of
every computable table in Nigel Pennick, *Runes and Astrology: Symbol and
Starcraft in the Northern Tradition* (2023). Sections: `runes`,
`half_months`, `runic_hours`, `planetary_hours`, `weekdays`, `zodiac`,
`tides`, `mansions`, `palaces`, `worlds`, `life_periods`. Every table carries
`source: "Pennick (2023)"` and `historical_claim: "modern synthesis"`.

## Rúnhild — architecture

- Rune records keyed by canonical Elder Futhark name; the 8 Anglo-Saxon
  additions flagged `"futhark": "anglo-saxon"`.
- Dates as ISO `MM-DD` plus local-apparent start time `HH:MM`.
- Planetary hours as a 7×24 grid of deity names, weekday-major.
- Runes named per the book: "Beare" is the book's spelling of Beorc in the
  half-month table (transcribe as printed, note the variant); "Eh" is the
  book's short form of Ehwaz; "Æsc" is the ash-rune of the mansions table.
- Data-quality notes (honest transcription):
  - Planetary hours: hours 00:00–11:00 follow a rotated deity sequence;
    hours 12:00–23:00 follow the classical Chaldean order from the day's
    ruling deity (the 12:00 hour of each day carries that day's ruler).
    Transcribe the book exactly as printed; record the discontinuity in a
    `note` field. Do NOT silently "correct" it.
  - 19:00 Friday reads "Prigg" in print: transcribe "Frigg" with a note.
  - Regulus is listed as β Leonis, Denebola as β Leonis in the mansions
    table: transcribe as printed with a note (modern designations differ).

## Eldra — build

Transcribe, from the appendices and chapters:

1. **runes**: 24 Elder Futhark + 8 Anglo-Saxon (Ac, Os, Yr, Ior, Ear,
   Cweorth, Cale, Stan) — tree, herb, color, polarity, element, deity,
   symbolic meaning (App. 1).
2. **half_months**: 24 entries, rune → start `MM-DD` + `HH:MM`
   (Feoh 06-29 03:00 … Dag 06-14 04:00; full list per App. 2).
3. **runic_hours**: 24 entries in futhark order, Feoh 12:30–13:30,
   each subsequent rune one solar hour later, Dag 11:30–12:30 (Ch. 4).
4. **planetary_hours**: 7 weekdays × 24 hour slots → deity (App. 3),
   exactly as printed including the noon discontinuity.
5. **weekdays**: deity, planet, rune, tree, herb, element, esoteric number,
   magic square (App. 4).
6. **zodiac**: 12 signs → rune, deity, day, stone, animal, with the book's
   alternative rows for Capricorn/Aquarius/Pisces labeled `variant: modern`
   (App. 5).
7. **tides**: 8 tides — English/Old English/Old Norse names, windows,
   plus the five day markers (App. 6).
8. **mansions**: 28 entries — rune, northern name, star, astronomical
   designation (Ch. 7 table).
9. **palaces**: 12 Grímnismál palaces — name, meaning, deity, sign (App. 7).
10. **worlds**: 9 worlds → non-invertible rune (Ch. 6).
11. **life_periods**: 7 entries — deity/planet, start age, end age, years
    (Máni 0–4 … Loki 68–98) (Ch. 6).

## Sólrún — verification

New `tests/test_runic.py`:

- Counts: 24 futhark + 8 additions; 24 half-months; 24 runic hours;
  168 planetary-hour cells (7×24, all seven deities present);
  7 weekdays; 12 zodiac (+3 labeled variants); 8 tides; 28 mansions;
  12 palaces; 9 worlds; 7 life-periods summing to 98 years.
- Spot checks against the book: Ken half-month starts 09-13;
  Odal runic hour 22:30–23:30; 21 Sep 23:00 grid cell Sunday/23:00 = Loki;
  Friday 19:00 = Frigg; mansion 1 = Feoh/Alcyone; mansion 28 = Ear;
  Bilskírnir → Aries; Helheim → Hagal; Loki life-period 68–98.
- JSON validity; every table carries source + historical_claim;
  `historical_claim` never asserts antiquity.
- Run `python -m pytest -q` in the venv; all green.

## Védis — cartography

- Register `data/runic.json` in `data/README.md` and COMPONENT_INDEX.md.
- Note the relationship to `data/vedic.json` (28 Norse mansions vs
  27/28 nakshatras: related in kind, distinct in definition — no conflation).
- No CLI surface in R01 (data only); capability registration comes in R09.

## Scribe — memory

- DEVLOG.md entry; TODO.md checkbox for R01; this task file kept as the
  slice's work order.
- **Push** the task document BEFORE code; push the slice after Sólrún is
  green; verify remote HEAD; sync the local clone.

## Acceptance gate

`data/runic.json` complete per the inventory above; tests green;
docs updated; pushed and remote HEAD verified. Then R02 is ready.
