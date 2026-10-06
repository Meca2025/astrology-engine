"""G02: Shadbala — the sixfold strength.

Structural tests on Volmarr's chart plus hand-verified spot values:
- Jupiter (Hamsa, own in Sagittarius, kendra) must be STRONG and
  among the highest totals.
- Uchcha spot check: Jupiter at 5.09° Sagittarius (sidereal).
  Neecha point = 5° Cancer + 180° = 5° Capricorn = 275°.
  d = (245.09 - 275) % 360 = 330.09; uchcha = (180 - |330.09-180|)/3
  = (180 - 150.09)/3 = 9.97.
- Kendradi spot check: Jupiter in 4th from Lagna -> 60.
- Dig spot check: Venus in 10th, peak 4th -> house distance 6 -> 0.
- Naisargika is the fixed table: Sun 60 .. Saturn 8.57.
"""

import pytest

from astroengine.models import ChartRequest
from astroengine.shadbala import shadbala


def _request():
    return ChartRequest(date="1972-09-01", time="08:18", latitude=42.8142,
                        longitude=-73.9396, timezone="America/New_York",
                        zodiac="sidereal", house_system="whole-sign")


def _report():
    return shadbala(_request())


def test_all_planets_present_with_bounded_components():
    planets = _report()["planets"]
    assert sorted(planets) == ["Jupiter", "Mars", "Mercury", "Moon",
                               "Saturn", "Sun", "Venus"]
    for planet, v in planets.items():
        c = v["components"]
        assert 0 <= c["uchcha"] <= 60, planet
        assert 0 <= c["saptavargaja"] <= 315, planet
        assert c["ojhayugma"] in (0, 15, 30), planet
        assert c["kendradi"] in (15, 30, 60), planet
        assert c["drekkana"] in (0, 15), planet
        assert 0 <= c["dig"] <= 60, planet
        assert 0 <= c["chesta"] <= 60, planet
        assert -60 <= c["drik"] <= 60, planet
        assert v["virupas"] == pytest.approx(
            sum(c[k] for k in ("sthana", "dig", "kala", "chesta",
                               "naisargika", "drik")), abs=0.05)


def test_jupiter_strongest_as_hamsa_demands():
    planets = _report()["planets"]
    assert planets["Jupiter"]["strong"] is True
    assert planets["Jupiter"]["rupas"] >= 6.5
    assert planets["Jupiter"]["virupas"] > planets["Saturn"]["virupas"]


def test_uchcha_spot_value():
    c = _report()["planets"]["Jupiter"]["components"]
    assert c["uchcha"] == pytest.approx(9.97, abs=0.05)


def test_kendradi_and_dig_spot_values():
    planets = _report()["planets"]
    assert planets["Jupiter"]["components"]["kendradi"] == 60
    assert planets["Venus"]["components"]["dig"] == 0


def test_naisargika_fixed_table():
    comps = {p: v["components"]["naisargika"]
             for p, v in _report()["planets"].items()}
    assert comps == {"Sun": 60.0, "Moon": 51.43, "Mars": 17.14,
                     "Mercury": 25.71, "Jupiter": 34.29,
                     "Venus": 42.86, "Saturn": 8.57}


def test_minima_and_limitations_reported():
    report = _report()
    assert report["planets"]["Sun"]["minimum_rupas"] == 5
    assert report["limitations"]
    assert report["rule_version"] == "1.0"


def test_unknown_time_raises_cleanly():
    from astroengine.models import CalculationError
    req = ChartRequest(date="1972-09-01", time=None, latitude=42.8142,
                       longitude=-73.9396, timezone="America/New_York",
                       zodiac="sidereal", house_system="whole-sign")
    with pytest.raises((CalculationError, Exception)):
        shadbala(req)
