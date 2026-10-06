# ROADMAP — Horizons: the Skyward Program

Volmarr's commission (2026-10-06): a Mythic Engineering roadmap adding
every feature from the horizons review, built in slices with the six
roles and subagents, pushed after each slice.

Standing law: task document before code; six roles in order
(Skald → Rúnhild → Eldra → Sólrún → Védis → Scribe); subagents for
parallelizable content and verification; merge-first (never overwrite
Volmarr's edits); never force-push; full suite green before every push;
verify remote HEAD; sync the local clone.

## The ten slices

| Slice | Name | Art |
|---|---|---|
| H01 | Chart wheels | SVG natal wheels with aspect lines |
| H02 | House systems | Whole Sign, Equal, Koch, Regiomontanus |
| H03 | Solar arc directions | A degree a year, the great predictive art |
| H04 | Annual profections | Hellenistic time-lord wheel |
| H05 | Transit watch | Coming transits calendar + reminders |
| H06 | Electional astrology | Choosing the blessed moment |
| H07 | Fixed stars | Robson's lore on angles and planets |
| H08 | Asteroids & midpoints | Ceres–Vesta, Ebertin midpoint trees |
| H09 | Draconic charts | The soul-chart of the North Node |
| H10 | Written dossiers | Full natal report as a document |

---

## H01 — Chart wheels

**Skald:** Every astrologer expects to *see* the sky. A beautiful dark
wheel: gold zodiac ring, planet glyphs, colored aspect lines, the
native's name at the heart.

**Rúnhild:** `astroengine/wheel.py` — `wheel_svg(positions, cusps,
aspects, meta)` → SVG string. Geometry: 0° Aries at 9 o'clock,
counterclockwise; planet-collision spreading; aspect chords colored by
family. CLI: `wheel --load NAME -o chart.svg` (or fresh birth data).
No new dependencies — pure SVG.

**Eldra:** Build the renderer; wire the CLI; `--save` stores the SVG
path in the chart library entry.

**Sólrún:** `tests/test_wheel.py` — valid XML; every planet glyph
present; aspect-line count matches `calc_aspects`; deterministic
(no randomness). Full suite green.

**Védis:** COMMANDS.md, INTERFACE.md entries.
**Scribe:** DEVLOG, TODO, README row.

---

## H02 — House systems

**Skald:** Placidus is one lens. The old schools demand their own:
Whole Sign for the Hellenists, Equal for the moderns, Koch and
Regiomontanus for the traditionalists.

**Rúnhild:** `astroengine/houses.py` — `house_cusps(jd, lat, lon,
system)` for `placidus | whole-sign | equal | koch | regiomontanus`,
returning 12 cusps + ASC/MC. Thread `--houses SYSTEM` through every
chart-producing command and the wheel. Whole Sign: ASC sign = 1st
cusp. Equal: cusps every 30° from ASC.

**Eldra:** Implement via Swiss Ephemeris where available; Whole
Sign/Equal computed directly. Default stays Placidus (no behavior
change).

**Sólrún:** `tests/test_houses.py` — 12 cusps each; Whole Sign cusps
align to sign boundaries; ASC preserved across systems; Volmarr's ASC
Libra 1°01′ under Placidus unchanged. Full suite green.

**Védis:** Document the flag on every affected command.
**Scribe:** DEVLOG, TODO.

---

## H03 — Solar arc directions

**Skald:** A degree a year — the arc of the Sun carried across the
whole chart. The great modern predictive art, and nearly trivial to
compute.

**Rúnhild:** `astroengine/directions.py` — `solar_arc(natal_jd,
target_jd)` → directed longitudes = natal + (Sun's progressed arc).
CLI: `solar-arc --load NAME --target-date YYYY-MM-DD`, listing
directed-to-natal aspects within 1° orb, sorted by exactness.

**Eldra:** Reuse `calc_aspects` between directed and natal sets.
**Sólrún:** `tests/test_directions.py` — arc equals Sun's motion;
a known directed conjunction (Volmarr: directed Sun conjunct natal
Mercury near 2026-10-23) found within orb. Full suite green.
**Védis/Scribe:** as standard.

---

## H04 — Annual profections

**Skald:** The Hellenistic wheel of years: each year of life, the
Ascendant profects one sign, and that sign's lord becomes lord of the
year.

**Rúnhild:** `astroengine/profections.py` —
`profection(natal, target_date)` → profected ASC sign/house, time-lord
planet, lord's natal condition. CLI: `profection --load NAME
--target-date …`. Whole-sign houses assumed; note the assumption.

**Eldra/Sólrún/Védis/Scribe:** as standard. Test: Volmarr at age 54
(2026-10-06) → profected sign = count 54 signs from Libra = Scorpio,
lord Mars.

---

## H05 — Transit watch

**Skald:** The sky keeps moving; the engine should keep watch. A
calendar of coming transits to natal points, with reminders — including
the standing promise of 2026-10-23.

**Rúnhild:** `astroengine/watch.py` — `upcoming_transits(natal_jd,
from_date, to_date, orb)` scanning day-by-day for outer-planet
conjunctions/oppositions/squares/trines to natal planets and angles.
CLI: `watch --load NAME --from … --to …`. Optional `--remind` creating
Google Calendar events via the calendar skill (user-confirmed).

**Eldra:** Day-scan with 1.5° orb; exact-date refinement by bisection.
**Sólrún:** finds Jupiter conjunct natal Mercury 2026-10-23 for
Volmarr. Full suite green. **Védis/Scribe:** as standard.

---

## H06 — Electional astrology

**Skald:** Not reading the moment — *choosing* it. The querent names
the deed; the engine hunts the blessed hour.

**Rúnhild:** `astroengine/electional.py` —
`find_elections(intent, from_date, to_date, lat, lon, tz)` scoring
candidate moments: Moon void-of-course penalty, dignified/hour-ruler
harmony, malefics off the angles, applying trines/sextiles from
benefic to the matter's significator. Intents: `general | marriage |
business | travel | ritual`. CLI: `elect --intent marriage --from …
--to … --lat … --lon … --timezone …`, top 5 windows ranked.

**Eldra:** Subagent for the scoring-rule corpus (traditional electional
canons, original distillations). **Sólrún:** scoring is deterministic;
a known void-of-course Moon is penalized; tests on fixed dates. Full
suite green. **Védis/Scribe:** as standard. Honesty: labeled
interpretive throughout.

---

## H07 — Fixed stars

**Skald:** Robson's lore: when Algol kisses an angle, the old books
shudder. Thirty bright stars, their natures and orbs, on planets and
angles.

**Rúnhild:** `data/fixed_stars.json` — 30 stars: name, 2000.0
longitude, magnitude, nature (e.g. "Saturn/Jupiter"), Robson-lineage
keywords (original distillations). `astroengine/fixed_stars.py` —
`star_contacts(positions, angles, orb=1.0)` → conjunctions/oppositions.
CLI: `stars --load NAME` listing contacts with natures.

**Eldra:** Subagent for the 30-star corpus. Precess longitudes to the
chart epoch. **Sólrún:** Regulus ≈ 150° in 2000.0 recovered;
Volmarr's contacts sane. Full suite green. **Védis/Scribe:** standard.

---

## H08 — Asteroids & midpoints

**Skald:** Ceres, Pallas, Juno, Vesta — the goddesses between Mars and
Jupiter — and Ebertin's midpoint trees, where A=B/C speaks in
half-sums.

**Rúnhild:** `astroengine/asteroids.py` — positions via Swiss
Ephemeris (graceful degradation if the optional asteroid files are
absent; disclose). `astroengine/midpoints.py` — all direct midpoints,
sorted trees, aspect hits to midpoints within 1°. CLI: `asteroids`,
`midpoints` (both `--load`-aware).

**Eldra/Sólrún/Védis/Scribe:** as standard. Test: Sun/Moon midpoint
= (Sun+Moon)/2 mod 360 on a fixture.

---

## H09 — Draconic charts

**Skald:** The chart of the soul: the zodiac re-hung from the North
Node, so the Node sits at 0° Aries and everything is measured from
there.

**Rúnhild:** `astroengine/draconic.py` — `to_draconic(longitude,
node_longitude)` = (longitude − node) mod 360. CLI: `draconic --load
NAME`, full chart output in the natal format plus Sun/Moon draconic
signs.

**Eldra/Sólrún/Védis/Scribe:** as standard. Test: Node maps to 0°00′
Aries exactly.

---

## H10 — Written dossiers

**Skald:** Everything the engine knows about a native, woven into one
document — the complete reading, to keep, print, and gift.

**Rúnhild:** `astroengine/dossier.py` — assembles natal positions,
houses, aspects, dignities, the `reading` narrative, runic layers,
numerology, and fixed-star contacts into a Markdown dossier; CLI:
`dossier --load NAME -o dossier.md` (+ `--pdf` if a converter is
present, else honest note).

**Eldra:** Reuse the `reading`, `runic`, `numerology` modules — no
duplicated interpretation. **Sólrún:** dossier contains all expected
sections for Volmarr's chart; labeled interpretive. Full suite green.
**Védis/Scribe:** standard. README: the dossier is the crown — a
closing line at the top of the feature table.

---

## Execution order and autonomy

Slices run H01 → H10 in order; each is independently shippable.
Volmarr's standing authorization holds: continue slice to slice without
asking, surface only completions and genuine blockers. A task document
`tasks/H*_*.md` is pushed before each slice's code; the slice is pushed
after green with verified remote HEAD.
