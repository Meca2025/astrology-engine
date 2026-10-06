"""G03: Ashtakavarga.

Acceptance fixture: B.V. Raman's Standard Horoscope (1918-10-16,
Bangalore) in sidereal signs — Sun Virgo, Moon Aquarius, Mars
Scorpio, Mercury Libra, Jupiter Gemini, Venus Virgo, Saturn Leo,
Lagna Capricorn. Raman's worked Sun BAV (Aries->Pisces):
[5,3,5,4,4,4,3,5,5,0,5,5], total 48.
"""

import pytest

from astroengine.ashtakavarga import bhinna, compute_ashtakavarga
from astroengine.models import ChartRequest
from astroengine.rules import load_rules

# sign indices: Virgo 5, Aquarius 10, Scorpio 7, Libra 6, Gemini 2, Leo 4, Capricorn 9
RAMAN_SIGNS = {"Sun": 5, "Moon": 10, "Mars": 7, "Mercury": 6,
               "Jupiter": 2, "Venus": 5, "Saturn": 4}
RAMAN_LAGNA = 9


def test_raman_standard_horoscope_sun_bav():
    result = bhinna(RAMAN_SIGNS, RAMAN_LAGNA)
    assert result["bhinna"]["Sun"] == [5, 3, 5, 4, 4, 4, 3, 5, 5, 0, 5, 5]


def test_canonical_totals():
    result = bhinna(RAMAN_SIGNS, RAMAN_LAGNA)
    canonical = load_rules("ashtakavarga.json")["canonical_totals"]
    assert result["totals"] == canonical


def test_constant_337():
    result = bhinna(RAMAN_SIGNS, RAMAN_LAGNA)
    assert result["sav_total"] == 337
    # and for an arbitrary chart too — the constant holds everywhere
    other = bhinna({"Sun": 0, "Moon": 1, "Mars": 2, "Mercury": 3,
                    "Jupiter": 4, "Venus": 5, "Saturn": 6}, 7)
    assert other["sav_total"] == 337


def test_table_rows_sum_to_canonical():
    tables = load_rules("ashtakavarga.json")["benefic_places"]
    canonical = load_rules("ashtakavarga.json")["canonical_totals"]
    for planet, rows in tables.items():
        assert sum(len(h) for h in rows.values()) == canonical[planet]


def test_compute_from_request_volmarr():
    report = compute_ashtakavarga(ChartRequest(
        date="1972-09-01", time="08:18", latitude=42.8142,
        longitude=-73.9396, timezone="America/New_York",
        zodiac="sidereal", house_system="whole-sign"))
    assert report["sav_total"] == 337
    assert report["lagna"] == "Virgo"
    assert report["signs"]["Jupiter"] == "Sagittarius"
    assert report["reading"]["weak_signs"] or report["reading"]["strong_signs"]


def test_unknown_time_raises_cleanly():
    with pytest.raises((ValueError, Exception)):
        compute_ashtakavarga(ChartRequest(
            date="1972-09-01", time=None, latitude=42.8142,
            longitude=-73.9396, timezone="America/New_York",
            zodiac="sidereal", house_system="whole-sign"))


def test_trikona_ekadhipatya_reductions_raman():
    from astroengine.ashtakavarga import apply_reductions
    result = bhinna(RAMAN_SIGNS, RAMAN_LAGNA)
    occupied = set(RAMAN_SIGNS.values()) | {RAMAN_LAGNA}
    red = apply_reductions(result["bhinna"], occupied)
    # Sun's BAV hand-reduced: trikona then ekadhipatya (Jupiter pair 8/11)
    assert red["bhinna_reduced"]["Sun"] == [1, 3, 2, 0, 0, 4, 0, 1, 0, 0, 2, 0]
    assert red["reduced_total"] == sum(
        sum(row) for row in red["bhinna_reduced"].values())
    assert red["reduced_total"] < 337


def test_reductions_present_in_compute():
    report = compute_ashtakavarga(__import__("astroengine.models", fromlist=["ChartRequest"]).ChartRequest(
        date="1972-09-01", time="08:18", latitude=42.8142,
        longitude=-73.9396, timezone="America/New_York",
        zodiac="sidereal", house_system="whole-sign"))
    assert "sarvashtakavarga_reduced" in report
    assert report["reduced_total"] < 337
