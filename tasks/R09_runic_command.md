# R09 — The `runic` Command and Capability Registration

Final slice of ROADMAP_RUNIC.md — the runic star-program stands complete
after this. Standing law: six roles in order, push via the PAT tool.
Merge-first: `git fetch` + diff before every push; never overwrite
Volmarr's edits; never force-push.

## Skald — vision and naming

One CLI command unifies the whole runic program:

```
python3 astrology_engine.py runic --datetime 2026-05-16T16:45 --lon 0 \
  --timezone UTC --age 54 --moon-lon 50 --full
```

Layer flags: `--half-month --hour --tide --station --weekday --mansion
--life-period --name --reading`; `--full` selects all; no layer flags
implies `--full`. `--json` switches text output to JSON.

## Rúnhild — architecture

- `astrology_engine.py`: `runic = sub.add_parser("runic", ...)` beside the
  other legacy subcommands; dispatch entry `"runic": cmd_runic`; a
  `cmd_runic(args)` that calls the R02–R08 functions and prints text
  sections (header/section helpers like cmd_planet_hours) or JSON.
- Text output carries the provenance footer: "Pennick (2023) · modern
  synthesis · computation and interpretation labeled separately".
- Registration:
  - `data/capabilities.json`: new capability id "runic", status
    available, scope + evidence fields.
  - `data/tool_schemas.json`: new tool "runic" with an input schema for
    the flags (plain JSON-schema object, no $ref needed).
  - `COMMANDS.md`: `## runic` section with usage example.
  - `astroengine/INTERFACE.md`: CLI entry.
  - `SKILL.md`: Hermes notes — add runic to the tool count sentence and
    a scope-boundary line (Norse runic layers are a modern synthesis per
    Pennick 2023; mansions use the declared Alcyone convention; the
    interpretive layer is labeled, not computed fact).

## Eldra — build

- Parser + dispatch + cmd_runic; five registration edits.

## Sólrún — verification

- `tests/test_runic_cli.py`: invoke `cmd_runic` via argparse namespace
  (no subprocess): `--full` text contains "Ing" and "Rad"; `--json`
  parses as JSON with computation+interpretation; a single layer flag
  (`--tide`) prints only that layer; bad timezone → CalculationError.
- Full suite green (target: 360+).

## Védis — cartography

- INTERFACE.md CLI entry; COMPONENT_INDEX.md runic CLI line;
  COMMANDS.md section (counts as cartography).

## Scribe — memory

- DEVLOG.md final entry ("the runic star-program stands complete");
  TODO.md R09 checkbox + roadmap-complete note; README runic section
  gains the `runic` command example (README is Volmarr-edited territory —
  APPEND a subsection, never rewrite his lines).
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

`runic --full` runs end-to-end, text + JSON; all five registrations
present; suite green; docs current; pushed with verified remote HEAD.
ROADMAP_RUNIC.md: all nine slices complete.
