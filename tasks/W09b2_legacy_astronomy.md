# W09b2: legacy house uncertainty and astronomy failures

Status: accepted locally, installed and across all six hosted jobs; documented before code, 2026-10-06.
Owner: legacy computation adapters and text rendering; part of W09b.

## Problem and required end state

W09b1 admits trustworthy time/location inputs, but legacy calc_houses can fabricate
fallback angles/cusps, unknown-time commands still compute noon houses, and
calc_planet_positions silently omits failed bodies or substitutes rough values.
These paths must expose uncertainty and real backend availability before output.
Keep function names and command access while migrating them to reliable typed
boundaries. Reuse the core lock/explicit settings where applicable; audit actual
legacy callers and third-party backend initialization before changing contracts.

Known-time Placidus failure must produce a clear nonzero calculation error, with
no successful chart output or invented cusp fallback. Unknown-time natal output
can show flagged noon-surrogate planetary positions but has no house/ASC/MC, sect,
lots or house-dependent conclusions. House-dependent commands require known time
or explicitly report unavailable components. Paired overlays depend on each
receiving person's known time; Davison houses require both times. Location lines
and profections must not be derived from an unknown instant.

Major-body failures reject; optional asteroids/Chiron are explicitly unavailable
with diagnostics when their ephemeris data is absent. Do not label missing-body
failure as a successful empty calculation. Preserve actual backend flags and
never claim physical accuracy from a requested flag. Document the legacy text
provenance contract and keep richer structured methods owned by the typed core.
All known computation errors use stderr/status 2; eliminate successful-error
returns only within the owning migration. Do not hide arbitrary programming bugs
with broad catch-all handlers.

## Acceptance

Offline fixtures cover valid houses and direct Swiss comparison, polar Placidus
failure, unknown-time single and paired rendering/admission, missing ephemeris
data for optional bodies, injected major-body failures, actual returned backend
selection, and CLI error status with no fabricated chart output. Retain W09a/b1
tests and review any test changes against the real new uncertainty contract.
Test JSON and existing text commands where the boundary is shared. Run full local
tests, build/install if public package wiring changes, inspect diff, update
interfaces/capabilities/evidence and push passing implementation. Verify exact
remote SHA and all six hosted jobs before closing.

W09b3 owns precision-aware bracketed astronomical event roots and date-window
results; R09 owns spherical Davison geography. Broader ephemeris provisioning,
license/environment freeze and historical timezone source confidence remain I01/I02.

## Initial caller/backend audit

calc_houses currently returns fabricated equal cusps and zero ASC/MC after either
missing Swiss or any exception. calc_planet_positions discards actual backend flags
and catches every body failure silently; its derived South Node negates North
Node speed and hardcodes retrograde. Correct the node motion when migrating this
shared body adapter and add an explicit regression. The typed ephemeris owner
already uses a reentrant lock, settings reset, actual flags and optional null
houses, so any new legacy bridge must coordinate through its public boundary
instead of importing its private lock or leaving raw sidereal state unprotected.
Nine single birth handlers and paired overlays/Davison still discard or bypass
time_known. Date-only antiscia/aspect-grid have no location/house contract.
Planet-hours catches any astronomy error, prints stdout and returns success;
that error path is in this slice, while sunrise calendrical semantics need their
own later V13/planetary-hour migration. Preserve all legacy function names; do
not treat a negative/zero fabricated value as a substitute for unavailable data.

## Chosen interface and rendering plan

Add frozen EphemerisRequest for an admitted UT Julian day, zodiac, ayanamsa and
optional data directory. Public ephemeris.positions_at_jd, houses_at_jd and
solar_day_events own the existing lock and reset their settings on every request.
The legacy bridge reads a versioned JSON required/optional body registry and
preserves the position dict and three-item house tuple. A dict-compatible snapshot
has unavailable-body and provenance attributes outside the iterable body keys;
each available position retains actual returned flags/backend. No metadata is
mistaken for a planet. Optional Swiss errors become named diagnostics; required
errors reject and arbitrary Python errors propagate. South Node inherits North
Node motion and mirrors latitude, with an explicit derived marker.

Preflight planets and all requested known-time houses before a chart header.
Unknown-time natal/transit/progressions retain clearly labeled noon planetary
surrogates and omit houses and dependent conclusions. Dignity needs no houses.
Lots/Hellenistic, solar-return, legacy prediction and location lines
require a known birth time. Synastry evaluates each receiving chart independently;
one unknown time removes only its own houses/receiving overlay. Midpoint composite
remains symbolic; Davison is unavailable unless both real locations and times
exist, and its requested calculations also preflight before composite output.
UTC-only date charts explicitly label an omitted-clock noon surrogate.

Planetary-hour rise/set calls check Swiss event status and strictly ordered finite
sunrise/sunset/next-sunrise instants. Polar/unavailable events reject, never become
6am/6pm substitutes. This preserves the legacy UTC search window and day-ruler
convention; local-date/sunrise calendar semantics are still V13 work. Legacy event
searches and approximate obliquity/GMST helpers are outside this bridge and remain
explicit W09b3/location-migration limitations.

Reproduced baseline at J2000: latitude 80 Placidus returns fabricated 0,30,...330
cusps and zero angles; South Node speed is the opposite of its North Node;
missing five optional bodies have no diagnostic. Swiss programming documentation
confirms polar Placidus failure and returned-backend fallback behavior:
https://www.astro.com/swisseph/swephprg.htm (sections 3.3 and 13).

Local result: 283 tests pass; full wiring and diff/AST review complete.
Hosted acceptance and installed-wheel evidence will close this slice by exact SHA.

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
