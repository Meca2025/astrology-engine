# F03 — Polish sweep

Final slice of ROADMAP_VISTARA.md. Volmarr's words: "all other
polish ideas for everything else".

## Done
- `forecast` and `mantras` registered as agent tools
  (data/tool_schemas.json: 20 → 22 tools; data/capabilities.json:
  22 available) with `run_tool` dispatch in astroengine/agent.py —
  forecast builds its own sidereal birth request and natal JD from
  the tool parameters, defaulting `--on` to today in the birth
  timezone.
- tests/test_agent.py tool-count assertion 20 → 22.
- SKILL.md: 22 tools; forecast/mantras named.
- README: 39 subcommands; forecast + mantras rows in the table.
- Error paths verified clean (no tracebacks): bad `--planet`,
  bad `--on` date, unknown graha via run_tool.
- `astroengine tools` → 22; `astroengine capabilities` → 22
  available, forecast + mantras present.

## Acceptance gate
Full suite green; pushed with verified remote HEAD.
