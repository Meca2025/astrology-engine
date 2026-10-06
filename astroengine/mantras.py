"""Remedial Vedic mantras: the traditional songs for pressured planets.

Takes the forecast's affliction signals and answers with mantras from
data/mantras.json — ancient public-domain verses, never invented.
Framed as devotional practice, never medical, never guaranteed.
"""

from __future__ import annotations

from typing import Any

from .models import CalculationError
from .rules import load_rules

_HARD = {"conjunction", "opposition", "square"}
_MALEFICS = {"Mars", "Saturn", "Uranus", "Neptune", "Pluto"}


def _corpus() -> dict:
    return load_rules("mantras.json")


def all_mantras() -> dict[str, Any]:
    """The whole graha → mantra corpus."""
    return _corpus()["grahas"]


def mantras_for(planet: str) -> dict[str, Any]:
    """Return the mantra set for one graha; raises on unknown names."""
    grahas = _corpus()["grahas"]
    if planet not in grahas:
        raise CalculationError(
            f"unknown graha '{planet}'; choose from {', '.join(sorted(grahas))}")
    return {"planet": planet, **grahas[planet]}


def remedies_for(afflictions: dict[str, Any],
                 active_transits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Recommend mantras from affliction signals, each with a reason.

    `afflictions` is the forecast's afflictions block; `active_transits`
    is its transit list. Deduplicated by planet, dasha lords first.
    """
    corpus = _corpus()["grahas"]
    ordered: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(planet: str, reason: str) -> None:
        if planet in corpus and planet not in seen:
            seen.add(planet)
            ordered.append((planet, reason))

    dasha = afflictions.get("dasha_lords") or {}
    if dasha.get("mahadasa") in corpus:
        add(dasha["mahadasa"], f"{dasha['mahadasa']} — mahadasha lord")
    if dasha.get("antardasha") in corpus:
        add(dasha["antardasha"], f"{dasha['antardasha']} — antardasha lord")

    for point in afflictions.get("pressured_planets", []):
        hits = [h for h in active_transits
                if h.get("natal_point") == point
                and h.get("aspect") in _HARD
                and h.get("transit_body") in _MALEFICS]
        if not hits:
            continue
        detail = "; ".join(
            f"{h['transit_body']} {h['aspect']} (orb {h['orb']}°)"
            for h in sorted(hits, key=lambda h: h["orb"])[:2])
        add(point, f"{point} — pressured: {detail}")

    remedies = []
    for planet, reason in ordered:
        entry = {"planet": planet, "deity": corpus[planet]["deity"],
                 "reason": reason, "mantras": corpus[planet]["mantras"]}
        remedies.append(entry)
    return remedies


def render_remedies(remedies: list[dict[str, Any]]) -> str:
    lines = ["REMEDIES — traditional Vedic mantras (devotional, not medical)",
             ""]
    if not remedies:
        return "\n".join(lines + ["  No strong pressures today — a simple "
                                  "gratitude mantra suffices: Om Shantih."])
    for r in remedies:
        lines.append(f"  {r['planet']} ({r['deity']}) — {r['reason']}")
        for m in r["mantras"]:
            lines.append(f"    {m['text']}  ×{m['repetitions']} — {m['purpose']}")
    return "\n".join(lines)
