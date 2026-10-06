# Roadmap — Vistara: Vargas Expansion & the Daily Forecast

Two commissions from Volmarr, 2026-10-06, built with Mythic
Engineering (Skald → Rúnhild → Eldra → Sólrún → Védis → Scribe),
task doc pushed before code, Sólrún subagent verification per
slice, push with verified remote HEAD after each slice.

## Part I — All the Vargas (V01)

The engine holds the 16 classical vargas (Shodasha-varga). "All"
means the extended set the traditions actually use:

- **V01 — Extended divisional charts**: D5 Panchamsha, D6
  Shashthamsha, D8 Ashtamsha, D11 Ekadashamsha. Their computation
  rules are less standardized than the 16 — research from BPHS /
  Jataka Chandrika / Saravali lineages, disclose variants, never
  present one school's rule as the only rule. Extend
  `data/vargas.json` + `vargas --divisions`, tests with hand-worked
  fixtures.

## Part II — The Daily Forecast (F01–F03)

- **F01 — `forecast` core**: one command taking birth data
  (`--date/--time/--lat/--lon/--timezone`, `--load` aware) and a
  target `--on` date. It gathers, for that day: Western transits to
  the natal chart (exact-day aspects, stations, ingresses),
  Vimshottari dasha position, panchanga (tithi, vara, nakshatra,
  yoga, karana), BaZi day pillar and its stem-branch relations to
  the four natal pillars, Tibetan daily mewa/parkha against the
  natal forces, the runic half-month and runic hour, and the day's
  Chinese zodiac animal relations (clash/harmony) to the birth
  animal. Computation stays computation; the reading is labeled
  interpretive.
- **F02 — Remedial Vedic mantras**: `data/mantras.json` — planet →
  traditional mantra (Gayatri for Sun, Shani Gayatri, Navagraha
  set, etc., all public-domain ancient verses). The forecast
  recommends mantras from the day's afflictions: planets the day's
  transits stress, the dasha lord, Saturn/Rahu/Ketu pressure.
  Presented as devotional practice, never medical or guaranteed
  remedy. Transliteration + deity + planet included.
- **F03 — Polish sweep**: every remaining polish idea — help-text
  consistency, JSON parity across the new commands, capability
  evidence strings, and anything Sólrún's earlier advisories left
  open.

## Standing rules

Same as the Oracles program: fetch+diff before every push, never
overwrite Volmarr's edits, never force-push, typed modules only,
explicit errors, offline tests with IANA zones, computation apart
from interpretation.
