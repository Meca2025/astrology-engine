"""Sólrún's scrutiny of the written natal dossier."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.dossier import natal_dossier, render_dossier  # noqa: E402

JD_NATAL = swe.julday(1972, 9, 1, 12.3)
LAT, LON = 42.81, -73.94


def _dossier():
    return natal_dossier(JD_NATAL, LAT, LON, "Volmarr", "1972-09-01",
                         "2026-10-23")


def test_all_sections_present():
    d = _dossier()
    for key in ("pillars", "wanderers", "chords", "bright_ones",
                "secret_chords", "soul_beneath", "directions",
                "year_lord", "coming_sky"):
        assert key in d, f"missing section {key}"


def test_pillars_correct():
    d = _dossier()
    assert "Virgo" in d["pillars"]["sun"]["placement"]
    assert "Gemini" in d["pillars"]["moon"]["placement"]
    assert "Libra" in d["pillars"]["ascendant"]["placement"]


def test_coming_sky_holds_october_23():
    d = _dossier()
    hit = next(h for h in d["coming_sky"]
               if h["date"] == "2026-10-23"
               and h["transit_body"] == "Jupiter"
               and h["natal_point"] == "Mercury")
    assert hit["aspect"] == "conjunction"


def test_year_lord_is_mars():
    d = _dossier()
    assert d["year_lord"]["time_lord"] == "Mars"
    assert d["year_lord"]["profected_sign"] == "Aries"


def test_render_mentions_name_and_sections():
    text = render_dossier(_dossier())
    assert "Volmarr" in text
    for heading in ("The Pillars", "The Wanderers", "The Chords",
                    "The Bright Ones", "The Secret Chords",
                    "The Soul Beneath", "The Year-Lord", "The Coming Sky"):
        assert heading in text
    assert "incline" in text  # the humble footer


def test_no_target_date_still_works():
    d = natal_dossier(JD_NATAL, LAT, LON, "Volmarr", "1972-09-01")
    assert "year_lord" not in d
    assert "coming_sky" not in d
    assert len(d["wanderers"]) == 8
