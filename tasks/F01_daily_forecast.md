# F01 — Daily forecast across all systems

Second slice of ROADMAP_VISTARA.md. Volmarr's words: "a daily
forecast for a person that uses all systems and their birth data".

## Skald
One question each morning: what does this day hold for me? The
answer should drink from every well we have dug — Western
transits, Vedic time-lords, the Chinese day pillar, Tibetan
forces, the runes — and speak with one voice, honestly labeled.

## Rúnhild
New module `astroengine/forecast.py` + `forecast` CLI:

Inputs: birth data (`--date/--time/--lat/--lon/--timezone`,
`--load` aware like the other birth-data commands) and
`--on DATE` (default: today in the birth timezone).

For the target day, gather (all computed, no interpretation):
- Western: transits to natal exact that day (orb <= 1°), stations,
  ingresses — reuse the transit/predict machinery.
- Vedic: panchanga (tithi, vara, nakshatra, yoga, karana) for the
  day; Vimshottari maha/antaradasha ruling the day.
- Chinese: BaZi day pillar; stem-branch clash/combine/harm
  relations between the day pillar and each natal pillar.
- Tibetan: day's element-animal and its element relation to the
  natal year's element; natal mewa/parkha/five-forces as context.
- Runic: half-month rune of the date.
- Zodiac relations: day's animal vs birth animal (clash, trine,
  secret friend).

Output: text + `--json`. JSON separates `computed` (facts) from
`reading` (labeled interpretive synthesis, one paragraph per
system + a closing synthesis). Interpretation is symbolic and
non-deterministic — say so in the text.

F02 (mantras) will consume this module's affliction signals, so
expose them cleanly: `pressured_planets`, `dasha_lords`,
`clashing_pillars`.

## Eldra
Build the module; wire the CLI; keep each system's existing
module as the single source of truth (no duplicated calendars).

## Sólrún (subagent verification)
`tests/test_forecast.py`: offline fixtures — a fixed birth
(Volmarr's) and a fixed target date; assert known transit hits,
known panchanga, known day pillar, known rune; JSON schema keys
present; bad `--on` date raises cleanly; suite green.

## Védis
INTERFACE.md, COMMANDS.md, capabilities evidence string if the
forecast becomes a tool (keep as CLI-only for F01; tool mapping
in F03 polish).

## Scribe
DEVLOG.md, TODO.md.

## Acceptance gate
`forecast --load volmarr --on 2026-10-23` (his Jupiter-Mercury
day) shows the conjunction; suite green; pushed with verified
remote HEAD.
