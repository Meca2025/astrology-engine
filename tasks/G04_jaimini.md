# G04 — Jaimini foundations: karakas, arudha padas, Chara dasha

Final slice of ROADMAP_GAMBHIRA.md.

## Skald
The other great school knocks. Jaimini counts not by stars but
by signs — karakas by degree, reflections of houses, dashas that
run forward or backward as the ninth house decrees.

## Rúnhild
- `data/jaimini.json`: karaka order, Arudha Pada method
  (Jaimini 1.1.30-32 with the 1st/7th → 10th exceptions), Chara
  dasha rules (start from Lagna; direction by 9th-from-Lagna
  odd/even; years = forward count from sign to lord minus one,
  12 if lord in own sign), all variants disclosed (7th→10
  special case, odd/even lord counting, start-from-7th,
  Rahu/Ketu co-lordships).
- `astroengine/jaimini.py`:
  - `chara_karakas(request)`: Sun..Saturn by intra-sign
    longitude, descending — Atmakaraka → Darakaraka.
  - `arudha_padas(request)`: all twelve padas, whole-sign.
  - `chara_dasha(request)`: sign sequence with years, current
    mahadasha + antardasha (12 equal sub-periods from the
    dasha sign, same direction).
  - Never mixed silently with Parashari timing; labeled
    "Jaimini school" throughout.
- `jaimini` CLI: birth-data flags, `--load` aware, text + `--json`.

## Eldra
Task doc first (done), then data, module, CLI.

## Sólrún (subagent verification)
`tests/test_jaimini.py`: Volmarr's karakas in hand-verified order
(Mars AK 27.77° → Mercury DK 5.09°); Arudha Lagna = Taurus;
Chara starts at Virgo running backward (9th-from-Lagna Taurus
even); Virgo dasha years = 10 (Mercury in Cancer, forward count
11 minus 1); antardashas 12 × 1/12; suite green.

## Védis
INTERFACE.md, COMMANDS.md entries.

## Scribe
DEVLOG.md; ROADMAP_GAMBHIRA.md marked complete.

## Acceptance gate
Hand-verified fixtures green; suite green; pushed with verified
remote HEAD.
