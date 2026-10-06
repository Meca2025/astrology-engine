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
- [x] R05 — zodiac/weekday/life-periods: zodiac_rune() on App. 5 (classical + modern-alternative rows labeled), weekday_rune() on App. 4, life_period() on the Ch. 6 wheel (Máni 0–4 … Loki 68–98; age 22 → Sól, age 68 → Loki), metonic_cycle() Golden Number with Aun note; tests/test_runic_layers.py 8/8 green incl. pyswisseph cross-check of the 19-year full-moon recurrence; full suite 344 green.
- [x] R06 — lunar mansions: lunar_mansion()/lunar_mansions() on the Ch. 7 wheel (28 equal sidereal segments, mansion 1 Feoh opening at Alcyone 36.1175° J2000 Lahiri — declared convention; boundary epsilon against float dust); tests/test_runic_mansions.py 6/6 green; full suite 350 green; nakshatra contrast note in INTERFACE.md.
- [x] R07 — palaces & worlds: grimnismal_palace() (App. 7, Bilskírnir→Aries … Noatún→Pisces), world_rune()/nine_worlds() (Ch. 6, Asgard/Gyfu … Helheim/Hagal); labeled as correspondence overlays, not computed quantities; tests/test_runic_palaces.py 3/3 green; full suite 353 green.
- [x] R08 — runic reading: runic_reading() composes half-month/hour/tide/station/weekday/life-period/mansion/name layers into computation + interpretive statements (Ch. 8 qualities & adverbs, corpus v1.2); golden-output fixture + anti-fabrication check; tests/test_runic_reading.py 4/4 green; full suite 357 green.
- [x] R09 — runic CLI command: `runic` subcommand with --half-month/--hour/--tide/--station/--weekday/--mansion/--life-period/--name/--reading/--full/--json; registered in capabilities, tool_schemas, COMMANDS.md, INTERFACE.md, SKILL.md; README runic table completed (28 subcommands); tests/test_runic_cli.py 6/6 green; full suite 363 green.
- [x] ROADMAP_RUNIC.md COMPLETE — all nine slices (R01–R09) forged, tested, and pushed. The runic star-program stands complete.
- [x] Chart library: --save/--load(--load1/--load2)/--chart-dir on all 16 legacy commands + --save on modern JSON commands; charts/chart-show/chart-delete; astroengine/charts.py; tests/test_chart_library.py green.
- [x] Full aspect spectrum: 10 obscure aspects (biseptile→vigintile) in ASPECTS + western.json (neutral weights); ASPECT_FAMILIES + calc_aspects families filter; aspect-grid --aspects {all,major,minor,obscure}; tests/test_aspects_full.py green.
- [x] Full suite 384 green.
- [x] Divination quartet: tarot (78 cards, 10 spreads, reversals, seeds), astrology readings (general/love/career, --load), numerology (life path/destiny/soul urge/personality/personal year, masters held), i-ching (64 hexagrams, coins/yarrow, changing lines); tests/test_divination.py 17/17 green; full suite 401 green.
- [x] Rune casting: 24 Elder Futhark runes, 7 layouts (single, norns, elements, cross, hammer, nine-worlds, wheel), merkstave for asymmetric runes only, optional flagged blank rune; tests/test_runecast.py 7/7 green; full suite 408 green.
- [x] H01 chart wheels: astroengine/wheel.py (pure SVG, ASC at 9 o'clock, aspect chords), `wheel` CLI (--load/-o), tests/test_wheel.py 10/10 green.
- [x] H02 house systems: astroengine/houses.py (placidus/whole-sign/equal/koch/regiomontanus), --houses on natal/transit/synastry/solar-return/composite/wheel/reading, tests/test_houses.py 8/8 green.
- [x] H03 solar arc directions: astroengine/directions.py (arc from progressed Sun, directed ASC/MC, applying/separating), `solar-arc` CLI, tests/test_directions.py 6/6 green.
- [x] H04 annual profections: astroengine/profections.py (time-lord wheel, traditional rulers/dignities), `profection` CLI, tests/test_profections.py 7/7 green.
- [x] H05 transit watch: astroengine/watch.py (outer-planet scan, refined exact dates), `watch` CLI, tests/test_watch.py 7/7 green.
- [x] H06 electional astrology: astroengine/electional.py (Moon state, Mercury rx, planetary hours, window search), `elect` CLI, tests/test_electional.py 7/7 green.
- [x] H07 fixed stars: data/fixed_stars.json (26 bright stars, Swiss Ephemeris positions), astroengine/stars.py (IAU 1976 precession), `stars` CLI, tests/test_stars.py 8/8 green.
- [x] H08 asteroids + midpoints: astroengine/asteroids.py (honest .se1 handling), astroengine/midpoints.py (45 midpoints, activations), `asteroids`/`midpoints` CLIs, tests/test_asteroids_midpoints.py 9/9 green.
- [x] H09 draconic charts: astroengine/draconic.py (node-reckoned zodiac, contacts), `draconic` CLI, tests/test_draconic.py 6/6 green.
- [x] H10 written natal dossiers: astroengine/dossier.py (nine sections, render_dossier), `dossier` CLI, capabilities/tool schemas for all nine Horizons commands, tests/test_dossier.py 6/6 green.
- [x] O01 Younger Futhark: data/runes_younger.json (16 runes, rune-poem meanings, long/short-twig glyphs), runecast --system, tests/test_younger_futhark.py 10/10 green.
- [x] O02 Anglo-Saxon futhorc: data/runes_futhorc.json (33 runes, OE Rune Poem + Northumbrian tradition), runecast --system futhorc live, tests/test_futhorc.py 7/7 green.
- [x] O03 Ogham readings: data/ogham.json (25 staves, Auraicept kennings per McManus 1988), astroengine/ogham.py + `ogham` CLI (single/triad/aicme/wheel/grove), tests/test_ogham.py 8/8 green.
- [x] O04 Chinese zodiac: data/chinese_zodiac.json (stems/branches/NaYin/allies/clashes), astroengine/chinese.py + `chinese` CLI (lunardate CNY boundaries, verified 1984 anchor), tests/test_chinese_zodiac.py 5/5 green.
- [x] O05 Four Pillars/BaZi: astroengine/bazi.py + `bazi` CLI (Lichun year turn, jie month branches via Swiss Ephemeris, Five Tigers/Rats, JDN day pillar from verified anchors), tests/test_bazi.py 6/6 green.
- [x] O06 Tibetan astrology: data/tibetan.json + astroengine/tibetan.py + `tibetan` CLI (element-animal year, rabjung, mewa, parkha, five forces; Losar approximation disclosed; lineage variation documented), tests/test_tibetan.py 7/7 green.
- [x] ORACLES ROADMAP COMPLETE — all six slices forged, tested, Sólrún-verified, pushed.
