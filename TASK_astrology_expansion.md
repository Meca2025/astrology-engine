# Task: astrology capability expansion

Date: 2026-10-06. Workflow: Mythic Engineering. Human authorization: create the
roadmap and standard documents, implement the first slice, validate and push it,
then repeat for subsequent slices. This supplies implementation/push approval;
individual slices remain documented before code. No existing files are removed.

## What exists

Baseline `a76174d`: a 3,277-line Python CLI, 16 text commands, Swiss Ephemeris,
optional geocoding/timezone libraries, Western aspects/dignities/lots, secondary
progressions, solar returns, midpoint relationships, approximate location lines,
and a modern Norse symbolic overlay. No packaging, automated tests, checked-in
Hermes skill, structured output, or explicit technique registry.

## Findings

`local_to_utc` loses UTC date rollover. Missing locations/timezones and failed
houses can silently produce seemingly valid charts. Nodes have inconsistent
South Node speed. Sidereal internals force Fagan/Bradley and are not exposed.
Synergy assumes London for both births. Import rewrites stdout. Existing docs
contain unsupported accuracy/canonical-chart claims. These are correctness and
agent-contract boundaries, not merely missing features.

## Desired end state

A reproducible, offline-capable computation package with explicit chart profiles,
UTC/time/location certainty, provenance, JSON contracts, data-owned tradition
rules, and truthful capability discovery. Preserve the existing CLI while adding
validated commands. Separate arithmetic from symbolic interpretation. A roadmap
covers comprehensive Vedic functions, advanced Western methods, location and
relationship astrology, and other traditions without claiming universal coverage.

## Domains and paths

- `astroengine/`: inputs, ephemeris adapter, calculations, service contracts.
- `data/`: immutable capability and technique definitions.
- `astrology_engine.py`: existing text CLI and additive command registration.
- `tests/`, `.github/workflows/`: mathematical, boundary, integration evidence.
- root orientation docs, `docs/DECISIONS/`, `tasks/`: continuity and slice records.

## Invariants

No fabricated positions/angles on failure. No silent timezone or tradition
selection. Sidereal settings serialized around Swiss Ephemeris calls. Western
Placidus remains the legacy default; Jyotisha explicitly selects sidereal profiles.
No API keys, cloud/LLM calls, birth-data persistence, or runtime writes to `data/`.
Rule variants, unavailable methods, uncertainty, and evidence are machine readable.

## Execution

1. Publish this task and the five-layer documentation set before implementation.
2. S01: installable chart foundation, JSON, provenance, capability discovery, CI.
3. S02: Vedic D1, ayanamsas, node selection, nakshatras and padas.
4. Continue dependency-ordered slices in `ROADMAP.md`; each task names ownership,
   invariant checks, acceptance criteria, and evidence before implementation.
5. Review/test each slice, update TODO/devlog/interfaces, commit, push, and verify
   remote HEAD. A failed acceptance gate is a defect to fix, not a completed slice.

## Verification

Offline deterministic inputs; compare coordinates with direct Swiss Ephemeris;
independent mathematical boundary fixtures; UTC midnight/DST tests; subprocess
JSON/error contracts; preserve legacy help and quick smoke commands; hosted CI.
Cross-platform CI evidence is distinct from physical Raspberry Pi/mobile evidence.
