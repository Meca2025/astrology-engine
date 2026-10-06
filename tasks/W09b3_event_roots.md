# W09b3: precise astronomical event roots

Status: active program; first longitude/solar-return slice, documented 2026-10-06.
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

## W09b3a chosen contract, before code

Reproduced two old defects with synthetic continuous direct motion: a crossing at
the exact t=1 sample returns no event; an interior conjunction appears twice.
The current implementation/doc commit is 4b1b7e7; W09b2 code f318383 passed all six
jobs. The published next work order is now activated without another approval.

Add data-owned solver settings and frozen scalar/motion/window inputs. The pure
root owner uses bracketed bisection with both residual and time-width acceptance,
half-open windows, local unwrapped longitude, and strict nonconvergence errors.
Adaptive cells use declared speed/acceleration/jerk envelopes: derivative-sign
or acceleration-sign certificates isolate monotonic segments/unique stations;
Taylor exclusion skips provably root-free cells under those assumptions. Split
at speed-zero before looking for near-station recrossings. Subdivide uncertain
cells; unresolved cells fail rather than imply event-free coverage. A stationary
contact within angular tolerance is labeled separately from a proven crossing.
Deduplicate shared endpoints/root brackets, never all events within five days.

Numerical envelopes are conservative declared model assumptions, checked at
samples; they are not an independently certified all-epochs planetary bound.
Reports must expose that condition and distinguish root residual/temporal bracket
from ephemeris accuracy. Independent motion-bound/source-corpus certification is
I04 work. Tests use known analytic functions satisfying their declared envelopes.
Swiss Sun/Moon crossing functions provide additional same-library checks only.

Add EventWindowRequest(start, end, zodiac, ayanamsa, node_type, ephemeris_path)
with explicit-offset ISO instants or date-only UTC midnight. End is exclusive.
events.compute_events(window, body, longitude) returns roots, contacts, settings,
window and actual sample backends. CLI events exposes this exact contract.
events.compute_solar_return(ChartRequest, year) requires known time, finds/proves
a Sun crossing in the requested local civil year, and returns natal/return chart,
root evidence and local/UTC instant. It retains natal coordinates; relocated
returns are W11. CLI returns and two whitelisted agent tools/schemas/catalog
capability entries are wired in this same slice. Unknown/selected unavailable
bodies and invalid input fail with explicit errors.

Preserve find_exact_transit_dates tuple lists through a typed adapter carrying
provenance/unavailable diagnostics outside tuple iteration; invalid names reject.
Adapt solar-return text output to the proven Sun root. Prediction longitude
aspects use the new owner; stations/ingresses/eclipse sections still have their
old owner until subsequent slices. Close the CLI end date at next UTC midnight,
not 23.9 hours; print refined timestamps and scoped aspect precision. No whole-
prediction provenance claim is made until its remaining sections are migrated.
All new APIs, resources, schema routes, CLI help/output/errors and installed-wheel
imports have meaningful acceptance before push. Next: W09b3b stations/ingresses.

## Return-year correction discovered during implementation

The proposed one-crossing-per-civil-year admission is incorrect near New Year:
the real 2000-01-01 noon natal Sun has two crossings during leap year 2000, one
during 2001 (December 31), and none during 2002. Selecting a civil-year crossing
can therefore choose the following birthday's return or fail a valid request.
The target year must identify the local Gregorian birthday anniversary. Search
around that birthday (local noon anchor, February 29 clamped to February 28), then
select the nearest proven Sun crossing; report the exact local/UTC instant, which
may belong to an adjacent calendar year. Equidistant candidates, failed brackets
or unavailable supported-calendar windows reject. The broad declared annual
search window also accommodates sidereal profiles; no silent tropical substitution.
This corrects the earlier proposed civil-year restriction before acceptance.

Astrodienst's own return-chart FAQ explains selecting a solar-return year and
birthday/place conventions: https://www.astro.com/faq/fq_fh_return_e.htm
This is method semantics, separate from independently verified astronomy.
