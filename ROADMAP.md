# Expansion roadmap — active plan

Updated 2026-10-06. This plan supersedes the historical backlog retained below.
"All astrology" is an extensible program: schools disagree, traditions evolve,
and some methods lack adequate sources. Coverage is tracked method by method.
Availability means working computation + CLI/API + tests + documented limits;
independent validation is a separate evidence level.

## Starting point and delivery loop

16 Western text commands already exist, including basic synergy and location
lines. Expand their correctness, structure and depth while adding Jyotisha and
other traditions. Each slice: document/push work order -> implement -> verify ->
update capability/interface/TODO/devlog -> commit/push -> confirm remote HEAD ->
advance to the next ready slice. Never promote a failed or merely planned method.

## First implementation wave

| Slice | Deliverable | Depends on | Acceptance gate |
| --- | --- | --- | --- |
| S01 | Typed chart request, complete UTC conversion, tropical/sidereal profiles, JSON, backend provenance, discovery, packaging and OS CI | baseline | Date rollover/DST/invalid-input tests; direct Swiss comparisons; JSON subprocess contract |
| S02 | Jyotisha D1: Lahiri/Raman/Krishnamurti/Fagan options, mean/true Rahu-Ketu, whole-sign/rasi houses, nakshatra/pada | S01 | Same frame for houses/planets; 27/108 segment boundaries; nodes exactly opposite, same motion |
| S03 | Classical vargas D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60 | S02 | Named Parashari mapping variants; odd/even/modality boundaries; no false harmonic substitution |
| S04 | Vimshottari 120-year maha/antar timeline, balance at birth, chosen year length and as-of lookup | S02 | Full cycle/order/sum/half-open intervals, independent timeline examples |
| S05 | Instant panchanga: tithi, paksha, karana, nakshatra, nitya yoga, civil weekday | S02 | Wrap/boundary examples; explicitly separate instant from sunrise calendar |
| S06 | JSON relationship workbench: locations/zones per person, cross-aspects, house overlays, midpoint composite and explainable synergy | S01 | Independent zones; no unknown-time overlays; circular/swap symmetry and score evidence |
| S07 | Relocation chart, exact query-latitude MC/IC/ASC/DSC lines, angular residuals, circumpolar status | S01 | Original UTC fixed; spherical geometry and horizon fixtures; antimeridian handling |
| S08 | Advanced Western starter: whole-sign annual profections, harmonics and sensitive midpoints | S01 | Birthday/age boundaries, rulership provenance, exact oppositions and orb fixtures |

## Comprehensive Jyotisha program

| Slice | Scope and school choices | Gate/dependencies |
| --- | --- | --- |
| V09 | D1-D60 extended variants, bhava/chalit (Sripati/equal), karakas (7/8), planetary/sign drishti, avasthas, combustion, planetary war | S02-S03; source variants and independent fixtures for each rule |
| V10 | Shadbala six components, ishta/kashta, bhava bala, vimsopaka, ashtakavarga/bhinna/sarva, shodhana | V09; each component benchmarked and summed with units |
| V11 | Yoga catalog: raja/dhana/pancha mahapurusha/nabhasa/viparita, cancellation and strength conditions; named dosha rules | V09-V10; declarative conditions, counterexamples and severity trace |
| V12 | Dasha framework: Vimshottari nested levels, Yogini/Ashtottari/Kalachakra, Chara and Narayana variants, conditional eligibility | S04/V09; school-specific clocks, independent reference timelines |
| V13 | Sunrise-based local panchanga, transition roots, sunrise/sunset, vara, rahu/gulika/yamaganda, hora, muhurta, festivals | S05 + robust event solver; location/day-length/DST/polar/lunisolar calendar gates |
| V14 | Gochara with natal Moon/lagna reference, vedha, sade sati, transit/dasha overlays; prashna, Tajika/varshaphala, KP cusp/sub-lord methods | V09-V13; declare traditions separately and test exact partitions |
| V15 | Ashtakoota 8 components/36 points, regional exceptions, mangala matching, multi-factor relationship explanations | S06/V09; validated table provenance; no deterministic marriage verdict |
| V16 | Jaimini arudhas/upapada/argala/chara karakas/drishti and optional Nadi research adapters | V09/V12; distinct rule profiles; no claimed lost/secret tradition coverage |

## Advanced Western, location and relationship program

| Slice | Scope | Acceptance gate |
| --- | --- | --- |
| W09 | Time/geo correctness migration for all 16 legacy commands; precision-aware event root finder, stations/VOC/eclipses/general planetary returns | S01; legacy regression plus motion/wrap/multiple-root fixtures |
| W10 | Sect correction, Dorothean/Ptolemaic triplicity, bounds/faces, reception, bonification/maltreatment, fixed stars, asteroids | Source profiles and actual ephemeris files; verified dignity/day/night examples |
| W11 | Firdaria, zodiacal releasing, decennials, primary directions, solar arcs, converse/tertiary progressions, progressed angles, return locations | S08/W09/W10; clock/direction conventions and independent references |
| W12 | Horary/electional rule engines, mundane/ingress charts, historical calendars, astronomical/lunation charts | W09-W11; explicit classical vs modern rule choices, calendars and limits |
| L09 | Map-ready GeoJSON/SVG, globe/2D rendering, geographic distances to curved lines, local-space azimuth, zenith/nadir, parans, relocated returns | S07/W09; geodesic distance, projection and polar/antimeridian fixtures |
| R09 | Davison with spherical geographic midpoint, progressed composite, relationship transits, declination parallels, multi-person/team analysis | S06/W09; midpoint ambiguity, time uncertainty and scoring normalization |
| W13 | Harmonic/dial (90/45), Uranian/midpoint trees, draconic charts, evolutionary/psychological overlays | S08/W10; school-tagged computational definitions and test datasets |

## Other traditions and research adapters

| Program | Required scope | Readiness gate |
| --- | --- | --- |
| Chinese | BaZi four pillars, solar terms/Li Chun boundaries, true solar time options, luck pillars; Zi Wei Dou Shu | Authoritative calendar algorithms, sexagenary fixtures, regional/time conventions |
| Tibetan | Element/animal/mewa/parkha calendars and named lineages | Source review, rights, calendar correlations and independent practitioner examples |
| Hellenistic/Arabic/Persian | expanded lots, distributions, planetary periods, historical house/rulership profiles | Critical source conventions, calendar/time scales and expected charts |
| Sidereal schools | Fagan/Bradley, true-star/constellation profiles and distinct zodiac definitions | Ayanamsa provenance; unequal constellations never mislabeled 12 equal signs |
| Mayan and other calendars | Tzolkin/Haab correlation choices and named cultural interpretations | Calendar correlation and contemporary community/source review; no generic "ancient" claims |
| Cultural/modern overlays | modern Norse/rune, decan images, lunar mansions and symbolic correspondences | Explicit modern vs historical labeling, optional overlays, source ownership |

These adapters use their own calendars and rule domains. Chinese/Tibetan methods
are not implemented by applying a sidereal offset to a Western chart. Medical,
financial and political symbolism remains interpretive material, not a validated
predictor or advice engine. Rectification is hypothesis exploration with explicit
uncertainty, never recovery of a supposedly proven birth time.

## Agent, product and infrastructure expansion

- A01: checked-in Hermes skill, capability/JSON schemas, request clarification,
  profile comparison and cited explanations; Python tool adapter now, MCP/OpenAPI later.
- A02: bounded batch jobs, cancellation/progress, event caching keyed by all settings,
  deterministic replay manifests and export/import profiles without automatic storage.
- A03: report/chart wheels, accessible labels, SVG/PDF/Markdown and interactive maps;
  separate computation from narrative and preserve calculation provenance on export.
- A04: optional local-model interpretation, retrieval with source/version trace,
  tool selection evaluation, cross-tradition comparisons and anti-fabrication tests.
- I01: dependency/license inventory, ephemeris data provisioning/checksums, frozen
  environment, CI platform matrix and resource measurements on Raspberry Pi.
- I02: offline gazetteer, ambiguity resolution and historical timezone confidence.
- I03: desktop/mobile/browser adapters and native packaging, each with build/runtime
  checks; do not imply pyswisseph runs natively on every target without a port.
- I04: independent reference corpus, property/fuzz tests, multilingual Sanskrit
  transliteration, source registry, documented tolerance and release evidence.

## Release criteria and uncertainty

Every result records conventions, input certainty, backend/version and warnings.
Tests distinguish formula fixtures, direct library checks, third-party/published
reference evidence and physical-device evidence. A 16-varga implementation does
not mean all Jyotisha is complete; panchanga snapshots do not mean festival timing
is complete. Technique profiles with unmet sources/fixtures stay planned.

## Historical roadmap (preserved)

The following backlog describes the pre-expansion engine. Its accepted limitations
are superseded by the active correctness gates above where they conflict.

# Roadmap — Astrology Engine

> Planned improvements, known gaps, and integration goals. Ordered roughly by value/effort ratio.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| `[done]` | Completed |
| `[next]` | High priority, low effort — pick up first |
| `[soon]` | Worth doing, moderate effort |
| `[later]` | Good idea, higher effort or lower urgency |
| `[wontfix]` | Acknowledged limitation, not worth fixing |

---

## Core Engine

### Calculation Quality

- `[next]` **Exact exaltation degree marker in `dignity` output** — `EXALT_DEG` is defined and the flag is computed; just needs a `★` glyph in `print_dignity_table()` when `exact_exalt=True`.

- `[next]` **Moon in `predict` mode** — default step size (1.0 day) misses Moon transits. Add auto-detection: if "Moon" is in `--transit-planets`, set `step=0.1` automatically.

- `[soon]` **Naibod arc progressions** — optional `--method naibod` flag for `progressions` subcommand. Current mean-tropical-year approximation (365.25) is close but not what specialist software uses. Naibod arc = 0.985647°/year.

- `[soon]` **Robust VOC Moon** — current detection checks aspects within the current sign but doesn't exhaustively scan all remaining degrees. Rewrite as: find next ingress JD, then scan for all aspect crossings between now and ingress JD. Return `True` if zero found. Accurate to minute.

- `[soon]` **Solar arc directions** — separate from progressions. Solar arc direction moves all planets at the Sun's progressed speed. Useful for event timing alongside secondaries.

- `[later]` **Primary directions** — classical Ptolemaic directions. Significant compute; requires `swe.time_equ()` for accurate poles. Highest value for traditional/Hellenistic clients.

- `[later]` **Tertiary progressions** — 1 day = 1 lunar month. Less commonly used but completing the progression suite.

- `[later]` **Firdaria periods** — Hellenistic time-lord technique. Day chart: Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars. Each planet rules a set number of years. Low effort to add as a `cmd_firdaria` subcommand.

- `[wontfix]` **Solar return convergence edge case near year boundary** — 50-iteration convergence can be slightly slow within 2 days of year boundary. Not meaningfully imprecise for practical use; fixing requires root-finding redesign.

---

## Geocoding & Timezone

- `[next]` **Nominatim caching** — currently every new city requires a live Nominatim call. A simple `dict`-based in-process cache (city string → lat/lon) would make repeated calls instantaneous and reduce OSM load. Optional SQLite persistence to survive restarts.

- `[next]` **Expand hardcoded fallback** — add: Anchorage, Honolulu, São Paulo, Buenos Aires, Cairo, Lagos, Nairobi, Mumbai, Beijing, Shanghai, Seoul, Mexico City, Bogotá, Lima. These cover the most common geocoding misses when offline.

- `[soon]` **Historical timezone data** — `pytz` handles most cases correctly via Olson database, but some pre-1970 timezone data is incomplete for certain regions. Document known edge cases (e.g. China used UTC+8 uniformly only after 1949; India uses UTC+5:30 year-round with no DST).

- `[later]` **Offline-first geocoding** — bundle a small SQLite of 10,000 major world cities (lat/lon/tz) so the engine works fully offline without kerykeion. File size ~2–3 MB. Would replace Tiers 2+3 in the cascade.

---

## New Subcommands / Modes

- `[next]` **`firdaria` subcommand** — time-lord periods. Requires only the sect light detection already implemented. Add `FIRDARIA_SEQUENCE_DAY` and `FIRDARIA_SEQUENCE_NIGHT` dicts with year counts, then compute current period from years elapsed since birth.

- `[next]` **`midpoints` subcommand** — `calc_midpoints()` already exists. Just needs a `cmd_midpoints` handler and subparser. Shows all planet midpoints, their signs/degrees, and which natal planets are within 1° of a midpoint (sensitive midpoints).

- `[soon]` **`eclipse-map` subcommand** — given an eclipse date, show which natal planets fall within 3° of the eclipse degree. Flag as activating if transit or progression also hits within 6 months. Uses existing `find_eclipses()`.

- `[soon]` **`return-chart` subcommand** — generalise `solar-return` to any planet return (lunar return, Mars return, Jupiter return). Lunar returns happen monthly and are excellent for monthly forecasting. Core logic is the same as solar return: iterate to find the moment a planet's longitude matches its natal degree.

- `[later]` **`bonification` subcommand** — show which planets are bonified (benefic trine/sextile from Venus or Jupiter) or afflicted (malefic conjunction/square/opposition from Mars or Saturn). Classic Hellenistic assessment beyond just dignity.

- `[later]` **`profections` subcommand** — annual profections time-lord system. Year 1 = House 1 is activated; year 13 = House 1 again. Each house = 30° = 1 sign progression per year from ASC. The activated house's ruling planet becomes the Lord of the Year. Requires only birth year and ASC sign.

- `[later]` **`sect-chart` subcommand** — full sect analysis showing which planets are in-sect (aligned with chart type) vs out-of-sect, with traditional bonification scoring. Extends current `hellenistic` sect detection.

---

## Output & Formatting

- `[next]` **Color output flag** — `--color` / `--no-color` toggle using ANSI codes. Benefics (Venus, Jupiter) in green; malefics (Mars, Saturn) in red; luminaries in yellow; angular planets in bold. Terminal-only; pipe detection should auto-disable.

- `[next]` **JSON output flag** — `--json` outputs the full data structure as JSON instead of formatted text. Enables Hermes to parse positions programmatically for WYRD Protocol feeds without screen-scraping.

- `[soon]` **SVG/ASCII chart wheel** — simple circular chart wheel output for `natal` mode. Full ASCII art in terminal; optional SVG file output via `--svg path/to/output.svg`. Chart wheels are high value for visual presentations but moderate build effort.

- `[later]` **Markdown report output** — `--markdown` flag outputs a clean Markdown document suitable for saving to Obsidian, Hugo, or any notes system. Each section becomes a Markdown heading.

---

## WYRD Protocol Integration

- `[next]` **Natal data as JSON for Ørlög** — `natal --json` output should map directly to WYRD Protocol PAD dimensions. Sun longitude → Arousal axis weight; Moon longitude → Valence axis weight; ASC → Dominance axis. Document the mapping in this repo.

- `[soon]` **Transit trigger events** — `predict` output as JSON with a `triggers` array that the Ørlög ChronoEngine can consume. Format: `[{"date": "2026-06-15", "type": "transit", "planet": "Saturn", "aspect": "Square", "natal": "Sun", "quality": "tension"}]`.

- `[soon]` **Sigrid astrological profile** — generate a character astrological profile (natal chart + Lot of Fortune + Lot of Spirit + sect light) in JSON format for Sigrid's persistent context. Sigrid can use this to modulate her responses during specific transits.

- `[later]` **RuneForge integration** — map the current `SIGN_RUNES` and `NORSE_CORRESPONDENCES` dicts to RuneForgeAI's rune grammar. A birth chart becomes a starting rune configuration; transits modify active rune weights.

---

## Infrastructure

- `[next]` **SKILL.md version bump** — update version from 3.0.0 to match engine after each release.

- `[soon]` **Basic smoke test script** — `test_smoke.sh` that runs 4–5 quick subcommands and greps for known-good values. Catches regressions without a full test framework.

- `[later]` **Type annotations** — add `-> ReturnType` annotations to `resolve_birth`, `calc_planet_positions`, `calc_houses`, `calc_aspects` for IDE support. Pyright flags are currently suppressed; proper annotations would clean them up properly.

- `[later]` **Ephemeris data files** — optionally install Swiss Ephemeris data files (`.se1` files) for extended date range and higher precision. Default `pyswisseph` built-in covers 1800–2400 CE adequately. Files extend to 5400 BCE / 9999 CE and improve accuracy outside the default range.

---

## Known Limitations (Accepted)

These are documented limitations that are not planned to be fixed because the impact is low or the fix isn't worth the complexity:

- **Pyright "possibly unbound" warnings on `swe` and `AstrologicalSubject`** — false positives from conditional imports guarded by `SWE`/`KK` runtime checks. Not real errors. Suppressing with `# type: ignore` would clutter every call site.
- **Sidereal zodiac not exposed via CLI** — `tropical=False` exists internally but no `--sidereal` flag. Vedic astrology requires Lahiri ayanamsa selection and different dignity tables; a full sidereal mode is its own sub-project.
- **Composite Davison uses average location** — the Davison relationship chart averages birth coordinates, which is a simplification. The full Davison calculation uses the average Julian Day only; location is technically irrelevant to the chart. This is a common software convention.
- **Secondary progressions use 365.25 day year** — off by ~0.06 days per century from the tropical year (365.2422 days). Negligible for most practical use.

---

*The Norns weave forward. So do we.*

## 2026-10-06 delivery state

S01-S08 and the local-contract portion of A01 are implemented and pushed with
verification records. MCP/HTTP hosting and external agent installation remain
future integration gates. W09 is divided into W09a (legacy time/coordinate truth)
and W09b (strict inputs/provenance and event solvers). TODO names the next task.

W09a is implemented with 150 passing local tests: UTC rollover, local-noon
conversion, explicit coordinate certainty and zero-coordinate synastry overlays.
W09b now proceeds through W09b1 strict legacy inputs, W09b2 house/backend contracts
and W09b3 event roots. Continuous Codex Goal continuation replaces the earlier
hourly heartbeat at the user's request; each verified slice leads immediately
to the next ready work order when the thread becomes idle.

W09b1 is verified: strict shared civil/location validation, explicit single and
per-person zone controls, synergy location inputs, secondary dates/windows and
zero-coordinate query admission. 223 tests pass locally and in the six-platform
matrix. Legacy house uncertainty/backend failures remain W09b2; robust event
roots remain W09b3. Neither parent W09 nor the full expansion is complete.
