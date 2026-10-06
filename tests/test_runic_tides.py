"""Sólrún's scrutiny of R04: tides, stations, and runic names (Pennick 2023).

Tides: App. 6 fixtures incl. boundary times and the Midnight wrap.
Stations: the Ch. 5 station table (rune/festival/hour/symbolism) and the
declared festival-span boundary convention.
Names: Ingrid's Ing-Rad pair (wheel-consistent); Darwin noted as literary.
"""

import json
import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runic import tide, year_station, runic_name  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402

CORPUS = json.load(open("/home/hatch/workspace/astrology-engine/data/runic.json"))


def test_corpus_version_bumped_for_stations():
    assert CORPUS["version"] == "1.1"
    assert len(CORPUS["stations"]["stations"]) == 8


def test_station_table_matches_book():
    by_num = {s["number"]: s for s in CORPUS["stations"]["stations"]}
    assert by_num[1]["runes"] == "As/Rad" and by_num[1]["day_hour"] == "16:30"
    assert by_num[2]["runes"] == "Ken" and by_num[2]["festival"] == "Autumn Equinox"
    assert by_num[3]["runes"] == "Hagal" and by_num[3]["festival"] == "Samhain"
    assert by_num[4]["runes"] == "Jera" and by_num[4]["festival"] == "Yule"
    assert by_num[5]["runes"] == "Beorc" and by_num[5]["festival"] == "Spring Equinox"
    assert by_num[6]["runes"] == "Lagu" and by_num[6]["festival"] == "Beltane"
    assert by_num[7]["runes"] == "Dag" and by_num[7]["festival"] == "Midsummer"
    assert by_num[8]["runes"] == "Thorn" and by_num[8]["festival"] == "Lammas"
    assert CORPUS["stations"]["boundary_method"] == "festival-span"


@pytest.mark.parametrize("clock,english", [
    ("04:30", "Morntide"), ("07:30", "Daytide (Undernoon)"),
    ("10:30", "Midday (Noontide)"), ("13:30", "Afternoon (Undorne)"),
    ("16:30", "Eventide"), ("19:30", "Nighttide"), ("22:30", "Midnight"),
    ("01:30", "Uht"), ("04:29", "Uht"),
])
def test_tide_boundaries(clock, english):
    t = tide(clock)
    assert t["english"] == english
    assert t["source"] == "Pennick (2023)"


def test_tide_midnight_wrap():
    assert tide("00:15")["english"] == "Midnight"
    assert tide("23:59")["english"] == "Midnight"
    assert tide("12:00")["english"] == "Midday (Noontide)"
    assert tide("16:30")["old_norse"] == "aftan"


def test_tide_bad_time():
    with pytest.raises(CalculationError):
        tide("25:00")


@pytest.mark.parametrize("day,station,runes", [
    ("2026-12-25", 4, "Jera"), ("2026-01-05", 4, "Jera"),
    ("2026-03-20", 5, "Beorc"), ("2026-05-01", 6, "Lagu"),
    ("2026-06-25", 7, "Dag"), ("2026-08-01", 8, "Thorn"),
    ("2026-08-20", 1, "As/Rad"), ("2026-09-22", 2, "Ken"),
    ("2026-10-06", 2, "Ken"), ("2026-11-05", 3, "Hagal"),
])
def test_year_station_fixtures(day, station, runes):
    s = year_station(day)
    assert (s["station"], s["runes"]) == (station, runes)
    assert s["historical_claim"] == "modern synthesis"


def test_year_station_declares_convention():
    s = year_station("2026-08-20")
    assert "declared engine convention" in s["method"]


def test_runic_name_ingrid_pair():
    n = runic_name("2026-05-16T16:45", 0.0, "UTC")
    assert n["pair"] == "Ing-Rad"
    assert n["half_month_rune"] == "Ing" and n["hour_rune"] == "Rad"


def test_runic_name_darwin_is_literary():
    # 27 Oct 20:27: Wyn half-month. The book places 8:27pm in the Wyn hour
    # by civil time; LAT adds the late-October +16min EoT (20:43 -> Hagal),
    # so the wheel-faithful pair is Wyn-Hagal. Either way, the book's
    # "Darwin / joy of day" is literary wordplay, not mechanical output.
    n = runic_name("2026-10-27T20:27", 0.0, "UTC")
    assert n["pair"] == "Wyn-Hagal"
    assert "literary" in n["note"]


def test_runic_name_bad_timezone():
    with pytest.raises(CalculationError):
        runic_name("2026-05-16T16:45", 0.0, "Moon/Oceanus")
