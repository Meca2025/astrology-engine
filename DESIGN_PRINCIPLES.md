# Design principles

1. Resolve civil time into a complete UTC datetime, preserving date rollover.
2. Reject invalid or unresolved inputs; never disguise errors as Aries houses.
3. Keep tropical/sidereal, house system, ayanamsa and node model explicit.
4. Keep rule content in versioned JSON; calculations return fresh snapshots.
5. Serialize access to Swiss Ephemeris mutable settings; expose actual backend flags.
6. Separate astronomy, tradition algorithms, reports, interpretation and integrations.
7. Missing birth time suppresses angles/houses rather than implying certainty.
8. Publish deterministic JSON with schema versions and structured errors.
9. Validate boundaries and externally grounded examples before capability promotion.
10. Preserve public CLI compatibility; add tested paths and document migration.
