# TODO — execution truth

Read this first. Current work: 2026-10-06 expansion under Mythic Engineering.

- [x] Inspect real repository and current code; map correctness/agent gaps.
- [x] Add standard documents and expanded roadmap; publish before code.
- [x] S01 — typed chart foundation, strict time/location handling, JSON, discovery, CI.
- [x] S02 — Vedic D1, ayanamsa variants, nodes, nakshatra/pada.
- [x] S03 — named classical divisional chart mappings.
- [x] S04 — Vimshottari maha/antar periods with balance at birth.
- [x] S05 — instant panchanga elements with named conventions.
- [x] S06 — structured relationship analysis with real locations/zones.
- [x] S07 — relocation and exact-latitude angular location lines.
- [x] S08 — profections, harmonics, midpoint sensitivity.

- [x] A01 — checked-in agent skill, eight tool schemas and local whitelisted routing.
- [x] W09a — repair legacy UTC date rollover and explicit coordinate certainty; 150 tests pass locally and across all six hosted jobs.
- [ ] W09b — strict legacy timezone/house errors, schema migration and event roots.
- [x] W09b1 — strict legacy civil/coordinate inputs, per-person timezone/location controls; 223 tests pass locally and in all six hosted jobs; installed wheel verified.
- [x] W09b2 — explicit house/backend failures, unknown-time rendering and node-motion repair; 283 tests pass locally and in all six hosted jobs; installed wheel verified.
- [x] R01 — runic corpus: data/runic.json transcribes all Pennick (2023) tables (32 runes, 24 half-months, 24 runic hours, 168 planetary-hour cells, weekdays, zodiac+variants, 8 tides, 28 mansions, 12 palaces, 9 worlds, 7 life-periods/98 years); tests/test_runic.py 12/12 green; full suite 295 green; print quirks documented, not corrected.
- [x] R02 — half-months engine: astroengine/runic.py half_month_rune(date, time, timezone) per Pennick App. 2 (latest-start rule, Eoh wrap, boundary-time refinement, explicit CalculationError on bad date/time/zone); tests/test_runic_half_months.py 7/7 green; full suite 302 green.
- [x] R03 — runic hours + planetary hours: runic_hour() on the Ch. 4 solar wheel, to_local_apparent_time() (declared longitude+EoT method), planetary_hour() on the App. 3 grid (clock hours), sele() coincidence detection; tests/test_runic_hours.py 7/7 green incl. Ingrid's Rad hour and a true-sele fixture; full suite 309 green.
- [ ] V09 — expanded classical Jyotisha mechanics, with named rule/source fixtures.

Next ready work order: tasks/W09b3_event_roots.md. W09b is split into inputs,
house/backend errors and event roots so each has independent acceptance evidence.
See ROADMAP for the complete expansion, including later validation/research gates.
Legacy paths still have known input/provenance limitations; do not advertise new
coverage through an unmodified legacy command. Report exact implementation scope.
- [x] R04 — tides, stations, names: tide() on the App. 6 day-tides (Midnight wraps); year_station() on the Ch. 5 Stations of the Mystic Year (rune/festival/day-hour/symbolism per the book table; declared festival-span boundaries, First station conventionally at Aug 13); runic_name() composing half-month + hour runes (Ingrid's Ing-Rad wheel-consistent; Darwin's 'Darwin' literary; Kenneth/Odal conflict documented); data/runic.json v1.1 with the 8-station table; tests/test_runic_tides.py 27/27 green; full suite 336 green.
