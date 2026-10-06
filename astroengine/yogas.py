"""Yoga engine: the great combinations of Jyotisha.

Detects the classical yogas from the D1 chart (whole-sign houses from
Lagna). Definitions live in data/yogas.json with sources and variants.
The engine computes *presence* from stated rules; the interpretive
weight the tradition gives each yoga is labeled lore, never fact.
"""

from __future__ import annotations

from typing import Any

from .models import ChartRequest
from .rules import load_rules
from .vedic import compute_vedic

_KENDRA = {1, 4, 7, 10}
_TRIKONA = {1, 5, 9}
_MAHAPURUSHA = {"Mars": "Ruchaka", "Mercury": "Bhadra",
                "Jupiter": "Hamsa", "Venus": "Malavya",
                "Saturn": "Shasha"}
_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn",
          "Aquarius", "Pisces"]


def _house(planet_sign: int, lagna_sign: int) -> int:
    return (planet_sign - lagna_sign) % 12 + 1


def _in_own_or_exalted(planet: str, sign: str, corpus: dict) -> bool:
    return (corpus["sign_lords"][sign] == planet
            or corpus["exaltation"].get(planet) == sign)


def _sambandha(a: str, b: str, signs: dict[str, int],
               lords: dict[str, str]) -> str | None:
    """Relationship between two planets: conjunction, mutual kendra, exchange."""
    sa, sb = signs[a], signs[b]
    if sa == sb:
        return "conjunction"
    ha = _house(sb, sa)
    hb = _house(sa, sb)
    if ha in _KENDRA and hb in _KENDRA:
        return "mutual kendra"
    if lords[_SIGNS[sa]] == b and lords[_SIGNS[sb]] == a:
        return "exchange of signs (parivartana)"
    return None


def detect_yogas(request: ChartRequest) -> dict[str, Any]:
    """Detect the great yogas in the D1 chart."""
    corpus = load_rules("yogas.json")
    lords = corpus["sign_lords"]
    d1 = compute_vedic(request)
    grahas = d1["grahas"]
    signs = {name: g["sign_index"] for name, g in grahas.items()
             if g.get("sign_index") is not None and name in
             ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")}
    lagna = (d1.get("lagna") or {}).get("longitude")
    lagna_sign = int((lagna % 360) // 30) if lagna is not None else None
    defs = corpus["yogas"]
    found: list[dict[str, Any]] = []

    def add(key: str, present: bool, planets: list[str],
            details: str) -> None:
        d = defs[key]
        found.append({"yoga": d["name"], "present": present,
                      "planets": planets, "details": details,
                      "rule": d["rule"], "signification": d["signification"],
                      "source": d["source"], "variants": d["variants"]})

    moon_sign = signs.get("Moon")
    jup_sign = signs.get("Jupiter")

    # Pancha Mahapurusha
    if lagna_sign is not None:
        for planet, yoga_name in _MAHAPURUSHA.items():
            s = signs.get(planet)
            if s is None:
                continue
            house = _house(s, lagna_sign)
            if house in _KENDRA and _in_own_or_exalted(
                    planet, _SIGNS[s], corpus):
                add("pancha_mahapurusha", True, [planet],
                    f"{yoga_name}: {planet} in {_SIGNS[s]} "
                    f"({'own' if lords[_SIGNS[s]] == planet else 'exalted'}), "
                    f"{house}th from Lagna")
    # Gaja Kesari
    if moon_sign is not None and jup_sign is not None:
        h = _house(jup_sign, moon_sign)
        add("gaja_kesari", h in _KENDRA, ["Jupiter", "Moon"],
            f"Jupiter {h}th from the Moon"
            + (" — kendra" if h in _KENDRA else ""))
    # Budha-Aditya
    sun_sign, mer_sign = signs.get("Sun"), signs.get("Mercury")
    if sun_sign is not None and mer_sign is not None:
        add("budha_aditya", sun_sign == mer_sign, ["Sun", "Mercury"],
            "Sun and Mercury share "
            f"{_SIGNS[sun_sign]}" if sun_sign == mer_sign
            else f"Sun in {_SIGNS[sun_sign]}, Mercury in {_SIGNS[mer_sign]}")
    # Dhana yogas: lords of 2/5/9/11 among themselves
    if lagna_sign is not None:
        dhana_lords = {}
        for house in (2, 5, 9, 11):
            sign = _SIGNS[(lagna_sign + house - 1) % 12]
            dhana_lords[lords[sign]] = house
        lords_list = sorted(set(dhana_lords))
        for i, a in enumerate(lords_list):
            for b in lords_list[i + 1:]:
                if a not in signs or b not in signs:
                    continue
                rel = _sambandha(a, b, signs, lords)
                if rel:
                    add("dhana", True, [a, b],
                        f"lords of {dhana_lords[a]}th and {dhana_lords[b]}th "
                        f"in {rel}")
    # Raja yogas: kendra lord + trikona lord sambandha
    if lagna_sign is not None:
        kendra_lords = {lords[_SIGNS[(lagna_sign + h - 1) % 12]]
                        for h in _KENDRA}
        trikona_lords = {lords[_SIGNS[(lagna_sign + h - 1) % 12]]
                         for h in _TRIKONA}
        seen = set()
        for k in sorted(kendra_lords):
            for t in sorted(trikona_lords):
                if k == t or (k, t) in seen or k not in signs or t not in signs:
                    continue
                seen.add((k, t))
                rel = _sambandha(k, t, signs, lords)
                if rel:
                    kh = next(h for h in _KENDRA
                              if lords[_SIGNS[(lagna_sign + h - 1) % 12]] == k)
                    th = next(h for h in _TRIKONA
                              if lords[_SIGNS[(lagna_sign + h - 1) % 12]] == t)
                    premier = {kh, th} == {9, 10}
                    add("raja", True, [k, t],
                        f"{kh}th lord {k} and {th}th lord {t} in {rel}"
                        + (" — the premier 9th+10th combination" if premier
                           else ""))
    # Kemadruma
    if moon_sign is not None:
        others = [n for n in signs if n not in ("Sun", "Moon")]
        flanked = any(_house(signs[n], moon_sign) in (2, 12)
                      for n in others)
        bhanga = []
        if lagna_sign is not None and _house(moon_sign, lagna_sign) in _KENDRA:
            bhanga.append("Moon in kendra from Lagna")
        add("kemadruma", not flanked,
            ["Moon"], "no planets in 2nd/12th from the Moon"
            + ("; bhanga flags: " + "; ".join(bhanga) if bhanga and not flanked
               else ""))
    # Sakata
    if moon_sign is not None and jup_sign is not None:
        h = _house(jup_sign, moon_sign)
        add("sakata", h in (6, 8, 12), ["Jupiter", "Moon"],
            f"Jupiter {h}th from the Moon")

    present = [y for y in found if y["present"]]
    return {"schema_version": "1.0", "kind": "yogas", "d1": d1,
            "method": "whole-sign houses from Lagna; definitions per "
                      + corpus["source"],
            "rule_version": corpus["version"],
            "yogas": found, "present_count": len(present)}


def render_yogas(report: dict) -> str:
    lines = ["The great yogas — computed patterns, traditional lore", ""]
    present = [y for y in report["yogas"] if y["present"]]
    if not present:
        lines.append("  No great yogas detected in this chart.")
    for y in present:
        lines.append(f"  ◆ {y['yoga']}")
        lines.append(f"    {y['details']}")
        lines.append(f"    Lore: {y['signification']} ({y['source']})")
    absent = [y["yoga"] for y in report["yogas"] if not y["present"]]
    if absent:
        lines += ["", f"  Absent: {', '.join(sorted(set(absent)))}"]
    return "\n".join(lines)
