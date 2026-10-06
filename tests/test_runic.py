"""R01 — tests for data/runic.json (the Runic Corpus).

Every assertion is a book fixture from Nigel Pennick, 'Runes and Astrology'
(2023), or a structural count from the appendices. Honest-transcription
policy: tests pin the book as printed, including its quirks.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "runic.json"
CORPUS = json.loads(DATA.read_text(encoding="utf-8"))

FUTHARK = ["Feoh", "Ur", "Thorn", "As", "Rad", "Ken", "Gyfu", "Wyn",
           "Hagal", "Nyd", "Is", "Jera", "Eoh", "Peorth", "Elhaz", "Sigel",
           "Tyr", "Beorc", "Ehwaz", "Man", "Lagu", "Ing", "Odal", "Dag"]


def _by(key, field="name"):
    return {r[field]: r for r in CORPUS[key]}


def test_provenance_on_every_table():
    assert CORPUS["source"] == "Pennick (2023)"
    assert CORPUS["historical_claim"] == "modern synthesis"
    for section in ("planetary_hours", "mansions", "palaces", "worlds"):
        assert CORPUS[section]  # sections exist


def test_rune_counts():
    runes = CORPUS["runes"]
    assert len(runes) == 32
    elder = [r for r in runes if r["futhark"] == "elder"]
    adds = [r for r in runes if r["futhark"] == "anglo-saxon"]
    assert [r["name"] for r in elder] == FUTHARK
    assert len(adds) == 8
    assert {r["name"] for r in adds} == {
        "Ac", "Os", "Yr", "Ior", "Ear", "Cweorth", "Cale", "Stan"}


def test_rune_correspondence_spot_checks():
    by = _by("runes")
    assert by["Feoh"]["deity"] == "Frey/Freyja"
    assert by["Feoh"]["symbolic_meaning"] == "the primal cow, Audhumla"
    assert by["Sigel"]["color"] == "gold"
    assert by["Is"]["element"] == "ice"
    assert by["Ear"]["deity"] == "Hela"
    for r in CORPUS["runes"]:
        for field in ("tree", "herb", "color", "polarity", "element",
                      "deity", "symbolic_meaning"):
            assert r[field], f"{r['name']} missing {field}"


def test_half_months():
    hm = CORPUS["half_months"]
    assert len(hm) == 24
    assert [h["rune"] for h in hm] == FUTHARK  # same futhark order as App. 2
    by = {h["rune"]: h for h in hm}
    assert by["Ken"]["start"] == "09-13"      # book: Ken rules 13-28 Sep
    assert by["Ing"]["start"] == "05-14"      # book: Ing rules 14-29 May
    assert by["Peorth"]["start"] == "01-13"   # book: 28 Jan Peorth...
    assert by["Elhaz"]["start"] == "01-28"    # ...until 12 Feb Elhaz
    assert by["Feoh"]["start"] == "06-29"
    assert by["Beorc"]["note"]                # printed as 'Beare'


def test_runic_hours():
    rh = CORPUS["runic_hours"]["hours"]
    assert len(rh) == 24
    assert [h["rune"] for h in rh] == FUTHARK
    assert rh[0] == {"rune": "Feoh", "start": "12:30", "end": "13:30"}
    assert rh[-1] == {"rune": "Dag", "start": "11:30", "end": "12:30"}
    by = {h["rune"]: h for h in rh}
    # wheel order per Ch. 4; the Kenneth example's "Odal 22:30" conflicts
    # with the wheel (22:30 is Is) and is documented, not encoded
    assert by["Odal"] == {"rune": "Odal", "start": "10:30", "end": "11:30"}
    assert by["Is"] == {"rune": "Is", "start": "22:30", "end": "23:30"}
    assert by["Rad"] == {"rune": "Rad", "start": "16:30", "end": "17:30"}
    assert "Kenneth" in CORPUS["runic_hours"]["note"]
    # contiguous wheel, no gaps or overlaps
    for a, b in zip(rh, rh[1:] + rh[:1]):
        assert a["end"] == b["start"]


def test_planetary_hours_grid():
    grid = CORPUS["planetary_hours"]["grid"]
    assert set(grid) == {"Sunday", "Monday", "Tuesday", "Wednesday",
                         "Thursday", "Friday", "Saturday"}
    cells = [d for day in grid.values() for d in day]
    assert len(cells) == 168
    assert set(cells) == {"Thor", "Frigg", "Loki", "Sól", "Máni", "Tyr",
                          "Odin"}
    # spot checks against App. 3 as printed
    assert grid["Sunday"][0] == "Thor"
    assert grid["Sunday"][23] == "Loki"
    assert grid["Friday"][19] == "Frigg"   # printed 'Prigg'
    assert grid["Monday"][12] == "Máni"    # noon carries the day's ruler
    assert grid["Sunday"][12] == "Sól"
    assert grid["Saturday"][12] == "Loki"
    assert "note" in CORPUS["planetary_hours"]  # discontinuity documented


def test_weekdays():
    wd = CORPUS["weekdays"]
    assert len(wd) == 7
    by = {w["day"]: w for w in wd}
    assert by["Sunday"]["rune"] == "Sigel"
    assert by["Monday"]["rune"] == "Lagu"
    assert by["Tuesday"]["rune"] == "Tyr"
    assert by["Wednesday"]["rune"] == "Odal"
    assert by["Thursday"]["rune"] == "Thorn"
    assert by["Friday"]["rune"] == "Peorth"
    assert by["Saturday"]["rune"] == "Dag"
    assert by["Sunday"]["magic_square"] == 36
    assert by["Friday"]["esoteric_number"] == 7


def test_zodiac():
    z = CORPUS["zodiac"]
    classical = [r for r in z if r["variant"] == "classical"]
    modern = [r for r in z if r["variant"] == "modern alternative"]
    assert len(classical) == 12
    assert len(modern) == 3
    by = {(r["sign"], r["variant"]): r for r in z}
    assert by[("Aries", "classical")]["rune"] == "Eh"
    assert by[("Pisces", "classical")]["rune"] == "Beorc"
    assert by[("Aquarius", "modern alternative")]["planet"] == "Uranus"
    assert by[("Capricorn", "modern alternative")]["deity"] == "Loki"


def test_tides():
    t = CORPUS["tides"]
    assert len(t["tides"]) == 8
    assert len(t["day_markers"]) == 5
    by = {x["english"]: x for x in t["tides"]}
    assert by["Midnight"]["old_norse"] == "miðnætti"
    assert by["Midnight"]["start"] == "22:30"
    assert by["Uht"]["end"] == "04:30"


def test_mansions():
    m = CORPUS["mansions"]["mansions"]
    assert len(m) == 28
    assert [x["number"] for x in m] == list(range(1, 29))
    assert m[0]["rune"] == "Feoh" and m[0]["star"] == "Alcyone"
    assert m[27]["rune"] == "Ear"
    by = {x["rune"]: x for x in m}
    assert by["Tyr"]["northern_name"] == "The Sword"
    assert by["Ing"]["star"] == "Sadalsuud"
    assert "note" in CORPUS["mansions"]


def test_palaces_and_worlds():
    p = CORPUS["palaces"]["palaces"]
    assert len(p) == 12
    by = {x["sign"]: x for x in p}
    assert by["Aries"]["palace"] == "Bilskírnir"
    assert by["Pisces"]["palace"] == "Noatún"
    assert by["Scorpio"]["deity"] == "Odin"
    w = {x["world"]: x["rune"] for x in CORPUS["worlds"]["worlds"]}
    assert len(w) == 9
    assert w["Helheim"] == "Hagal"
    assert w["Asgard"] == "Gyfu"
    assert w["Midgard"] == "Jera"


def test_life_periods():
    lp = CORPUS["life_periods"]
    assert len(lp) == 7
    assert sum(p["years"] for p in lp) == 98
    assert lp[0] == {"deity": "Máni", "planet": "Moon", "start_age": 0,
                     "end_age": 4, "years": 4}
    assert lp[-1]["deity"] == "Loki" and lp[-1]["end_age"] == 98
    # contiguous, non-overlapping
    for a, b in zip(lp, lp[1:]):
        assert a["end_age"] == b["start_age"]
