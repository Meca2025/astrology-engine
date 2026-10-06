"""F02: remedial Vedic mantras.

The corpus holds only traditional, public-domain verses — this suite
guards that every graha is covered and every string is non-empty.
"""

import pytest

from astroengine.forecast import daily_forecast
from astroengine.mantras import all_mantras, mantras_for, remedies_for
from astroengine.models import CalculationError, ChartRequest

GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter",
          "Venus", "Saturn", "Rahu", "Ketu"]


def test_all_nine_grahas_covered():
    corpus = all_mantras()
    assert sorted(corpus) == sorted(GRAHAS)
    for planet, entry in corpus.items():
        assert entry["deity"], planet
        assert entry["mantras"], planet
        for m in entry["mantras"]:
            assert m["text"].strip(), planet
            assert m["repetitions"] > 0, planet
            assert m["purpose"].strip(), planet


def test_gayatri_present_for_sun():
    texts = [m["text"] for m in mantras_for("Sun")["mantras"]]
    assert any("Bhur Bhuvah Svah" in t for t in texts)


def test_unknown_graha_raises_cleanly():
    with pytest.raises(CalculationError):
        mantras_for("Pluto")


def _afflictions_2026_10_23():
    import datetime as _dt
    import swisseph as _swe
    from zoneinfo import ZoneInfo
    local = _dt.datetime(1972, 9, 1, 8, 18,
                         tzinfo=ZoneInfo("America/New_York"))
    utc = local.astimezone(_dt.timezone.utc)
    natal_jd = _swe.julday(utc.year, utc.month, utc.day,
                           utc.hour + utc.minute / 60.0, _swe.GREG_CAL)
    birth = ChartRequest(date="1972-09-01", time="08:18", latitude=42.8142,
                         longitude=-73.9396, timezone="America/New_York",
                         zodiac="sidereal", house_system="whole-sign")
    report = daily_forecast(natal_jd, 42.8142, -73.9396, "Volmarr",
                            birth, "2026-10-23")
    return (report["computed"]["afflictions"],
            report["computed"]["transits"]["active"])


def test_remedies_recommend_dasha_lords_first():
    aff, active = _afflictions_2026_10_23()
    remedies = remedies_for(aff, active)
    planets = [r["planet"] for r in remedies]
    assert planets[0] == "Saturn"  # mahadasha lord
    assert planets[1] == "Rahu"    # antardasha lord
    assert all("reason" in r and r["reason"] for r in remedies)


def test_remedies_include_pressured_planets_with_reasons():
    aff = {"pressured_planets": ["Moon"],
           "dasha_lords": {"mahadasa": "Jupiter", "antardasha": "Venus"},
           "clashing_pillars": []}
    active = [{"transit_body": "Mars", "natal_point": "Moon",
               "aspect": "square", "orb": 1.2}]
    remedies = remedies_for(aff, active)
    moon = next(r for r in remedies if r["planet"] == "Moon")
    assert "Mars square" in moon["reason"]
