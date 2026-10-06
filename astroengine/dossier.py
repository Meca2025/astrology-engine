"""Written natal dossiers: the whole chart speaking as one story.

Assembles the Horizons arts — pillars, wanderers, aspects, stars,
midpoints, the draconic deep, solar arc directions, the year-lord,
the coming sky — into one structured dossier with a rendered text.
Descriptive synthesis from computed facts; traditional lore is
labeled; the framing is symbolic, never causal.
"""

from .aspects import cross_aspects, house_of
from .directions import directed_aspects, solar_arc
from .draconic import draconic_chart, draconic_contacts
from .houses import house_cusps
from .legacy_astronomy import legacy_positions
from .midpoints import midpoint_hits
from .models import CalculationError
from .profections import essential_dignity, profection
from .stars import star_hits
from .watch import upcoming_transits

_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
           "Saturn", "Uranus", "Neptune", "Pluto")


def _fmt(lon: float, sign: str, degree: int, minutes: int) -> str:
    return f"{degree}°{minutes:02d}' {sign}"


def natal_dossier(natal_jd_ut: float, lat: float, lon: float,
                  name: str = "Seeker", birth_iso: str | None = None,
                  target_iso: str | None = None,
                  houses: str = "placidus") -> dict:
    """Build the full dossier as structured data."""
    natal = legacy_positions(natal_jd_ut, True)
    cusps, asc, mc = house_cusps(natal_jd_ut, lat, lon, houses)

    def place(body: str) -> dict:
        p = natal[body]
        plon = p["longitude"] % 360.0
        return {"body": body,
                "longitude": round(plon, 3),
                "placement": _fmt(plon, p["sign"], p["degree"], p["minutes"]),
                "house": house_of(plon, cusps),
                "dignity": essential_dignity(body, p["sign"]),
                "retrograde": bool(p["retrograde"])}

    pillars = {
        "sun": place("Sun"), "moon": place("Moon"),
        "ascendant": {"longitude": round(asc % 360.0, 3),
                      "placement": _sign_placement(asc % 360.0)},
        "mc": {"longitude": round(mc % 360.0, 3),
               "placement": _sign_placement(mc % 360.0)},
    }
    wanderers = [place(b) for b in _BODIES if b not in ("Sun", "Moon")]

    lons = {b: (natal[b]["longitude"] % 360.0) for b in _BODIES}
    raw = cross_aspects({b: {"longitude": v} for b, v in lons.items()},
                        {b: {"longitude": v} for b, v in lons.items()})
    seen: set[tuple[str, str, str]] = set()
    chords = []
    for a in raw:
        if a["body1"] == a["body2"]:
            continue
        key = tuple(sorted((a["body1"], a["body2"]))) + (a["aspect"],)
        if key in seen:
            continue
        seen.add(key)
        chords.append({"bodies": f"{a['body1']} {a['aspect']} {a['body2']}",
                       "orb": round(a["orb"], 3)})
        if len(chords) == 8:
            break

    dossier: dict = {
        "name": name,
        "houses": houses,
        "pillars": pillars,
        "wanderers": wanderers,
        "chords": chords,
        "bright_ones": star_hits(natal_jd_ut, lat, lon)[:5],
        "secret_chords": midpoint_hits(natal_jd_ut, lat, lon)[:5],
        "soul_beneath": draconic_contacts(natal_jd_ut, lat, lon, orb=3.0)[:5],
        "draconic_note": draconic_chart(natal_jd_ut, lat, lon)["node_kind"],
    }

    if target_iso:
        import datetime as _dt
        try:
            ty, tm, td = (int(x) for x in target_iso.split("-"))
            _dt.date(ty, tm, td)  # rejects the impossible, e.g. month 13
        except (ValueError, TypeError, AttributeError) as exc:
            raise CalculationError(
                f"invalid target date '{target_iso}': use YYYY-MM-DD"
            ) from exc
        import swisseph as _swe
        target_jd = _swe.julday(ty, tm, td, 12.0)
        arc = solar_arc(natal_jd_ut, target_jd, lat, lon, houses)
        dossier["directions"] = {
            "arc": round(arc["arc"], 2),
            "hits": directed_aspects(arc["directed"], lons)[:5],
        }
        if birth_iso:
            asc_lon = asc % 360.0
            lord = profection(asc_lon, birth_iso, target_iso)["time_lord"]
            dossier["year_lord"] = profection(
                asc_lon, birth_iso, target_iso,
                lord_longitude=lons.get(lord))
        dossier["coming_sky"] = upcoming_transits(
            natal_jd_ut, target_jd - 2.0, target_jd + 90.0, lat, lon)[:8]
        dossier["target_date"] = target_iso
    return dossier


def _sign_placement(lon: float) -> str:
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
             "Pisces"]
    s = signs[int(lon // 30) % 12]
    d = lon % 30
    return f"{int(d)}°{int((d % 1) * 60):02d}' {s}"


def render_dossier(d: dict) -> str:
    """Render the dossier as a readable written report."""
    L: list[str] = []
    add = L.append
    add(f"# Natal Dossier — {d['name']}")
    add("")
    p = d["pillars"]
    add("## The Pillars")
    add(f"Sun {p['sun']['placement']} (house {p['sun']['house']}), "
        f"{p['sun']['dignity']}.")
    add(f"Moon {p['moon']['placement']} (house {p['moon']['house']}), "
        f"{p['moon']['dignity']}.")
    add(f"Ascendant {p['ascendant']['placement']}; "
        f"MC {p['mc']['placement']}.")
    add("")
    add("## The Wanderers")
    for w in d["wanderers"]:
        rx = " retrograde" if w["retrograde"] else ""
        add(f"{w['body']}: {w['placement']}, house {w['house']}, "
            f"{w['dignity']}{rx}.")
    add("")
    add("## The Chords — tightest natal aspects")
    for c in d["chords"]:
        add(f"{c['bodies']}, orb {c['orb']:.2f}°.")
    add("")
    add("## The Bright Ones — fixed star contacts")
    if d["bright_ones"]:
        for h in d["bright_ones"]:
            add(f"{h['star']} conjunct {h['natal_point']} "
                f"(orb {h['orb']:.2f}°) — {h['meaning']}.")
    else:
        add("No bright star within a degree of planet or angle.")
    add("")
    add("## The Secret Chords — midpoint activations")
    if d["secret_chords"]:
        for h in d["secret_chords"]:
            add(f"{h['activated_by']} on {h['pair']} (orb {h['orb']:.2f}°).")
    else:
        add("No midpoint activations within a degree.")
    add("")
    add("## The Soul Beneath — draconic contacts")
    add(f"({d['draconic_note']})")
    if d["soul_beneath"]:
        for h in d["soul_beneath"]:
            add(f"Draconic {h['draconic']} conjunct natal {h['natal']} "
                f"(orb {h['orb']:.2f}°).")
    else:
        add("The two zodiacs keep their distance — for now.")
    if "directions" in d:
        add("")
        add(f"## Directions of the Year — solar arc {d['directions']['arc']}°")
        for h in d["directions"]["hits"]:
            state = "applying" if h["applying"] else "separating"
            mark = " — exact" if h["exact"] else ""
            add(f"Directed {h['directed']} {h['aspect']} natal "
                f"{h['natal']} (orb {h['orb']:.2f}°, {state}{mark}).")
    if "year_lord" in d:
        yl = d["year_lord"]
        add("")
        add(f"## The Year-Lord — age {yl['age']}")
        add(f"Profected {yl['profected_sign']} (house {yl['profected_house']}); "
            f"lord of the year: {yl['time_lord']}"
            + (f", natal {yl.get('lord_sign')}, {yl.get('lord_dignity')}"
               if yl.get("lord_sign") else "")
            + ".")
    if "coming_sky" in d:
        add("")
        add("## The Coming Sky — next ninety days")
        if d["coming_sky"]:
            for h in d["coming_sky"]:
                add(f"{h['date']}: {h['transit_body']} {h['aspect']} natal "
                    f"{h['natal_point']} (orb {h['orb']:.2f}°).")
        else:
            add("The slow movers keep their counsel in this window.")
    add("")
    add("---")
    add("A symbolic reading, woven from computed positions. The stars "
        "incline; they do not compel.")
    return "\n".join(L)


__all__ = ["natal_dossier", "render_dossier"]
