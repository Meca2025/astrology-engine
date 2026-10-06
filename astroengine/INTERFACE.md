# Computation interface — S01 target contract

## Public entry points

`ChartRequest(date, time, latitude, longitude, timezone, zodiac, ayanamsa,
house_system, node_type, ephemeris_path)` is a frozen request. Civil time uses an
IANA timezone or UTC explicitly. No auto-geocoding occurs here.

`compute_chart(request)` returns a fresh JSON-safe chart snapshot: schema version,
request, UTC timestamp, Julian day, calculation profile, positions, optional houses
and angles, warnings, and ephemeris provenance. `capabilities()` returns fresh
read-only-rule-derived availability data. New CLI commands: `chart` and
`capabilities`, emitting JSON by default.

## Inputs and invariants

Finite latitude [-90,90], longitude [-180,180], ISO civil date/time, recognized
profile keys. Missing time uses flagged local noon and omits angles/houses.
Ambiguous/nonexistent DST times reject until the caller disambiguates with an
explicit fixed UTC instant. Invalid zones, failed houses and failed bodies reject.
Tropical is default for chart; sidereal explicitly selects a named ayanamsa.

## Side effects and boundaries

Swiss Ephemeris state changes occur under an adapter lock; optional ephemeris paths
are resolved dynamically. No data mutation, birth persistence, network or AI calls.
The adapter does not serialize unrelated external direct Swiss Ephemeris calls.
CLI catches known errors, logs structured diagnostics to stderr and returns 2.

## Jyotisha D1 (S02)

`vedic.compute_vedic(request)` requires sidereal inputs and returns navagraha
positions/nakshatras/rasi houses, optional lagna and underlying chart provenance.
`vedic.nakshatra(longitude)` returns 1-based index/pada, lord and fraction elapsed.
CLI `vedic` shares chart arguments with sidereal/Lahiri/whole-sign/mean defaults.
No interpretation, yoga, strength or marriage scoring is inferred.

## Divisional charts (S03)

`vargas.varga_position(longitude, division)` returns a classical mapped sign and
source subdivision/fraction, with unsupported divisions rejected.
`vargas.compute_vargas(request, divisions=None)` requires sidereal input, defaults
to sixteen charts, and returns named method/source and optional divisional lagna.
No physical varga longitude is asserted; D30 uses unequal segments.

## Vimshottari (S04)

`dashas.compute_dashas(request, years=None, year_model=None, as_of=None)` returns
D1, Moon-based maha/antar periods, birth balance, chosen continuous day clock and
optional active pair. `vimshottari_timeline(birth, moon_longitude, years, year_days)`
is pure period arithmetic with an aware birth datetime; `active_period` uses
half-open intervals. Antars originate at full maha start before birth, then clip.
As-of outside the report window returns null; no event interpretation is implied.
