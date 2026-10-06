# S06: structured relationship analysis

Status: documented before code, 2026-10-06. Owner: relationships.
Files: astroengine/aspects.py, relationships.py, data/western.json,
tests/test_relationships.py, CLI/interfaces.

Separate explicit coordinates/zones/time certainty for both births. Same zodiac
frame required. Calculate all configured cross-aspects, bidirectional house
overlays only when receiving chart houses are known, and circular midpoint
composite. Antipodal midpoint is ambiguous, not arbitrarily resolved. Synastry
across different birth epochs has no physically meaningful applying/separating
motion status. Synergy is a transparent modern symbolic heuristic with each
contribution shown, never a measured compatibility probability.

Gate: timezone independence, wrap/antipode midpoint/swap symmetry, no invented
unknown-time overlays, exact aspect thresholds, deterministic score contributions,
profile mismatch rejection and two-person CLI wiring. Retain legacy synergy text.

## Receipt

108 total tests passed. Swap invariance exposed floating-order sensitivity in
midpoints; sorted normalized inputs now give deterministic symmetric results.
Zones, uncertainty, antipodes, contribution trace and CLI checked.
