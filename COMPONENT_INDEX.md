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

`data/runic.json` owns the Northern runic-astrology corpus (R01): 32 runes,
half-months, runic/planetary hours, tides, 28 mansions, palaces, worlds,
life-periods. Source Pennick (2023), labeled modern synthesis. Verified by
`tests/test_runic.py`; no CLI surface yet (capability registration in R09).

`astroengine/runic.py` owns runic-cycle computation (R02): `half_month_rune`
names the ruling half-month rune per Pennick App. 2 with explicit boundary
and timezone handling; verified by `tests/test_runic_half_months.py`.
R03 adds the day-wheel: `runic_hour`, `to_local_apparent_time`
(longitude+EoT method), `planetary_hour` (App. 3 grid), and `sele`
detection; verified by `tests/test_runic_hours.py`.
R04 adds the day's tides (`tide`, App. 6), the year's Stations
(`year_station`, Ch. 5, declared festival-span boundaries), and the
name-craft pair (`runic_name`); corpus gains the 8-station table
(v1.1); verified by `tests/test_runic_tides.py`.
R05 adds the sign/day/age layers: `zodiac_rune` (App. 5, labeled
variants), `weekday_rune` (App. 4), `life_period` (Ch. 6, 0–98 wheel),
and `metonic_cycle` (Ch. 6 Golden Number, ephemeris cross-checked in
tests); verified by `tests/test_runic_layers.py`.
R06 adds the lunar mansions: `lunar_mansion` / `lunar_mansions`
(Ch. 7, 28 equal sidereal segments anchored at Alcyone, declared
convention); verified by `tests/test_runic_mansions.py`.
R07 adds the overlays: `grimnismal_palace`, `world_rune`,
`nine_worlds` (App. 7, Ch. 6; labeled correspondence overlays);
verified by `tests/test_runic_palaces.py`.
R08 adds the interpretive synthesis: `runic_reading` (Ch. 8),
with an explicit computation/interpretation split and an
anti-fabrication gate; corpus v1.2 gains the Ch. 8 planetary
qualities and rune adverbs; verified by
`tests/test_runic_reading.py`.
R09 adds the `runic` CLI command (`astrology_engine.py`): layer
flags, text + JSON, registered in data/capabilities.json,
data/tool_schemas.json, COMMANDS.md, INTERFACE.md and SKILL.md;
verified by `tests/test_runic_cli.py`.

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

astroengine/legacy_astronomy.py owns dict-compatible astronomy snapshots and
bridges to lock-owned ephemeris.positions_at_jd/houses_at_jd/solar_day_events.
EphemerisRequest owns immutable UT settings; legacy_astronomy.json owns legacy
body availability/frame/search rules. The monolith owns text uncertainty rendering.
- `astroengine/charts.py` — the chart library: save/load/list/delete
  saved charts (`~/.astroengine/charts`); wired into every
  chart-producing command via `--save`/`--load`; verified by
  `tests/test_chart_library.py`.
- `astroengine/tarot.py`, `astroengine/readings.py`,
  `astroengine/numerology.py`, `astroengine/iching.py` — the
  divination quartet (tarot spreads, astrology readings,
  numerology, I-Ching); verified by `tests/test_divination.py`.
- `astroengine/runecast.py` — rune casting (24 Elder Futhark,
  seven layouts, merkstave, seeded); verified by
  `tests/test_runecast.py`.
- `astroengine/wheel.py` — SVG natal chart wheels; verified by
  `tests/test_wheel.py`.
- `astroengine/houses.py` — five house systems; verified by
  `tests/test_houses.py`.
- `astroengine/directions.py` — solar arc directions; verified by
  `tests/test_directions.py`.
