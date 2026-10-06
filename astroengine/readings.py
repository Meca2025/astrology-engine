"""Astrology readings: interpretive narratives woven from a computed chart.

Template-based and deterministic. Every paragraph is tagged interpretive —
symbolic counsel, never computed fact. Consumes a positions mapping
(legacy calc_planet_positions shape) plus optional angles.
"""

import math as _math

ELEMENTS = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}

_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
          "Pisces"]

# Compact original cookbook lines: Sun / Moon / Ascendant per sign.
SIGN_LINES = {
 "Aries": {"sun": "A direct, pioneering will — you lead by moving first and thinking mid-stride.",
           "moon": "Feelings arrive fast and hot; you need motion the way others need rest.",
           "asc": "You meet the world head-on: frank, energetic, unmistakably present."},
 "Taurus": {"sun": "A steady, sensual will — you build slowly and keep what you build.",
            "moon": "Feelings root deep; loyalty and comfort are your emotional bedrock.",
            "asc": "You meet the world calmly and tangibly — people trust your steadiness."},
 "Gemini": {"sun": "A curious, quicksilver will — you live to connect ideas and people.",
            "moon": "Feelings want words; you process the heart through conversation.",
            "asc": "You meet the world bright and talkative — youthful, clever, everywhere at once."},
 "Cancer": {"sun": "A protective, tidal will — you nurture what you love into strength.",
            "moon": "Feelings run oceanic; home and kin are your sanctuary and your mirror.",
            "asc": "You meet the world gently but guardedly — warmth behind a careful shell."},
 "Leo": {"sun": "A radiant, generous will — you shine brightest when giving joy.",
         "moon": "Feelings need a stage and applause; your heart is loyal and theatrical.",
         "asc": "You meet the world with warmth and drama — impossible to overlook."},
 "Virgo": {"sun": "A precise, serviceful will — you perfect what others overlook.",
           "moon": "Feelings want order; you care by noticing everything.",
           "asc": "You meet the world modestly and attentively — competent, kind, exact."},
 "Libra": {"sun": "A harmonizing will — you create balance and beauty between people.",
           "moon": "Feelings seek partnership; you feel most yourself in duet.",
           "asc": "You meet the world gracefully — charming, fair, and disarming."},
 "Scorpio": {"sun": "An intense, transformative will — you go all the way or not at all.",
             "moon": "Feelings run fathomless; you love and grieve with total commitment.",
             "asc": "You meet the world with quiet power — people sense depths at once."},
 "Sagittarius": {"sun": "A questing, philosophical will — you aim at horizons, literal and moral.",
                 "moon": "Feelings need freedom and meaning; restlessness is your compass.",
                 "asc": "You meet the world expansively — jovial, honest, always going somewhere."},
 "Capricorn": {"sun": "A masterful, enduring will — you climb because the mountain is there.",
               "moon": "Feelings are private and controlled; you show love through provision.",
               "asc": "You meet the world with sober authority — people hand you responsibility."},
 "Aquarius": {"sun": "An original, humane will — you belong to the future and to everyone.",
              "moon": "Feelings need space and principle; you love humanity, one person at a time.",
              "asc": "You meet the world as the fascinating outsider — friendly, unpredictable, free."},
 "Pisces": {"sun": "A dreamy, compassionate will — you dissolve boundaries to heal them.",
            "moon": "Feelings are boundless and porous; you absorb the room's weather.",
            "asc": "You meet the world softly and elusively — gentle, artistic, hard to pin down."},
}

_ASPECT_COOKBOOK = {
    "Conjunction": "fusion — the two drives act as one force",
    "Opposition": "polarity — a seesaw demanding conscious balance",
    "Trine": "harmony — talents that flow with unusual ease",
    "Square": "tension — friction that forges strength through effort",
    "Sextile": "opportunity — a door that opens when knocked upon",
}

_DIGNITY_LINES = {
    "Domicile": "at home and commanding",
    "Exaltation": "exalted — its finest expression",
}


def _sign_of(longitude: float) -> str:
    return _SIGNS[int(longitude % 360 // 30)]


def _temperament(positions: dict) -> str:
    counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    used = 0
    for body in ("Sun", "Moon", "Mercury", "Venus", "Mars",
                 "Jupiter", "Saturn"):
        p = positions.get(body) or {}
        lon = p.get("longitude")
        if lon is None:
            continue
        counts[ELEMENTS[_sign_of(lon)]] += 1
        used += 1
    top = max(counts, key=counts.get)
    return (f"Elemental temperament: {top} leads "
            f"({counts['fire']} fire, {counts['earth']} earth, "
            f"{counts['air']} air, {counts['water']} water).")


def _luminary_paragraphs(positions: dict, asc_sign: str | None) -> list[str]:
    out = []
    for body, label in (("Sun", "core will"), ("Moon", "emotional nature")):
        p = positions.get(body) or {}
        lon = p.get("longitude")
        if lon is None:
            continue
        sign = p.get("sign") or _sign_of(lon)
        out.append(f"{body} in {sign} — your {label}: "
                   f"{SIGN_LINES[sign][body.lower()]}")
    if asc_sign:
        out.append(f"Ascendant in {asc_sign} — your outward mask: "
                   f"{SIGN_LINES[asc_sign]['asc']}")
    return out


def _aspect_paragraphs(positions: dict, limit: int = 5) -> list[str]:
    from astrology_engine import calc_aspects  # deferred: heavy module
    norm = {k: ({**v, "speed": v.get("speed", 0.0)} if isinstance(v, dict) else v)
            for k, v in positions.items()}
    hits = [h for h in calc_aspects(norm, families={"major"})
            if h[2] in _ASPECT_COOKBOOK
            and {h[0], h[1]} != {"N.Node", "S.Node"}]
    out = []
    for p1, p2, name, orb, _q, _g, applying in hits[:limit]:
        out.append(f"{p1} {name.lower()} {p2} (orb {orb:.1f}°, "
                   f"{'applying' if applying else 'separating'}): "
                   f"{_ASPECT_COOKBOOK[name]}.")
    return out


def reading(kind: str = "general", positions: dict | None = None,
            asc_sign: str | None = None,
            mc_sign: str | None = None) -> dict:
    """Weave an interpretive reading from chart data.

    kind: general | love | career. positions: legacy positions mapping.
    """
    kind = (kind or "general").strip().lower()
    if kind not in ("general", "love", "career"):
        from .models import CalculationError
        raise CalculationError(
            f"unknown reading kind '{kind}': general, love or career")
    positions = positions or {}
    paragraphs = [_temperament(positions)]
    paragraphs += _luminary_paragraphs(positions, asc_sign)
    if kind == "love":
        paragraphs += _love_paragraphs(positions)
    elif kind == "career":
        paragraphs += _career_paragraphs(positions, mc_sign)
    paragraphs += _aspect_paragraphs(positions)
    return {
        "kind": kind,
        "paragraphs": [{"text": t, "type": "interpretive"} for t in paragraphs],
        "label": "interpretive — symbolic counsel, not computed fact",
        "source": "astrology-engine cookbook",
        "historical_claim": "modern synthesis",
    }


def _love_paragraphs(positions: dict) -> list[str]:
    out = []
    venus = (positions.get("Venus") or {}).get("longitude")
    if venus is not None:
        sign = _sign_of(venus)
        out.append(f"Venus in {sign} — your love language: "
                   f"{_venus_line(sign)}")
    moon = (positions.get("Moon") or {}).get("longitude")
    if moon is not None:
        sign = _sign_of(moon)
        element = ELEMENTS[sign]
        need = {"fire": "passion and play",
                "earth": "steadiness and physical comfort",
                "air": "conversation and mental kinship",
                "water": "emotional attunement and tenderness"}[element]
        out.append(f"With Moon in {sign}, emotional safety comes through "
                   f"{need}.")
    return out


def _venus_line(sign: str) -> str:
    lines = {
        "Aries": "bold pursuit and passionate immediacy.",
        "Taurus": "sensual devotion and steadfast loyalty.",
        "Gemini": "witty exchange and mental spark.",
        "Cancer": "tender caretaking and deep attachment.",
        "Leo": "grand romance and generous adoration.",
        "Virgo": "thoughtful service and quiet devotion.",
        "Libra": "romantic harmony and beautiful partnership.",
        "Scorpio": "all-consuming intensity and soul-bonding.",
        "Sagittarius": "adventure shared and freedom honored.",
        "Capricorn": "committed building and proven loyalty.",
        "Aquarius": "friendship-first love with room to breathe.",
        "Pisces": "dreamy merger and boundless compassion.",
    }
    return lines[sign]


def _career_paragraphs(positions: dict, mc_sign: str | None) -> list[str]:
    out = []
    if mc_sign:
        out.append(f"Midheaven in {mc_sign} — your public calling bends "
                   f"toward {_mc_line(mc_sign)}")
    saturn = (positions.get("Saturn") or {}).get("longitude")
    if saturn is not None:
        out.append(f"Saturn in {_sign_of(saturn)} — mastery comes through "
                   f"discipline in {_sign_of(saturn).lower()} matters; "
                   f"your authority deepens with time.")
    sun = (positions.get("Sun") or {}).get("longitude")
    if sun is not None:
        out.append(f"With Sun in {_sign_of(sun)}, purpose is found by "
                   f"embodying {SIGN_LINES[_sign_of(sun)]['sun']}")
    return out


def _mc_line(sign: str) -> str:
    lines = {
        "Aries": "leadership, initiative, blazing trails.",
        "Taurus": "craft, finance, building lasting value.",
        "Gemini": "communication, teaching, connecting.",
        "Cancer": "care, hospitality, protecting others.",
        "Leo": "performance, leadership, creative spotlight.",
        "Virgo": "craftsmanship, healing, systems.",
        "Libra": "diplomacy, art, partnership.",
        "Scorpio": "research, transformation, depth work.",
        "Sagittarius": "teaching, publishing, exploration.",
        "Capricorn": "management, mastery, institutions.",
        "Aquarius": "innovation, reform, community.",
        "Pisces": "healing, art, spiritual service.",
    }
    return lines[sign]


__all__ = ["reading", "SIGN_LINES", "ELEMENTS"]
