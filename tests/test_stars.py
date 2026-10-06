"""Sólrún's scrutiny of the fixed stars."""

import sys

import pytest
import swisseph as swe

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.stars import load_stars, star_hits, star_longitude  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402

JD_NATAL = swe.julday(1972, 9, 1, 12.3)
LAT, LON = 42.81, -73.94


def test_catalog_schema():
    stars = load_stars()
    assert len(stars) == 26
    names = [s["name"] for s in stars]
    assert "Regulus" in names and "Spica" in names and "Algol" in names
    for s in stars:
        assert 0.0 <= s["j2000_lon"] < 360.0
        assert -90.0 <= s["j2000_lat"] <= 90.0
        assert s["nature"] and s["meaning"]


def test_regulus_precession():
    # Regulus J2000 149.8290°; ~1.4°/century -> ~150.2° in 2026
    lon = star_longitude("Regulus", swe.julday(2026, 10, 23))
    assert 150.0 < lon < 150.5


def test_spica_precession():
    lon = star_longitude("Spica", swe.julday(2026, 10, 23))
    assert 204.0 < lon < 204.5


def test_precession_rate_sane():
    # ~26 years of precession should move a star ~0.3-0.4° in longitude
    d = star_longitude("Antares", swe.julday(2026, 1, 1)) - star_longitude(
        "Antares", 2451545.0)
    assert 0.2 < d < 0.6


def test_volmarr_hits():
    hits = star_hits(JD_NATAL, LAT, LON)
    by_star = {h["star"]: h for h in hits}
    assert by_star["Capella"]["natal_point"] == "Moon"
    assert by_star["Capella"]["orb"] < 1.0
    assert by_star["Pollux"]["natal_point"] == "Venus"
    assert by_star["Pollux"]["orb"] < 1.0
    orbs = [h["orb"] for h in hits]
    assert orbs == sorted(orbs)


def test_tight_orb_finds_nothing_or_less():
    wide = star_hits(JD_NATAL, LAT, LON, orb=1.0)
    tight = star_hits(JD_NATAL, LAT, LON, orb=0.1)
    assert len(tight) <= len(wide)


def test_unknown_star_raises():
    with pytest.raises(CalculationError):
        star_longitude("Not A Star", swe.julday(2026, 1, 1))


def test_bad_orb_raises():
    with pytest.raises(CalculationError):
        star_hits(JD_NATAL, LAT, LON, orb=0)


def test_cli_list_needs_no_birth_data():
    # Sólrún D1: `stars --list` must run with no chart at all
    import subprocess, os
    env = dict(os.environ)
    env["ASTROENGINE_CHART_DIR"] = "/tmp/solrun-h07-cli"
    r = subprocess.run(
        [sys.executable, "astrology_engine.py", "stars", "--list"],
        capture_output=True, text=True, env=env,
        cwd="/home/hatch/workspace/astrology-engine")
    assert r.returncode == 0, r.stderr
    assert "Regulus" in r.stdout
