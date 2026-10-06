"""G01: yoga engine.

Volmarr's chart (1972-09-01, hand-verified): Hamsa Mahapurusha
(Jupiter own in Sagittarius, 4th from Lagna), Dhana (Moon+Saturn,
11th+5th lords conjoined in Taurus), Raja (4th lord Jupiter and
9th lord Venus in mutual 7ths), Sakata (Jupiter 8th from Moon);
absent: Gaja Kesari (Jupiter 8th from Moon), Budha-Aditya
(Sun Leo, Mercury Cancer), Kemadruma (Venus 2nd from Moon).
2000-01-01: Gaja Kesari (Jupiter 7th from Moon in Libra) and
Budha-Aditya (Sun+Mercury in Sagittarius) — verified by hand.
"""

import pytest

from astroengine.models import ChartRequest
from astroengine.yogas import detect_yogas, render_yogas


def _request(**kw):
    base = dict(date="1972-09-01", time="08:18", latitude=42.8142,
                longitude=-73.9396, timezone="America/New_York",
                zodiac="sidereal", house_system="whole-sign")
    base.update(kw)
    return ChartRequest(**base)


def _present(report):
    return {y["yoga"]: y for y in report["yogas"] if y["present"]}


def test_volmarr_hamsa_mahapurusha():
    present = _present(detect_yogas(_request()))
    assert "Pancha Mahapurusha Yogas" in present
    assert "Hamsa" in present["Pancha Mahapurusha Yogas"]["details"]
    assert present["Pancha Mahapurusha Yogas"]["planets"] == ["Jupiter"]


def test_volmarr_dhana_raja_sakata():
    present = _present(detect_yogas(_request()))
    dhana = present["Dhana Yogas"]
    assert set(dhana["planets"]) == {"Moon", "Saturn"}
    assert "conjunction" in dhana["details"]
    raja = present["Raja Yogas (basic)"]
    assert set(raja["planets"]) == {"Jupiter", "Venus"}
    assert "mutual kendra" in raja["details"]
    assert "Sakata Yoga" in present


def test_volmarr_absent_yogas():
    report = detect_yogas(_request())
    absent = {y["yoga"] for y in report["yogas"] if not y["present"]}
    assert {"Gaja Kesari Yoga", "Budha-Aditya Yoga",
            "Kemadruma Yoga"} <= absent


def test_gaja_kesari_and_budha_aditya_positive():
    report = detect_yogas(_request(date="2000-01-01", time="12:00",
                                   latitude=0, longitude=0,
                                   timezone="UTC"))
    present = _present(report)
    assert "7th from the Moon" in present["Gaja Kesari Yoga"]["details"]
    assert "Sagittarius" in present["Budha-Aditya Yoga"]["details"]


def test_every_detection_carries_provenance():
    report = detect_yogas(_request())
    for y in report["yogas"]:
        assert y["rule"] and y["signification"] and y["source"]
    assert report["rule_version"] == "1.0"


def test_render_mentions_present_and_absent():
    text = render_yogas(detect_yogas(_request()))
    assert "Hamsa" in text and "Sakata" in text
    assert "Absent" in text
