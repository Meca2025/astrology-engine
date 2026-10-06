# V01 — Extended divisional charts (D5, D6, D8, D11)

First slice of ROADMAP_VISTARA.md.

## Skald
Sixteen vargas were the classical canon. But the almanacs whisper
of more: the fifth for merit, the sixth for illness, the eighth
for the sudden hand of fate, the eleventh for gains.

## Rúnhild
- Research the computation rules for D5 Panchamsha, D6
  Shashthamsha, D8 Ashtamsha, D11 Ekadashamsha from classical
  sources (BPHS, Jataka Chandrika, Saravali commentaries).
  These are LESS standardized than the 16 — where schools differ,
  implement the best-attested rule and disclose the variant.
- Extend `data/vargas.json` `divisions` with 5, 6, 8, 11 (names,
  spans, counting rules, significations, sources).
- Extend the varga computation in `astroengine/vargas.py` (check
  how it generalizes — it may already be formula-driven).
- `vargas --divisions 5 6 8 11` works; `--divisions` with no args
  (or `all`) includes the extended set.
- No changes to the existing 16 — regression-tested.

## Eldra
Research first, then extend data + computation.

## Sólrún (subagent verification)
`tests/test_vargas_extended.py`: hand-worked fixtures for each new
division (compute expected signs by hand from the documented rule
for 2-3 longitudes each, incl. an even sign and an odd sign);
existing 16 vargas regression green; suite green.

## Védis
INTERFACE.md entry update; COMMANDS.md `vargas` section note.

## Scribe
DEVLOG.md, TODO.md.

## Acceptance gate
`vargas --divisions 5 6 8 11` for Volmarr matches hand computation;
suite green; pushed with verified remote HEAD.
