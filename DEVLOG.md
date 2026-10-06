# Development log

## 2026-10-06 — orientation

Inspected remote `main` at `a76174d`. Existing local Ember copy belongs to a different
repository, so work uses a fresh clone of astrology-engine and leaves Ember alone.
Mapped 16 legacy CLI commands and found time-rollover/fallback/agent-contract gaps.
Added five-layer Mythic Engineering documentation and a dependency-ordered roadmap.
User authorized implementation/push loops; no repeated approval gate is needed.

## S01 — chart foundation

Implemented the typed/profile/data/provenance/CLI boundaries. 24 tests and wheel
resource check passed. UTC midnight and DST/polar failures are explicit. Existing
text commands preserved; their historical gaps remain separately documented.

## S02 — Jyotisha D1

Added data-defined navagraha/nakshatra profile and wired JSON command. All 34 tests
passed, including direct Lahiri house/position checks and 108 pada interiors.
Restored original ignore rules after detecting the initial ignore-file overwrite.

Hosted Windows S01/S02 jobs exposed cp1252 decoding in test subprocesses.
Explicit UTF-8 decoding and ASCII-safe JSON transport added; Linux/macOS
computation jobs passed. Follow-up acceptance awaits the repaired hosted matrix.

## S03 — classical vargas

Sixteen sign mappings wired through API/CLI. 78 total tests passed, including
source worked placements and D2/D30 boundaries. Documented D27 Example 23
counting error; calculation follows the stated rule. No physical longitudes
or exhaustive school coverage claimed.

## S04 — Vimshottari

87 total tests passed. Added maha/antar timeline, birth balance, three named year
clocks and as-of lookup. Example 50 balance matched; subperiods are anchored before
birth and exact boundary belongs to next period. Hosted repaired Windows matrix
passed together with Linux/macOS on Python 3.11/3.12.

## S05 — panchanga snapshot

101 total tests passed. Implemented instant lunar/solar partitions and explicit
calendar limits. Local weekday tested across UTC date rollover.

## S06 — relationships

108 total tests passed. Separate birth zones, static aspects, receiving-chart
certainty-aware overlays, deterministic circular composites and explainable
symbolic synergy exposed via relationship/synergy-json. Exact antipodal midpoint
ambiguity is retained. No applying/separating motion across birth epochs.

## S07 — locations

113 total tests passed. Added fixed-instant relocation, Swiss equatorial positions
and exact-latitude geometric angular lines with circumpolar states. Tested
antimeridian normalization, horizon roots and zodiac-independent geometry.

## S08 — Western starter tools

122 total tests passed. Added whole-sign annual profections, configurable integer
harmonics and midpoint sensitivity; CLI registration split by owning domain.
Birthday/leap/missing-time conventions and mathematical coordinates are explicit.

## A01 — agent contracts and boundary audit

136 total tests passed. Added checked-in skill, data-owned request schemas and
whitelisted local service routing. Exact-pada audit found nine nominal floor
partition failures; explicit half-open boundary lookup repaired them, with all
108 boundaries and every equal-varga subdivision plus neighboring floats checked.
Agent manifest is provided, not installed into an external host registry.

## Continuation

Hourly thread continuation configured in Codex as Astrology Engine Expansion.
It continues documented, validated, verified pushes from W09a onward. Completion
means roadmap acceptance criteria, not the initial eight slices. The automation
reports completed slices or actionable failures and stays quiet on unchanged state.

Final implementation 45c7a3e passed all six hosted jobs in run 37443735522.
Fresh installed wheel outside source exercised all eight tools and nine JSON
resources. Initial first wave plus local agent contracts are verified; the full
roadmap remains active. No physical Pi/mobile or external agent deployment claimed.

## W09a — legacy UTC calendar repair and immediate continuation

Published the signed-hour/normalized-date compatibility work order before code.
Reproduced thirteen failing regressions; fixed date carry in both directions,
local-noon conversion, explicit coordinate certainty and zero-coordinate synastry
overlays. All 150 local tests pass. pytz is now a declared runtime dependency.
Legacy DST ambiguity/gap and unavailable-zone fallbacks remain W09b work.

The user requested immediate next-slice continuation. Activated a continuous
Codex Goal and paused the prior hourly heartbeat. W09b1 is the next documented
input-contract slice, followed by house/backend and event-root slices.

W09a hosted Linux/macOS checks passed; Windows found the new import-based CLI
test subprocess using cp1252. The script entry point normally installs its UTF-8
wrapper, but the test intentionally imports main to mock timezone discovery.
Set Python's UTF-8 mode in that child process and retain explicit UTF-8 decoding.
Computation assertions stay unchanged; repaired hosted acceptance remains pending.

W09a hosted acceptance: c1c8c2cabf537d9827fcd17d523846fdbf8558d0, [run 37445523298](https://github.com/hrabanazviking/astrology-engine/actions/runs/37445523298), all six jobs successful. All 150 tests pass; W09b1 is next.

## W09b1 — strict legacy input contracts

Published and pushed work-order revisions before implementation. Added shared
parse_civil and a typed legacy_inputs adapter; preserved entry-point names, tuple
shapes, UTC rollover and normal historical same-day display. Replaced standard-time
DST guesses and unresolved UTC/Greenwich fallbacks with explicit input errors.
Wired single-chart zone overrides and independent paired location/zone controls
including synergy; paired output exposes inherited London defaults. Davison
admission now requires both locations and accepts zero. Secondary date/year/window
and query/planet-hour coordinate admission is strict, including leap-window rules.

223 local tests pass, including 73 added cases for DST, uncertainty, discovery
bypass, numeric overflow, every birth handler's zone propagation, independent
paired Julian days, real subprocess errors and historical IANA seconds. Agent
schemas already declare these date/time formats; no new tool is needed. Legacy
house/backend failures and astronomical root solving remain W09b2/W09b3.

W09b1 hosted/wheel acceptance: c6a3696718d87791b7cb87b98b3cbdfddd1eb0cc, [run 37447854001](https://github.com/hrabanazviking/astrology-engine/actions/runs/37447854001), all six jobs successful with 223 tests. A rebuilt wheel installed outside source passed strict adapter and nine-resource checks. Next: W09b2.

## W09b2 — house uncertainty and real astronomy failures

Pushed the adapter/rendering plan before code; reproduced fabricated polar houses,
wrong South Node motion and silent optional absence. Added a frozen UT request,
public lock-owned ephemeris boundaries and JSON required/optional body rules.
Preserved legacy function names/dict iteration/house tuple while retaining actual
backend flags and named optional diagnostics. Required failures reject; no invented
cusps/angles/solar hours. Corrected South Node motion/latitude and derived marker.

Text commands preflight requested houses and honor unknown time. Natal omits
house/sect/lot conclusions; transit/progressions keep flagged noon positions.
Receiving synastry overlays are independent; Davison requires both known times
and locations. Dignity no longer makes an unused house calculation. Known-time
requirements are explicit for house/instant-dependent commands. 283 local tests
pass; exact hosted and installed-wheel receipts follow after push. W09b3 event
roots are next; approximate location helpers and local sunrise calendars remain
separate later migrations. No new cloud/LLM tool or external deployment is claimed.

W09b2 installed-wheel check passed in a fresh Python 3.12 environment outside the
source checkout: all ten JSON resources, frozen UT request/import, required and
optional bodies with actual Moshier flags, same-motion nodes, requested houses and
polar failure, ordered solar events, unknown-time chart and updated capability
scope. The wheel ships the typed bridge; the legacy text script still runs from
the source checkout. Hosted acceptance remains pending the implementation push.

W09b2 hosted acceptance: f318383a3488bad685e74b49da4fd4ab95563866, [run 37450000246](https://github.com/hrabanazviking/astrology-engine/actions/runs/37450000246), all six jobs successful
(Linux/macOS/Windows, Python 3.11/3.12), with 283 tests. Fresh installed wheel passes
the ten-resource/astronomy bridge checks outside source. Next: W09b3 longitude
crossings and solar-return roots, then the remaining event-method migrations.

## 2026-10-06 — R01 Runic Corpus complete (ROADMAP_RUNIC.md slice 1)

Skald named it `data/runic.json`; Rúnhild set the schema; Eldra transcribed
all eleven table groups from Pennick (2023); Sólrún verified with
tests/test_runic.py (12/12 green, full suite 295 green). Honest-transcription
findings preserved in the data: (1) planetary-hours grid has a noon
discontinuity — hours 00-11 follow a rotated deity sequence while 12-23 follow
the classical Chaldean order from each day's ruler, consistent across all seven
columns, transcribed as printed; (2) Friday 19:00 printed 'Prigg', read as
'Frigg'; (3) the Kenneth worked example's 'Odal 22:30-23:30' conflicts with the
defined wheel (22:30 is Is; Odal is 10:30-11:30) — the systematic wheel,
cross-confirmed by the tide breakdown, is encoded. All tables labeled
historical_claim: modern synthesis. Védis registered the corpus in
data/README.md and COMPONENT_INDEX.md; no CLI surface in R01 (R09). Next: R02
runic half-months engine.

## 2026-10-06 — R02 Half-Months Engine complete

Skald/Rúnhild set the contract: frozen RunicDateRequest, half_month_rune with
explicit boundary/timezone rules. Eldra built astroengine/runic.py (datetime +
zoneinfo only, no ephemeris — the wheel is calendrical). Sólrún verified with
tests/test_runic_half_months.py (7/7 green, full suite 302 green) against the
book's fixtures: Peorth 13 Jan, Elhaz 28 Jan (05:00 refinement tested),
Ken 13 Sep, Ing 14 May, Feoh 29 Jun, Eoh year-wrap both ends. Two defects found
and fixed in-slice: a parameter shadowing datetime.date, and a wrong test
fixture (01-28 is Elhaz's start, not Peorth's). Védis recorded the module in
astroengine/INTERFACE.md and COMPONENT_INDEX.md. No CLI surface (R09). Next: R03
runic hours + planetary hours.

## 2026-10-06 — R03 Runic Hours + Planetary Hours complete

Extended astroengine/runic.py: runic_hour() on the Ch. 4 solar wheel,
to_local_apparent_time() with the declared longitude+EoT approximation
(the book's "real time", midday = sun due south), planetary_hour() on the
App. 3 grid (hour-to-hour CLOCK divisions), and sele() detecting when the
hour-rune's deity correspondence contains the planetary deity — Pennick's
"especially powerful" coincidence. Sólrún verified with
tests/test_runic_hours.py (7/7 green, full suite 309 green): Ingrid's Rad
hour (16:45), a constructed true-sele (Saturday 13:05 civil at lon +7.5 ->
LAT 13:51 Ur/Thor), LAT conversion bounds, grid spot checks, explicit
CalculationErrors. One wrong test fixture fixed in-slice (LAT at the false-
sele probe is 03:28 Elhaz, not Tyr). The Kenneth example remains excluded
as a fixture per the R01 wheel-conflict note. Védis updated INTERFACE.md
and COMPONENT_INDEX.md. No CLI surface (R09). Next: R04 tides, eightfold
year, runic names.

## 2026-10-06 — R04 complete: tides, eightfold year, runic names

The fourth runic slice is forged and sealed. Eldra extended
`astroengine/runic.py` with `tide()` (the 8 App. 6 day-tides on civil clock
time, Midnight wrapping 22:30-01:30), `year_station()` (the Ch. 5 Stations
of the Mystic Year: number, runes, festival, day-hour, symbolic event), and
`runic_name()` (half-month rune + LAT hour-rune pair per Ch. 5). The book
defines the station table but NOT its calendar boundaries, so boundaries
are a declared engine convention (`festival-span`): each station spans
[festival, next festival) at conventional festival dates; the First
station, festival-less in the book, is conventionally anchored at Aug 13
(start of the As half-month). `data/runic.json` v1.1 gains the 8-station
table. Sólrún's `tests/test_runic_tides.py`: 27/27 green, full suite 336
green. Two honesty findings in-slice: a station boundary bug caught before
it escaped (Dec 25 must be Fourth/Jera), and the Darwin probe revealed the
book's example ignores the equation of time (civil 20:27 = Wyn hour; LAT
20:43 = Hagal) — documented, not corrected. The book's rendered names
(Kenneth, Ingrid, Darwin) are literary wordplay, not mechanical output.
Védis mapped the new surface in INTERFACE.md and COMPONENT_INDEX.md. Next:
R05 lunar mansions + 12 Grímnismál palaces.

## 2026-10-06 — R05 complete: zodiacal, weekday, and life-period layers

The fifth runic slice is forged. `astroengine/runic.py` gains `zodiac_rune()`
(App. 5: rune/deity/planet/day/stone/animal, with the Capricorn/Aquarius/
Pisces classical-vs-modern rows labeled), `weekday_rune()` (App. 4: deity/
planet/rune/tree/herb/element/esoteric number/magic square),
`life_period()` (the Ch. 6 wheel Máni 0–4 … Loki 68–98, with years elapsed
and remaining; outside 0–98 is an explicit error), and `metonic_cycle()`
(the calendrical Golden Number, (year mod 19)+1, with the Aun 310-year
recalibration noted). No corpus changes were needed — R01 transcribed it
all. Sólrún's `tests/test_runic_layers.py`: 8/8 green, full suite 344
green, including the roadmap's ephemeris gate: full moons 19 years apart
(2007 vs 2026) land within 2 days of each other, as Ch. 6 describes.
runic.py remains ephemeris-free by design. Védis mapped the surface in
INTERFACE.md and COMPONENT_INDEX.md. Pushed via the PAT tool — no approval
prompts, binary-safe. Next: R06 lunar mansions + palaces.

## 2026-10-06 — R06 complete: the 28 lunar mansions

The sixth runic slice is forged. `astroengine/runic.py` gains
`lunar_mansion()` and `lunar_mansions()` for the Ch. 7 wheel: 28 equal
sidereal segments of 360/28 degrees, mansion 1 (Feoh, "Boars' Throng",
Alcyone) opening at Alcyone's J2000 sidereal longitude 36.1175° (Lahiri;
derived from RA 3h47m24.3s Dec +24°06'18"). The anchor is a declared
modern convention, labeled as such — the book says the mansions "began
with the star Alcyone" but gives no degree. runic.py stays
ephemeris-free: the caller supplies the Moon's sidereal longitude.
Sólrún's `tests/test_runic_mansions.py`: 6/6 green, full suite 350 green.
One float-dust defect fixed in-slice (exact-boundary longitudes need an
epsilon, else 0.99999… floors into the previous mansion). Védis mapped the
surface in INTERFACE.md incl. the contrast note vs. Vedic nakshatras (27
vs 28, Ashwini zero point vs Alcyone — computed separately, never
synthesized). Pushed via the PAT tool. Next: R07 palaces and nine worlds.

## 2026-10-06 — R07 complete: twelve palaces and nine worlds

The seventh runic slice is forged. `astroengine/runic.py` gains
`grimnismal_palace()` (App. 7: Bilskírnir→Aries … Noatún→Pisces, with the
meaning of each palace-name and its deity), `world_rune()`, and
`nine_worlds()` (Ch. 6: Asgard/Gyfu … Helheim/Hagal). These are fixed
correspondence overlays — looked up, not computed — and every result says
so (`"kind": "correspondence overlay"`), honoring the standing
computation/interpretation split. Sólrún's `tests/test_runic_palaces.py`:
3/3 green, full suite 353 green. Védis mapped the surface. Pushed via the
PAT tool. Next: R08 interpretation synthesis.

## 2026-10-06 — R08 complete: interpretation of runic cycles

The eighth runic slice is forged. `astroengine/runic.py` gains
`runic_reading()`, the Ch. 8 "Chronomantic Methods" synthesis: one
structured object with a `computation` section (raw R02–R07 layer
results) and an `interpretation` section of deterministic symbolic
statements. The corpus grows to v1.2 with the Ch. 8 tables transcribed
verbatim — planetary qualities (Sól=self-expression … Máni=response)
and the 24 Elder Futhark adverbs (Feoh=richly … Dag=changingly). The
anti-fabrication law is enforced in code: a quality clause appears only
when a Ch. 8 key matches the rune's App. 1 deity; runes outside the 24
get no adverb; anything uncovered is omitted, never invented. Sólrún's
`tests/test_runic_reading.py`: 4/4 green (golden-output fixture pinned
word-for-word, anti-fabrication sweep across four moments), full suite
357 green. Védis mapped the split in INTERFACE.md. Pushed via the PAT
tool. Next: R09, the `runic` command — the final slice.

## 2026-10-06 — R09 complete: the `runic` command — THE PROGRAM STANDS COMPLETE

The ninth and final runic slice is forged. `astrology_engine.py` gains
the `runic` subcommand: one command for the whole star-program, with
layer flags (--half-month --hour --tide --station --weekday --mansion
--life-period --name --reading), --full, and --json. Text output wears
the legacy header/section style with a provenance footer; JSON carries
computation + optional interpretation + provenance. Registered in five
places: data/capabilities.json, data/tool_schemas.json, COMMANDS.md,
astroengine/INTERFACE.md, and the Hermes SKILL.md. The README's runic
table now tells the whole saga R01–R09, and the subcommand count reads
28. Sólrún's `tests/test_runic_cli.py`: 6/6 green; one pre-existing
test needed its hard-coded tool count bumped 8→9; full suite 363 green.
Pushed via the PAT tool — no approval prompts, binary-safe, Volmarr's
edits merged-first always.

ROADMAP_RUNIC.md is complete. Nine slices, nine pushes, every table
labeled modern synthesis, computation forever apart from interpretation.
The runic star-program stands complete. 🌙

## 2026-10-06 — Chart library + full aspect spectrum

Volmarr's commission: saving/loading for every kind of chart, and every
form of aspect however obscure. Both are forged.

**Chart library** (`astroengine/charts.py`): charts persist as JSON under
`~/.astroengine/charts` (or `$ASTROENGINE_CHART_DIR` / `--chart-dir`),
each carrying name, type, save time, engine version, request and result.
All 16 legacy commands take `--save NAME`; birth-data commands take
`--load NAME` (`--load1/--load2` for the two-person commands), filling
any date/time/lat/lon/timezone flags the user did not pass — so
`transit --load volmarr --transit-date 2026-10-23` just works. The modern
JSON commands honor `--save` through `run_command` (notice on stderr,
stdout stays pure JSON). `charts`, `chart-show`, `chart-delete` manage
the library. Wiring is centralized in `main()`'s dispatch: every command
returns its headline result, one `maybe_save_chart` call saves it.

**Aspects**: the spectrum grows from 12 to 22 — biseptile, triseptile,
novile, binovile, quadnovile, decile, undecile, tredecile, quindecile,
vigintile, with tight 1.5°/1.0° orbs. `ASPECT_FAMILIES` + a `families`
filter on `calc_aspects`; `aspect-grid --aspects {all,major,minor,
obscure}`. `data/western.json` mirrors the ten with weight 0, so synergy
scores do not shift; the high-noise inline loops (transit, synastry,
predict, progressions) keep their strong-aspect focus. Sólrún's new
suites: 21/21 green, full suite 384 green. Pushed via the PAT tool.

## 2026-10-06 — The divination quartet: tarot, readings, numerology, I-Ching

Volmarr asked for them separately, and separately they stand — four new
divination systems, each its own module, data, and CLI command, all held
to the house honesty standard (labeled interpretive, never computed
fact).

**Tarot** (`astroengine/tarot.py`, `data/tarot.json`): the full 78-card
RWS deck with original one-line meanings, ten spreads (single, three,
five-cross, celtic-cross, horseshoe, relationship, career, choice,
year-ahead, chakra), reversals, and seeded reproducible draws.

**Astrology readings** (`astroengine/readings.py`): general/love/career
narratives woven from real chart data — elemental temperament, Sun/Moon/
Ascendant lines, the tightest major aspects, Venus/MC foregrounding for
love/career. Reads `--load NAME` saved charts or computes fresh.

**Numerology** (`astroengine/numerology.py`, `data/numerology.json`):
Pythagorean life path, destiny, soul urge, personality, birthday,
personal year; masters 11/22/33 held; ð/þ/æ/ø transliterated for Norse
names. (Volmarr: Life Path 11, Soul Urge 22 — a double master.)

**I-Ching** (`astroengine/iching.py`, `data/iching.json`): 64 hexagrams
in King Wen order with original renderings; coin or yarrow casting with
true changing lines and the relating hexagram.

Sólrún's `tests/test_divination.py`: 17/17 green, full suite 401 green.
Pushed via the PAT tool.

## 2026-10-06 — Rune casting joins the divination line

Volmarr asked for rune readings in a variety of layouts, and the runes
answered: `runecast` casts the 24 Elder Futhark runes (original one-line
meanings, `data/runes.json`) across seven layouts — single, the Norns,
the elements, the cross, Thor's hammer, the Nine Worlds, and the
twelve-month wheel. Merkstave readings apply only to asymmetric runes;
the nine symmetric ones read the same either way, as tradition holds.
The blank rune is available via `--blank`, honestly flagged as a modern
invention. Seeded and reproducible like its tarot sibling.

Sólrún's `tests/test_runecast.py`: 7/7 green, full suite 408 green.
Pushed via the PAT tool.

## 2026-10-06 — H01: chart wheels (SVG)

First slice of the Horizons program. `astroengine/wheel.py` renders a
natal chart wheel as dependency-free SVG — deep-night background, gold
zodiac ring with glyphs and degree ticks, house cusps and numbers,
planet glyphs spread across two rings when crowded, aspect chords
colored by kind (white/red/orange/blue/green), ASC rotated to 9 o'clock
and MC near the top as tradition demands, the native's name at the
heart. The module takes plain data only and never imports the legacy
monolith (house rule); the `wheel` CLI computes via the legacy boundary
and passes data in. Also fixed the wheel subtitle to prefer explicit
coordinates over legacy default city names ("London GB" quirk).

Sólrún: `tests/test_wheel.py` 10/10 green plus independent subagent
verification. Pushed via the PAT tool.

## 2026-10-06 — H02: house systems

Second slice of the Horizons program. `astroengine/houses.py` exposes
`house_cusps()` for five systems — placidus, whole-sign, equal, koch,
regiomontanus — with system codes read from data/profiles.json (nothing
hardcoded) and explicit errors on unknown systems. The `--houses` flag
now rides on natal, transit, synastry, solar-return, composite, wheel,
and reading; `_optional_houses` defaults to placidus so existing
behavior is untouched, and `wheel --load NAME --houses whole-sign`
recomputes cusps in the requested system. Saved charts record the flag
in their request automatically.

Sólrún: `tests/test_houses.py` 8/8 green plus independent subagent
verification. Pushed via the PAT tool.
