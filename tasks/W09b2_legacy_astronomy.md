# W09b2: legacy house uncertainty and astronomy failures

Status: next ready slice; documented before code, 2026-10-06.
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
