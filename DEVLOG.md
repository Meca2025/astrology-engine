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
