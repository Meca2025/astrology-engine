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

## UT ephemeris and legacy astronomy bridge (W09b2)

EphemerisRequest(julian_day, zodiac, ayanamsa, ephemeris_path) is frozen; UT JD
must be finite. ephemeris.positions_at_jd(request, required, optional=None) takes
internal, named Swiss constant registries and returns positions, named unavailable
optional bodies and provenance. Required Swiss errors reject; optional Swiss errors
are recorded; unexpected programming errors propagate. Actual/requested flags live
on every available body. Registry identifiers are implementation data, not free
user-selected plugins. All settings changes/calculations hold the core owner lock.

houses_at_jd(request, latitude, longitude, system=b"P") returns twelve finite cusps
and ASC/MC or CalculationError. Profile house codes plus equal alias E are supported;
failed/polar systems never substitute. solar_day_events(request, latitude, longitude)
returns ordered sunrise/sunset/next-sunrise instants after a UT starting JD; nonzero
rise status, bad event times or Swiss errors reject. Its requested Swiss flag is
not an independently reported actual backend (rise_trans exposes no returned flags).
It preserves the legacy UT search convention, not a local calendrical-day API.

legacy_astronomy.legacy_positions provides dict-compatible text fields plus
unavailable/provenance attributes outside body iteration. legacy_houses preserves
the three-item tuple; legacy_request declares tropical or Fagan-Bradley sidereal.
legacy_astronomy.json owns the required/optional body registry and search settings.
The bridge never imports the monolith, prints, persists or performs network calls.

## Runic cycles (R02)

`runic.RunicDateRequest(date, time, timezone)` is a frozen request. `date` is
ISO YYYY-MM-DD (required); `time` ISO HH:MM (optional, refines boundary days);
`timezone` IANA/UTC (optional, only with `time`). Unknown zones, bad dates and
timezone-without-time raise `CalculationError`.

`runic.half_month_rune(iso_date, time, timezone)` returns a JSON-safe dict:
ruling rune, half-month start/end, days remaining, next rune, corpus
correspondences (data, not interpretation), source and historical_claim.
Boundary rule per Pennick App. 2: latest start on/before the date; pre-01-13
dates belong to Eoh; on a start date with a clock time, the new rune begins at
the book's local-apparent start time. No ephemeris, no interpretation.

## Runic hours (R03)

`runic.RunicHourRequest(iso_datetime, longitude, timezone)` is a frozen
request. `runic_hour(local_apparent_time)` names the rune ruling a solar
hour on the Ch. 4 wheel (Feoh 12:30-13:30 … Dag 11:30-12:30).
`to_local_apparent_time(iso_datetime, longitude, timezone)` converts civil
clock time to the book's "real time" (sundial time; midday = sun due south)
via declared method `longitude+eot-approx` (longitude correction plus
low-precision equation of time; accurate to a few minutes).
`planetary_hour(weekday, clock_hour)` names the Northern Tradition planetary
hour deity from the App. 3 grid (hour-to-hour divisions on CLOCK time).
`sele(iso_datetime, longitude, timezone)` reports whether the runic
hour-rune's deity correspondence contains the planetary hour's deity —
Pennick's "especially powerful" coincidence. No interpretation.

## Tides, stations, runic names (R04)

`tide(clock_time)` names the tide ruling a civil HH:MM clock time from the
App. 6 table (Morntide 04:30-07:30 … Midnight 22:30-01:30, wrapping
midnight … Uht 01:30-04:30), with English/Old English/Old Norse names.
`year_station(iso_date)` names the Station of the Mystic Year (Ch. 5):
station number, rune(s), festival, day-hour, symbolic event. Boundary
method is a DECLARED engine convention (`festival-span`): each station spans
[festival_date, next festival_date) in cycle order; festival anchors are
Yule Dec 21, Spring Equinox Mar 20, Beltane May 1, Midsummer Jun 21,
Lammas Aug 1, Autumn Equinox Sep 22, Samhain Oct 31. The book gives the
First station no festival; it is conventionally anchored at Aug 13 (start of
the As half-month, first of its "As/Rad" runes). `runic_name(iso_datetime,
longitude, timezone)` composes the birth/name-taking pair: half-month rune
+ local-apparent hour-rune (e.g. Ingrid's Ing-Rad). The book's rendered
names (Kenneth, Ingrid, Darwin) are literary English wordplay on such
pairs, not mechanical output; the Kenneth/Odal wheel conflict (R01) and the
Darwin EoT shift (civil 20:27 Wyn hour vs LAT 20:43 Hagal) are documented
in tests, not silently corrected. No interpretation.
