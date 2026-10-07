# C01 — Playing-card cartomancy (`cartomancy` command)

**Status:** proposed 2026-10-07 · **Owner:** Yrsa (Mythic Engineering, all six roles, sequential)
**Commission:** Volmarr, 2026-10-07 — "also my cutie add regular playing cards too!"

## Goal

Add traditional playing-card cartomancy (standard 52-card French deck) as a
new CLI subcommand `cartomancy`, completing the cartomancy seat beside
`tarot` and `lenormand` in the divination line. Same established pattern:
corpus in `data/`, typed module in `astroengine/`, seeded reproducible
draws, text + JSON output, offline tests, CLI-only (no agent tool).

## Lineage and honesty

- Playing-card fortune-telling is old European folk cartomancy; the card
  meanings here are the **traditional shared folk meanings** (suit domains +
  per-card keywords), written fresh for this corpus. No modern author's
  copyrighted text is reproduced.
- Like Lenormand, this tradition reads in **combination**: pairs and chains
  carry the sentence. The module foregrounds pair fusion.
- Suit domains (traditional): Hearts = love/emotions/home; Diamonds =
  money/material/enterprise; Clubs = work/action/ambition; Spades =
  challenges/obstacles/transformation. Labeled as traditional
  correspondence, computation kept separate from interpretation.

## Data — `data/playing_cards.json` (new, immutable)

52 cards, each:

```json
{
  "suit": "hearts",
  "rank": "ace",
  "name": "Ace of Hearts",
  "keywords": ["love", "new romance", "the home"],
  "meaning": "New love or deep affection; the heart of the home."
}
```

Fields: `suit` (hearts/diamonds/clubs/spades), `rank`
(ace/2..10/jack/queen/king), `name`, `keywords` (3), `meaning` (one fresh
traditional sentence). Top-level `suit_domains` maps each suit to its
traditional domain keywords. Top-level `lineage` + `version` as in
`data/lenormand.json`.

## Module — `astroengine/cartomancy.py` (new, typed)

Public API (mirrors `lenormand.py`):

- `cards() -> list[dict]` — 52 cards, suit-major order
  (hearts, diamonds, clubs, spades × ace..king), lru-cached corpus.
- `suits() -> dict` — suit → traditional domain keywords.
- `spreads() -> dict[str, list[str]]` — spread name → position names:
  - `single`: ["The Card"]
  - `line3`: ["Past", "Present", "Future"]
  - `line5`: ["Past", "Present", "Bridge", "Near Future", "Outcome"]
  - `line7`: ["Distant Past", "Past", "Present", "Near Future",
    "Outcome", "Advice", "Long-term Result"]
  - `nine`: 3×3, center = "Focus — the heart of the matter"
  - `fifteen`: three rows of five — "Past Row", "Present Row",
    "Future Row" (positions named e.g. "Past — 1" … "Future — 5")
- `draw(spread="line3", seed=None, question=None) -> dict` — seeded
  shuffle; same seed → same draw.
- `pair_reading(a, b) -> str` — mechanical keyword fusion, labeled
  interpretive (shared shape with Lenormand's; keep the two modules
  independent, no cross-imports).
- `chain(drawn) -> list[str]` — pair-wise chain.
- `suit_of(card)`, `is_court(card)` helpers for the CLI summary
  (dominant suit of the draw, courts present).
- Unknown spread → `CalculationError` with S01 `suggest()` hints.
- No reversals (folk playing-card tradition reads upright).

## CLI — `astrology_engine.py`

- `sub.add_parser("cartomancy", help="Playing-card cartomancy readings")`
- Flags: `--spread` (default `line3`), `--list-spreads`, `--seed int`,
  `--question str`, `--json`, `add_chart_lib(..., with_load=False)`.
- `cmd_cartomancy(args)`: header, question, per-position card + keywords +
  meaning, chain for multi-card draws, draw summary (dominant suit with
  domain, courts drawn); standard interpretive closing line.
- Dispatch entry in the command map. No date/time/geo inputs → S01
  pre-dispatch healing needs no changes.

## Registration and docs

- `COMMANDS.md`: add `## cartomancy` section with examples.
- `README.md`: subcommand count 46 → 47 (three spots), extend the
  divination table row.
- `SKILL.md`: divination line is absent from SKILL.md — match existing
  coverage, no change.
- No capability/agent-tool changes (divination line is CLI-only).

## Tests — `tests/test_cartomancy.py` (new, offline)

- Corpus: 52 cards; 4 suits × 13 ranks each; every card has
  suit/rank/name/keywords/meaning; names unique.
- Seeded determinism: `draw(seed=7)` twice → identical cards + chain.
- No duplicate cards within any draw.
- Spread position counts: 1/3/5/7/9/15.
- Suit helpers: `suits()` has 4 entries; `is_court` true exactly for
  J/Q/K; dominant-suit summary names a real suit.
- Unknown spread raises `CalculationError` (with suggestion hint).
- CLI smoke: `cartomancy --spread line3 --seed 7 --json` parses as JSON.

## Acceptance

- `python astrology_engine.py cartomancy --spread fifteen --seed 7`
  prints three labeled rows with chains.
- Full suite green; task doc pushed before implementation; verify remote HEAD.

## Mythic Engineering roles

- **Skald** — vision: the plain deck every sailor carried, now in the forge.
- **Rúnhild** — architecture above.
- **Eldra** — implementation.
- **Sólrún** — verification: seeded fixtures, suit/rank census.
- **Védis** — interface: CLI flags, COMMANDS.md, README.
- **Scribe** — this doc, DEVLOG entry.
