"""Shadbala: the sixfold strength of planets.

Computes Sthana, Dig, Kala, Chesta, Naisargika and Drik bala in
virupas (60 virupas = 1 rupa) against the classical minima.
Constant tables live in data/shadbala.json; approximations are
disclosed in `limitations` — this is the classical structure with
honestly simplified components, not a claim of exact traditional
parity.
"""

from __future__ import annotations

import math
from typing import Any

from .electional import planetary_hour, solar_day_events
from .inputs import resolve_utc
from .legacy_astronomy import legacy_positions, legacy_request
from .models import CalculationError, ChartRequest
from .rules import load_rules
from .vargas import varga_position
from .vedic import compute_vedic

_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn",
          "Aquarius", "Pisces"]
_KENDRA = {1, 4, 7, 10}
_PANAPARA = {2, 5, 8, 11}


def _house(planet_sign: int, ref_sign: int) -> int:
    return (planet_sign - ref_sign) % 12 + 1


def _swe_jd(dt) -> float:
    import swisseph as _swe
    return _swe.julday(dt.year, dt.month, dt.day,
                       dt.hour + dt.minute / 60.0 + dt.second / 3600.0,
                       _swe.GREG_CAL)


def _panchadha(planet: str, varga_sign: str,
               others: dict[str, str], corpus: dict) -> str:
    """Panchadha dignity of `planet` in one varga.

    Relationship is with the lord of the occupied varga sign:
    natural (naisargika) combined with temporal (tatkalika, from
    varga positions — one of the two classical opinions, disclosed).
    """
    if corpus["moolatrikona"].get(planet) == varga_sign:
        return "moolatrikona"
    lords = load_rules("yogas.json")["sign_lords"]
    lord = lords[varga_sign]
    if lord == planet:
        return "own"
    nf = corpus["natural_friends"].get(planet, [])
    ne = corpus["natural_enemies"].get(planet, [])
    natural = ("friend" if lord in nf else
               "enemy" if lord in ne else "neutral")
    temporal_friend = _house(_SIGNS.index(others[lord]),
                             _SIGNS.index(varga_sign)) in (2, 3, 4, 10, 11, 12)
    if natural == "friend" and temporal_friend:
        return "adhimitra"
    if natural == "friend" and not temporal_friend:
        return "sama"
    if natural == "neutral" and temporal_friend:
        return "mitra"
    if natural == "neutral" and not temporal_friend:
        return "shatru"
    if natural == "enemy" and temporal_friend:
        return "sama"
    return "adhishatru"


def _saptavargaja(planet: str, longitudes: dict[str, float],
                  corpus: dict) -> float:
    total = 0.0
    dignity_scale = corpus["saptavargaja_dignity"]
    others_all = {p: None for p in _PLANETS}
    for div in corpus["saptavargaja_divisions"]:
        vsigns = {}
        for p in _PLANETS:
            vsigns[p] = varga_position(longitudes[p], div)["sign"]
        others = {p: s for p, s in vsigns.items() if p != planet}
        dignity = _panchadha(planet, vsigns[planet], others, corpus)
        total += dignity_scale[dignity]
    return total


def shadbala(request: ChartRequest) -> dict[str, Any]:
    """Compute the sixfold strength for Sun..Saturn."""
    corpus = load_rules("shadbala.json")
    d1 = compute_vedic(request)
    grahas = d1["grahas"]
    longitudes = {p: grahas[p]["longitude"] % 360.0 for p in _PLANETS}
    signs = {p: int(longitudes[p] // 30) for p in _PLANETS}
    lagna_lon = (d1.get("lagna") or {}).get("longitude")
    if lagna_lon is None:
        raise CalculationError("Shadbala needs a known birth time (Lagna)")
    lagna_sign = int((lagna_lon % 360) // 30)

    utc = resolve_utc(request)
    natal_jd = _swe_jd(utc)
    speeds = {}
    tpos = legacy_positions(natal_jd, True)
    for p in _PLANETS:
        speeds[p] = (tpos.get(p) or {}).get("speed")

    # Kala helpers
    ph = planetary_hour(natal_jd, request.latitude, request.longitude,
                        request.timezone)
    sect = (ph or {}).get("sect", "day")
    hora_lord = (ph or {}).get("hour_ruler")
    vara_lord = (ph or {}).get("day_ruler")
    elongation = (longitudes["Moon"] - longitudes["Sun"]) % 360.0
    waxing = elongation < 180.0
    eps = math.radians(23.44)
    sun_decl = math.degrees(math.asin(
        math.sin(math.radians(longitudes["Sun"])) * math.sin(eps)))
    try:
        sunrise, sunset, _ = solar_day_events(
            legacy_request(natal_jd - 1.0), request.latitude,
            request.longitude)
        day_third = None
        if sunrise <= natal_jd <= sunset:
            day_third = min(2, int((natal_jd - sunrise)
                                   / ((sunset - sunrise) / 3.0)))
    except CalculationError:
        day_third = None

    kala_cfg = corpus["kala"]
    result: dict[str, Any] = {}
    for planet in _PLANETS:
        comp: dict[str, float] = {}
        lon, sign = longitudes[planet], signs[planet]

        # --- Sthana ---
        ex_sign, ex_deg = corpus["exaltation_points"][planet]
        neecha_lon = (_SIGNS.index(ex_sign) * 30 + ex_deg + 180.0) % 360.0
        d = (lon - neecha_lon) % 360.0
        comp["uchcha"] = round((180.0 - abs(d - 180.0)) / 3.0, 2)
        comp["saptavargaja"] = round(_saptavargaja(planet, longitudes, corpus), 2)
        nav_sign = varga_position(lon, 9)["sign"]
        ojjha = corpus["ojhayugma_groups"]
        rasi_ok = ((sign % 2 == 0) == (planet in ojjha["odd"]))
        nav_ok = ((_SIGNS.index(nav_sign) % 2 == 0) == (planet in ojjha["odd"]))
        comp["ojhayugma"] = float(15 * rasi_ok + 15 * nav_ok)
        house = _house(sign, lagna_sign)
        comp["kendradi"] = float(60 if house in _KENDRA
                                else 30 if house in _PANAPARA else 15)
        drekkana = int((lon % 30) // 10)
        dgroup = corpus["drekkana_groups"]
        want = (0 if planet in dgroup["male"]
                else 1 if planet in dgroup["neuter"] else 2)
        comp["drekkana"] = 15.0 if drekkana == want else 0.0
        comp["sthana"] = round(sum(comp[k] for k in
                                   ("uchcha", "saptavargaja", "ojhayugma",
                                    "kendradi", "drekkana")), 2)

        # --- Dig ---
        peak = corpus["dig_peaks"][planet]
        hdiff = min((house - peak) % 12, (peak - house) % 12)
        comp["dig"] = round(60.0 * (1.0 - hdiff / 6.0), 2)

        # --- Kala ---
        day_p, night_p = kala_cfg["day_planets"], kala_cfg["night_planets"]
        if planet == "Mercury":
            comp["natonnata"] = 60.0
        elif sect == "day":
            comp["natonnata"] = 60.0 if planet in day_p else 0.0
        else:
            comp["natonnata"] = 60.0 if planet in night_p else 0.0
        benefic = planet in kala_cfg["paksha_benefic"]
        if planet == "Moon":
            benefic = waxing
        comp["paksha"] = 60.0 if (benefic == waxing) else 0.0
        comp["tribhaga"] = 0.0
        if day_third is not None:
            groups = kala_cfg["tribhaga_day"]
            key = f"part{day_third + 1}"
            members = groups[key] if sect == "day" else groups[
                f"part{3 - day_third}"]
            comp["tribhaga"] = 60.0 if planet in members else 0.0
        comp["vara"] = float(kala_cfg["vara_bala"]
                            if vara_lord == planet else 0.0)
        comp["hora"] = float(kala_cfg["hora_bala"]
                            if hora_lord == planet else 0.0)
        ayana = kala_cfg["ayana_groups"]
        uttarayana_now = sun_decl >= 0
        if planet in ayana["ubhayana"]:
            # Mercury draws from both ayanas; use the current one
            group = "uttarayana" if uttarayana_now else "dakshinayana"
        elif planet in ayana["uttarayana"]:
            group = "uttarayana"
        else:
            group = "dakshinayana"
        if group == "uttarayana":
            comp["ayana"] = round(60.0 * (sun_decl + 23.44) / 46.88, 2)
        else:
            comp["ayana"] = round(60.0 * (23.44 - sun_decl) / 46.88, 2)
        comp["kala"] = round(sum(comp[k] for k in
                                 ("natonnata", "paksha", "tribhaga", "vara",
                                  "hora", "ayana")), 2)

        # --- Chesta ---
        if planet in ("Sun", "Moon"):
            comp["chesta"] = 30.0
        else:
            speed = speeds.get(planet)
            mean = corpus["chesta_means"][planet]
            if speed is None or mean == 0:
                comp["chesta"] = 30.0
            else:
                r = speed / mean
                if abs(speed) < 0.02 * mean:
                    comp["chesta"] = 15.0  # Vikala, stationary
                elif speed < 0 and abs(r) > 0.5:
                    comp["chesta"] = 60.0  # Vakra
                elif speed < 0:
                    comp["chesta"] = 30.0  # Anuvakra
                elif r > 1.1:
                    comp["chesta"] = 45.0  # Atichara
                elif r > 0.3:
                    comp["chesta"] = 30.0  # Sama/Chara
                else:
                    comp["chesta"] = 15.0  # Manda
        comp["chesta"] = float(comp["chesta"])

        # --- Naisargika ---
        comp["naisargika"] = float(corpus["naisargika"][planet])

        # --- Drik ---
        special = corpus["special_aspects"]
        bpos, mpos = 0.0, 0.0
        for q in _PLANETS:
            if q == planet:
                continue
            aspects = {7} | set(special.get(q, []))
            if _house(sign, signs[q]) in aspects:
                q_benefic = q in ("Jupiter", "Venus", "Mercury") or (
                    q == "Moon" and waxing)
                if q_benefic:
                    bpos += 60.0
                else:
                    mpos += 60.0
        comp["drik"] = round(max(-60.0, min(60.0, (bpos - mpos) / 4.0)), 2)

        total = round(comp["sthana"] + comp["dig"] + comp["kala"]
                      + comp["chesta"] + comp["naisargika"] + comp["drik"], 2)
        rupas = round(total / 60.0, 2)
        minimum = corpus["minima_rupas"][planet]
        result[planet] = {"components": comp, "virupas": total,
                          "rupas": rupas, "minimum_rupas": minimum,
                          "ratio": round(rupas / minimum, 2),
                          "strong": rupas >= minimum}

    return {"schema_version": "1.0", "kind": "shadbala",
            "method": "sixfold strength in virupas; classical structure, "
                      "simplified components — see limitations",
            "rule_version": corpus["version"],
            "limitations": corpus["limitations"],
            "planets": result}
