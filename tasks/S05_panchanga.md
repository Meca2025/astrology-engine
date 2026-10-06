# S05: instant panchanga snapshot

Status: documented before code, 2026-10-06. Owner: Jyotisha calendrical elements.
Files: astroengine/panchanga.py, data/panchanga.json, tests/test_panchanga.py.

Compute instantaneous tithi/paksha, fixed/repeating karana, 27 nakshatras and nitya
yoga from same-profile Sun/Moon positions. Include local civil weekday labeled as
such; sunrise-based vara is unavailable in this slice. No festival calendar,
sunrise transition times, muhurta or rahu-kala claims. Sidereal profile required.

Gate: elongation wrap and 12°/6° boundaries; fixed-karana transitions and repeating
cycle; yoga sum wrap; civil timezone date; command and metadata coverage.

## Receipt

101 total local tests passed; fixed and cyclical karana boundaries, lunar month
wrap, yoga sum, local weekday and CLI tested. No sunrise calendar claimed.
