# ADR 0001: additive computation package and explicit profiles

Status: accepted under the expansion instruction, 2026-10-06.

The monolithic text engine mixes rule content, I/O, astronomy and interpretation.
Add `astroengine` with strict request validation, a serialized ephemeris adapter,
versioned JSON and data-defined methods. Register additive CLI commands through an
internal adapter. Preserve existing APIs and text commands during migration.

Sidereal flags apply to positions and houses using the same explicit ayanamsa.
Unknown-time charts have positions at a flagged surrogate but no houses/angles.
Failed computations produce typed errors; fallback backends are disclosed by the
actual Swiss Ephemeris return flags. No reinterpretation of missing astronomy.

Consequences: two paths temporarily coexist, with known legacy limitations recorded.
New capabilities use the safe path; legacy migration follows regression evidence.
Global Swiss Ephemeris state is serialized within the new package. Concurrent
external direct calls to the library are outside this adapter's guarantee.
