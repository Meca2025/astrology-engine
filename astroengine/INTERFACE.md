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

## Panchanga snapshot (S05)

`panchanga.panchanga_elements(sun, moon)` takes same-frame sidereal degrees and
returns instantaneous tithi/paksha, karana, nakshatra and nitya yoga partitions.
`compute_panchanga(request)` supplies D1/provenance and local civil weekday.
Sunrise-based vara is null; no transition/festival/muhurta calculation is claimed.

## Relationships (S06)

`relationships.compute_relationship(first, second)` takes independent typed
requests with a shared zodiac/ayanamsa/node frame. Returns both charts, static
cross-aspects, bidirectional overlays, midpoint positions and score contributions.
Receiving houses unknown -> corresponding overlay null; source positions remain
flagged noon surrogates when time is missing. Composite houses are null. Antipodal
midpoints are null with ambiguity metadata. `relationships.synergy(aspects)` uses
versioned modern symbolic weights. It is not a compatibility probability.
`aspects` owns signed arcs, symmetric midpoint, cusp assignment and cross-aspects.

## Location astrology (S07)

`locations.compute_location(request, latitude, longitude)` requires a known birth
time and returns natal/relocated charts at identical UTC, plus geocentric
equatorial angular lines at the exact destination latitude.
`angular_lines(ra, declination, sidereal_degrees, latitude)` solves the zero-altitude
geometric horizon and meridians. Circumpolar/grazing/polar states are explicit.
Residuals are signed longitude differences at that latitude, not km or shortest
distances to curves. Equatorial coordinates never use sidereal zodiac offsets.

## Western starter tools (S08)

`western.compute_western(request, as_of, harmonic=None, midpoint_orb=None)`
returns civil-calendar whole-sign annual profection (null without birth time),
mathematical harmonic positions and sensitive third-body midpoint hits.
`annual_profection`, `harmonic_positions` and `sensitive_midpoints` are pure domain
functions. February 29 birthdays use February 28 in non-leap years. Profection
clock is calendar birthday, not an exact solar-return instant. Midpoints preserve
antipodal ambiguities; harmonics invent neither physical instants nor houses.

## Agent routing (A01)

`agent.tool_catalog()` returns fresh versioned JSON schemas for eight available
computation tools. `agent.run_tool(name, parameters)` validates the declared schema,
rejects unknown fields/tools/non-finite values, applies declared Jyotisha defaults
and dispatches directly to internal APIs. No subprocess, cloud or storage.
`capabilities()` also includes tool schemas. CLI `tools` returns the catalog.
`partitions.uniform_partition` owns half-open boundary/fraction arithmetic, using
explicit boundaries to preserve exact nominal and neighboring-float behavior.

## Strict civil and legacy compatibility inputs (W09b1)

`inputs.parse_civil(date_string, time_string=None)` returns a validated naive civil
datetime. YYYY-MM-DD and HH:MM[:SS[.ffffff]] are required; only omitted time selects
local noon. `resolve_utc` rejects DST ambiguity/gaps, invalid zones and UTC calendar
overflow. Coordinate checks include enormous integers without overflow leaks.
`legacy_inputs.coordinate_pair` converts legacy numeric flags, requiring a complete
finite pair; absent pairs return None. `local_hour_to_utc` preserves signed hours
relative to civil midnight; `birth_tuple` converts ChartRequest to the ten-item
legacy compatibility tuple with actual UTC date/clock, offset and uncertainty.
`date_window` validates ordered prediction dates and a clamped civil-year default
end; `return_year` validates integer solar-return years. Offset/clock formatting
retains historical seconds. None of these adapters imports the legacy monolith,
geocodes, stores birth data or fabricates houses.
