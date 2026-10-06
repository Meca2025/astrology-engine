# W09b3: precise astronomical event roots

Status: next ready program after W09b2 acceptance; documented 2026-10-06.
Owner: typed event domain, serialized ephemeris and legacy event adapters.

## Problem and required end state

Legacy find_exact_transit_dates has raw unprotected Swiss calls, silent exceptions,
fixed-step crossings, missed endpoints and duplicated conjunction/opposition targets.
Its five-day duplicate test compares tuple element 3 (glyph) to natal planet, and
would discard legitimate nearby recrossings if repaired without redesign.
Stations/ingresses similarly hide failures and use fixed-iteration approximations;
solar return estimates Newton increments with a constant Sun speed and can return
without a proven root. Prediction closes its end date at 23.9 hours, dropping six
minutes. Lunar VOC/lunations and eclipses need explicit event/result contracts.

Provide typed, frame-aware event requests and bounded bracket/refinement results
with time/angular residuals, convergence, actual calculation provenance, explicit
unavailable bodies and half-open UTC windows. Preserve legacy function names and
tuple shapes by adapting completed domain methods. No failed/unconverged search
becomes a successful empty event list. Never invent roots across the 180-degree
signed-distance discontinuity or fabricate results from fallback coordinates.
Any selected optional body unavailable must be named, not silently treated as
an event-free interval. Rules/settings/tolerances live in versioned JSON.

## First bounded slice: longitude roots and solar returns

Audit/reproduce concrete old failures before implementing. Build the reusable
scalar bracket/refiner and circular longitude crossing scan with declared motion
and sampling guarantees, half-open endpoint rules, wrap and station recrossing
handling. Use public lock-owned ephemeris snapshots for every astronomy sample;
direct raw swe calls and private-lock imports are forbidden in new domains.
Replace the legacy transit-to-natal aspect and solar-return computation with this
owner, completing their text output/diagnostics and available Python API wiring.
Include precision/tolerance/provenance in structured results and truthful text
scope. Check uniqueness by event identity and root-time tolerance; preserve close
retrograde repeats. Solar return must prove a root in the requested civil year,
with January/December, calendar-year/UTC rollover and nonconvergence cases covered.

Complete/push this bounded slice before moving to stations/ingresses, then lunar
VOC/lunation and eclipses/general returns. Those follow-on work orders must define
their own schemas/CLI/agent integration before code. If a public events CLI/tool
is introduced, publish its complete schema/catalog/whitelisted dispatch/tests in
that same slice; do not leave a callable API orphaned. W09 remains incomplete
until all named event submethods and error paths have evidence.

## Acceptance and boundaries

Pure synthetic fixtures exercise exact endpoints, 0/360 wrap, opposition branch,
fast Moon motion, multiple close roots, station reversals/tangencies and rejected
invalid/nonconverged brackets. Real ephemeris roots compare residuals/speeds with
direct Swiss output, separately labeled as same-library checks. Test required and
optional failures, mixed-frame isolation, calendar windows and real offline CLI.
Full regression suite, wheel/import if package APIs change, diff/ownership audit,
updated interfaces/capabilities/TODO/devlog, passing push and all six hosted jobs
are required before acceptance. No independent ephemeris accuracy claim follows
from refinement tolerances; inspect authoritative sources for event conventions.

Local sunrise-calendar semantics remain V13; spherical Davison is R09; approximate
legacy obliquity/GMST/angular-line migration is L09. W10 owns actual astronomical
sect and dignity/triplicity variants (legacy sect is still simplified). Preserve
all existing functions, registry data and historical docs. No AI/network/persistence
or ephemeris provisioning is introduced by this work.

Primary astronomy reference: https://www.astro.com/swisseph/swephprg.htm
