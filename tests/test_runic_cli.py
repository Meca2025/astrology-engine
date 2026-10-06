"""Sólrún's scrutiny of R09: the `runic` CLI command."""

import argparse
import io
import json
import sys
from contextlib import redirect_stdout

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
import astrology_engine  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402


def _args(**kw):
    base = dict(datetime="2026-05-16T16:45", lon=0.0, timezone="UTC",
                age=None, moon_lon=None, half_month=False, hour=False,
                tide=False, station=False, weekday=False, mansion=False,
                life_period=False, name=False, reading=False,
                full=False, json=False)
    base.update(kw)
    return argparse.Namespace(**base)


def _run(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        astrology_engine.cmd_runic(args)
    return buf.getvalue()


def test_full_text():
    out = _run(_args(full=True, age=54, moon_lon=50.0))
    for needle in ("RUNIC STAR-PROGRAM", "Ing", "Rad", "Eventide",
                   "Mystical Union", "Ing-Rad", "Pennick (2023)"):
        assert needle in out, needle


def test_single_layer_flag():
    out = _run(_args(tide=True))
    assert "TIDE OF DAY" in out
    assert "HALF-MONTH" not in out


def test_json_output():
    out = _run(_args(full=True, json=True, age=54, moon_lon=50.0))
    d = json.loads(out)
    assert set(d) == {"computation", "interpretation", "provenance"}
    assert d["computation"]["name"]["pair"] == "Ing-Rad"
    assert d["provenance"]["source"] == "Pennick (2023)"
    assert len(d["interpretation"]["statements"]) == 7


def test_json_single_layer():
    out = _run(_args(json=True, tide=True))
    d = json.loads(out)
    assert set(d["computation"]) == {"tide"}
    assert "interpretation" not in d


def test_bad_timezone_raises():
    try:
        _run(_args(full=True, timezone="Moon/Oceanus"))
    except CalculationError:
        return
    raise AssertionError("expected CalculationError")


def test_subcommand_registered():
    import subprocess
    r = subprocess.run(
        [sys.executable, "astrology_engine.py", "runic", "--help"],
        capture_output=True, text=True,
        cwd="/home/hatch/workspace/astrology-engine", timeout=60)
    assert r.returncode == 0
    assert "--half-month" in r.stdout and "--full" in r.stdout
