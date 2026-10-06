"""R02 — tests for astroengine.runic.half_month_rune.

Book fixtures from Pennick (2023), App. 2 (runic half-months).
"""
import pytest

from astroengine.models import CalculationError
from astroengine.runic import half_month_rune, runic_date_request


def rune_on(day, time=None, timezone=None):
    return half_month_rune(day, time=time, timezone=timezone)["rune"]


def test_book_fixtures():
    assert rune_on("2026-01-27") == "Peorth"   # Peorth rules 13 Jan - 28 Jan
    assert rune_on("2026-02-11") == "Elhaz"    # Elhaz rules 28 Jan - 12 Feb
    assert rune_on("2026-02-12") == "Sigel"
    assert rune_on("2026-09-13") == "Ken"      # Ken rules 13-28 Sep
    assert rune_on("2026-09-28") == "Gyfu"
    assert rune_on("2026-05-14") == "Ing"      # Ing rules 14-29 May
    assert rune_on("2026-06-29") == "Feoh"     # the wheel opens at midsummer
    assert rune_on("2026-10-06") == "Gyfu"     # today: 28 Sep-13 Oct


def test_year_wrap():
    assert rune_on("2026-01-01") == "Eoh"      # before Peorth's 01-13
    assert rune_on("2026-01-12") == "Eoh"
    assert rune_on("2026-12-28") == "Eoh"
    assert rune_on("2026-12-31") == "Eoh"


def test_boundary_time_refinement():
    # Elhaz begins 01-28 at 05:00 local apparent
    assert rune_on("2026-01-28", time="04:59") == "Peorth"
    assert rune_on("2026-01-28", time="05:00") == "Elhaz"
    assert rune_on("2026-01-28", time="05:00",
                   timezone="America/New_York") == "Elhaz"


def test_result_shape():
    out = half_month_rune("2026-09-20")
    assert out["rune"] == "Ken"
    assert out["half_month_start"] == "09-13"
    assert out["half_month_end"] == "09-28"
    assert out["next_rune"] == "Gyfu"
    assert out["days_remaining"] == 8
    assert out["correspondences"]["deity"] == \
        "Heimdall/Freyja/Frey"
    assert out["source"] == "Pennick (2023)"
    assert out["historical_claim"] == "modern synthesis"


def test_wrap_result_shape():
    out = half_month_rune("2026-12-31")
    assert out["rune"] == "Eoh"
    assert out["next_rune"] == "Peorth"
    assert out["days_remaining"] == 13  # 01-13 next year


def test_invalid_inputs_raise():
    with pytest.raises(CalculationError):
        half_month_rune("not-a-date")
    with pytest.raises(CalculationError):
        half_month_rune("2026-09-20", time="25:00")
    with pytest.raises(CalculationError):
        half_month_rune("2026-09-20", time="12:00",
                        timezone="Not/AZone")
    with pytest.raises(CalculationError):
        # timezone without a clock time is meaningless
        half_month_rune("2026-09-20", timezone="UTC")


def test_frozen_request():
    req = runic_date_request("2026-09-20", time="12:00", timezone="UTC")
    assert req.date == "2026-09-20"
    with pytest.raises(CalculationError):
        runic_date_request("2026-13-40")
