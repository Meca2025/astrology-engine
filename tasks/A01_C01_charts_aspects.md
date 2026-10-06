# Chart Library + Full Aspect Spectrum

Volmarr's commission (2026-10-06): *"for all types of astrology add chart
saving and loading, and all forms of aspects even the more obscure ones."*

Standing law: six Mythic Engineering roles in order; push via the PAT
tool (no approval prompts); merge-first (`git fetch` + diff before every
push; never overwrite Volmarr's edits, esp. README.md); never force-push.

## Skald — vision and naming

Two features, one release:

1. **Chart library** — compute once, reuse forever. `--save NAME` on every
   chart-producing command; `--load NAME` (and `--load1/--load2` for
   two-person commands) fills birth data from a saved chart; `charts`,
   `chart-show NAME`, `chart-delete NAME` manage the library.
2. **Full aspect spectrum** — the 12 classical/minor aspects plus the
   obscure harmonic family: biseptile, triseptile, novile, binovile,
   quadnovile, decile, undecile, tredecile, quindecile, vigintile.
   `aspect-grid --aspects` filters by family (all/major/minor/obscure).

## Rúnhild — architecture

### Aspects
- `astrology_engine.py` `ASPECTS` gains (angle, orb_lum, orb_other, glyph,
  quality):
  - Biseptile 102.857° (2/7), Triseptile 154.286° (3/7)
  - Novile 40° (1/9), Binovile 80° (2/9), Quadnovile 160° (4/9)
  - Decile 36° (1/10), Undecile 32.727° (1/11), Tredecile 108° (3/10),
    Quindecile 165°, Vigintile 18° (1/20)
  - Obscure orbs: 1.5° luminaries / 1.0° otherwise (tight, as tradition
    demands for high harmonics).
- New `ASPECT_FAMILIES` map: major {Conjunction, Sextile, Square, Trine,
  Opposition}, minor {Semi-Sextile, Semi-Square, Sesquisquare, Quincunx},
  quintile {Quintile, Bi-Quintile}, septile {Septile, Biseptile,
  Triseptile}, novile {Novile, Binovile, Quadnovile}, harmonic {Decile,
  Undecile, Tredecile, Quindecile, Vigintile}. "Obscure" = everything not
  major/minor.
- `calc_aspects(positions, luminaries, families=None)` — optional family
  filter; `aspect-grid --aspects {all,major,minor,obscure}` (default all).
- `data/western.json` aspects gain the same ten (orb 1.5, weight 0 —
  neutral for synergy scoring, so existing scores don't shift).

### Chart library
- New `astroengine/charts.py`:
  - `chart_dir()` — `$ASTROENGINE_CHART_DIR`, else `~/.astroengine/charts`
    (created on demand).
  - `save_chart(name, chart_type, request, result)` — validates name
    (`^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`), writes `{name}.json`
    {name, chart_type, saved_at, engine_version, request, result};
    overwrites with a printed notice.
  - `load_chart(name)`, `list_charts()`, `delete_chart(name)`,
    `chart_exists(name)`; missing → CalculationError.
- `astrology_engine.py` helpers:
  - `add_chart_lib(parser, two_person=False)` — adds `--save`,
    `--load`/`--load1`/`--load2`, `--chart-dir`.
  - `apply_chart_load(args, prefix="")` — for each of
    date/time/lat/lon/timezone/city/nation: if the CLI arg is None (or
    the legacy default), fill from the saved chart's request.
  - `maybe_save_chart(args, chart_type, result)` — saves when `--save`
    given; request = the args namespace minus save/load/chart-dir keys.
- Wiring: `--save`/`--load` on all 16 legacy dispatch commands
  (natal, transit, synastry, solar-return, progressions, lunar,
  planet-hours, lots, hellenistic, dignity, antiscia, composite,
  synergy, predict, geoastrology, aspect-grid, runic) via
  `add_chart_lib`; `--load1/--load2` on synastry/composite/synergy.
  Each `cmd_*` calls `apply_chart_load` first and `maybe_save_chart`
  last with its headline result structure.
- Modern JSON commands (`astroengine/cli.py::run_command`): honor a
  top-level `--save` added in `register_commands` — saves the result
  dict with chart_type = the subcommand name.
- Management: `charts` (list table), `chart-show NAME` (metadata +
  request summary), `chart-delete NAME`.

## Eldra — build

- `astroengine/charts.py`; ASPECTS + ASPECT_FAMILIES + calc_aspects
  filter; western.json additions; helpers + 16 wiring sites; modern
  `--save`; 3 management subcommands.

## Sólrún — verification

- `tests/test_aspects_full.py`: every new aspect fires at exact
  separation; orb boundary respected (1.01° separation with 1.0 orb →
  no hit); family filter returns only the family; western.json additions
  parse and keep synergy weights neutral (sum of new weights == 0).
- `tests/test_chart_library.py` (tmp chart dir): save→load round-trip
  preserves request+result; list shows it; delete removes it; bad names
  rejected; load of missing chart → CalculationError; `--load` fills a
  blank argparse namespace from a saved chart.
- Full suite green.

## Védis — cartography

- `COMMANDS.md`: chart-library section + `--save`/`--load` notes +
  aspect-grid `--aspects`; `astroengine/INTERFACE.md`: both features;
  COMPONENT_INDEX.md: `astroengine/charts.py` line.

## Scribe — memory

- DEVLOG.md entry; TODO.md checkboxes; this task file as work order;
  README gets one appended line under the runic table (Volmarr's
  territory — append only).
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

`natal --save` → `transit --load` round-trip works end-to-end;
`aspect-grid --aspects obscure` shows septiles/noviles; suite green;
pushed with verified remote HEAD.
