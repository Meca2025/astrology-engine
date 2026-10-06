"""Ashtakavarga: the 337 bindus.

Each planet's Bhinnashtakavarga counts benefic points (bindus) in
each sign from eight reference points (the seven planets + Lagna).
The Sarvashtakavarga sums all seven: always 337, in every chart.
Tables per B.V. Raman in data/ashtakavarga.json. Reading notes are
labeled lore; Trikona/Ekadhipatya reductions are future work.
"""

from __future__ import annotations

from typing import Any

from .models import ChartRequest
from .rules import load_rules
from .vedic import compute_vedic

_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn",
          "Aquarius", "Pisces"]


def bhinna(signs: dict[str, int], lagna_sign: int) -> dict[str, Any]:
    """Pure Ashtakavarga from sign indices (0=Aries).

    `signs`: planet -> sign index for Sun..Saturn.
    Returns the seven BAVs (bindus per sign, Aries first),
    the Sarvashtakavarga, and per-planet totals.
    """
    tables = load_rules("ashtakavarga.json")["benefic_places"]
    refs = {**signs, "Lagna": lagna_sign}
    bavs: dict[str, list[int]] = {}
    for planet in _PLANETS:
        row = [0] * 12
        for contributor, houses in tables[planet].items():
            csign = refs[contributor]
            for house in houses:
                row[(csign + house - 1) % 12] += 1
        bavs[planet] = row
    sav = [sum(bavs[p][i] for p in _PLANETS) for i in range(12)]
    return {"bhinna": bavs,
            "sarvashtakavarga": sav,
            "totals": {p: sum(bavs[p]) for p in _PLANETS},
            "sav_total": sum(sav)}


def compute_ashtakavarga(request: ChartRequest) -> dict[str, Any]:
    """Ashtakavarga from the D1 chart."""
    corpus = load_rules("ashtakavarga.json")
    d1 = compute_vedic(request)
    grahas = d1["grahas"]
    signs = {p: grahas[p]["sign_index"] % 12 for p in _PLANETS}
    lagna_lon = (d1.get("lagna") or {}).get("longitude")
    if lagna_lon is None:
        raise ValueError("Ashtakavarga needs a known birth time (Lagna)")
    lagna_sign = int((lagna_lon % 360) // 30)
    result = bhinna(signs, lagna_sign)
    lore = corpus["reading_lore"]
    weak = [(_SIGNS[i], v) for i, v in enumerate(result["sarvashtakavarga"])
            if v < 28]
    strong = [(_SIGNS[i], v) for i, v in enumerate(result["sarvashtakavarga"])
              if v > 30]
    return {"schema_version": "1.0", "kind": "ashtakavarga",
            "method": "Bhinnashtakavarga per B.V. Raman; Lagna included "
                      "as eighth contributor",
            "rule_version": corpus["version"],
            "source": corpus["source"],
            "future_work": corpus["future_work"],
            **result,
            "signs": {p: _SIGNS[signs[p]] for p in _PLANETS},
            "lagna": _SIGNS[lagna_sign],
            "reading": {"weak_signs": weak, "strong_signs": strong,
                        "weak_note": lore["sav_weak"],
                        "strong_note": lore["sav_strong"]}}


def render_ashtakavarga(report: dict) -> str:
    lines = ["Ashtakavarga — the 337 bindus", "",
             "Sign      " + " ".join(f"{s[:3]:>4}" for s in _SIGNS)]
    for planet in _PLANETS:
        row = report["bhinna"][planet]
        lines.append(f"{planet:8s}  " + " ".join(f"{v:>4}" for v in row)
                     + f"  = {sum(row)}")
    sav = report["sarvashtakavarga"]
    lines.append(f"{'SAV':8s}  " + " ".join(f"{v:>4}" for v in sav)
                 + f"  = {sum(sav)}")
    weak = ", ".join(f"{s} ({v})" for s, v in report["reading"]["weak_signs"])
    strong = ", ".join(f"{s} ({v})" for s, v in report["reading"]["strong_signs"])
    lines += ["", f"Weak signs (SAV<28): {weak or 'none'}",
              f"Strong signs (SAV>30): {strong or 'none'}"]
    return "\n".join(lines)
