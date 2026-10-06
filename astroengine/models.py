"""Frozen public inputs and explicit calculation failures."""

from dataclasses import dataclass

from .rules import load_rules

_DEFAULTS = load_rules("profiles.json")["defaults"]


class CalculationError(ValueError):
    """A request cannot produce a trustworthy calculation."""


@dataclass(frozen=True)
class ChartRequest:
    date: str
    latitude: float
    longitude: float
    timezone: str
    time: str | None = None
    zodiac: str = _DEFAULTS["zodiac"]
    ayanamsa: str = _DEFAULTS["ayanamsa"]
    house_system: str = _DEFAULTS["house_system"]
    node_type: str = _DEFAULTS["node_type"]
    ephemeris_path: str | None = None
