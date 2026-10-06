"""Dict-compatible legacy astronomy snapshots without importing the text CLI."""

from typing import Any

from .ephemeris import houses_at_jd, positions_at_jd
from .models import CalculationError, EphemerisRequest
from .rules import load_rules


class LegacyPositions(dict[str, dict[str, Any]]):
    """Body keys only; diagnostics/provenance live outside planet iteration."""

    def __init__(self, snapshot: dict[str, Any]) -> None:
        super().__init__(snapshot["positions"])
        self.unavailable: dict[str, str] = snapshot["unavailable"]
        self.provenance: dict[str, Any] = snapshot["provenance"]


def legacy_request(jd: float, tropical: bool = True) -> EphemerisRequest:
    if not isinstance(tropical, bool):
        raise CalculationError("tropical must be an explicit boolean")
    defaults = load_rules("legacy_astronomy.json")["defaults"]
    return EphemerisRequest(jd, defaults["zodiac"] if tropical else "sidereal",
                            defaults["ayanamsa"])


def _text_position(position: dict[str, Any]) -> dict[str, Any]:
    degree = position["degree_in_sign"]
    return {**position, "sign_idx": position["sign_index"],
            "degree": int(degree), "minutes": int((degree % 1) * 60)}


def legacy_positions(jd: float, tropical: bool = True) -> LegacyPositions:
    rules = load_rules("legacy_astronomy.json")
    snapshot = positions_at_jd(legacy_request(jd, tropical), rules["required_bodies"],
                               rules["optional_bodies"])
    snapshot["positions"] = {name: _text_position(position)
                             for name, position in snapshot["positions"].items()}
    north = snapshot["positions"]["N.Node"]
    longitude = (north["longitude"] + 180) % 360
    degree = longitude % 30
    snapshot["positions"]["S.Node"] = {
        **north, "longitude": longitude, "latitude": -north["latitude"],
        "sign_idx": int(longitude // 30), "sign_index": int(longitude // 30),
        "sign": load_rules("profiles.json")["signs"][int(longitude // 30)],
        "degree_in_sign": degree, "degree": int(degree), "minutes": int((degree % 1) * 60),
        "derived_from": "N.Node"}
    snapshot["provenance"]["rule_version"] = rules["version"]
    return LegacyPositions(snapshot)


def legacy_houses(jd: float, latitude: float, longitude: float,
                   system: bytes = b"P") -> tuple[list[float], float, float]:
    return houses_at_jd(legacy_request(jd), latitude, longitude, system)
