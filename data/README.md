# data

Read-only versioned capability and tradition rules. Runtime consumers return fresh snapshots; never rewrite base data.

Follow root RULES.AI.md and the relevant task before changing this folder.

legacy_astronomy.json owns legacy required/optional bodies, frame defaults and
ordered solar-event search settings; this is packaged with the other JSON resources.

runic.json owns the Northern runic-astrology corpus (R01, ROADMAP_RUNIC.md):
32 runes with correspondences, 24 runic half-months, 24 runic hours,
7x24 Northern planetary hours, weekday/zodiac correspondences, 8 day tides,
28 lunar mansions, 12 Grímnismál palaces, 9 worlds, 7 planetary life-periods.
Source: Pennick (2023); historical_claim: modern synthesis. Print quirks are
recorded in per-section notes, never silently corrected. Related in kind to
vedic.json (28 mansions vs nakshatras) but distinct in definition.
