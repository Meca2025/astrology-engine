# Runic Astrology Roadmap — the Northern Star-Program

Date: 2026-10-06. Owner: Volmarr. Engine: astrology-engine v4.0.0.

## Vision (Skald's charge)

Give the engine the **full runic astrology of the Northern Tradition** as
systematized by Nigel Pennick in *Runes and Astrology: Symbol and Starcraft
in the Northern Tradition* (2023, 311 pp). Every computable cycle in the book
becomes a tested, wired, pushed engine capability: the 24 runic half-months,
the 24 runic hours, the Northern planetary hours, the eight tides of day and
the eightfold year, the 28 lunar mansions, the planetary life-periods, the
zodiacal and weekday rune correspondences, the Twelve Palaces, the Nine Worlds,
and the runic-name craft. One new CLI command, `runic`, gathers them all.

## Standing law

- **Source provenance on everything.** Every table is labeled
  *modern Norse runic astrology per Pennick (2023)* — a modern synthesis, not a
  historical reconstruction. This honors the parent ROADMAP's cultural-overlay
  gate: explicit modern-vs-historical labeling, optional overlays, source
  ownership. Never present runic astrology as validated prediction; it is
  symbolic interpretation material.
- **Computation and interpretation stay separate.** Engines compute positions
  and cycle memberships; symbolic readings are a distinct, labeled layer
  (repo rule: never silently promote planned techniques).
- **Data is immutable JSON** under `data/` (new file: `data/runic.json`).
  No runtime mutation. Unknown times/timezones fail loudly at boundaries.
- **Six Mythic Engineering roles per slice, in order:** Skald (vision and
  true naming) → Rúnhild (architecture: schema, boundaries, interfaces) →
  Eldra (forge: implementation) → Sólrún (auditor: tests, fixtures,
  verification) → Védis (cartographer: capability/interface registration,
  cross-module mapping) → Scribe (DEVLOG, TODO, docs, task-file updates).
- **Push discipline:** each slice begins with a task document in `tasks/`
  (pushed before code), and ends with **commit → push → verify remote HEAD**
  before the next slice begins. No force pushes, no unrelated edits, no
  deletions without human permission.

## Book inventory (what is computable)

| Book element | Location in book | Engine slice |
| --- | --- | --- |
| 24 Elder Futhark + 8 Anglo-Saxon runes: tree, herb, color, polarity, element, deity, symbolic meaning | App. 1 | R01 |
| 24 runic half-months with Gregorian start dates and local-apparent start times (Feoh 29 Jun → Dag 14 Jun) | App. 2 | R01, R02 |
| 24 runic hours: solar-hour wheel in futhark order (Feoh 12:30–13:30 … Dag 11:30–12:30) | Ch. 4 | R01, R03 |
| Northern Tradition planetary hours: 7×24 deity table, hour-to-hour divisions; sele (coincidence of runic + planetary hour) | App. 3 | R01, R03 |
| Weekday correspondences: deity, planet, rune, tree, herb, element, esoteric number, magic square | App. 4 | R01, R05 |
| Zodiacal correspondences: 12 signs → rune, deity, day, stone, animal (+ modern alternatives for Capricorn/Aquarius/Pisces) | App. 5 | R01, R05 |
| Eight tides of day: 3-hour tides, English/Old English/Old Norse names, day markers (dægred, dagmálastaðr, nón, eyktarstaðr) | App. 6 | R01, R04 |
| Eightfold year cycle: 8 year-tides; winter quarter centered on Jera | Ch. 5 | R04 |
| 28 Norse lunar mansions: rune, Old Norse name, star (Alcyone … Last Ones) | Ch. 7 | R01, R06 |
| Planetary life-periods: Máni 0–4, Odin 4–14, Frigg 14–22, Sól 22–41, Tyr 41–56, Thor 56–68, Loki 68–98 (years) | Ch. 6 | R05 |
| Metonic 19-year Sun/Moon cycle | Ch. 6 | R05 |
| Twelve Palaces (Grímnismál) ↔ zodiac signs | App. 7 | R07 |
| Nine Worlds ↔ 9 non-invertible runes (Gyfu, Dag, Ing, Jera, Is, Nyd, Eoh, Sigel, Hagal) | Ch. 6 | R07 |
| Runic-name craft: birth half-month rune + birth hour rune (Kenneth, Ingrid, Darwin) | Ch. 5 | R04 |
| Interpretation of runic cycles (synthesis rules) | Ch. 8 | R08 |

## Slices

### R01 — The Runic Corpus (data)

- **Skald:** name the corpus `data/runic.json`; sections: `runes`,
  `half_months`, `runic_hours`, `planetary_hours`, `weekdays`, `zodiac`,
  `tides`, `mansions`, `palaces`, `worlds`, `life_periods`.
- **Rúnhild:** JSON schema per section; rune records keyed by canonical
  Elder Futhark name with Anglo-Saxon additions flagged; dates as
  ISO month-day + start-time; planetary hours as 7×24 deity grid.
- **Eldra:** transcribe all tables from the appendices; include `source`
  and `edition` fields on every table.
- **Sólrún:** counts asserted in tests (24 futhark, 8 additions, 24
  half-months, 24 hours, 168 planetary-hour cells, 7 weekdays, 12 signs,
  8 tides, 28 mansions, 12 palaces, 9 worlds, 7 life-periods); spot-check
  values against the book (e.g. Ken rules 13–28 Sep; Odal hour 22:30–23:30).
- **Védis:** register `data/runic.json` in `data/README.md` and the
  component index; map relationships to `vedic.json` (nakshatra contrast
  for the 28 mansions — related, not identical).
- **Scribe:** task doc `tasks/R01_runic_corpus.md`; DEVLOG entry; TODO
  checkbox. **Push.**

### R02 — Runic Half-Months engine

- Given a civil date → ruling half-month rune, using the book's
  Gregorian-corrected start dates and local-apparent start times.
- Module `astroengine/runic.py`; pure function
  `half_month_rune(date, tz)` with explicit unknown-time handling.
- **Gate:** book fixtures — 28 Jan → Peorth until 12 Feb Elhaz;
  13 Sep → Ken; 14 May → Ing; boundary rollover at 29 Jun Feoh.
- **Push.**

### R03 — Runic Hours and Planetary Hours

- Runic hour from apparent solar time (declare LAT method: longitude
  correction + equation-of-time approximation; mean-time fallback labeled).
- Northern planetary hours from weekday × clock hour (hour-to-hour grid).
- **Sele detection:** when runic hour-rune and planetary-hour deity share
  the book's correspondences, flag the hour as especially potent.
- **Gate:** book examples — 21 Sep 23:00 → Odal hour; 16 May 16:45 → Rad
  hour; weekday grids spot-checked against App. 3.
- **Push.**

### R04 — Tides of Day, Eightfold Year, Runic Names

- Eight tides (name, EN/OE/ON, window) for any clock time; eight year-tides
  from the half-month wheel (winter quarter centered on Jera; Feoh opens at
  midsummer).
- Runic-name composer: half-month rune + hour rune of birth/name-taking
  (reproduce Kenneth/Ingrid/Darwin from the book).
- **Gate:** tide-boundary fixtures (e.g. 04:30 rismál/morginn boundary);
  name fixtures from Ch. 5.
- **Push.**

### R05 — Zodiacal, Weekday, and Life-Period layers

- Sign → rune/deity/day/stone/animal (both classical and modern-alternative
  rows, labeled); weekday → rune correspondences.
- Planetary life-periods: age → ruling deity/planet with years remaining;
  Metonic 19-year cycle position for Sun/Moon.
- **Gate:** age 22 → Sól begins; age 68 → Loki begins (30-year reign to 98);
  Metonic alignment cross-checked against the ephemeris.
- **Push.**

### R06 — The 28 Lunar Mansions

- Moon's sidereal longitude → mansion index (28 equal sidereal segments;
  **declared convention:** anchored at Alcyone per the book's first mansion,
  labeled as modern convention, not historical fact).
- Output: rune, Old Norse name, star.
- **Gate:** mansion-boundary fixtures; Alcyone anchor test; contrast note
  vs. Vedic nakshatras in docs.
- **Push.**

### R07 — Twelve Palaces and Nine Worlds

- Sign → Grímnismál palace (deity, meaning of name) as overlay;
  Nine-Worlds ↔ rune table as interpretive overlay.
- **Gate:** fixed-mapping tests (Bilskírnir→Aries … Noatún→Pisces).
- **Push.**

### R08 — Interpretation of Runic Cycles (Ch. 8)

- Rule-based synthesis combining half-month, hour, tide, mansion, life
  period, and weekday into a structured reading object.
- Deterministic; every symbolic statement tagged `interpretive` with
  `source: Pennick 2023`; computation functions remain importable without
  the interpretive layer.
- **Gate:** golden-output fixtures; anti-fabrication check (no invented
  correspondences beyond the book's tables).
- **Push.**

### R09 — The `runic` command and capability registration

- Single CLI command `runic` with flags selecting layers
  (`--half-month`, `--hour`, `--tide`, `--mansion`, `--life-period`,
  `--name`, `--full`), text + JSON output.
- Registered in `data/capabilities.json`, `data/tool_schemas.json`,
  `COMMANDS.md`, `astroengine/INTERFACE.md`, and the Hermes skill notes.
- Full test-suite pass, docs current, final DEVLOG.
- **Push** — the runic star-program stands complete.

## Acceptance for the whole program

- All nine slices implemented, tested, and pushed with verified remote HEADs.
- `runic --full` reproduces every book fixture cited above.
- Every output carries `tradition: "northern-runic"`, `source: "Pennick 2023"`,
  and `historical_claim: "modern synthesis"`.
- No slice is advertised in capabilities until its tests pass and its push
  is verified.

*Heill, and may the runes turn true. — Yrsa, for Volmarr*
