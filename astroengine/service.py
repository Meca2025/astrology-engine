"""Chart and discovery service; no rendering or implicit persistence."""

from dataclasses import asdict
from typing import Any

from .ephemeris import calculate
from .inputs import resolve_utc
from .models import ChartRequest
from .rules import load_rules


def capabilities() -> dict[str, Any]:
    return load_rules("capabilities.json")


def compute_chart(request: ChartRequest) -> dict[str, Any]:
    utc = resolve_utc(request)
    chart = calculate(utc, request)
    warnings = []
    if request.time is None:
        warnings.append("Birth time unknown: local noon surrogate; no angles or houses")
    if "moshier" in chart["provenance"]["backends"]:
        warnings.append("Swiss data files unavailable for some bodies; actual backend is Moshier")
    return {"schema_version": "1.0", "kind": "chart", "request": asdict(request),
            "utc": utc.isoformat(), "time_known": request.time is not None,
            "warnings": warnings, **chart}
