# O04 — Chinese zodiac astrology

Fourth slice of ROADMAP_ORACLES.md.

## Skald
The twelve earthly branches turn with Jupiter's twelve-year road;
the ten heavenly stems breathe the five phases twice. A year is
named by their meeting.

## Rúnhild
- `astroengine/chinese.py`: pure typed module (no legacy import).
  `zodiac(iso_date)` -> {animal, branch, stem, branch_element,
  stem_element, nayin, yin_yang, trine_allies, secret_friend,
  clash, year_starts (CNY date)}. Sexagenary anchor VERIFIED by
  computation: (year-4) mod 10 / mod 12 must yield Jia-Zi for 1984.
- Lunar New Year boundary via the `lunardate` package if it proves
  trustworthy (cross-check ~15 known CNY dates); otherwise an
  embedded verified table. No guessing.
- NaYin table transcribed from a published source and independently
  spot-checked, not recalled loosely.
- CLI: `chinese 1972-09-01` (ISO date; --json).
- Interpretive text labeled as such; the computation (stem/branch/
  allies/clash) is deterministic calendar math.

## Eldra
Build module + CLI.

## Sólrún (subagent verification)
`tests/test_chinese_zodiac.py`: 1984 -> Jia-Zi Wood Rat (yang);
2024 -> Jia-Chen Wood Dragon; boundary behavior (2024-02-09 is
Gui-Mao Water Rabbit, 2024-02-10 is Jia-Chen Wood Dragon);
2026-02-16 vs 2026-02-17 (Horse boundary); trine/secret/clash for
Rat; suite green.

## Védis
COMMANDS.md + INTERFACE.md.

## Scribe
DEVLOG.md, TODO.md, README row.

## Acceptance gate
`chinese 1972-09-01` names Volmarr a Ren-Zi Water Rat with correct
allies; suite green; pushed with verified remote HEAD.
