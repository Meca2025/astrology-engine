# CLI Reference — Astrology Engine

Complete flag reference for all 16 subcommands.

```
python3 astrology_engine.py <subcommand> [options]
```

---

## Global Notes

- `--date` always expects `YYYY-MM-DD` format
- `--time` expects `HH:MM[:SS[.ffffff]]`; if omitted, flagged noon positions have no houses/ASC/MC. Lots, Hellenistic, solar-return, legacy prediction and geoastrology require known time
- `--city` / `--nation` feed the geocoding pipeline (Nominatim → kerykeion → hardcoded fallback)
- `--lat` / `--lon` always override geocoding when both are provided
- `--nation` should be an ISO 2-letter country code (`US`, `GB`, `DE`, `NO`, etc.)
- Birth-aware local times use an explicit `--timezone` or optional timezonefinder discovery, then strict ZoneInfo UTC conversion; unresolved zones and DST folds/gaps reject

W09a preserves the UTC date when conversion crosses midnight. For example, local
2000-01-01 00:15 in Asia/Kolkata computes 1999-12-31 18:45 UTC and displays that
UTC date. With time omitted, noon means local noon in the resolved zone; birth
time remains unknown and houses/angles/sect/lots are unavailable. Explicit
coordinates, including zero, bypass geocoding and count as resolved. Legacy
timezone discovery still requires the geo extra. W09b1 provides explicit timezone
overrides and rejects unresolved/ambiguous/nonexistent inputs in both text and
typed commands. W09b2 makes house/required-body failures explicit and reports
actual backends/optional missing bodies. Event roots remain W09b3 work.

---

## `natal`

Full natal chart.

```
python3 astrology_engine.py natal
    --date   YYYY-MM-DD        birth date (required)
    --time   HH:MM             birth time local (optional; default noon)
    --city   CITY              birth city (optional)
    --nation CC                ISO country code (optional)
    --name   NAME              name to display in output (optional)
    --lat    DECIMAL           latitude override (optional)
    --lon    DECIMAL           longitude override (optional)
```

**Output sections:** timezone label, ASC/MC, Sun/Moon/Rising summary, chart type (day/night), planetary positions table, aspects, essential dignities, Arabic Lots, antiscia, Hellenistic analysis, Norse/Rune overlay, house overview.

**Example:**
```bash
python3 astrology_engine.py natal \
  --date 1975-11-22 --time 14:30 \
  --city Indianapolis --nation US --name Volmarr
```

---

## `transit`

Transiting planets vs a natal chart.

```
python3 astrology_engine.py transit
    --date          YYYY-MM-DD   natal birth date (required)
    --time          HH:MM        natal birth time local (optional)
    --city          CITY         natal birth city (optional)
    --nation        CC           natal birth nation (optional)
    --transit-date  YYYY-MM-DD   sky date to compare (default: now)
    --transit-time  HH:MM        sky time (default: noon if transit-date given)
    --lat           DECIMAL      lat override (optional)
    --lon           DECIMAL      lon override (optional)
```

**Example — current transits:**
```bash
python3 astrology_engine.py transit \
  --date 1975-11-22 --time 14:30 \
  --city Indianapolis --nation US
```

**Example — forecast to specific date:**
```bash
python3 astrology_engine.py transit \
  --date 1975-11-22 --time 14:30 \
  --city Indianapolis --nation US \
  --transit-date 2027-06-21 --transit-time 12:00
```

---

## `synastry`

Two-chart cross-aspect analysis with optional house overlays.

```
python3 astrology_engine.py synastry
    --date1    YYYY-MM-DD   Person A birth date (required)
    --date2    YYYY-MM-DD   Person B birth date (required)
    --time1    HH:MM        Person A birth time (optional)
    --time2    HH:MM        Person B birth time (optional)
    --name1    NAME         Person A display name (default: "Person A")
    --name2    NAME         Person B display name (default: "Person B")
    --city1    CITY         Person A birth city (optional; enables house overlays)
    --city2    CITY         Person B birth city (optional; enables house overlays)
    --nation1  CC           Person A birth nation (optional)
    --nation2  CC           Person B birth nation (optional)
    --lat1     DECIMAL      Person A lat override (optional)
    --lon1     DECIMAL      Person A lon override (optional)
    --lat2     DECIMAL      Person B lat override (optional)
    --lon2     DECIMAL      Person B lon override (optional)
```

House overlays are independent: each receiving chart needs its own known time
and explicit city/location pair. One unknown birth time disables only that
receiving overlay; its source positions remain flagged noon surrogates.

**Example:**
```bash
python3 astrology_engine.py synastry \
  --date1 1975-11-22 --time1 14:30 --name1 Volmarr \
  --city1 Indianapolis --nation1 US \
  --date2 1985-06-14 --time2 09:00 --name2 Seeker \
  --city2 London --nation2 GB
```

---

## `composite`

Composite chart (midpoint method) with optional Davison relationship chart.

```
python3 astrology_engine.py composite
    --date1    YYYY-MM-DD   Person A birth date (required)
    --date2    YYYY-MM-DD   Person B birth date (required)
    --time1    HH:MM        Person A birth time (optional)
    --time2    HH:MM        Person B birth time (optional)
    --name1    NAME         (optional; default "Person A")
    --name2    NAME         (optional; default "Person B")
    --city1    CITY         Person A city (optional; enables Davison chart)
    --city2    CITY         Person B city (optional; enables Davison chart)
    --nation1  CC           (optional)
    --nation2  CC           (optional)
    --lat1 / --lon1 / --lat2 / --lon2   coordinate overrides (optional)
```

Davison requires both real city/location inputs and known times. Otherwise only
the symbolic midpoint composite is shown. Geographic averaging remains legacy
arithmetic pending the spherical midpoint/antipodal gate in R09.

---

## `synergy`

Full relationship analysis: score + aspects + composite.

```
python3 astrology_engine.py synergy
    --date1    YYYY-MM-DD   Person A birth date (required)
    --date2    YYYY-MM-DD   Person B birth date (required)
    --time1    HH:MM        (optional)
    --time2    HH:MM        (optional)
    --name1    NAME         (optional; default "Person A")
    --name2    NAME         (optional; default "Person B")
```

Outputs: harmony/challenge synergy score bar (%), weighted cross-aspect breakdown, composite chart positions with dignities, cross-midpoints table.

**Example:**
```bash
python3 astrology_engine.py synergy \
  --date1 1975-11-22 --time1 14:30 --name1 Volmarr \
  --date2 1985-06-14 --time2 09:00 --name2 Seeker
```

---

## `solar-return`

Solar return chart: exact moment Sun returns to natal degree.

```
python3 astrology_engine.py solar-return
    --date    YYYY-MM-DD   birth date (required)
    --time    HH:MM        birth time local (required for accurate results)
    --city    CITY         birth city (optional)
    --nation  CC           (optional)
    --year    YYYY         target year (default: current calendar year)
    --lat     DECIMAL      (optional)
    --lon     DECIMAL      (optional)
```

The engine iterates to convergence to find the exact solar return moment accurate to arc-seconds.

**Example:**
```bash
python3 astrology_engine.py solar-return \
  --date 1975-11-22 --time 14:30 \
  --city Indianapolis --nation US \
  --year 2026
```

---

## `progressions`

Secondary progressions (1 day after birth = 1 progressed year).

```
python3 astrology_engine.py progressions
    --date       YYYY-MM-DD   birth date (required)
    --time       HH:MM        birth time local (optional)
    --city       CITY         birth city (optional)
    --nation     CC           (optional)
    --prog-date  YYYY-MM-DD   target date for progressed chart (default: today)
    --lat        DECIMAL      (optional)
    --lon        DECIMAL      (optional)
```

Shows all progressed positions plus tight-orb (≤2°) aspects between progressed and natal planets.

---

## `lunar`

Current lunar intelligence. No arguments required.

```
python3 astrology_engine.py lunar
```

Outputs: Moon's current sign and degree, phase name (New/Waxing/Full/Waning), illumination %, void-of-course status (with time until next ingress), next New Moon date, next Full Moon date, Moon aspects to current transiting planets, Norse overlay (Máni's phase).

---

## `planet-hours`

Chaldean planetary hours for a date and location.

```
python3 astrology_engine.py planet-hours
    --date    YYYY-MM-DD   date to calculate (default: today)
    --city    CITY         location city (optional)
    --nation  CC           (optional)
    --lat     DECIMAL      latitude decimal (optional)
    --lon     DECIMAL      longitude decimal (optional)
```

If no location is given, defaults to Indianapolis (39.7684°N, 86.1581°W). Each hour shows: start time, end time, planet ruler, Norse deity, and quality keywords.

**Example:**
```bash
python3 astrology_engine.py planet-hours \
  --city Oslo --nation NO
```

---

## `runic`

The runic star-program: Nigel Pennick's *Runes and Astrology* (2023) as
computable layers — a modern synthesis, with computation and
interpretation labeled separately.

```
python3 astrology_engine.py runic
    --datetime   ISO        moment, e.g. 2026-05-16T16:45 (required)
    --lon        DECIMAL    longitude degrees east (required)
    --timezone   IANA       e.g. UTC, America/New_York (required)
    --age        DECIMAL    age in years (enables --life-period)
    --moon-lon   DECIMAL    Moon's sidereal longitude (enables --mansion)
    --half-month --hour --tide --station --weekday --mansion
    --life-period --name    layer flags (no flags implies --full)
    --reading              include the Ch. 8 interpretive statements
    --full                 all layers
    --json                 JSON output instead of text
```

Layers: half-month rune, runic hour + Northern planetary hour + sele,
eight tides, eightfold-year stations, runic name pair, zodiac/weekday
correspondences, planetary life-periods, Metonic Golden Number, 28 lunar
mansions (declared Alcyone convention), Grímnismál palaces, nine worlds.

**Example:**
```bash
python3 astrology_engine.py runic --datetime 2026-05-16T16:45 \
  --lon 0 --timezone UTC --age 54 --moon-lon 50 --full
```

---

## `dossier`

The whole chart as one written story: pillars, wanderers, aspects,
fixed stars, midpoints, the draconic deep, solar arc directions, the
year-lord, and the coming ninety days.

```bash
python3 astrology_engine.py dossier --load volmarr --target-date 2026-10-23 --out dossier.md
```

---

## `draconic`

The soul-chart: every position reckoned from the natal north node,
plus the contacts where the draconic and tropical zodiacs touch.

```bash
python3 astrology_engine.py draconic --load volmarr --orb 2
```

---

## `asteroids`

Chiron, Ceres, Pallas, Juno, Vesta — when their ephemeris files are
present. When they are not, the engine says so plainly instead of
inventing positions.

```bash
python3 astrology_engine.py asteroids --load volmarr
```

## `midpoints`

The secret chords: every planetary pair's midpoint, and the planets
and angles standing upon them.

```bash
python3 astrology_engine.py midpoints --load volmarr
```

---

## `stars`

Fixed stars: the bright ones — Regulus, Spica, Antares — and their
conjunctions to your planets and angles, precessed to the birth date.

```bash
python3 astrology_engine.py stars --load volmarr
python3 astrology_engine.py stars --list
```

---

## `elect`

Electional astrology: choose the moment instead of reading it. Scores
candidate hours by the Moon's state, Mercury retrograde, and planetary
hours, and ranks the most fortunate windows.

```bash
python3 astrology_engine.py elect --load volmarr --from-date 2026-10-20 --to-date 2026-10-27 --top 5
```

---

## `watch`

Transit watch: a calendar of coming outer-planet transits
(Jupiter–Pluto) to your natal planets and angles, with exact dates.

```bash
python3 astrology_engine.py watch --load volmarr --from-date 2026-10-06 --to-date 2026-11-06
python3 astrology_engine.py watch --load volmarr --to-date 2027-12-31 --json
```

---

## `profection`

Annual profections — the Hellenistic time-lord wheel. Each year of
life the Ascendant profects one whole sign; that sign's traditional
lord becomes lord of the year.

```bash
python3 astrology_engine.py profection --load volmarr --target-date 2026-10-23
```

---

## `solar-arc`

Solar arc directions: the secondary-progressed Sun's arc carried
across the whole chart, listing directed-to-natal aspects within a
tight orb — the great modern predictive art.

```bash
python3 astrology_engine.py solar-arc --load volmarr --target-date 2026-10-23
python3 astrology_engine.py solar-arc --date 1972-09-01 --time 08:18 \
  --lat 42.81 --lon -73.94 --timezone America/New_York \
  --target-date 2027-09-06 --orb 1.5
```

---

## `wheel`

Render a natal chart wheel as a beautiful dark-gold SVG: zodiac ring,
house cusps and numbers, planet glyphs (collision-spread), colored
aspect lines, ASC at 9 o'clock as tradition demands, MC near the top.

```bash
python3 astrology_engine.py wheel --load volmarr -o volmarr.svg
python3 astrology_engine.py wheel --date 1972-09-01 --time 08:18 \
  --lat 42.81 --lon -73.94 --timezone America/New_York -o wheel.svg
```

Five house systems are available on every chart-bearing command
(`natal`, `transit`, `synastry`, `solar-return`, `composite`, `wheel`,
`reading`) via `--houses`: `placidus` (default), `whole-sign`, `equal`,
`koch`, `regiomontanus`.

```bash
python3 astrology_engine.py wheel --load volmarr --houses whole-sign -o volmarr-ws.svg
```

---

## `tarot`

Tarot readings from the 78-card Rider-Waite-Smith deck (original
distillations, modern synthesis), with ten spreads and optional reversals.
Draws are seeded and reproducible.

```bash
python3 astrology_engine.py tarot --spread celtic-cross --seed 7
python3 astrology_engine.py tarot --list-spreads
python3 astrology_engine.py tarot --spread horseshoe --question "What of my path?" --no-reversals
```

Spreads: `single`, `three`, `five-cross`, `celtic-cross`, `horseshoe`,
`relationship`, `career`, `choice`, `year-ahead`, `chakra`.

---

## `runecast`

Rune casting in three rows: Elder Futhark (24), Younger Futhark (16),
Anglo-Saxon futhorc (33) — `--system elder|younger|futhorc`.

```bash
python3 astrology_engine.py runecast --system younger --layout norns
```



Rune readings from the 24 Elder Futhark runes, cast in seven layouts —
from a single rune to the Nine Worlds. Merkstave (reversed) readings
apply only to the asymmetric runes; the nine symmetric runes read the
same face-up or face-down, as tradition holds. Casts are seeded and
reproducible.

```bash
python3 astrology_engine.py runecast --layout nine-worlds --seed 7
python3 astrology_engine.py runecast --list-layouts
python3 astrology_engine.py runecast --layout norns --question "What of my path?"
```

Layouts: `single`, `norns`, `elements`, `cross`, `hammer`,

## `ogham`

Ogham readings — the twenty-five Irish staves: twenty feda in four
aicmí plus the five forfeda, with kennings from the Auraicept na
n-Éces (Bríatharogam Morainn mac Moín, per McManus, Ériu 39 (1988)).
The aicme layout draws a true census — one stave from each aicme.
Reads by position; no reversed meanings. Interpretive, seeded,
reproducible.

```bash
python3 astrology_engine.py ogham --layout aicme --seed 5
python3 astrology_engine.py ogham --list-layouts
python3 astrology_engine.py ogham --layout grove --question "What of my path?" --no-forfeda
```

Layouts: `single`, `triad`, `aicme`, `wheel`, `grove`.

## `chinese`

Chinese zodiac for a Gregorian birth date: the year's heavenly stem
and earthly branch (anchored so 1984 = Jia-Zi), its NaYin, yin/yang,
trine allies, secret friend, and clash animal. The zodiac year opens
at Lunar New Year (1900–2100 supported), not January 1. Stem/branch/
allies are computed calendar math; animal keywords are interpretive.

```bash
python3 astrology_engine.py chinese 1972-09-01
python3 astrology_engine.py chinese 2024-02-09 --json
```

## `bazi`

Four Pillars (BaZi) for a birth moment: year, month, day, and hour
ganzhi with NaYin and the Day Master. The year turns at Lichun and
the month branches follow the twelve solar-term jie (Swiss
Ephemeris); month stems by the Five Tigers rule, hour stems by the
Five Rats. Requires --time.

```bash
python3 astrology_engine.py bazi --date 1972-09-01 --time 08:18 --timezone America/New_York
```

## `tibetan`

Tibetan astrology (nag rtsis elemental tradition) for a birth date:
the element-animal year with rabjung cycle position, the year's
mewa, the year's parkha, and the five personal forces — srog, lus,
dbang-thang, rlung-ta, bla. The Losar year boundary is approximated
by Chinese New Year (disclosed; boundary births flagged). Lineage
variation in the force computations is documented, not hidden.

```bash
python3 astrology_engine.py tibetan 1972-09-01
python3 astrology_engine.py tibetan 2024-02-09 --json
```
`nine-worlds`, `wheel`. The optional `--blank` adds the modern blank
rune (a 1980s invention, flagged as such); `--no-merkstave` reads all
runes upright.

---

## `reading`

Interpretive astrology readings — general, love, or career — woven from a
computed chart. Reads a saved chart (`--load NAME`) or computes from birth
data. Every paragraph is labeled interpretive: symbolic counsel, never
computed fact.

```bash
python3 astrology_engine.py reading --load volmarr --kind love
python3 astrology_engine.py reading --date 1972-09-01 --time 08:18 \
  --lat 42.81 --lon -73.94 --timezone America/New_York --kind career
```

---

## `numerology`

Pythagorean numerology: Life Path, Destiny, Soul Urge, Personality,
Birthday, and Personal Year numbers. Master numbers 11/22/33 are held,
never reduced.

```bash
python3 astrology_engine.py numerology --date 1972-09-01 --name "Volmarr Godi"
```

---

## `iching`

The I-Ching oracle: cast by coins or simulated yarrow stalks, with
changing lines and the relating hexagram. All 64 hexagrams in King Wen
order, with original renderings.

```bash
python3 astrology_engine.py iching --question "What of the morrow?"
python3 astrology_engine.py iching --method yarrow --seed 42
```

---

## Chart library — save, load, reuse

Every chart-producing command accepts `--save NAME`; birth-data commands
accept `--load NAME` (`--load1`/`--load2` for synastry, composite, synergy).

```bash
python3 astrology_engine.py natal --date 1972-09-01 --time 08:18 \
  --lat 42.81 --lon -73.94 --timezone America/New_York --save volmarr

python3 astrology_engine.py transit --load volmarr --transit-date 2026-10-23
python3 astrology_engine.py charts              # list the library
python3 astrology_engine.py chart-show volmarr  # inspect a saved chart
python3 astrology_engine.py chart-delete volmarr
```

Charts live in `~/.astroengine/charts` (override with `--chart-dir` or
`$ASTROENGINE_CHART_DIR`). `--load` fills any birth-data flags you did not
pass yourself — date, time, lat, lon, timezone — from the saved chart's
request. The modern JSON commands (`chart`, `vedic`, …) honor `--save` too.

## `aspect-grid` aspect families

`aspect-grid` now spans the full spectrum: the 5 major, 4 minor, quintile
and septile series, the novile series, and the obscure harmonic family
(decile, undecile, tredecile, quindecile, vigintile — tight 1.5°/1.0°
orbs, as tradition demands).

```bash
python3 astrology_engine.py aspect-grid --date 1972-09-01 --aspects obscure
python3 astrology_engine.py aspect-grid --date 1972-09-01 --aspects major
```

---

## `lots`

Arabic Lots / Hermetic Parts.

```
python3 astrology_engine.py lots
    --date    YYYY-MM-DD   birth date (required)
    --time    HH:MM        birth time local (optional)
    --city    CITY         (optional)
    --nation  CC           (optional)
    --lat     DECIMAL      (optional)
    --lon     DECIMAL      (optional)
```

All seven classical Lots: Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis. Day/night chart formula switching applied automatically. Output shows longitude, sign, house placement, and brief interpretation.

---

## `hellenistic`

Hellenistic analysis layer.

```
python3 astrology_engine.py hellenistic
    --date    YYYY-MM-DD   birth date (required)
    --time    HH:MM        birth time (optional)
    --city    CITY         (optional)
    --nation  CC           (optional)
    --lat     DECIMAL      (optional)
    --lon     DECIMAL      (optional)
```

Outputs: sect (day/night), sect light (Sun or Moon as chart ruler), planetary joys by house, triplicity rulers for fire/earth/air/water, stellium detection, mutual receptions.

---

## `dignity`

Standalone essential dignities table.

```
python3 astrology_engine.py dignity
    --date    YYYY-MM-DD   birth date (required)
    --time    HH:MM        birth time (optional)
    --city    CITY         (optional)
    --nation  CC           (optional)
    --lat     DECIMAL      (optional)
    --lon     DECIMAL      (optional)
```

Full Ptolemaic dignity hierarchy for all planets: domicile, exaltation (with exact-degree flag), fall, detriment, triplicity, Egyptian terms, Chaldean face. Scored and ranked. Mutual receptions listed.

---

## `antiscia`

Standalone antiscia table.

```
python3 astrology_engine.py antiscia
    --date    YYYY-MM-DD   birth date (required)
    --time    HH:MM        birth time (optional)
```

No location needed. Shows antiscia (solstice reflection across 0°Cancer/Capricorn axis) and contra-antiscia (reflection across 0°Aries/Libra axis) for all planets. Inter-planet connections highlighted when two antiscia are within orb.

---

## `predict`

Event prediction within a time window.

```
python3 astrology_engine.py predict
    --date              YYYY-MM-DD   natal birth date (required)
    --time              HH:MM        natal birth time (optional)
    --city              CITY         natal birth city (optional)
    --nation            CC           (optional)
    --start             YYYY-MM-DD   window start (default: today)
    --end               YYYY-MM-DD   window end (default: today + 1 year)
    --transit-planets   LIST         comma-separated transit planet list
    --natal-planets     LIST         comma-separated natal target list
    --lat               DECIMAL      (optional)
    --lon               DECIMAL      (optional)
```

Default transit planets: `Jupiter,Saturn,Uranus,Neptune,Pluto,Chiron,N.Node,Mars,Sun,Venus,Mercury`
Default natal targets: `Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Chiron,N.Node,Asc,MC`

Four prediction layers:
1. **Exact transit-to-natal aspects** (bisection to 0.01°)
2. **Planetary stations** (retrograde / direct)
3. **Sign ingresses** (planet crosses sign boundary)
4. **Eclipses** (New Moon / Full Moon eclipses)

**Example — outer planets only, one year:**
```bash
python3 astrology_engine.py predict \
  --date 1975-11-22 --time 14:30 \
  --city Indianapolis --nation US \
  --start 2026-01-01 --end 2027-01-01 \
  --transit-planets "Jupiter,Saturn,Uranus,Neptune,Pluto"
```

**Performance note:** A full one-year window with all planets takes 5–15 seconds on the Raspberry Pi 5. Narrow the window or use `--transit-planets` to reduce compute time.

---

## `geoastrology`

Astrocartography — MC/IC/ASC/DSC lines.

```
python3 astrology_engine.py geoastrology
    --date       YYYY-MM-DD   birth date (required)
    --time       HH:MM        birth time local (optional)
    --city       CITY         birth city (optional)
    --nation     CC           (optional)
    --name       NAME         display name (optional)
    --lat        DECIMAL      birth location lat override (optional)
    --lon        DECIMAL      birth location lon override (optional)
    --query-lat  DECIMAL      analyse proximity to this location (optional)
    --query-lon  DECIMAL      analyse proximity to this location (optional)
```

**Output sections:**
- MC/IC lines table: planet RA, Dec, and Earth longitude where it culminates/anti-culminates
- ASC lines: latitude-sampled table of where each planet rises
- DSC lines: brief summary for Sun, Moon, Venus, Mars, Jupiter, Saturn
- Power spot analysis: when `--query-lat`/`--query-lon` provided, shows which chart lines pass within 3° of that location

**Example:**
```bash
python3 astrology_engine.py geoastrology \
  --date 1975-11-22 --time 14:30 \
  --city Indianapolis --nation US \
  --name Volmarr \
  --query-lat 59.91 --query-lon 10.75
```

---

## `aspect-grid`

Full aspect matrix for all planets.

```
python3 astrology_engine.py aspect-grid
    --date    YYYY-MM-DD   birth date (required)
    --time    HH:MM        birth time (optional)
```

N×N grid showing all 11 aspect types between all 12 planet points. Glyph-based display. No location needed.

---

## Coordinate Reference

When using `--lat` / `--lon`:

- North latitudes are positive: `--lat 39.7684` (Indianapolis)
- South latitudes are negative: `--lat -33.8688` (Sydney)
- East longitudes are positive: `--lon 10.7522` (Oslo)
- West longitudes are negative: `--lon -86.1581` (Indianapolis)

---

## Nation Code Examples

| Code | Country |
|------|---------|
| `US` | United States |
| `GB` | United Kingdom |
| `DE` | Germany |
| `NO` | Norway |
| `SE` | Sweden |
| `DK` | Denmark |
| `IS` | Iceland |
| `FI` | Finland |
| `IE` | Ireland |
| `FR` | France |
| `AU` | Australia |
| `JP` | Japan |
| `CA` | Canada |
| `MX` | Mexico |

---

*The stars wait for no one's permission.*

## Structured commands (4.0.0)

`chart --date DATE [--time TIME] --lat LAT --lon LON --timezone IANA` emits
schema-versioned JSON. Optional `--zodiac tropical|sidereal`, `--ayanamsa
lahiri|raman|krishnamurti|fagan-bradley`, `--house-system` (placidus, whole-sign,
equal, koch, regiomontanus, campanus, porphyry), `--node-type true|mean`, and
`--ephemeris-path DIRECTORY`. Same commands via `astroengine` or
`python -m astroengine`. `capabilities` reports availability, scope and evidence.

Failures: stderr JSON + exit 2; stdout has no partial result. Argument syntax
errors use argparse's standard stderr/help behavior. Success exit 0. No automatic
city resolution, zone guessing, persistence or LLM calls in new commands.

`vedic` takes the same chart flags; defaults: sidereal, Lahiri, whole-sign, mean
nodes. Output contains navagraha, Moon nakshatra, pada, rasi houses and lagna.
Unknown time suppresses lagna/houses; explicit tropical input rejects.

`vargas` shares Vedic chart flags. Optional `--divisions 9 10 30` selects charts;
omit it for all sixteen. Mapping profile: classical-rao-2000, with D27 source
example discrepancy recorded in docs/references/technique-sources.md.

`dashas` shares Vedic flags and accepts `--years NUMBER`, `--year-model
tropical|julian|savana` and `--as-of ISO_TIMESTAMP_WITH_OFFSET`. Defaults: 120 years
and 365.2425-day tropical clock. Antars are clipped, preserving full boundaries.

`panchanga` shares Vedic flags and returns instant elements plus local civil
weekday. It does not compute sunrise vara, transitions or a festival calendar.

`relationship` (alias `synergy-json`) takes `--date1/2`, optional `--time1/2`,
required `--lat1/2 --lon1/2 --timezone1/2`, plus shared chart profile flags.
This new command resolves real separate locations/zones; legacy `synergy` remains
its historical text path. Scores include every contribution and method label.

`location` shares chart flags and requires `--query-lat LAT --query-lon LON`.
Known birth time is required. Relocation holds birth UTC fixed. Results include
MC/IC/ASC/DSC longitudes and query residuals in degrees, with circumpolar status.

`western` shares chart flags and requires `--as-of YYYY-MM-DD`; optional
`--harmonic POSITIVE_INTEGER` (default 9) and `--midpoint-orb DEGREES` (default 1).
Whole-sign annual profection uses civil birthday age and traditional rulership.

`tools` emits the eight agent request schemas. Python callers use
`astroengine.agent.run_tool(name, parameters)`; schemas reject invented fields and
unsupported techniques. The checked-in SKILL.md documents safe agent invocation.

## Strict legacy inputs — W09b1

Birth-aware `natal`, `transit`, `solar-return`, `progressions`, `lots`, `hellenistic`,
`dignity`, `predict` and `geoastrology` accept `--timezone IANA_ZONE`. The explicit
zone bypasses optional timezone discovery, so explicit coordinates plus timezone
work offline without the geo extra. Supply `UTC` for input already expressed in
UTC. Missing/unresolved zones now fail; ambiguous or nonexistent DST clocks require
the known UTC instant supplied as UTC date/time. Dates use YYYY-MM-DD and times use
HH:MM[:SS[.ffffff]]. Empty time is an error; omitted time stays flagged local noon.

`synastry`, `composite` and `synergy` each accept `--city1/--nation1/--lat1/--lon1/
--timezone1` and corresponding person-2 flags. Their output exposes each resolved
UTC time and any inherited London location default. Both locations must be supplied
for Davison; a partial location no longer manufactures the other person's (0,0).
Explicit zero coordinates work for overlays, Davison admission and location queries.

```bash
python astrology_engine.py synergy --date1 2000-01-01 --time1 00:15 \
  --lat1 19.076 --lon1 72.8777 --timezone1 Asia/Kolkata \
  --date2 2000-01-01 --time2 23:45 --lat2 40.7128 --lon2 -74.006 \
  --timezone2 America/New_York
```

Invalid dates/years, nonfinite/out-of-range or incomplete coordinate pairs, failed
location resolution, DST folds/gaps and invalid zones produce stderr/status 2
before chart output. `--transit-time` needs `--transit-date`; prediction end must
follow start, and its one-civil-year default clamps February 29 to February 28.
`planet-hours` still has its documented Indianapolis default and legacy sunrise
engine, while its explicit date/coordinate admission is now strict. Legacy house,
optional-body/backend and event-root behavior is still being migrated separately.

## W09b2 calculation and uncertainty behavior

Known-time house failures (including polar Placidus) reject before any chart
header with stderr/status 2. No equal-house or zero-angle fallback is printed.
Unknown-time natal omits sect/lots/Hellenistic house conclusions and house overview;
transit/progressions retain positions/aspects without houses. Dignity uses no house
calculation even at polar latitudes. UTC date-only antiscia/aspect-grid label noon.
Synastry preflights known receiving houses before output; Davison preflights before
composite output. Planetary positions disclose requested/actual backend flags and
log named optional-body failures to stderr; required bodies must all calculate.
Planetary hours reject missing/polar rise/set events, preserving the legacy UTC
search/day-ruler convention. Local sunrise-calendar semantics remain V13 work.
