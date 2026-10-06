# S01 — Self-healing, error correction, robustness

Volmarr: "add self healing and error correction, and robustness to it."

## Skald
A good instrument forgives the hand that holds it. Typos in
timezones, dates in human words, a chart name half-remembered —
the engine should mend what it can, say plainly what it cannot,
and never die halfway through a reading.

## Rúnhild
- `astroengine/recovery.py`: the mending toolkit —
  - `heal_date` / `heal_time`: strict ISO first, then human
    forms ("Oct 7 2026", "7 Oct 2026", MM/DD/YYYY documented,
    "2026.10.07" / "8:18am", "8pm", "0818"). Returns
    (value, note); note logged, never silent.
  - `correct_timezone`: space→underscore, case-insensitive
    IANA match; suggestions on failure, never a blind guess
    (abbreviations like EST are ambiguous — suggested, not
    assumed).
  - `suggest`: difflib did-you-mean for house systems, zodiac,
    ayanamsa, node types, chart names.
  - `graceful(label, fn, ...)`: degradation wrapper returning
    ok/result or ok/error.
- Wiring:
  - `resolve_birth`: heal date/time/timezone before the strict
    path; notes to stderr.
  - `resolve_utc` (library): timezone correction so the
    healing works below the CLI too.
  - `validate_profile`: did-you-mean on unknown selections.
  - `load_chart`: "no saved chart" gains close matches.
  - `main()`: global `--debug`; unexpected exceptions become
    one clean stderr line (exit 3), traceback only with
    --debug; `--json` mode emits a JSON error object instead
    of plain text.
  - `daily_forecast`: optional systems (BaZi, Tibetan, runic,
    Jaimini) degrade to "unavailable: reason" notes instead of
    killing the whole reading; core (transits, panchanga,
    dasha) still raises.
  - `natal_dossier`: the Vedic Depths section degrades the
    same way.
- `run_tool` keeps raising CalculationError (tested contract);
  messages are now suggestion-rich.

## Eldra
recovery.py first, then wiring points one by one.

## Sólrún
`tests/test_recovery.py`: human dates/times heal; bad timezone
suggests; unknown house system suggests; missing chart suggests;
graceful() catches; forecast survives a broken optional system;
JSON error object shape; suite green.

## Védis
INTERFACE.md, COMMANDS.md entries.

## Scribe
DEVLOG.md.

## Acceptance gate
`astrology_engine.py yogas --date "Oct 7 2026" ...` heals;
`--timezone America/New_Yrok` suggests; full suite green;
pushed with verified remote HEAD.
