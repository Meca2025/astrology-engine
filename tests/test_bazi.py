"""Sólrún's scrutiny of the Four Pillars."""

import sys

import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.bazi import lichun_moment, pillars  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def test_lichun_moment_sane():
    # Lichun 2024 fell on Feb 4 (08:27 UTC per the almanac)
    m = lichun_moment(2024)
    assert (m.month, m.day, m.hour) == (2, 4, 8)


def test_published_anchors():
    # 1939-01-17: Wu-Yin year, Yi-Chou month, Jia-Yin day (published)
    r = pillars("1939-01-17", "12:00", "UTC")
    assert r["year"]["ganzhi"] == "Wu-Yin"
    assert r["month"]["ganzhi"] == "Yi-Chou"
    assert r["day"]["ganzhi"] == "Jia-Yin"
    # 1985-09-12: Yi-Chou year, Yi-You month, Jia-Yin day (published)
    r = pillars("1985-09-12", "12:00", "UTC")
    assert r["year"]["ganzhi"] == "Yi-Chou"
    assert r["month"]["ganzhi"] == "Yi-You"
    assert r["day"]["ganzhi"] == "Jia-Yin"


def test_year_turns_at_lichun_not_cny():
    # 2024-02-03 (before Lichun Feb 4 08:27 UTC): still Gui-Mao year
    assert pillars("2024-02-03", "12:00", "UTC")["year"]["ganzhi"] == "Gui-Mao"
    # 2024-02-05 (after Lichun, before CNY Feb 10): already Jia-Chen
    r = pillars("2024-02-05", "12:00", "UTC")
    assert r["year"]["ganzhi"] == "Jia-Chen"


def test_month_turns_at_jie():
    # Jingzhe 2024 was Mar 5; Mar 4 is still Yin month, Mar 6 Mao
    assert pillars("2024-03-04", "12:00", "UTC")["month"]["branch"] == "Yin"
    assert pillars("2024-03-06", "12:00", "UTC")["month"]["branch"] == "Mao"
    assert pillars("2024-03-06", "12:00", "UTC")["month"]["ganzhi"] == "Ding-Mao"


def test_volmarr():
    r = pillars("1972-09-01", "08:18", "America/New_York")
    assert r["year"]["ganzhi"] == "Ren-Zi"
    assert r["month"]["ganzhi"] == "Wu-Shen"
    assert r["day"]["ganzhi"] == "Yi-Wei"
    assert r["hour"]["ganzhi"] == "Geng-Chen"
    assert r["day_master"] == "Yi"
    assert r["day"]["nayin"] == "Sand Gold"


def test_bad_inputs():
    with pytest.raises(CalculationError, match="bad date"):
        pillars("yesterday", "12:00", "UTC")
    with pytest.raises(CalculationError, match="bad time"):
        pillars("1972-09-01", "morning", "UTC")
    with pytest.raises(CalculationError, match="unknown timezone"):
        pillars("1972-09-01", "12:00", "Atlantis/Nowhere")
