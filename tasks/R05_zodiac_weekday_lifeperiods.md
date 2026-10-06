# R05 — Zodiacal, Weekday, and Life-Period Layers

Slice R05 of ROADMAP_RUNIC.md. Standing law: six roles in order, push after
the slice via the PAT tool (`~/workspace/skills/github-pat/bin/gh-pat-push`;
no approval prompts). Merge-first rule: `git fetch` + diff before every
push; never overwrite Volmarr's own edits (esp. README.md); never
force-push.

## Skald — vision and naming

Extend `astroengine/runic.py` with the sign/day/age layers:

- `zodiac_rune(sign, variant="classical")` — App. 5 correspondences.
- `weekday_rune(weekday)` — App. 4 correspondences.
- `life_period(age_years)` — Ch. 6 planetary life-periods.
- `metonic_cycle(year)` — Ch. 6 Golden Number / 19-year cycle position.

## Rúnhild — architecture

- `zodiac_rune`: case-insensitive sign name; returns rune, deity, planet,
  day, stone, animal, variant. Capricorn/Aquarius/Pisces have two rows
  ("classical", "modern alternative"); other signs have one. Unknown sign
  or variant → CalculationError. Result labeled with variant + source +
  historical_claim.
- `weekday_rune`: case-insensitive English weekday → deity, planet, rune,
  tree, herb, element, esoteric number, magic square. Unknown → error.
- `life_period`: float age in years; finds the period with
  start_age <= age < end_age (Máni 0–4 … Loki 68–98). Returns deity,
  planet, years elapsed in period, years remaining, period index. Age < 0
  or >= 98 → CalculationError (the book's wheel ends at 98).
- `metonic_cycle`: Golden Number = (year % 19) + 1; also years elapsed in
  the current 19-year cycle and the Aun 310-year recalibration note. Pure
  calendrical computation (the book's own framing); no ephemeris in
  runic.py (kept ephemeris-free by R02 design).
- All JSON-safe; reuse `_corpus()` and CalculationError.

## Eldra — build

- Append the four functions + `__all__` to `astroengine/runic.py`. No
  corpus changes needed (R01 already transcribed App. 4/5 and Ch. 6).

## Sólrún — verification

New `tests/test_runic_layers.py`:

- `zodiac_rune("Aries")` → rune Eh, deity Tyr (classical).
- `zodiac_rune("Pisces", "modern alternative")` → deity Aegir; classical →
  Thor. Unknown variant → CalculationError.
- `weekday_rune("Wednesday")` → Odin/Mercury; check tree/herb/element
  present.
- `life_period(22)` → Sól begins (years elapsed 0); `life_period(68)` →
  Loki begins; `life_period(54.5)` → Tyr, 13.5 elapsed, 1.5 remaining;
  `life_period(98)` and `(-1)` → CalculationError.
- `metonic_cycle(2000)` → golden number 6 (known reference);
  `metonic_cycle(2026)` → 13; periodicity: GN(y) == GN(y+19).
- Ephemeris cross-check (the roadmap gate): with pyswisseph, find the full
  moon nearest Jan 15 in 2007 and in 2026 (19 years apart); assert the two
  month-days are within 2 days — the Metonic recurrence the book describes.
  Keep it to these two dates so the suite stays fast.
- Full suite green.

## Védis — cartography

- `astroengine/INTERFACE.md`: "Zodiac, weekday, life-periods (R05)".
- COMPONENT_INDEX.md: extend runic.py line.

## Scribe — memory

- DEVLOG.md entry; TODO.md R05 checkbox; this task file as work order.
- **Push** task doc BEFORE code (PAT tool); push slice after green; verify
  remote HEAD (`git ls-remote`); sync local clone (`git fetch` + merge —
  never clobber).

## Acceptance gate

Sign/day/age layers reproduce App. 4/5 and Ch. 6 fixtures; Metonic
periodicity + ephemeris cross-check green; docs updated; pushed with
verified remote HEAD. Then R06.
