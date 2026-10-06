# H04 — Annual profections

Fourth slice of ROADMAP_HORIZONS.md.

## Skald
The Hellenistic wheel of years: each year of life the Ascendant
profects one whole sign, and that sign's traditional lord becomes lord
of the year. Simple, ancient, beloved.

## Rúnhild
- `astroengine/profections.py` (typed path): `profection(asc_lon,
  birth_date, target_date)` → `{age, profected_sign, profected_house,
  time_lord, lord_sign, lord_dignity}`. Whole-sign houses assumed and
  stated. Traditional domicile rulers only.
- Essential dignity of the lord: domicile / exaltation / detriment /
  fall / peregrine, from traditional tables in the module (small,
  sourced as traditional).
- CLI: `profection --load NAME --target-date YYYY-MM-DD` (or birth
  data), `--json`. Prints the year-wheel: age, profected sign/house,
  lord, lord's natal sign and dignity.

## Eldra
Build module + CLI. Birth date from --load request or --date; target
defaults to today.

## Sólrún (subagent verification)
`tests/test_profections.py`: Volmarr (ASC Libra, born 1972-09-01) at
2026-10-06 → age 54 → profected Scorpio, lord Mars; age 0 → Libra;
dignity table spot-checks (Mars in Scorpio = domicile). Full suite
green.

## Védis
COMMANDS.md section; `astroengine/INTERFACE.md` entry.

## Scribe
DEVLOG.md entry; TODO.md checkbox; README row.

## Acceptance gate
`profection --load volmarr --target-date 2026-10-23` names Scorpio and
Mars; suite green; pushed with verified remote HEAD.
