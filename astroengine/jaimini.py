"""Jaimini foundations: Chara karakas, Arudha padas, Chara dasha.

The other great school — sign-based, distinct from the Parashari
system. Rules and disclosed variants in data/jaimini.json.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any
from zoneinfo import ZoneInfo

from .models import ChartRequest
from .rules import load_rules
from .vedic import compute_vedic

_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn",
          "Aquarius", "Pisces"]


def _d1(request: ChartRequest) -> tuple[dict, dict[str, float], int]:
    d1 = compute_vedic(request)
    grahas = d1["grahas"]
    lons = {p: grahas[p]["longitude"] % 360.0 for p in _PLANETS}
    lagna_lon = (d1.get("lagna") or {}).get("longitude")
    if lagna_lon is None:
        raise ValueError("Jaimini computations need a known birth time")
    return d1, lons, int((lagna_lon % 360) // 30)


def _lords() -> dict[str, str]:
    return load_rules("yogas.json")["sign_lords"]


def chara_karakas(request: ChartRequest) -> dict[str, Any]:
    """The seven Chara karakas by intra-sign longitude, descending."""
    corpus = load_rules("jaimini.json")
    _, lons, _ = _d1(request)
    ranked = sorted(_PLANETS, key=lambda p: (lons[p] % 30.0), reverse=True)
    karakas = []
    for name, planet in zip(corpus["karakas"]["order"], ranked):
        karakas.append({"karaka": name, "planet": planet,
                        "intra_sign_degree": round(lons[planet] % 30.0, 4),
                        "sign": _SIGNS[int(lons[planet] // 30)]})
    return {"schema_version": "1.0", "kind": "chara_karakas",
            "rule": corpus["karakas"]["rule"],
            "tie_note": corpus["karakas"]["note"],
            "karakas": karakas}


def arudha_padas(request: ChartRequest) -> dict[str, Any]:
    """The twelve Arudha padas (whole-sign)."""
    corpus = load_rules("jaimini.json")
    _, lons, lagna_sign = _d1(request)
    lords = _lords()
    planet_signs = {p: int(lons[p] // 30) for p in _PLANETS}
    padas = []
    for house in range(1, 13):
        house_sign = (lagna_sign + house - 1) % 12
        lord = lords[_SIGNS[house_sign]]
        lord_sign = planet_signs[lord]
        distance = (lord_sign - house_sign) % 12 + 1
        pada = (lord_sign + distance - 1) % 12
        if (pada - house_sign) % 12 + 1 in (1, 7):
            pada = (pada + 9) % 12  # 10th from the computed pada
        padas.append({"house": house,
                      "house_sign": _SIGNS[house_sign],
                      "lord": lord,
                      "pada_sign": _SIGNS[pada]})
    return {"schema_version": "1.0", "kind": "arudha_padas",
            "method": corpus["arudha"]["method"],
            "exceptions": corpus["arudha"]["exceptions"],
            "padas": padas}


def _chara_years(sign_idx: int, planet_signs: dict[str, int],
                 corpus: dict) -> int:
    lord = _lords()[_SIGNS[sign_idx]]
    lord_sign = planet_signs[lord]
    if lord_sign == sign_idx:
        return corpus["chara_dasha"]["year_special_cases"]["lord_in_own_sign"]
    return (lord_sign - sign_idx) % 12  # count minus one


def chara_dasha(request: ChartRequest,
                as_of: str | None = None) -> dict[str, Any]:
    """Chara dasha: sign sequence with years, current mahadasha/antardasha."""
    corpus = load_rules("jaimini.json")
    _, lons, lagna_sign = _d1(request)
    lords = _lords()
    planet_signs = {p: int(lons[p] // 30) for p in _PLANETS}

    ninth = (lagna_sign + 8) % 12
    forward = ninth % 2 == 0  # odd signs (0-indexed even) -> savya
    step = 1 if forward else -1

    sequence = []
    sign = lagna_sign
    for _ in range(12):
        years = _chara_years(sign, planet_signs, corpus)
        sequence.append({"sign": _SIGNS[sign], "years": years,
                         "lord": lords[_SIGNS[sign]]})
        sign = (sign + step) % 12

    # anchor at birth, walk forward
    birth = _dt.datetime.fromisoformat(request.date)
    if request.time:
        h, m, *_ = request.time.split(":")
        birth = birth.replace(hour=int(h), minute=int(m))
    try:
        tz = ZoneInfo(request.timezone)
    except Exception:
        tz = _dt.timezone.utc
    cursor = birth.replace(tzinfo=tz)
    target = (_dt.datetime.fromisoformat(as_of).replace(tzinfo=tz)
              if as_of else _dt.datetime.now(tz))
    if target.tzinfo is None:
        target = target.replace(tzinfo=tz)

    mahadasha = None
    for dasha in sequence * 20:  # walk cycles until we pass `target`
        start = cursor
        end = start + _dt.timedelta(days=dasha["years"] * 365.25)
        if start <= target < end:
            mahadasha = {**dasha, "start": start.date().isoformat(),
                         "end": end.date().isoformat()}
            # antardashas: 12 equal, from the dasha sign, same direction
            sub_len = _dt.timedelta(days=dasha["years"] * 365.25 / 12.0)
            subs, sub_cursor, ssign = [], start, _SIGNS.index(dasha["sign"])
            for _ in range(12):
                subs.append({"sign": _SIGNS[ssign],
                             "start": sub_cursor.date().isoformat(),
                             "end": (sub_cursor + sub_len).date().isoformat()})
                ssign = (ssign + step) % 12
                sub_cursor += sub_len
            current_sub = next(s for s in subs
                               if s["start"] <= target.date().isoformat()
                               < s["end"])
            mahadasha["antardashas"] = subs
            mahadasha["current_antardasha"] = current_sub["sign"]
            break
        cursor = end

    cfg = corpus["chara_dasha"]
    return {"schema_version": "1.0", "kind": "chara_dasha",
            "school": "Jaimini — not mixed with Parashari timing",
            "start_sign": _SIGNS[lagna_sign],
            "direction": "forward (savya)" if forward
                         else "backward (apasavya)",
            "direction_rule": cfg["direction"],
            "year_rule": cfg["year_rule"],
            "variants": cfg["variants"],
            "sequence": sequence,
            "current": mahadasha}


def render_jaimini(karakas: dict, padas: dict, dasha: dict) -> str:
    lines = ["Jaimini foundations — the other great school", "",
             "Chara karakas:"]
    for k in karakas["karakas"]:
        lines.append(f"  {k['karaka']:14s} {k['planet']:8s} "
                     f"{k['intra_sign_degree']:.2f}° in {k['sign']}")
    lines += ["", "Arudha padas:"]
    for p in padas["padas"]:
        marker = " ← Arudha Lagna" if p["house"] == 1 else ""
        lines.append(f"  house {p['house']:2d} ({p['house_sign']:11s}, "
                     f"lord {p['lord']:8s}) → {p['pada_sign']}{marker}")
    lines += ["", f"Chara dasha — from {dasha['start_sign']}, "
                   f"{dasha['direction']}:"]
    for s in dasha["sequence"]:
        lines.append(f"  {s['sign']:11s} {s['years']:2d} years "
                     f"(lord {s['lord']})")
    cur = dasha.get("current")
    if cur:
        lines += ["", f"Current: {cur['sign']} mahadasha "
                       f"({cur['start']} → {cur['end']}), "
                       f"antardasha {cur['current_antardasha']}"]
    return "\n".join(lines)
