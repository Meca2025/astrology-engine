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
