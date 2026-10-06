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
to twenty charts (sixteen classical + D5/D6/D8/D11, V01), and returns named
method/source and optional divisional lagna. No physical varga longitude is
asserted; D30 uses unequal segments. The four extra vargas follow the
Jaimini/Tajika tradition per the JHora Traditional method (not Parasara's
scheme); D11 uses the new `scaled-relative` target mode.

## Daily forecast (Vistara F01)

`forecast.daily_forecast(natal_jd_ut, lat, lon, name, birth, target_iso)`
gathers computed facts for one day — Western transits (active, exact,
stations, ingresses), panchanga, Vimshottari dasha position, BaZi day
pillar with pillar relations, Tibetan day-element relation, runic
half-month, zodiac day ties — and renders a labeled symbolic reading.
`computed` and `reading` are separate keys; `afflictions` exposes
pressured planets, dasha lords and clashing pillars for F02.

## Remedial mantras (Vistara F02)

`mantras.mantras_for(planet)` / `mantras.all_mantras()` read
data/mantras.json (traditional public-domain Navagraha verses only).
`mantras.remedies_for(afflictions, active_transits)` recommends mantras
for dasha lords then pressured planets, each with a reason string.
Framed as devotional practice, never medical.

## Yoga engine (Gambhira G01)

`yogas.detect_yogas(request)` finds the great combinations from D1
(whole-sign houses from Lagna): Pancha Mahapurusha, Gaja Kesari,
Budha-Aditya, Dhana, Raja (basic kendra-trikona sambandha), Kemadruma,
Sakata. Definitions, sources and variants in data/yogas.json (rule
version 1.0); each detection carries rule, signification, source.
Sambandha = conjunction, mutual kendra, or exchange of signs.

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

## Zodiac, weekday, life-periods (R05)

`zodiac_rune(sign, variant="classical")` returns the App. 5 correspondences
(rune, deity, planet, day, stone, animal); Capricorn/Aquarius/Pisces carry
both "classical" and "modern alternative" rows, labeled. `weekday_rune(weekday)`
returns the App. 4 correspondences (deity, planet, rune, tree, herb,
element, esoteric number, magic square). `life_period(age_years)` names the
Ch. 6 planetary life-period ruling an age (Máni 0–4 … Loki 68–98), with
years elapsed and remaining; ages outside 0–98 raise CalculationError.
`metonic_cycle(year)` gives the calendrical Golden Number, (year mod 19)+1,
and the year's place in the 19-year Sun/Moon reconciliation cycle, with the
Aun 310-year recalibration noted. runic.py stays ephemeris-free by design;
the Metonic recurrence is cross-checked against the ephemeris in tests.

## Lunar mansions (R06)

`lunar_mansion(sidereal_longitude_deg)` maps a sidereal longitude onto the
28 Ch. 7 lunar mansions (rune, Old Norse name, star, designation, segment
bounds). `lunar_mansions()` lists all 28. Declared modern convention (not
historical fact): 28 equal sidereal segments of 360/28 degrees, mansion 1
(Feoh, "Boars' Throng") opening at Alcyone's J2000 sidereal longitude
36.1175° (Lahiri). runic.py stays ephemeris-free: the caller supplies the
Moon's sidereal longitude.

Contrast note vs. Vedic nakshatras: nakshatras are 27 in the classical
count (28 with Abhijit), anchored at 0° sidereal Aries (Ashwini), each
13°20' wide. Pennick's mansions are 28 equal segments of 12°51' anchored
at Alcyone — a different zero point and a different count convention.
Both are "lunar zodiacs" in their own traditions; the engine computes
each in its own terms and does not synthesize the two systems.

## Palaces and worlds (R07)

`grimnismal_palace(sign)`, `world_rune(world)`, and `nine_worlds()` are
fixed correspondence overlays (App. 7, Ch. 6) — sign → palace/meaning/deity
and world → rune. Results carry `"kind": "correspondence overlay"`: they
are looked up, not computed.

## Runic reading (R08)

`runic_reading(iso_datetime, longitude, timezone, age_years=None,
moon_sidereal_longitude=None)` composes one structured reading: a
`computation` section (raw layer results from the R02–R07 functions —
half-month, hour, planetary hour, sele, tide, station, weekday, life
period, mansion, name pair) and an `interpretation` section of
deterministic symbolic statements drawn ONLY from the book's tables
(Ch. 8 planetary qualities and rune adverbs, transcribed in
`data/runic.json` v1.2). Every statement carries kind=interpretive,
source Pennick (2023), historical_claim "modern synthesis". Anything the
tables do not cover is omitted, never invented. The computation
functions remain importable without the interpretive layer.

## `runic` CLI command (R09)

`python3 astrology_engine.py runic --datetime … --lon … --timezone …`
with layer flags (`--half-month --hour --tide --station --weekday
--mansion --life-period --name --reading`), `--full`, and `--json`.
Text output uses the legacy header/section style with a provenance
footer; JSON output carries computation + optional interpretation +
provenance. Registered in `data/capabilities.json`,
`data/tool_schemas.json`, `COMMANDS.md`, and the Hermes `SKILL.md`.

## Chart library (save/load)

`astroengine/charts.py`: `save_chart` / `load_chart` / `list_charts` /
`delete_chart` / `chart_exists`, rooted at `$ASTROENGINE_CHART_DIR` or
`~/.astroengine/charts`. `astrology_engine.py` adds `--save NAME` and
`--load NAME` (`--load1`/`--load2` for two-person commands) to every
chart-producing subcommand, plus `charts`, `chart-show NAME`,
`chart-delete NAME`; the modern JSON commands honor `--save` through
`run_command`. Saved files carry name, chart_type, saved_at,
engine_version, request and result.

## Aspect families

`ASPECTS` in `astrology_engine.py` now holds 22 aspects; `ASPECT_FAMILIES`
maps each to major/minor/quintile/septile/novile/harmonic, and
`calc_aspects(..., families=...)` filters (the pseudo-family "obscure"
selects the four non-classical families). `data/western.json` mirrors the
ten new aspects with neutral weight 0 so synergy scoring is unchanged.

## Divination quartet

- `astroengine/tarot.py` + `data/tarot.json`: 78-card RWS deck, ten
  spreads (`draw(spread, seed, reversals, question)`), seeded
  reproducibility. CLI: `tarot`.
- `astroengine/readings.py`: `reading(kind, positions, asc_sign,
  mc_sign)` — general/love/career interpretive narratives from chart
  data; every paragraph tagged interpretive. CLI: `reading` (with
  `--load`).
- `astroengine/numerology.py` + `data/numerology.json`: Pythagorean
  life_path/destiny/soul_urge/personality/birthday/personal_year;
  masters 11/22/33 held. CLI: `numerology`.
- `astroengine/iching.py` + `data/iching.json`: 64 hexagrams (King Wen
  order, original renderings); `cast(question, method, seed)` by coins
  or yarrow with changing lines + relating hexagram. CLI: `iching`.

- `astroengine/runecast.py` + `data/runes.json`: 24 Elder Futhark runes
  (original one-line meanings; nine symmetric runes have null
  merkstave); `cast(layout, seed, merkstave, blank, question)` across
  seven layouts (single, norns, elements, cross, hammer, nine-worlds,
  wheel); optional modern blank rune, off by default. CLI: `runecast`.

- `astroengine/wheel.py`: `wheel_svg(planets, cusps, aspects, meta)` —
  dependency-free SVG chart wheel (gold zodiac ring, house numbers,
  planet glyphs, aspect chords colored by kind, ASC rotated to 9
  o'clock). Pure data in, SVG out; never imports the legacy monolith.
  CLI: `wheel` (`--load` or birth data, `-o` output file).

- `astroengine/houses.py`: `house_cusps(jd_ut, lat, lon, system)` —
  twelve cusps + ASC/MC for placidus | whole-sign | equal | koch |
  regiomontanus; system codes from data/profiles.json; explicit
  CalculationError on unknown systems. Threaded through the monolith
  via `_optional_houses(..., system)` and the `--houses` flag.

- `astroengine/directions.py`: `solar_arc(natal_jd_ut, target_jd_ut,
  lat, lon, houses)` — arc = progressed-Sun motion (day-for-a-year),
  all natal longitudes + arc; directed ASC/MC when lat/lon given.
  `directed_aspects(directed, natal, orb)` — major aspects, tightest
  first, applying/separating, exact-hit flag. CLI: `solar-arc`.

- `astroengine/profections.py`: `profection(asc_longitude, birth_iso,
  target_iso, lord_longitude)` — annual profection (whole-sign houses
  assumed); `essential_dignity(planet, sign)` — traditional domicile /
  exaltation / detriment / fall / peregrine. CLI: `profection`.

- `astroengine/watch.py`: `upcoming_transits(natal_jd_ut, from_jd_ut,
  to_jd_ut, lat, lon, orb)` — outer-planet (Jupiter–Pluto)
  conjunctions/oppositions/squares/trines to natal planets + ASC/MC;
  daily scan with ternary-refined exact dates. CLI: `watch`.

- `astroengine/electional.py`: `score_moment(jd_ut, lat, lon)`,
  `moon_void_of_course(jd_ut)`, `planetary_hour(jd_ut, lat, lon)`,
  `find_windows(from_jd, to_jd, lat, lon, step_hours, timezone)` —
  traditional electional scoring and window search. CLI: `elect`.

- `astroengine/stars.py`: `load_stars()`, `star_longitude(name, jd_ut)`,
  `star_hits(natal_jd_ut, lat, lon, orb)` — 26 bright stars from
  `data/fixed_stars.json`, IAU 1976 precession to date. CLI: `stars`.

- `astroengine/asteroids.py`: `asteroid_positions(jd_ut)` —
  Chiron/Ceres/Pallas/Juno/Vesta via Swiss Ephemeris asteroid files;
  honest CalculationError when the .se1 files are absent. CLI:
  `asteroids`.
- `astroengine/midpoints.py`: `midpoint(a, b)`,
  `all_midpoints(positions)`, `midpoint_hits(natal_jd_ut, lat, lon,
  orb)` — 45 planetary midpoints and their activations. CLI:
  `midpoints`.

- `astroengine/draconic.py`: `draconic_longitude(tropical_lon,
  node_lon)`, `draconic_chart(natal_jd_ut, lat, lon)`,
  `draconic_contacts(natal_jd_ut, lat, lon, orb)` — the draconic
  zodiac reckoned from the true north node. CLI: `draconic`.

- `astroengine/dossier.py`: `natal_dossier(natal_jd_ut, lat, lon, name,
  birth_iso, target_iso, houses)`, `render_dossier(d)` — the nine-part
  written natal dossier assembled from all Horizons modules. CLI:
  `dossier`.

- `astroengine/runecast.py`: `cast(..., system="elder"|"younger"|"futhorc")`,
  `runes(include_blank, system)`, `systems()` — corpus files
  `data/runes.json`, `data/runes_younger.json`, `data/runes_futhorc.json`.
  CLI: `runecast --system`.

- `astroengine/ogham.py` + `data/ogham.json`: 25 ogham staves
  (20 feda + 5 forfeda, kennings per the Auraicept via McManus 1988,
  tree-lore caveat recorded); `cast(layout, seed, question, forfeda)`
  across five layouts (single, triad, aicme, wheel, grove); the aicme
  layout draws one stave per aicme. CLI: `ogham`.

- `astroengine/chinese.py` + `data/chinese_zodiac.json`: `zodiac(iso_date)`,
  `year_pillar(lunar_year)` — ganzhi by (lunar_year-4) mod 10/12,
  NaYin per the Sixty Jiazi verse, trine allies / secret friend /
  clash; Lunar New Year boundaries via lunardate (round-trip
  guarded). CLI: `chinese`.

- `astroengine/bazi.py`: `pillars(iso_date, time, timezone)` —
  year/month/day/hour ganzhi + NaYin + Day Master; Lichun year turn
  and jie month branches via Swiss Ephemeris; day ganzhi from JDN;
  Five Tigers / Five Rats stem rules. CLI: `bazi`.

- `astroengine/tibetan.py` + `data/tibetan.json`: `tibetan(iso_date)`,
  `year_name(lunar_year)`, `forces(lunar_year)` — element-animal year,
  rabjung position, mewa, parkha, five personal forces; Losar boundary
  approximated by CNY with uncertainty flag. CLI: `tibetan`.
