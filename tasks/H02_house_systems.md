# H02 — House systems (Whole Sign, Equal, Koch, Regiomontanus)

Second slice of ROADMAP_HORIZONS.md.

## Skald
Placidus is one lens. The old schools demand their own: Whole Sign for
the Hellenists, Equal for the moderns, Koch and Regiomontanus for the
traditionalists. One flag, `--houses`, on every chart-bearing command.

## Rúnhild
- `astroengine/houses.py` (typed path): `house_cusps(jd_ut, lat, lon,
  system)` → `(cusps[12], asc, mc)` for `placidus | whole-sign |
  equal | koch | regiomontanus`. Swiss Ephemeris native systems where
  available ('P','K','R','E','W'); Whole Sign cusps at sign ingresses
  from the ASC sign; Equal cusps every 30° from ASC. Explicit
  CalculationError on unknown system or polar failure.
- Thread `--houses SYSTEM` (default `placidus`) through the
  chart-bearing commands: natal, transit, synastry, solar-return,
  composite, wheel, reading. Shared helper `add_houses(parser)`;
  `_optional_houses` gains a system parameter (default placidus — no
  behavior change for existing invocations).
- Saved charts record the house system in the request.

## Eldra
Implement module + flag threading + saved-request recording.

## Sólrún (subagent verification)
`tests/test_houses.py`: all five systems return 12 cusps; Whole Sign
cusps sit on sign boundaries; Equal cusps exactly 30° apart from ASC;
ASC preserved across systems (±1′); Volmarr's Placidus ASC Libra 1°01′
unchanged (default path); `--houses whole-sign` CLI smoke test on
`wheel`. Full suite green.

## Védis
COMMANDS.md flag docs; `astroengine/INTERFACE.md` entry; GOALS.md line.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row (append to wheel line —
Yrsa's own line, safe).

## Acceptance gate
`wheel --load volmarr --houses whole-sign` renders with sign-boundary
cusps; suite green; pushed with verified remote HEAD.
