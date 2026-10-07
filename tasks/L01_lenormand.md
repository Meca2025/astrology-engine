# L01 — Lenormand cartomancy (`lenormand` command)

**Status:** proposed 2026-10-07 · **Owner:** Yrsa (Mythic Engineering, all six roles, sequential)
**Commission:** Volmarr, 2026-10-07 — "go for adding that to the astrology engine"
(muse: Isabella Rotman's *Might Hurt Lenormand* Kickstarter launch; Lenormand is
the one classic cartomancy system the engine's divination line lacks).

## Goal

Add a complete, traditional Petit Lenormand system to the engine as a new CLI
subcommand `lenormand`, following the established divination-line pattern
(`tarot`, `runecast`, `iching`, `numerology`, `reading`): corpus in
`data/`, typed module in `astroengine/`, seeded reproducible draws, text + JSON
output, offline tests. CLI-only (no agent tool), like its divination siblings.

## Lineage and honesty

- The 36-card Petit Lenormand is 19th-century European folk cartomancy
  (Marie Anne Lenormand namesake tradition). Card meanings here are the
  **traditional shared folk meanings**, written fresh; no modern author's
  copyrighted text is reproduced.
- Lenormand is read in **combination**: pairs and chains carry the sentence.
  Single-card keywords are given, but the module foregrounds pair fusion.
- Grand Tableau houses, knighting, and mirroring are traditional techniques,
  implemented as documented geometric rules — the *interpretation* they yield
  is symbolic counsel, never computed fact. Keep computation and
  interpretation separate per project law.

## Data — `data/lenormand.json` (new, immutable)

36 cards in traditional order, each:

```json
{
  "number": 1,
  "name": "Rider",
  "playing_card": "9 of Hearts",
  "keywords": ["news", "messages", "visitors", "speed"],
  "meaning": "Swift incoming news or a visitor; energy arriving at pace.",
  "timing": "fast — days"
}
```

Fields: `number`, `name`, `playing_card` (French-suited insert, traditional),
`keywords` (3–5), `meaning` (one fresh traditional sentence), `timing`
(traditional timing note: fast/slow + unit where the tradition assigns one).
Significators: 28 Man, 29 Woman.

## Module — `astroengine/lenormand.py` (new, typed)

Public API:

- `cards() -> list[dict]` — the 36-card deck in order (lru-cached corpus).
- `spreads() -> dict[str, list[str]]` — spread name → position names.
- `draw(spread="line3", seed=None, question=None) -> dict` — shuffle with
  `random.Random(seed)`; same seed → same draw. Positions:
  - `single`: ["The Card"] (daily card)
  - `line3`: ["Past", "Present", "Future"]
  - `line5`: ["Past", "Present", "Bridge", "Near Future", "Outcome"]
  - `line7`: ["Distant Past", "Past", "Present", "Near Future",
    "Outcome", "Advice", "Long-term Result"]
  - `nine`: 3×3 square, center position named "Focus — the heart of the matter"
  - `tableau`: Grand Tableau, all 36 cards (see below)
- `pair_reading(a, b) -> str` — fuse two cards: "{A} + {B}: {keyword-a} {verb} {keyword-b}"
  style sentence from corpus keywords (no invented lore; mechanical fusion,
  labeled interpretive).
- `chain(cards) -> list[str]` — pair-wise chain for line spreads.
- `tableau(seed=None, question=None, significator="woman") -> dict` —
  4 rows × 9 grid; each cell: card + house (position N sits in the house of
  card N, e.g. position 24 = House of the Heart). Returns:
  - `grid`: 36 cells in row-major order with `position` (1–36), `row`, `col`,
    `card`, `house` (house card name + domain keywords)
  - `significator`: card 28/29, its position, row, col
  - `knighting`: cards a chess-knight's move from the significator
  - `mirroring`: pairs at positions (i, 37−i) — cards mirroring each other
  - `corners`: the four corner cards (overall theme)
  - `fate_line`: the row containing the significator (the "fate line")
- Unknown spread → `CalculationError` naming available spreads (recovery
  `suggest()` integration for near-miss spread names, per S01).

Lenormand traditionally has **no reversals** — do not implement reversals.

## CLI — `astrology_engine.py`

- `sub.add_parser("lenormand", help="Lenormand card reading with classic spreads")`
- Flags: `--spread` (default `line3`), `--list-spreads`, `--seed int`,
  `--question str`, `--significator {man,woman}` (default `woman`),
  `--json`, `add_chart_lib(..., with_load=False)`.
- `cmd_lenormand(args)`: text mode prints header, question, each position with
  card + keywords + meaning, pair chain for line spreads, tableau summary
  (significator location, knighting, mirroring, corners); closes with the
  standard "Interpretive — symbolic counsel, not computed fact." line.
- Dispatch entry in the command map. Pre-dispatch healing (S01) needs no
  changes: no date/time/geo inputs.

## Registration and docs

- `COMMANDS.md`: add `## lenormand` section with examples.
- `README.md`: subcommand count 45 → 46 (three spots), add table row.
- `SKILL.md`: check whether divination commands are listed; if the file
  covers the divination line, add `lenormand` consistently (tarot/runecast are
  absent from SKILL.md as of 2026-10-07 — match existing coverage, do not
  expand scope).
- No capability/agent-tool changes: divination line is CLI-only by established
  pattern.

## Tests — `tests/test_lenormand.py` (new, offline)

- Corpus: 36 cards, numbers 1–36 unique, every card has number/name/
  playing_card/keywords/meaning/timing; significators are 28/29.
- Seeded determinism: `draw(seed=7)` twice → identical.
- No duplicate cards within any single draw; tableau contains all 36 exactly once.
- Spread position counts: single 1, line3 3, line5 5, line7 7, nine 9.
- Tableau geometry: 4×9; cell (row, col) ↔ position mapping correct;
  house of position N is card N.
- Knighting: from a known significator position, knight-move cells match
  hand-computed set (fixture).
- Mirroring: pairs (i, 37−i) for i in 1..18.
- Unknown spread raises `CalculationError`.
- CLI smoke: `lenormand --spread line3 --seed 7 --json` parses as JSON.

## Acceptance

- `python astrology_engine.py lenormand --spread tableau --seed 7 --significator woman`
  prints a full Grand Tableau with houses, knighting, mirroring, corners.
- Full suite green; push task doc first, then implementation; verify remote HEAD.

## Mythic Engineering roles

- **Skald** — vision: the missing cartomancy seat at the divination table.
- **Rúnhild** — architecture above.
- **Eldra** — implementation.
- **Sólrún** — verification: seeded fixtures, hand-checked knighting set.
- **Védis** — interface: CLI flags, COMMANDS.md, README, SKILL.md.
- **Scribe** — this doc, DEVLOG entry.
