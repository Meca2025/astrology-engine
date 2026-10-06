"""G04: Jaimini foundations.

Hand-verified fixtures for Volmarr (1972-09-01, sidereal D1):
- Karakas by intra-sign degree, descending: Venus 29.94 (AK),
  Mercury 29.70 (AmK), Moon 28.47 (BK), Saturn 26.25 (MK),
  Mars 17.63 (PK), Sun 15.66 (GK), Jupiter 5.09 (DK).
- Arudha Lagna: Virgo lord Mercury in Cancer; 11 signs to the
  lord, 11 forward from Cancer -> Taurus; Taurus is 9th from
  Virgo (no exception) -> AL = Taurus.
- Chara: starts Virgo; 9th-from-Lagna Taurus is even ->
  backward (apasavya). Virgo years: Mercury in Cancer,
  forward count 11 -> 10 years. Leo: Sun in own sign -> 12.
"""

import pytest

from astroengine.jaimini import (arudha_padas, chara_dasha, chara_karakas,
                                 render_jaimini)
from astroengine.models import ChartRequest


def _request():
    return ChartRequest(date="1972-09-01", time="08:18", latitude=42.8142,
                        longitude=-73.9396, timezone="America/New_York",
                        zodiac="sidereal", house_system="whole-sign")


def test_chara_karakas_order():
    karakas = chara_karakas(_request())["karakas"]
    assert [k["planet"] for k in karakas] == [
        "Venus", "Mercury", "Moon", "Saturn", "Mars", "Sun", "Jupiter"]
    assert [k["karaka"] for k in karakas] == [
        "Atmakaraka", "Amatyakaraka", "Bhratrukaraka", "Matrukaraka",
        "Putrakaraka", "Gnatikaraka", "Darakaraka"]
    assert karakas[0]["intra_sign_degree"] == pytest.approx(29.94, abs=0.01)
    assert karakas[-1]["intra_sign_degree"] == pytest.approx(5.09, abs=0.01)


def test_arudha_lagna_taurus():
    padas = arudha_padas(_request())["padas"]
    assert len(padas) == 12
    assert padas[0]["pada_sign"] == "Taurus"
    assert padas[0]["lord"] == "Mercury"


def test_chara_dasha_direction_and_years():
    dasha = chara_dasha(_request())
    assert dasha["start_sign"] == "Virgo"
    assert dasha["direction"] == "backward (apasavya)"
    seq = {s["sign"]: s["years"] for s in dasha["sequence"]}
    assert seq["Virgo"] == 10
    assert seq["Leo"] == 12  # Sun in own sign
    assert seq["Cancer"] == 10
    assert seq["Gemini"] == 1
    assert len(dasha["sequence"]) == 12


def test_chara_current_and_antardashas():
    dasha = chara_dasha(_request())
    cur = dasha["current"]
    assert cur is not None
    assert len(cur["antardashas"]) == 12
    assert cur["current_antardasha"] in [s["sign"] for s in dasha["sequence"]]
    assert dasha["school"].startswith("Jaimini")


def test_variants_disclosed():
    dasha = chara_dasha(_request())
    assert any("7th" in v for v in dasha["variants"])


def test_render_mentions_school():
    text = render_jaimini(chara_karakas(_request()),
                          arudha_padas(_request()), chara_dasha(_request()))
    assert "Arudha Lagna" in text and "Chara dasha" in text


def test_unknown_time_raises_cleanly():
    with pytest.raises((ValueError, Exception)):
        chara_karakas(ChartRequest(
            date="1972-09-01", time=None, latitude=42.8142,
            longitude=-73.9396, timezone="America/New_York",
            zodiac="sidereal", house_system="whole-sign"))
