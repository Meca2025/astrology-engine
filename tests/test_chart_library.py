"""Sólrún's scrutiny of the chart library.

Save/load/list/delete round-trips in an isolated directory, name
validation, and the --load arg-filling behavior.
"""

import argparse
import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.charts import (  # noqa: E402
    save_chart, load_chart, list_charts, delete_chart, chart_exists)
from astroengine.models import CalculationError  # noqa: E402
import astrology_engine as ae  # noqa: E402


@pytest.fixture
def tdir(tmp_path, monkeypatch):
    monkeypatch.setenv("ASTROENGINE_CHART_DIR", str(tmp_path))
    return str(tmp_path)


def test_round_trip(tdir):
    req = {"date": "1972-09-01", "time": "08:18", "lat": 42.81,
           "lon": -73.94, "timezone": "America/New_York"}
    res = {"positions": {"Sun": {"longitude": 138.7}}}
    save_chart("volmarr", "natal", req, res)
    c = load_chart("volmarr")
    assert c["name"] == "volmarr" and c["chart_type"] == "natal"
    assert c["request"] == req and c["result"] == res
    assert c["engine_version"] and c["saved_at"]
    assert chart_exists("volmarr")


def test_list_and_delete(tdir):
    save_chart("a", "natal", {}, {})
    save_chart("b", "transit", {}, {})
    names = {r["name"] for r in list_charts()}
    assert {"a", "b"} <= names
    delete_chart("a")
    assert not chart_exists("a") and chart_exists("b")
    with pytest.raises(CalculationError):
        delete_chart("a")


def test_bad_names_rejected(tdir):
    for bad in ["", "../evil", "a/b", "x" * 65, "has space"]:
        with pytest.raises(CalculationError):
            save_chart(bad, "natal", {}, {})
    with pytest.raises(CalculationError):
        load_chart("missing-chart")


def test_load_fills_args(tdir):
    save_chart("v", "natal",
               {"date": "1972-09-01", "time": "08:18", "lat": 42.81,
                "lon": -73.94, "timezone": "America/New_York",
                "city": "Schenectady", "nation": "US"}, {})
    args = argparse.Namespace(date=None, time=None, lat=None, lon=None,
                              timezone=None, city="Indianapolis",
                              nation="US", load="v", chart_dir=None)
    ae.apply_chart_load(args)
    assert (args.date, args.time) == ("1972-09-01", "08:18")
    assert (args.lat, args.lon) == (42.81, -73.94)
    assert args.timezone == "America/New_York"
    # city keeps the explicit non-default the user passed
    assert args.city == "Indianapolis"


def test_load_two_person(tdir):
    save_chart("p1", "natal", {"date": "2000-01-01", "time": "12:00",
                               "lat": 1.0, "lon": 2.0,
                               "timezone": "UTC"}, {})
    args = argparse.Namespace(date1=None, time1=None, lat1=None,
                              lon1=None, timezone1=None,
                              load1="p1", load2=None, chart_dir=None)
    ae.apply_chart_load(args, "1")
    assert (args.date1, args.timezone1) == ("2000-01-01", "UTC")


def test_require_date():
    args = argparse.Namespace(date=None)
    with pytest.raises(CalculationError):
        ae.require_date(args)
    args.date = "2026-01-01"
    ae.require_date(args)  # no raise


def test_maybe_save_noop_without_flag(tdir, capsys):
    args = argparse.Namespace(save=None, chart_dir=None)
    ae.maybe_save_chart(args, "natal", {"a": 1})
    assert capsys.readouterr().out == ""
