# Development log

## 2026-10-06 — orientation

Inspected remote `main` at `a76174d`. Existing local Ember copy belongs to a different
repository, so work uses a fresh clone of astrology-engine and leaves Ember alone.
Mapped 16 legacy CLI commands and found time-rollover/fallback/agent-contract gaps.
Added five-layer Mythic Engineering documentation and a dependency-ordered roadmap.
User authorized implementation/push loops; no repeated approval gate is needed.

## S01 — chart foundation

Implemented the typed/profile/data/provenance/CLI boundaries. 24 tests and wheel
resource check passed. UTC midnight and DST/polar failures are explicit. Existing
text commands preserved; their historical gaps remain separately documented.

## S02 — Jyotisha D1

Added data-defined navagraha/nakshatra profile and wired JSON command. All 34 tests
passed, including direct Lahiri house/position checks and 108 pada interiors.
Restored original ignore rules after detecting the initial ignore-file overwrite.

Hosted Windows S01/S02 jobs exposed cp1252 decoding in test subprocesses.
Explicit UTF-8 decoding and ASCII-safe JSON transport added; Linux/macOS
computation jobs passed. Follow-up acceptance awaits the repaired hosted matrix.

## S03 — classical vargas

Sixteen sign mappings wired through API/CLI. 78 total tests passed, including
source worked placements and D2/D30 boundaries. Documented D27 Example 23
counting error; calculation follows the stated rule. No physical longitudes
or exhaustive school coverage claimed.

## S04 — Vimshottari

87 total tests passed. Added maha/antar timeline, birth balance, three named year
clocks and as-of lookup. Example 50 balance matched; subperiods are anchored before
birth and exact boundary belongs to next period. Hosted repaired Windows matrix
passed together with Linux/macOS on Python 3.11/3.12.
