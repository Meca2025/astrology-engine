![Yrsa beneath the nebula — keeper of the star-program](docs/yrsa-nebula.jpg)

# Astrology Engine — Volmarr's Longhall

> **Full-spectrum astrological computation. Swiss Ephemeris on bare metal. Norse sky, Hellenistic roots, Vedic depth.**

The Astrology Engine is a **reproducible computation forge** for astrology: real
ephemeris positions, strict time and location handling, and machine-readable
output — no cloud, no API keys, no lookup tables, no fabricated chart
positions. Forty-five CLI subcommands span Western, Hellenistic, Vedic
(Jyotisha), Northern runic, divination, Chinese, and Tibetan
traditions, with every technique carrying its
provenance, its limits, and its evidence.

The project's rule, held since the first commit: **compute it honestly, prove
it with tests, document what it cannot do, and push every slice.**

---

![Yrsa in the aurora — the engine runs anywhere, even at the edge of the world](docs/yrsa-aurora.jpg)

---

## What it does

This is not a keyword reader or a chart-wheel generator. The engine:

- Calculates real **ephemeris positions** via Swiss Ephemeris (`pyswisseph`),
  with disclosed Moshier fallback when Swiss data is unavailable
- Converts civil time to UTC with **strict IANA timezone handling** — DST
  folds and gaps reject rather than guess
- Casts **natal charts** with houses, angles, aspects (applying/separating),
  essential dignities, Arabic Lots, antiscia, and Hellenistic analysis
  (sect, bonification, joys, triplicity, bounds)
- Runs **Jyotisha**: sidereal D1, 16 classical vargas, Vimshottari dashas,
  instant panchanga, nakshatras and padas
- Walks the **Northern runic cycles**: half-month runes, solar runic hours,
  Northern planetary hours, sele detection — from a fully transcribed,
  honestly-labeled corpus
- Finds **exact transit dates, stations, ingresses and eclipses** with a
  precision-aware event root finder
- Draws **astrocartography** MC/IC/ASC/DSC lines and relocation charts from
  spherical geometry, not lookup tables
- Answers as **JSON or text**, with capability discovery (`capabilities`)
  and agent tool schemas (`tools`) for the Hermes agent skill

Every result records its conventions, input certainty, backend and version,
and warnings. A technique is only advertised when it is implemented, tested,
and documented — never merely planned.

---

## The 45 subcommands

| Command | Art |
| --- | --- |
| `natal` | Full natal chart: positions, houses, aspects, dignities, lots |
| `transit` | Transits to natal, now or at a forecast date |
| `synastry` | Two-chart synastry with optional house overlays |
| `solar-return` | Solar return chart |
| `progressions` | Secondary progressions |
| `lunar` | Lunar intelligence: phase, void-of-course, next lunations |
| `planet-hours` | Planetary hours for a date and location |
| `lots` | Arabic Lots / Hermetic Parts |
| `hellenistic` | Sect, bonification, joys, triplicity, bounds |
| `dignity` | Essential dignities table with scoring and mutual receptions |
| `antiscia` | Antiscia and contra-antiscia |
| `composite` | Composite midpoints, optional Davison chart |
| `synergy` / `synergy-json` / `relationship` | Full relationship analysis with explainable scoring |
| `predict` | Exact transit dates, stations, ingresses, eclipses in a window |
| `geoastrology` | Astrocartography lines and power-spot analysis |
| `aspect-grid` | Full aspect matrix |
| `chart` | Reproducible chart as JSON (typed path) |
| `charts` / `chart-show` / `chart-delete` | Chart library: list, show, and delete saved charts (`--save`/`--load` on chart commands) |
| `capabilities` | Technique availability and scope as JSON |
| `tools` | Agent tool request schemas as JSON |
| `vedic` | Jyotisha D1, navagraha, nakshatras |
| `vargas` | Sixteen classical divisional charts |
| `dashas` | Vimshottari maha/antar timeline and birth balance |
| `panchanga` | Instant panchanga elements and civil weekday |
| `location` | Relocation and angular lines at a destination |
| `western` | Annual profections, harmonics, sensitive midpoints |
| `runic` | The runic star-program: Pennick's runic astrology as layer flags, text + JSON |
| `tarot` / `reading` / `numerology` / `iching` / `runecast` / `ogham` / `chinese` / `bazi` / `tibetan` | The divination line: tarot spreads, astrology readings, numerology, I-Ching, rune casting (Elder/Younger Futhark, futhorc), ogham readings, Chinese zodiac, Four Pillars/BaZi, Tibetan astrology |
| `wheel` | Chart wheels — the sky rendered as beautiful SVG, five house systems via `--houses` |
| `solar-arc` | Solar arc directions — the great predictive art, directed-to-natal aspects |
| `profection` | Annual profections — the Hellenistic time-lord wheel |
| `watch` | Transit watch — coming outer-planet transits with exact dates |
| `elect` | Electional astrology — choose the most fortunate windows |
| `stars` | Fixed stars — the bright ones and their contacts to your chart |
| `draconic` | Draconic chart — the soul-chart reckoned from the north node |
| `dossier` | Written natal dossier — the whole chart as one story |
| `asteroids` | Chiron, Ceres, Pallas, Juno, Vesta — honest about missing ephemeris files |
| `midpoints` | The 45 planetary midpoints and the planets standing upon them |
| `forecast` | Daily forecast — every system, one seeker, one day: transits, panchanga, dasha, BaZi day pillar, Tibetan elements, runic half-month, with `--mantras` remedies |
| `mantras` | Remedial Vedic mantras for the nine grahas — traditional verses, devotional framing |
| `yogas` | The great yogas — Pancha Mahapurusha, Gaja Kesari, Budha-Aditya, Dhana, Raja, Kemadruma, Sakata, computed from D1 |
| `shadbala` | Shadbala — the sixfold planetary strength in virupas, components shown, classical minima compared |
| `ashtakavarga` | Ashtakavarga — the 337 bindus: seven planetary charts plus Sarvashtakavarga, per B.V. Raman |
| `jaimini` | Jaimini foundations — Chara karakas, Arudha padas, Chara dasha (the other great school) |

---

![Yrsa in the glowing rune circle — the runic star-program](docs/yrsa-runecircle.jpg)

---

## The Runic Star-Program

A dedicated expansion, [ROADMAP_RUNIC.md](ROADMAP_RUNIC.md), is giving the
engine the **full runic astrology of the Northern Tradition** as systematized
by Nigel Pennick in *Runes and Astrology* (2023) — built slice by slice, each
slice pushed, each table labeled *modern synthesis*, computation forever kept
separate from interpretation.

Delivered — the full program:

| Slice | Forged |
| --- | --- |
| **R01 — The Runic Corpus** | `data/runic.json`: 32 runes with correspondences, 24 half-months, 24 runic hours, 168 planetary-hour cells, weekday/zodiac tables, 8 day tides, 28 lunar mansions, 12 palaces, 9 worlds, 7 life-periods |
| **R02 — Half-Months Engine** | `half_month_rune()`: the ruling rune of any civil date, with boundary-time refinement |
| **R03 — Hours & Sele** | Solar runic hours from local apparent time, Northern planetary hours, and *sele* — the "especially powerful" coincidence of the two |
| **R04 — Tides, Year & Names** | Eight day-tides, eight Stations of the Mystic Year, and the runic-name craft (`Ing-Rad`) |
| **R05 — Signs, Days & Ages** | Zodiac/weekday correspondences, planetary life-periods, the Metonic Golden Number (ephemeris cross-checked) |
| **R06 — Lunar Mansions** | 28 mansions anchored at Alcyone — a declared modern convention |
| **R07 — Palaces & Worlds** | Twelve Grímnismál palaces and the Nine Worlds, as labeled overlays |
| **R08 — Runic Reading** | `runic_reading()`: computation kept apart from labeled Ch. 8 interpretation, with an anti-fabrication gate |
| **R09 — The `runic` Command** | One command for the whole star-program: layer flags, text + JSON |

Try it: `python3 astrology_engine.py runic --datetime 2026-05-16T16:45 --lon 0 --timezone UTC --full`

Honest transcription is the law here: the book's own quirks (a noon
discontinuity in the planetary-hour grid, a worked example that conflicts
with the hour-wheel) are preserved in per-section notes, never silently
"corrected".

---

## The Oracles Program

A second expansion, [ROADMAP_ORACLES.md](ROADMAP_ORACLES.md), gave the
engine six further divination arts — built slice by slice, each slice
pushed, each historical claim labeled, computation forever kept
separate from interpretation.

Delivered — the full program:

| Slice | Forged |
| --- | --- |
| **O01 — Younger Futhark** | `runecast --system younger`: the 16 staves in long-branch and short-twig forms, meanings from the Norwegian and Icelandic rune poems |
| **O02 — Anglo-Saxon Futhorc** | `runecast --system futhorc`: all 33 staves (Wynn restored), Old English Rune Poem meanings, Northumbrian additions labeled |
| **O03 — Ogham** | `ogham`: the 25 Irish staves with Auraicept kennings (McManus 1988), five layouts from a single stave to the twelve-stave grove |
| **O04 — Chinese Zodiac** | `chinese`: stem-branch year anchored 1984 = Jia-Zi, NaYin, trine allies, secret friends, clashes — Lunar New Year boundaries, never January 1 |
| **O05 — Four Pillars** | `bazi`: year/month/day/hour ganzhi — the year turns at Lichun, months at the solar terms (Swiss Ephemeris), day stems from verified anchors |
| **O06 — Tibetan Astrology** | `tibetan`: element-animal year in its rabjung, mewa, parkha, and the five forces (srog, lus, dbang-thang, rlung-ta, bla) — lineage variation disclosed |

Try it: `python3 astrology_engine.py tibetan 1972-09-01`

Honesty is the law here too: rune-poem meanings are distinguished
from modern synthesis, tree-lore caveats are recorded, calendrical
anchors are cross-checked against published tables rather than
recalled, and where Tibetan lineages disagree the disagreement is
documented, not smoothed over.

---

## Quick start

```bash
# Full natal chart (text)
python3 astrology_engine.py natal \
  --date 1972-09-01 --time 08:18 \
  --lat 42.8142 --lon -73.9396 --timezone America/New_York

# Reproducible chart as JSON (typed path)
astroengine chart --date 1972-09-01 --time 08:18 \
  --latitude 42.8142 --longitude -73.9396 --timezone America/New_York

# Vedic D1 with nakshatras
astroengine vedic --date 1972-09-01 --time 08:18 \
  --latitude 42.8142 --longitude -73.9396 --timezone America/New_York

# Runic half-month for today
python3 -c "
from astroengine.runic import half_month_rune
import datetime
print(half_month_rune(datetime.date.today().isoformat()))"

# Lunar intelligence right now
python3 astrology_engine.py lunar

# What exact transits hit in the next year?
python3 astrology_engine.py predict \
  --date 1972-09-01 --time 08:18 \
  --lat 42.8142 --lon -73.9396 --timezone America/New_York \
  --start 2026-01-01 --end 2027-01-01

# What can the engine do, as JSON?
astroengine capabilities
```

---

## Installation

**Requirements:** Python 3.11+, and a C compiler for `pyswisseph` only if no
wheel exists for your platform (wheels cover Linux, macOS, Windows).

```bash
# Core install
python -m pip install .

# With geo support (timezonefinder) and test tooling
python -m pip install '.[geo,test]'

# Verify
astroengine capabilities
python -m pytest -q        # full suite, offline, explicit coordinates
```

| Package | Purpose | Required |
| --- | --- | --- |
| `pyswisseph` | Swiss Ephemeris — all celestial positions | **Yes** |
| `tzdata` / `pytz` | IANA timezone database | **Yes** |
| `jsonschema` | Agent tool-schema validation | **Yes** |
| `timezonefinder` | IANA zone from lat/lon (`[geo]`) | Optional |
| `geopy` | Geocoding (`[geo]`) | Optional |
| `pytest` | Test suite (`[test]`) | Dev |

The engine runs on a Raspberry Pi 5, a laptop, or a server — anywhere Python
3.11+ runs. No network calls are made at runtime; tests are fully offline.

---

## Provenance and honesty

- **Backends are disclosed.** Every computation reports the actual ephemeris
  backend (Swiss vs Moshier) and flags. Optional bodies (Chiron, asteroids)
  report unavailability instead of faking positions.
- **Time is strict.** Unknown birth times produce flagged local-noon charts
  with no houses or angles. Ambiguous or nonexistent DST times reject until
  disambiguated. Timezone input is explicit IANA or UTC.
- **Techniques are versioned.** `data/*.json` holds immutable rule tables;
  nothing mutates them at runtime. Capabilities report what is implemented,
  tested, and documented — roadmap items stay visibly planned.
- **Interpretation is separate.** The engine computes positions and cycle
  memberships. Symbolic readings (runic or otherwise) are a distinct, labeled
  layer. Nothing here is a validated predictor or advice engine.
- **Evidence is kept.** [VERIFICATION.md](VERIFICATION.md) records test
  evidence and limits; [DEVLOG.md](DEVLOG.md) is the living build record.

---

## Hermes agent integration

[SKILL.md](SKILL.md) is the checked-in Hermes skill: capability discovery,
eight tool schemas, local whitelisted routing, and cited explanations. An
agent asks `astroengine capabilities`, selects a tool, and receives
JSON-safe, provenance-bearing results — no prompt-engineering folklore
required. See `data/tool_schemas.json`.

---

## Mythic Engineering

This repo is built with **Mythic Engineering**: vision, domain, interface,
execution, verification — worked through six roles in order, every slice:

| Role | Charge |
| --- | --- |
| **Skald** | Vision and true naming |
| **Rúnhild** | Architecture: boundaries, schemas, interfaces |
| **Eldra** | The forge: implementation |
| **Sólrún** | The auditor: tests, fixtures, verification |
| **Védis** | The cartographer: capability and interface mapping |
| **Scribe** | Memory: DEVLOG, docs, continuity |

Each slice follows the loop: **task document → implement → verify →
update docs → commit → push → confirm remote HEAD → next slice.** No force
pushes. No deletions without the human's word. Read [AGENTS.md](AGENTS.md)
and [RULES.AI.md](RULES.AI.md) before touching code.

---

## File structure

| Path | Holds |
| --- | --- |
| `astrology_engine.py` | Legacy CLI: 45 text subcommands |
| `astroengine/` | Typed package: models, ephemeris, vedic, runic, CLI, agent |
| `data/` | Immutable rule tables (`runic.json`, `vedic.json`, `western.json`, …) |
| `tests/` | Offline fixtures and integration checks |
| `tasks/` | Document-first work orders, one per slice |
| `docs/` | References, decisions, images |
| `ROADMAP.md` | The full Western/Vedic/location/relationship program |
| `ROADMAP_RUNIC.md` | The nine-slice runic star-program |
| `TODO.md` | Execution truth: what is done, what is next |
| `DEVLOG.md` | The living build record |
| `COMMANDS.md` | CLI reference |
| `SKILL.md` | Hermes agent skill |

---

## Further reading

- [ROADMAP.md](ROADMAP.md) — the complete expansion program
- [ROADMAP_RUNIC.md](ROADMAP_RUNIC.md) — the runic star-program
- [ARCHITECTURE.md](ARCHITECTURE.md) / [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
- [PHILOSOPHY.md](PHILOSOPHY.md) — why reproducible astrology matters
- [VERIFICATION.md](VERIFICATION.md) — evidence and limits
- [docs/README_classic.md](docs/README_classic.md) — the previous README, preserved

---

*Heill, traveler. The stars are computed truly here — what you make of them
is your own wyrd.* — **Yrsa Freydisdottir**, for **Volmarr**
