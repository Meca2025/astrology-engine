# R07 — Twelve Palaces and Nine Worlds

Slice R07 of ROADMAP_RUNIC.md. Standing law: six roles in order, push via
the PAT tool. Merge-first: `git fetch` + diff before every push; never
overwrite Volmarr's edits; never force-push.

## Skald — vision and naming

Extend `astroengine/runic.py` with the two correspondence overlays:

- `grimnismal_palace(sign)` — zodiac sign → Grímnismál palace (App. 7).
- `world_rune(world)` / `nine_worlds()` — Nine Worlds ↔ runes (Ch. 6).

## Rúnhild — architecture

- Both are FIXED lookup tables transcribed in R01 — no computation, pure
  overlay. Per the roadmap and the standing computation/interpretation
  split, results carry `"kind": "correspondence overlay"` (not a computed
  quantity) alongside source + historical_claim.
- `grimnismal_palace`: case-insensitive sign → palace, meaning, deity.
  Unknown sign → CalculationError.
- `world_rune`: case-insensitive world name → rune. Unknown → error.
- `nine_worlds()`: the full ordered list of 9 world/rune pairs.
- No corpus changes.

## Eldra — build

- Append the three functions + `__all__` to `astroengine/runic.py`.

## Sólrún — verification

New `tests/test_runic_palaces.py`:

- `grimnismal_palace("Aries")` → Bilskírnir / Thor / "Lightning";
  `grimnismal_palace("Pisces")` → Noatún (the gate's endpoints);
  all 12 signs resolve, each with palace+meaning+deity.
- `world_rune("Asgard")` → Gyfu; `nine_worlds()` → 9 pairs, first
  Asgard/Gyfu, last Helheim/Hagal; unknown world → CalculationError.
- Full suite green.

## Védis — cartography

- `astroengine/INTERFACE.md`: "Palaces and worlds (R07)" — labeled as
  correspondence overlays, not computed quantities.
- COMPONENT_INDEX.md: extend runic.py line.

## Scribe — memory

- DEVLOG.md entry; TODO.md R07 checkbox; this task file as work order.
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

Fixed-mapping fixtures green; overlays labeled as overlays; pushed with
verified remote HEAD. Then R08.
