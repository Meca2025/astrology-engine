"""S01: self-healing, error correction, robustness."""

import json
import subprocess
import sys

import pytest

from astroengine.models import CalculationError
from astroengine.recovery import (chart_suggestions, correct_timezone,
                                  graceful, heal_date, heal_time, suggest)

BIN = [sys.executable, "astrology_engine.py"]
BASE = ["--date", "1972-09-01", "--time", "08:18", "--lat", "42.8142",
        "--lon", "-73.9396", "--timezone", "America/New_York"]


def test_heal_date_human_forms():
    iso, note = heal_date("Oct 7 2026")
    assert iso == "2026-10-07" and note
    assert heal_date("7 Oct 2026")[0] == "2026-10-07"
    assert heal_date("10/7/2026")[0] == "2026-10-07"
    assert heal_date("2026.10.07")[0] == "2026-10-07"


def test_heal_date_strict_passthrough():
    iso, note = heal_date("2026-10-07")
    assert (iso, note) == ("2026-10-07", None)


def test_heal_date_rejects():
    with pytest.raises(CalculationError, match="supply YYYY-MM-DD"):
        heal_date("yesterday")
    with pytest.raises(CalculationError):
        heal_date("2026-13-40")


def test_heal_time_human_forms():
    assert heal_time("8:18am")[0] == "08:18"
    assert heal_time("8:18 AM")[0] == "08:18"
    assert heal_time("8pm")[0] == "20:00"
    assert heal_time("0818")[0] == "08:18"
    assert heal_time("08:18") == ("08:18", None)
    assert heal_time(None) == (None, None)
    with pytest.raises(CalculationError, match="supply HH:MM"):
        heal_time("quarter past")


def test_correct_timezone():
    assert correct_timezone("America/New_York") == ("America/New_York", None)
    zone, note = correct_timezone("America/New York")
    assert zone == "America/New_York" and note
    zone, note = correct_timezone("america/new_york")
    assert zone == "America/New_York" and note
    with pytest.raises(CalculationError, match="did you mean"):
        correct_timezone("America/New_Yrok")


def test_suggest_house_system():
    assert suggest("Placiduss", ["placidus", "whole-sign", "equal"]) == ["placidus"]


def test_graceful():
    ok, result, error = graceful("ok", lambda: 42)
    assert (ok, result, error) == (True, 42, None)
    ok, result, error = graceful("bad", lambda: 1 / 0)
    assert ok is False and result is None and "ZeroDivisionError" in error
    def _boom():
        raise CalculationError("nope")
    ok, result, error = graceful("calc", _boom)
    assert (ok, result, error) == (False, None, "nope")


def test_chart_suggestions(tmp_path):
    from astroengine.charts import load_chart, save_chart
    save_chart("volmarr", "natal", {"date": "1972-09-01"}, {},
               str(tmp_path))
    with pytest.raises(CalculationError, match="did you mean"):
        load_chart("volmar", str(tmp_path))
    assert chart_suggestions("volmar", str(tmp_path)) == ["volmarr"]


def test_cli_heals_human_date():
    proc = subprocess.run(BIN + ["yogas", "--date", "Oct 7 2026",
                                 "--time", "8:18am"] + BASE[4:],
                          capture_output=True, text=True, cwd=".")
    assert proc.returncode == 0
    assert "healed" in proc.stderr


def test_cli_bad_timezone_suggests():
    proc = subprocess.run(
        BIN + ["yogas", "--date", "1972-09-01", "--time", "08:18",
               "--lat", "42.8142", "--lon", "-73.9396",
               "--timezone", "America/New_Yrok"],
        capture_output=True, text=True, cwd=".")
    assert proc.returncode == 2
    assert "did you mean" in proc.stderr


def test_cli_json_error_object():
    proc = subprocess.run(BIN + ["yogas", "--date", "2026-13-99",
                                 "--json"] + BASE[2:],
                          capture_output=True, text=True, cwd=".")
    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["kind"] == "calculation" and "error" in payload


def test_validate_profile_suggests():
    from astroengine.inputs import validate_profile
    from astroengine.models import ChartRequest
    req = ChartRequest(date="1972-09-01", time="08:18", latitude=42.8,
                       longitude=-73.9, timezone="America/New_York",
                       house_system="placiduss")
    with pytest.raises(CalculationError, match="did you mean"):
        validate_profile(req)
