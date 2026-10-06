"""The chart library: save, load, list and delete computed charts.

Charts live as JSON files in a library directory:
  $ASTROENGINE_CHART_DIR, else ~/.astroengine/charts

Each file holds the chart's name, type, save time, engine version, the
request (input arguments) and the computed result, so a chart computed
once can be re-examined or reused (e.g. a natal chart feeding transits)
without retyping birth data.
"""

import datetime as _datetime
import json as _json
import os as _os
import re as _re
from pathlib import Path as _Path

from .models import CalculationError

_NAME_RE = _re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
ENGINE_VERSION = "4.0.0"


def chart_dir(explicit: str | None = None) -> _Path:
    """Resolve the chart library directory, creating it on demand."""
    raw = explicit or _os.environ.get("ASTROENGINE_CHART_DIR") or \
        str(_Path.home() / ".astroengine" / "charts")
    path = _Path(raw).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _check_name(name: str) -> str:
    if not isinstance(name, str) or not _NAME_RE.match(name):
        raise CalculationError(
            f"invalid chart name '{name}': use 1-64 characters of "
            "letters, digits, dash and underscore")
    return name


def _path(name: str, directory: str | None = None) -> _Path:
    return chart_dir(directory) / f"{_check_name(name)}.json"


def save_chart(name: str, chart_type: str, request: dict,
               result: dict, directory: str | None = None) -> str:
    """Save a chart; returns the file path. Overwrites with notice."""
    path = _path(name, directory)
    existed = path.exists()
    payload = {
        "name": name,
        "chart_type": chart_type,
        "saved_at": _datetime.datetime.now(_datetime.timezone.utc)
        .isoformat(timespec="seconds"),
        "engine_version": ENGINE_VERSION,
        "request": request,
        "result": result,
    }
    path.write_text(_json.dumps(payload, ensure_ascii=False, indent=2,
                                sort_keys=True, default=str),
                    encoding="utf-8")
    return f"{path}{' (overwrote previous)' if existed else ''}"


def load_chart(name: str, directory: str | None = None) -> dict:
    """Load a saved chart; raises CalculationError when missing."""
    path = _path(name, directory)
    if not path.exists():
        raise CalculationError(
            f"no saved chart named '{name}' in {chart_dir(directory)}")
    return _json.loads(path.read_text(encoding="utf-8"))


def list_charts(directory: str | None = None) -> list[dict]:
    """List saved charts as {name, chart_type, saved_at} rows."""
    rows = []
    for path in sorted(chart_dir(directory).glob("*.json")):
        try:
            data = _json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rows.append({"name": data.get("name", path.stem),
                     "chart_type": data.get("chart_type", "?"),
                     "saved_at": data.get("saved_at", "?")})
    return rows


def delete_chart(name: str, directory: str | None = None) -> None:
    """Delete a saved chart; raises CalculationError when missing."""
    path = _path(name, directory)
    if not path.exists():
        raise CalculationError(f"no saved chart named '{name}' to delete")
    path.unlink()


def chart_exists(name: str, directory: str | None = None) -> bool:
    try:
        return _path(name, directory).exists()
    except CalculationError:
        return False


__all__ = ["ENGINE_VERSION", "chart_dir", "save_chart", "load_chart",
           "list_charts", "delete_chart", "chart_exists"]
