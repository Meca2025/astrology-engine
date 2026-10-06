"""F01: daily forecast across all systems.

Offline fixtures with Volmarr's birth data and fixed target dates.
2026-10-23 is his Jupiter-conjunct-natal-Mercury day (independently
established by the watch slice); the forecast must show it.
"""

import pytest

from astroengine.forecast import daily_forecast, render_forecast
from astroengine.models import CalculationError, ChartRequest

BIRTH = dict(date="1972-09-01", time="08:18", latitude=42.8142,
             longitude=-73.9396, timezone="America/New_York",
             zodiac="sidereal", house_system="whole-sign")


def _birth_request():
    return ChartRequest(**BIRTH)


def _natal_jd():
    import swisseph as _swe
    from zoneinfo import ZoneInfo
    import datetime as _dt
    local = _dt.datetime(1972, 9, 1, 8, 18, tzinfo=ZoneInfo("America/New_York"))
    utc = local.astimezone(_dt.timezone.utc)
    return _swe.julday(utc.year, utc.month, utc.day,
                       utc.hour + utc.minute / 60.0, _swe.GREG_CAL)


def _report(target="2026-10-23"):
    return daily_forecast(_natal_jd(), 42.8142, -73.9396, "Volmarr",
                          _birth_request(), target)


def test_jupiter_mercury_day_shows_conjunction():
    report = _report("2026-10-23")
    hits = [h for h in report["computed"]["transits"]["active"]
            if h["transit_body"] == "Jupiter"
            and h["natal_point"] == "Mercury"
            and h["aspect"] == "conjunction"]
    assert hits and hits[0]["orb"] < 0.5
    exact = report["computed"]["transits"]["exact_today"]
    assert any(h["transit_body"] == "Jupiter"
               and h["natal_point"] == "Mercury" for h in exact)


def test_mercury_station_window_detected():
    report = _report("2026-10-23")
    stations = report["computed"]["transits"]["stations"]
    assert any(s["body"] == "Mercury" for s in stations)


def test_panchanga_and_dasha_present():
    c = _report("2026-10-23")["computed"]
    assert c["panchanga"]["tithi"] == "Trayodashi"
    assert c["panchanga"]["nakshatra"] == "Uttara Bhadrapada"
    assert c["dasha"]["mahadasa"] == "Saturn"
    assert c["dasha"]["antardasha"] == "Rahu"


def test_chinese_day_pillar_and_relations():
    c = _report("2026-10-23")["computed"]
    assert c["bazi_day"]["stem_branch"] == "Geng-Wu"
    assert c["bazi_day"]["animal"] == "Horse"
    assert c["bazi_day"]["day_master"] == "Yi"
    assert set(c["bazi_day"]["pillar_relations"]) == {"year", "month", "day", "hour"}
    assert c["zodiac_day"]["birth_animal"] == "Rat"


def test_tibetan_and_rune_present():
    c = _report("2026-10-23")["computed"]
    assert c["tibetan"]["natal_element"] == "Water"
    assert c["tibetan"]["day_element"] == "Metal"
    assert c["rune"]["name"] == "Wyn"


def test_reading_is_labeled_symbolic():
    r = _report("2026-10-23")["reading"]
    assert "not a prediction" in r["note"]
    assert set(r) >= {"western", "vedic", "chinese", "tibetan", "runic", "synthesis"}


def test_afflictions_exposed_for_mantras():
    a = _report("2026-10-23")["computed"]["afflictions"]
    assert set(a) == {"pressured_planets", "dasha_lords", "clashing_pillars"}
    assert a["dasha_lords"]["mahadasa"] == "Saturn"


def test_bad_target_date_raises_cleanly():
    with pytest.raises(CalculationError):
        daily_forecast(_natal_jd(), 42.8142, -73.9396, "Volmarr",
                       _birth_request(), "not-a-date")


def test_text_render_mentions_every_system():
    text = render_forecast(_report("2026-10-23"))
    for word in ("Jupiter", "Saturn", "Geng-Wu", "Metal", "Wyn"):
        assert word in text
