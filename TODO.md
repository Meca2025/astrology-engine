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
- [ ] V09 — expanded classical Jyotisha mechanics, with named rule/source fixtures.

Next ready work order: tasks/W09b3_event_roots.md. W09b is split into inputs,
house/backend errors and event roots so each has independent acceptance evidence.
See ROADMAP for the complete expansion, including later validation/research gates.
Legacy paths still have known input/provenance limitations; do not advertise new
coverage through an unmodified legacy command. Report exact implementation scope.
