"""House systems: five lenses for the twelve houses.

Names follow data/profiles.json so no system code is hardcoded here.
The typed ephemeris boundary (legacy_houses -> houses_at_jd) does the
computation; this module only resolves names and validates.
"""

from .legacy_astronomy import legacy_houses
from .models import CalculationError
from .rules import load_rules

SYSTEMS = ("placidus", "whole-sign", "equal", "koch", "regiomontanus")


def _codes() -> dict[str, bytes]:
    """Name -> Swiss Ephemeris system code, from data/profiles.json."""
    houses = load_rules("profiles.json").get("houses", {})
    return {name: code.encode("ascii") for name, code in houses.items()
            if name in SYSTEMS}


def house_cusps(jd_ut: float, lat: float, lon: float,
                system: str = "placidus") -> tuple[list[float], float, float]:
    """Twelve cusps plus ASC/MC for the requested house system.

    Returns (cusps[12], asc, mc). Raises CalculationError on an unknown
    system or a failed computation — failed houses never fabricate.
    """
    key = (system or "placidus").strip().lower().replace("_", "-")
    codes = _codes()
    if key not in codes:
        raise CalculationError(
            f"unknown house system '{system}'; "
            f"available: {sorted(codes)}")
    return legacy_houses(jd_ut, lat, lon, codes[key])


__all__ = ["SYSTEMS", "house_cusps"]
