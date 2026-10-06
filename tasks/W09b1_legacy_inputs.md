# W09b1: strict legacy time and location input contracts

Status: implementing; documented before code, 2026-10-06.
Owner: legacy input adapter and CLI; part of W09b.

## Problem and intended behavior

W09a repaired date rollover but legacy local_to_utc still guesses standard time
for ambiguous/nonexistent civil clocks. Missing timezone discovery treats local
input as UTC, unresolved cities can become (0,0), and partial/invalid explicit
coordinates can fall through. These paths must fail clearly rather than generate
a plausible chart. The typed chart input domain already owns strict validation.

Reuse strict typed date/time/coordinate/ZoneInfo validation through a focused
legacy adapter while retaining legacy function names and W09a tuple shapes.
Add explicit IANA --timezone overrides to birth-aware legacy commands and separate
--timezone1/--timezone2 flags to paired charts. Require a resolved or explicitly
supplied timezone; an explicit UTC override supports intentional UTC input.
Keep no-location commands whose interface explicitly uses UTC scoped as UTC.
Invalid dates/clocks, DST folds/gaps, unresolved cities/zones, incomplete coordinate
pairs, nonfinite values and out-of-range coordinates return an actionable error
with nonzero CLI status and no successful chart output. Valid (0,0) remains valid.
Unknown time remains a local-noon surrogate and flagged unknown.

## Acceptance and ownership

Inspect every caller/CLI parser before changing the adapter. Publish any revised
contract before code. Add offline fixtures for New York fold/gap, invalid zone,
date/time/coordinate failures, explicit-zone bypass of discovery, each paired
chart's distinct UTC, and subprocess stderr/status. Retain all W09a fixtures and
normal-day regression. Test without optional geocoding libraries and with mocked
unresolved discovery so network availability never decides test results.
Wire API/CLI/help/docs/capability evidence and inspect the full diff. Run complete
tests, push passing implementation, then verify remote SHA and hosted matrix.

W09b2 owns unknown-time house suppression, polar-house and optional-body/backend
failure contracts. W09b3 owns precision-aware bracketed event roots; neither is
claimed by this input slice. A default city deliberately supplied by an existing
command remains an explicit documented legacy assumption until its own migration.

## Caller audit prepared during W09a hosted verification

Nine single-chart handlers share add_geo and resolve_birth. Synastry/composite
have separate coordinate fields but no timezone overrides. Synergy still hardcodes
London and has no location fields, so add the full paired input flags and pass
them through explicitly. Composite Davison admission also uses coordinate
truthiness and a latitude-zero sentinel; replace admission with actual input
presence so explicit zero coordinates survive. Preserve the existing Davison
formula here; spherical midpoint correctness belongs to R09. Aspect-grid and
antiscia explicitly consume UTC without locations; planet-hours is a distinct
civil-date/sunrise interface requiring its own migration review. Keep main's
error handler before any successful output and avoid a broad catch-all that
would hide computation defects.

## Chosen adapter and reproduced evidence

Add `inputs.parse_civil` as the shared civil validator and
`legacy_inputs` as the typed compatibility adapter; the legacy monolith imports
these domains, never the reverse. `resolve_birth` adds only the optional final
`timezone_override` argument, retaining all older positional arguments and the
ten-item result. `local_to_utc` retains signed relative hours and its two-item
result, now using the strict ZoneInfo path. Historical offset seconds are retained
when present; ordinary minute-offset display stays unchanged. Empty supplied
times reject in both legacy and typed APIs rather than silently becoming noon.

Geocode results must be finite/in-range; invalid explicit pairs reject before
any network call. Unresolved locations raise CalculationError rather than return
a Greenwich fallback; unresolved timezone discovery requests an explicit IANA
override. All legacy CLI CalculationErrors go to stderr with status 2. Single
and paired handlers propagate the new flags. Paired chart headers expose each
resolved time/zone and label the pre-existing London assumption if no location
was supplied; callers can now provide real independent locations for synergy.
Davison admission requires location inputs for both people and accepts (0,0).
Planet-hours still owns sunrise/date behavior, but this slice also routes its
explicit coordinate and date validation through the shared boundary so partial
or zero coordinates cannot silently select Indianapolis.

Before code, reproduced New York fold 2024-11-03 01:30 and gap 2024-03-10 02:30
silently returning standard-time UTC; missing zone returning a successful UTC
chart; Feb 30, 24:00 and empty time accepted by parse_date_time; and explicit NaN
coordinates accepted as resolved. New regression fixtures must reject those paths.

The caller audit also found secondary dates bypassing validation: progression
targets and prediction windows went directly to Julian-day formulas, and location
queries used truthiness after printing chart output. This slice admits those
inputs before output: strict target dates/years, ordered prediction windows,
paired finite query coordinates (including zero), and transit-time requiring its
transit-date. The existing default prediction duration remains one civil year;
February 29 defaults to February 28 the following year. Event-finding mathematics
and backend/house errors stay in W09b2/W09b3.
