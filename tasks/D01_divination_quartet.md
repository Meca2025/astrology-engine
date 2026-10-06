# Divination Quartet — Tarot, Astrology Readings, Numerology, I-Ching

Volmarr's commission (2026-10-06): *"now seperately make tarot and
astrology reading.. both with a whole bunch of possible layouts to use..
and numerology readings.. and i-ching"*.

Four standalone divination systems, each its own module + CLI command,
built to the same honesty standard as the runic program: everything
labeled `interpretive` / symbolic, nothing presented as computed fact.

Standing law: six Mythic Engineering roles in order; push via the PAT
tool; merge-first (never overwrite Volmarr's edits); never force-push.

## Skald — vision and naming

| Command | Art |
|---|---|
| `tarot` | 78-card deck, 10 spreads, reversals, seeded draws |
| `reading` | Astrology interpretation from a chart: general / love / career layouts |
| `numerology` | Life Path, Destiny, Soul Urge, Personality, Birthday, Personal Year |
| `iching` | 64 hexagrams, coin/yarrow casting, changing lines |

## Rúnhild — architecture

### Tarot (`astroengine/tarot.py`, `data/tarot.json`)
- `data/tarot.json`: 78 cards. Major Arcana: number 0–21, name, upright
  {keywords, meaning}, reversed {keywords, meaning}. Minor: suit
  (Wands/Cups/Swords/Pentacles), rank (Ace–10, Page/Knight/Queen/King),
  same meaning structure. Meanings are original one-line distillations
  in the Rider-Waite-Smith lineage, labeled modern synthesis.
- Spreads (10): `single`, `three` (past/present/future), `five-cross`,
  `celtic-cross` (10), `horseshoe` (7), `relationship` (7),
  `career` (5), `choice` (7), `year-ahead` (12), `chakra` (7).
  Each: ordered position names + position meanings.
- `draw(spread, seed=None, reversals=True)` → seeded `random.Random`;
  returns cards with orientation; JSON-safe. Same seed → same draw
  (reproducibility is a feature, stated in docs).

### Astrology reading (`astroengine/readings.py`)
- `chart_reading(kind, positions, ...)` — kinds: `general`, `love`,
  `career`. Consumes a positions dict (+houses/angles when available).
- Template-based paragraphs, all tagged interpretive: elemental
  temperament; Sun/Moon/Ascendant sign paragraphs (12 signs × 3
  luminaries, compact original text); tightest major aspects (top 5 by
  orb) with cookbook lines; strongest dignity notes. Love layout
  foregrounds Venus/Moon/7th-house; career foregrounds MC/Saturn/
  10th-house and Sun purpose.
- Input: `--load NAME` chart or explicit birth data (reuse the chart
  library!). Never fabricates positions — it reads a computed chart.

### Numerology (`astroengine/numerology.py`)
- Pythagorean values (A=1…I=9, J=1…R=9, S=1…Z=9).
- `life_path(date)` — digit sum, master numbers 11/22/33 held.
- `destiny(name)`, `soul_urge(name)` (vowels; Y rules), `personality`
  (consonants), `birthday(date)`, `personal_year(date)`.
- `data/numerology.json`: meanings for 1–9, 11, 22, 33 (original
  distillations).
- CLI: `numerology --date 1972-09-01 --name "Volmarr Goði"`.

### I-Ching (`astroengine/iching.py`, `data/iching.json`)
- `data/iching.json`: 64 hexagrams {number, name, chinese, judgment,
  meaning} — original brief renderings in the classical lineage (not
  copied from any copyrighted translation), labeled accordingly.
- Casting: coin method (3 coins × 6 lines, 6/7/8/9 values) and yarrow
  simulation (statistically equivalent distribution); changing lines →
  relating hexagram. `--method coins|yarrow`, `--seed`.
- `cast(question=None, method="coins", seed=None)` → primary hexagram,
  changing lines, relating hexagram (or None), full JSON-safe reading.

## Eldra — build

- Two content subagents (tarot.json, iching.json) in parallel; engines +
  numerology data by hand; CLI wiring; `--save` on all four (they
  produce charts-of-a-kind — save the reading).

## Sólrún — verification

- `tests/test_tarot.py`: 78 cards load; every spread's positions unique
  and covered; seeded draw reproducible; reversals flag honored.
- `tests/test_numerology.py`: Volmarr's Life Path = 9 (1+9+7+2+9+1=29→11?
  recompute: 1972-09-01 → 1+9+7+2+0+9+0+1=29 → 2+9=11 master) — assert 11;
  master numbers held; personal year formula.
- `tests/test_iching.py`: coin distribution sanity (old yin/yang occur);
  changing lines produce a valid relating hexagram; 64 entries.
- `tests/test_readings.py`: reading consumes Volmarr's saved chart data
  shape; all paragraphs tagged interpretive; love layout mentions Venus.
- Full suite green.

## Védis — cartography

- `COMMANDS.md`: four sections; `astroengine/INTERFACE.md`: four
  entries; COMPONENT_INDEX.md lines.

## Scribe — memory

- DEVLOG.md entry; TODO.md checkboxes; this task file; README: one
  appended line under the subcommand table (Volmarr's territory —
  append only).
- **Push** task doc BEFORE code; push after green; verify remote HEAD;
  sync local clone.

## Acceptance gate

`tarot --spread celtic-cross`, `reading --load volmarr`,
`numerology --date … --name …`, `iching` all run end-to-end, text + JSON
where applicable; suite green; pushed with verified remote HEAD.
