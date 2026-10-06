# R06 — The 28 Lunar Mansions

Slice R06 of ROADMAP_RUNIC.md. Standing law: six roles in order, push via
the PAT tool (no approval prompts). Merge-first: `git fetch` + diff before
every push; never overwrite Volmarr's edits; never force-push.

## Skald — vision and naming

Extend `astroengine/runic.py` with the lunar mansions (Ch. 7):

- `lunar_mansion(sidereal_longitude_deg)` — Moon's sidereal longitude →
  mansion (rune, Old Norse name, star).
- `lunar_mansions()` — the full 28-mansion table with segment bounds.

## Rúnhild — architecture

- The book (Ch. 7): 28 equal divisions of 12°51' (360/28), numbered with
  runes Feoh…Ear (Ior left out), each marked by a star; "early systems of
  lunar mansions began with the star Alcyone (η Tauri)".
- **Declared convention** (labeled as modern engine convention, not
  historical fact): 28 equal sidereal segments of 360/28 degrees;
  mansion 1 (Feoh, "Boars' Throng") begins at Alcyone's J2000 sidereal
  longitude **36.1175°** (Lahiri ayanamsa; derived from Alcyone J2000
  RA 3h47m24.3s Dec +24°06'18" → tropical 59.9746° − Lahiri 23.8571°).
  Stored as module constant `MANSION_ANCHOR_DEG`.
- `lunar_mansion(lon)`: normalizes lon with % 360; index =
  floor(((lon − anchor) % 360) / (360/28)); returns number, rune,
  northern_name, star, designation, segment [start, end) in sidereal
  degrees, anchor + method notes, source + historical_claim.
  Non-numeric lon → CalculationError.
- `lunar_mansions()`: all 28 with computed segment bounds.
- runic.py stays ephemeris-free: the caller supplies the sidereal
  longitude (the engine's lunar/vedic modules compute it). No corpus
  changes (R01 transcribed all 28).

## Eldra — build

- Append `MANSION_ANCHOR_DEG`, the two functions, and `__all__` to
  `astroengine/runic.py`.

## Sólrún — verification

New `tests/test_runic_mansions.py`:

- `lunar_mansion(36.1175)` → mansion 1, Feoh, "Boars' Throng", Alcyone.
- `lunar_mansion(48.9747)` → mansion 2, Ur, "The Follower", Aldebaran.
- `lunar_mansion(36.0)` → mansion 28, Ear, "The Last Ones" (wrap).
- `lunar_mansion(370.0)` normalizes like 10.0; 28 segment bounds tile
  [anchor, anchor+360) exactly; `lunar_mansions()` returns 28 rows.
- Non-numeric ("full") → CalculationError.
- Full suite green.

## Védis — cartography

- `astroengine/INTERFACE.md`: "Lunar mansions (R06)" incl. the contrast
  note vs. Vedic nakshatras: nakshatras are 27 (28 with Abhijit), anchored
  at 0° sidereal Aries (Ashwini); Pennick's are 28 equal segments anchored
  at Alcyone — different zero point, different count convention, both
  "lunar zodiacs" in their own traditions. Computation only, no synthesis
  of the two systems.
- COMPONENT_INDEX.md: extend runic.py line.

## Scribe — memory

- DEVLOG.md entry; TODO.md R06 checkbox; this task file as work order.
- **Push** task doc BEFORE code; push slice after green; verify remote
  HEAD; sync local clone.

## Acceptance gate

Mansion fixtures green incl. Alcyone anchor and wrap; docs carry the
declared-convention label and the nakshatra contrast note; pushed with
verified remote HEAD. Then R07.
