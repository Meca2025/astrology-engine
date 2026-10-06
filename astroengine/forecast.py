"""Daily forecast: one seeker, one day, every system we have.

Gathers computed facts from the Western, Vedic, Chinese, Tibetan and
runic arts for a target date, then renders a labeled symbolic reading.
Computation and interpretation are kept in separate keys; the reading
is symbolic and non-deterministic, never a prediction of events.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any
from zoneinfo import ZoneInfo

from .bazi import pillars as bazi_pillars
from .chinese import zodiac as chinese_zodiac
from .dashas import active_period, compute_dashas
from .houses import house_cusps
from .legacy_astronomy import legacy_positions
from .models import CalculationError, ChartRequest
from .panchanga import compute_panchanga
from .runic import half_month_rune
from .tibetan import tibetan as tibetan_year
from .watch import upcoming_transits

_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars",
           "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
_ASPECTS = (("conjunction", 0.0), ("opposition", 180.0),
            ("square", 90.0), ("trine", 120.0), ("sextile", 60.0))
_HARD_ASPECTS = {"conjunction", "opposition", "square"}
_MALEFICS = {"Mars", "Saturn", "Uranus", "Neptune", "Pluto"}
_ORB = 1.5

_GENERATES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal",
              "Metal": "Water", "Water": "Wood"}
_CONTROLS = {"Wood": "Earth", "Fire": "Metal", "Earth": "Water",
             "Metal": "Wood", "Water": "Fire"}


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _jd(y: int, m: int, d: int, hour: float) -> float:
    import swisseph as _swe
    return _swe.julday(y, m, d, hour, _swe.GREG_CAL)


def _element_relation(a: str, b: str) -> str:
    if a == b:
        return "same element — resonance"
    if _GENERATES.get(a) == b:
        return f"{a} generates {b} — supportive flow"
    if _GENERATES.get(b) == a:
        return f"{b} generates {a} — you feed the day"
    if _CONTROLS.get(a) == b:
        return f"{a} controls {b} — friction, handle with care"
    if _CONTROLS.get(b) == a:
        return f"{b} controls {a} — the day presses on you"
    return "no direct elemental tie"


def _day_transits(natal_jd: float, target_jd: float, target_iso: str,
                  lat: float, lon: float) -> dict[str, Any]:
    natal = legacy_positions(natal_jd, True)
    points: dict[str, float] = {}
    for body in _BODIES:
        p = natal.get(body) or {}
        if p.get("longitude") is not None:
            points[body] = p["longitude"] % 360.0
    _, asc, mc = house_cusps(natal_jd, lat, lon, "placidus")
    points["ASC"] = asc % 360.0
    points["MC"] = mc % 360.0

    tpos = legacy_positions(target_jd, True)
    active: list[dict[str, Any]] = []
    for tbody in _BODIES:
        tp = tpos.get(tbody) or {}
        if tp.get("longitude") is None:
            continue
        tlon = tp["longitude"] % 360.0
        for pname, plon in points.items():
            if tbody == pname:
                continue
            sep = _sep(tlon, plon)
            for aname, target in _ASPECTS:
                orb = abs(sep - target)
                if orb <= _ORB:
                    active.append({"transit_body": tbody, "natal_point": pname,
                                   "aspect": aname, "orb": round(orb, 2)})
    active.sort(key=lambda h: h["orb"])

    exact = upcoming_transits(natal_jd, target_jd - 4.0, target_jd + 4.0,
                              lat, lon, orb=1.0)
    # hits carry 'date' as YYYY-MM-DD strings; keep those landing on the day
    exact_today = [h for h in exact if h.get("date") == target_iso]

    # Stations and ingresses: compare day-1, day, day+1 at noon UT.
    stations: list[dict[str, Any]] = []
    ingresses: list[dict[str, Any]] = []
    prev = legacy_positions(target_jd - 1.0, True)
    now = tpos
    nxt = legacy_positions(target_jd + 1.0, True)
    for body in _BODIES:
        p0, p1, p2 = prev.get(body) or {}, now.get(body) or {}, nxt.get(body) or {}
        if p1.get("longitude") is None:
            continue
        s0, s1 = int((p0.get("longitude", 0) % 360) // 30), int((p1["longitude"] % 360) // 30)
        if p0.get("longitude") is not None and s0 != s1:
            ingresses.append({"body": body,
                              "sign": p1.get("sign", "?")})
        v0, v1 = (p0.get("speed"), p1.get("speed"))
        v2 = p2.get("speed")
        if v0 is not None and v1 is not None and v2 is not None:
            if (v0 > 0) != (v1 > 0) or (v1 > 0) != (v2 > 0):
                stations.append({"body": body,
                                 "direction": "direct" if v1 > 0 else "retrograde"})
    return {"active": active, "exact_today": exact_today,
            "stations": stations, "ingresses": ingresses}


def _branch_animal(branch: str, corpus: dict) -> str:
    for b in corpus["branches"]:
        if b["name"] == branch:
            return b["animal"]
    raise CalculationError(f"unknown branch '{branch}'")


def daily_forecast(natal_jd_ut: float, lat: float, lon: float, name: str,
                   birth: ChartRequest, target_iso: str) -> dict[str, Any]:
    """Build the full daily forecast as structured data."""
    try:
        target = _dt.date.fromisoformat(target_iso)
    except ValueError as exc:
        raise CalculationError(
            f"bad target date '{target_iso}'; use YYYY-MM-DD") from exc
    tz = birth.timezone
    target_jd = _jd(target.year, target.month, target.day, 12.0)

    sky = _day_transits(natal_jd_ut, target_jd, target_iso, lat, lon)

    day_req = ChartRequest(date=target_iso, time="12:00", latitude=lat,
                           longitude=lon, timezone=tz, zodiac="sidereal",
                           house_system="whole-sign")
    pan_full = compute_panchanga(day_req)
    pan = pan_full["elements"]
    vara = pan_full.get("vara") or pan_full.get("civil_weekday") or "unknown vara"

    _elname = _element_name

    timeline = compute_dashas(birth)["timeline"]
    noon_utc = _dt.datetime(target.year, target.month, target.day, 12, 0,
                            tzinfo=_dt.timezone.utc)
    dasha = active_period(timeline, noon_utc) or {"mahadasa": "unknown",
                                                  "antardasha": "unknown"}
    from .recovery import graceful
    degraded: list[str] = []

    def _optional(label, fn, fallback):
        ok, result, error = graceful(label, fn)
        if not ok:
            degraded.append(f"{label} unavailable: {error}")
            return fallback
        return result

    def _chara_block():
        from .jaimini import chara_dasha
        _chara = chara_dasha(birth, as_of=target_iso)
        _chara_cur = _chara.get("current") or {}
        return {"mahadasha": _chara_cur.get("sign", "unknown"),
                "antardasha": _chara_cur.get("current_antardasha",
                                             "unknown"),
                "direction": _chara.get("direction", ""),
                "school": "Jaimini"}

    jaimini_dasha = _optional(
        "Jaimini Chara dasha", _chara_block,
        {"mahadasha": "unknown", "antardasha": "unknown",
         "direction": "", "school": "Jaimini"})

    natal_pillars = bazi_pillars(birth.date, birth.time or "12:00", tz)
    day_pillar = bazi_pillars(target_iso, "12:00", tz)["day"]
    day_branch, day_stem = day_pillar["branch"], day_pillar["stem"]

    from .chinese import _corpus as _chinese_corpus
    zc = _chinese_corpus()
    day_animal = _branch_animal(day_branch, zc)
    birth_animal = chinese_zodiac(birth.date)["animal"]

    def branch_tie(a: str, b: str) -> str:
        if a == b:
            return "same branch — doubled emphasis"
        if zc["clashes"].get(a) == b:
            return "clash — friction, best met with flexibility"
        if zc["secret_friends"].get(a) == b:
            return "secret friend — quiet support"
        for trine in zc["trines"]:
            if a in trine and b in trine:
                return "trine ally — harmonious flow"
        return "no special branch tie"

    pillar_relations = {}
    for pname in ("year", "month", "day", "hour"):
        pb = natal_pillars[pname]
        pillar_relations[pname] = {
            "pillar": f"{pb['stem']}-{pb['branch']}",
            "branch_tie": branch_tie(day_branch, pb["branch"]),
        }

    day_master = natal_pillars["day"]["stem"]
    stem_el = {s["name"]: s["element"] for s in zc["stems"]}
    day_element = stem_el[day_stem]
    master_element = stem_el[day_master]

    def _tibetan_block():
        natal_tib = tibetan_year(birth.date)
        day_tib = tibetan_year(target_iso)
        return {"natal": natal_tib, "day": day_tib,
                "relation": _element_relation(day_element,
                                              natal_tib["element"])}

    _tib = _optional("Tibetan year", _tibetan_block,
                     {"natal": {}, "day": {}, "relation": "unknown"})
    natal_tib, day_tib, tib_relation = _tib["natal"], _tib["day"], _tib["relation"]

    def _runic_block():
        rune_raw = half_month_rune(target_iso)
        return {"name": rune_raw.get("rune"),
                "meaning": (rune_raw.get("correspondences") or {}).get("symbolic_meaning")}

    rune = _optional("runic half-month", _runic_block,
                     {"name": "unknown", "meaning": None})

    animal_tie = branch_tie(
        next(b["name"] for b in zc["branches"] if b["animal"] == day_animal),
        next(b["name"] for b in zc["branches"] if b["animal"] == birth_animal))

    pressured = sorted({h["natal_point"] for h in sky["active"]
                        if h["aspect"] in _HARD_ASPECTS
                        and h["transit_body"] in _MALEFICS})
    clashing = [k for k, v in pillar_relations.items()
                if v["branch_tie"].startswith("clash")]

    computed: dict[str, Any] = {
        "target_date": target_iso,
        "name": name,
        "transits": sky,
        "panchanga": {"tithi": _elname(pan.get("tithi")), "vara": vara,
                      "nakshatra": _elname(pan.get("nakshatra")),
                      "yoga": _elname(pan.get("yoga")),
                      "karana": _elname(pan.get("karana"))},
        "dasha": dasha,
        "jaimini_dasha": jaimini_dasha,
        "bazi_day": {"stem_branch": f"{day_stem}-{day_branch}",
                     "element": day_element, "animal": day_animal,
                     "pillar_relations": pillar_relations,
                     "day_master": day_master,
                     "day_master_element": master_element,
                     "element_relation_to_day_master":
                         _element_relation(day_element, master_element)},
        "tibetan": {"day_element": day_element,
                    "natal_year": natal_tib.get("year_name"),
                    "natal_element": natal_tib.get("element"),
                    "element_relation": tib_relation,
                    "natal_mewa": _elname(natal_tib.get("mewa")),
                    "natal_parkha": (_element_name(natal_tib.get("parkha")) + ""
                                     if not isinstance(natal_tib.get("parkha"), dict)
                                     else natal_tib["parkha"]["name"])},
        "rune": {"name": rune.get("name"),
                 "meaning": rune.get("meaning") or rune.get("summary")},
        "zodiac_day": {"animal": day_animal, "birth_animal": birth_animal,
                       "tie": animal_tie},
        "degraded": degraded,
        "afflictions": {"pressured_planets": pressured,
                        "dasha_lords": dasha,
                        "clashing_pillars": clashing},
    }

    n_hard = sum(1 for h in sky["active"] if h["aspect"] in _HARD_ASPECTS)
    reading = {
        "note": "Symbolic reading — an interpretive synthesis of computed "
                "facts, not a prediction of events."
                + (" Degraded sections: " + "; ".join(degraded) + "."
                   if degraded else ""),
        "western": _western_reading(sky, n_hard),
        "vedic": _vedic_reading(pan, dasha, vara, jaimini_dasha),
        "chinese": _chinese_reading(day_stem, day_branch, day_animal,
                                    pillar_relations, day_element,
                                    master_element),
        "tibetan": _tibetan_reading(
            day_element, natal_tib.get("element"), tib_relation,
            computed["tibetan"]["natal_mewa"],
            computed["tibetan"]["natal_parkha"])
        if not any(d.startswith("Tibetan year") for d in degraded)
        else "Tibetan astrology unavailable for this day — see the note.",
        "runic": _runic_reading(rune)
        if not any(d.startswith("runic half-month") for d in degraded)
        else "The runes are silent for this day — see the note.",
        "synthesis": _synthesis(sky, dasha, pillar_relations,
                                tib_relation, rune, n_hard),
    }
    return {"schema_version": "1.0", "kind": "daily-forecast",
            "computed": computed, "reading": reading}


def _fmt_hit(h: dict) -> str:
    return (f"{h['transit_body']} {h['aspect']} natal "
            f"{h['natal_point']} (orb {h['orb']}°)")


def _western_reading(sky: dict, n_hard: int) -> str:
    parts = []
    if sky["exact_today"]:
        parts.append("Exact today: " + "; ".join(
            _fmt_hit(h) for h in sky["exact_today"]) + ".")
    if sky["active"]:
        shown = "; ".join(_fmt_hit(h) for h in sky["active"][:6])
        parts.append(f"The sky is in conversation with your chart: {shown}.")
    else:
        parts.append("No close transit aspects today — the sky leaves you "
                     "to your own counsel.")
    for s in sky["stations"]:
        parts.append(f"{s['body']} stations {s['direction']} — a hinge day "
                     "for its themes; avoid forcing outcomes.")
    for g in sky["ingresses"]:
        parts.append(f"{g['body']} enters {g['sign']} — a change of tone "
                     "in that planet's affairs.")
    if n_hard >= 3:
        parts.append("Several hard aspects converge: a day for steady work "
                     "rather than new ventures.")
    return " ".join(parts)


def _element_name(el):
    if not isinstance(el, dict):
        return el
    if "name" in el:
        return el["name"]
    # mewa: {'number': 1, 'color': 'White', 'element': 'Metal'}
    if "number" in el and "color" in el:
        return f"{el['number']} {el['color']} ({el.get('element', '?')})"
    return str(el)


def _vedic_reading(pan: dict, dasha: dict | None, vara: str = "",
                   jaimini: dict | None = None) -> str:
    bits = []
    if dasha:
        bits.append(f"You walk in {dasha['mahadasa']} mahadasha, "
                    f"{dasha['antardasha']} antardasha — the {dasha['mahadasa']} "
                    "themes color everything.")
    if jaimini and jaimini.get("mahadasha") != "unknown":
        bits.append(f"In the Jaimini school, the Chara dasha runs "
                    f"{jaimini['direction']}: {jaimini['mahadasha']} "
                    f"mahadasha, {jaimini['antardasha']} antardasha.")
    bits.append(f"{_element_name(pan.get('tithi'))} tithi, {vara}, Moon in "
                f"{_element_name(pan.get('nakshatra'))} nakshatra, "
                f"{_element_name(pan.get('yoga'))} yoga, "
                f"{_element_name(pan.get('karana'))} karana.")
    return " ".join(bits)


def _chinese_reading(day_stem: str, day_branch: str, day_animal: str,
                     relations: dict, day_element: str,
                     master_element: str) -> str:
    ties = [f"{k} pillar: {v['branch_tie']}" for k, v in relations.items()
            if not v["branch_tie"].startswith("no special")]
    line = (f"The day pillar is {day_stem}-{day_branch} ({day_element} "
            f"{day_animal}). {_element_relation(day_element, master_element)} "
            f"toward your day master {master_element}.")
    if ties:
        line += " " + "; ".join(ties) + "."
    return line


def _tibetan_reading(day_element: str, natal_element: str | None,
                     relation: str, mewa: str, parkha: str) -> str:
    return (f"The day carries {day_element} against your {natal_element} "
            f"birth year: {relation}. Your mewa {mewa} and "
            f"parkha {parkha} hold the year's deeper weather — "
            "the day is only weather within that climate.")


def _runic_reading(rune: dict) -> str:
    return (f"The rune of this half-month is {rune.get('name')}: "
            f"{rune.get('meaning') or rune.get('summary') or ''} "
            "Let it be the day's counsel, not its commander.".strip())


def _synthesis(sky: dict, dasha: dict | None, relations: dict,
               tib_relation: str, rune: dict, n_hard: int) -> str:
    if n_hard >= 3 or any(v["branch_tie"].startswith("clash")
                          for v in relations.values()):
        tone = ("a day of friction — meet it with patience, finish old work, "
                "begin nothing that needs luck")
    elif sky["exact_today"] or n_hard == 0:
        tone = ("a day with open roads — the pressures are few, and exact "
                "transits lend their themes willingly")
    else:
        tone = "a mixed day — take what serves, leave the rest"
    lord = f" under {dasha['mahadasa']}/{dasha['antardasha']}" if dasha else ""
    return (f"In synthesis: {tone}{lord}. {rune.get('name')} watches over it. "
            "This is counsel drawn from symbols, not a verdict on what will be.")


def render_forecast(report: dict) -> str:
    """Render the forecast as readable text."""
    c, r = report["computed"], report["reading"]
    lines = [f"Daily forecast for {c['name']} — {c['target_date']}", ""]
    lines.append("THE DAY'S SKY (computed)")
    for h in c["transits"]["active"][:8]:
        lines.append(f"  - {_fmt_hit(h)}")
    if not c["transits"]["active"]:
        lines.append("  - no close transit aspects")
    for s in c["transits"]["stations"]:
        lines.append(f"  - {s['body']} stations {s['direction']}")
    for g in c["transits"]["ingresses"]:
        lines.append(f"  - {g['body']} enters {g['sign']}")
    lines += ["",
              f"Vedic: {c['dasha']['mahadasa']}/{c['dasha']['antardasha']} | "
              f"Jaimini Chara: {c['jaimini_dasha']['mahadasha']}/"
              f"{c['jaimini_dasha']['antardasha']} | "
              f"{c['panchanga']['tithi']} tithi, {c['panchanga']['vara']}, "
              f"{c['panchanga']['nakshatra']}",
              f"Chinese: day pillar {c['bazi_day']['stem_branch']} "
              f"({c['bazi_day']['animal']})",
              f"Tibetan: day {c['tibetan']['day_element']} vs birth "
              f"{c['tibetan']['natal_element']} — {c['tibetan']['element_relation']}",
              f"Runic: {c['rune']['name']}",
              "",
              "READING (symbolic, not predictive)"]
    for key in ("western", "vedic", "chinese", "tibetan", "runic", "synthesis"):
        lines.append(f"[{key}] {r[key]}")
    return "\n".join(lines)
