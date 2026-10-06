# Component index

| Path | Responsibility | State at orientation |
| --- | --- | --- |
| `astrology_engine.py` | 16 legacy text commands and legacy arithmetic | Existing |
| `astroengine/` | New typed request and computation boundaries | S01 target |
| `data/` | Technique profiles and capability states | S01 target |
| `tests/` | Independent fixtures and integration/error checks | S01 target |
| `.github/workflows/` | Python/platform validation | S01 target |
| `docs/references/` | Historical gap analyses | Existing, may be stale |
| `docs/DECISIONS/` | Architectural decisions | Added |
| `tasks/` | Document-first work orders and acceptance evidence | Added |
| `COMMANDS.md` | CLI reference | Existing; extend each slice |
| `ROADMAP.md`, `TODO.md` | Sequence and current execution truth | Added/extended |

Update this index when new public modules are introduced; their API is recorded in
`astroengine/INTERFACE.md` with folder boundaries in `README_AI.md`.

`astroengine/vedic.py` owns Jyotisha D1/nakshatras; `data/vedic.json` owns names,
graha mappings and default profile. Input and astronomy domains stay independent.

`astroengine/vargas.py` owns divisional sign arithmetic; `data/vargas.json` owns
the sixteen named mappings. Technique discrepancy ledger lives in docs/references.

`astroengine/dashas.py` owns continuous-day Vimshottari arithmetic; timing.json
owns year-clock choices and reporting defaults.

`astroengine/panchanga.py` and data/panchanga.json own instant calendrical
partitions; sunrise-based calendars remain a separate domain slice.

`astroengine/aspects.py` owns circular/house/static aspect geometry;
relationships.py owns comparisons/composites/synergy; western.json owns rules.

`astroengine/locations.py` owns relocation and spherical horizon geometry;
ephemeris.equatorial_positions supplies zodiac-independent equatorial snapshots.

`astroengine/western.py` owns profections/harmonic/midpoint analysis.

`astroengine/agent.py` owns validated local routing; tool_schemas.json owns requests;
SKILL.md is the portable agent manifest. partitions.py owns half-open partitions.

`astroengine/legacy_inputs.py` owns typed compatibility tuples, numeric coordinate
flags and secondary date windows/years. inputs.parse_civil is the shared strict
civil admission boundary; profiles.json owns input formats and legacy defaults.
The text CLI owns discovery and exposes explicit per-person location/zone flags.
