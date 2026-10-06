#!/usr/bin/env python3
"""
ASTROLOGY ENGINE — Volmarr's Longhall / Hermes Divination Skill
================================================================
Full-spectrum astrological computation for the Hermes Agent.

Capabilities:
  natal          Full natal chart — planets, houses, aspects, dignities, lots
  transit        Current sky transiting natal positions
  synastry       Two-chart overlay for relationship analysis
  solar-return   Solar return chart for a given year
  progressions   Secondary progressed chart
  lunar          Current lunar phase, void-of-course, next lunation
  planet-hours   Planetary hours for today or a given date
  aspect-grid    Full aspect matrix for a chart
  dignity        Complete dignity table for a chart
  lots           Arabic Lots / Hermetic Parts for a chart
  antiscia       Antiscia and contra-antiscia for a chart
  hellenistic    Sect, bonification, joy, triplicity, and sect light

Usage:
  python3 astrology_engine.py natal --date 1975-11-22 --time 14:30 --city Indianapolis --nation US --name Volmarr
  python3 astrology_engine.py transit --date 1975-11-22 --time 14:30 --city Indianapolis --nation US
  python3 astrology_engine.py synastry --date1 1975-11-22 --date2 1980-03-15
  python3 astrology_engine.py solar-return --date 1975-11-22 --time 14:30 --city Indianapolis --nation US --year 2026
  python3 astrology_engine.py progressions --date 1975-11-22 --time 14:30 --city Indianapolis --nation US --prog-date 2026-05-03
  python3 astrology_engine.py lunar
  python3 astrology_engine.py planet-hours --date 2026-05-03 --lat 39.7684 --lon -86.1581
  python3 astrology_engine.py lots --date 1975-11-22 --time 14:30 --city Indianapolis --nation US
  python3 astrology_engine.py hellenistic --date 1975-11-22 --time 14:30 --city Indianapolis --nation US
"""

import argparse
import datetime
import sys
import io
import json
import math
import textwrap
import warnings
import logging
from typing import Any

from astroengine.inputs import parse_civil
from astroengine.ephemeris import solar_day_events
from astroengine.legacy_astronomy import LegacyPositions, legacy_houses, legacy_positions, legacy_request
from astroengine.legacy_inputs import (
    BirthTuple, birth_tuple, coordinate_pair, date_window, local_hour_to_utc, return_year,
)
from astroengine.models import CalculationError, ChartRequest
from astroengine.rules import load_rules

if __name__ == "__main__" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Suppress verbose kerykeion geonames warning
warnings.filterwarnings("ignore", message=".*GEONAMES.*")
warnings.filterwarnings("ignore", message=".*geonames.*")

try:
    import swisseph as swe
    SWE = True
except ImportError:
    SWE = False
    print("WARNING: pyswisseph not installed. pip install pyswisseph", file=sys.stderr)

try:
    from kerykeion import AstrologicalSubject
    KK = True
except ImportError:
    KK = False

# ---------------------------------------------------------------------------
# GEO / TIMEZONE BACKENDS  (loaded lazily — only on first use)
# ---------------------------------------------------------------------------
_nominatim  = None   # geopy Nominatim geocoder instance
_tf         = None   # TimezoneFinder instance
_GEO_AVAIL  = None   # bool: is geopy available?
_TZ_AVAIL   = None   # bool: is timezonefinder available?

def _geo():
    """Lazily initialise Nominatim geocoder."""
    global _nominatim, _GEO_AVAIL
    if _GEO_AVAIL is None:
        try:
            from geopy.geocoders import Nominatim
            _nominatim = Nominatim(user_agent="volmarr_astrology_engine/3.0", timeout=6)
            _GEO_AVAIL = True
        except Exception:
            _GEO_AVAIL = False
    return _nominatim if _GEO_AVAIL else None

def _tzf():
    """Lazily initialise TimezoneFinder."""
    global _tf, _TZ_AVAIL
    if _TZ_AVAIL is None:
        try:
            from timezonefinder import TimezoneFinder
            _tf = TimezoneFinder()
            _TZ_AVAIL = True
        except Exception:
            _TZ_AVAIL = False
    return _tf if _TZ_AVAIL else None

import logging
logging.getLogger("geopy").setLevel(logging.ERROR)
logging.getLogger("kerykeion").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

W = 76  # output width

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_SYMBOL = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
ELEMENTS = {
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water",
}
MODALITIES = {
    "Aries": "Cardinal", "Taurus": "Fixed", "Gemini": "Mutable",
    "Cancer": "Cardinal", "Leo": "Fixed", "Virgo": "Mutable",
    "Libra": "Cardinal", "Scorpio": "Fixed", "Sagittarius": "Mutable",
    "Capricorn": "Cardinal", "Aquarius": "Fixed", "Pisces": "Mutable",
}

# Planets and their Swiss Ephemeris IDs
PLANETS = {
    "Sun":      0,
    "Moon":     1,
    "Mercury":  2,
    "Venus":    3,
    "Mars":     4,
    "Jupiter":  5,
    "Saturn":   6,
    "Uranus":   7,
    "Neptune":  8,
    "Pluto":    9,
    "Chiron":   15,
    "Ceres":    17,
    "Pallas":   18,
    "Juno":     19,
    "Vesta":    20,
    "N.Node":   11,   # True (osculating) Node
    "S.Node":   -1,   # Calculated as 180 from N.Node
}

PLANET_SYMBOL = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    "Chiron": "⚷", "Ceres": "⚳", "Pallas": "⚴", "Juno": "⚵", "Vesta": "⚶",
    "N.Node": "☊", "S.Node": "☋",
}

PLANET_KEYWORDS = {
    "Sun":     "Identity · ego · vitality · purpose · the conscious self",
    "Moon":    "Emotion · instinct · memory · the unconscious · the mother",
    "Mercury": "Mind · communication · thought · travel · wit · commerce",
    "Venus":   "Love · beauty · pleasure · values · attraction · what we desire",
    "Mars":    "Drive · ambition · desire · aggression · war · will to act",
    "Jupiter": "Expansion · luck · philosophy · higher learning · faith · abundance",
    "Saturn":  "Discipline · structure · karma · time · restriction · mastery",
    "Uranus":  "Revolution · sudden change · genius · liberation · the unexpected",
    "Neptune": "Dreams · illusion · spirituality · dissolution · the mystical",
    "Pluto":   "Transformation · death/rebirth · power · shadow · the underworld",
    "Chiron":  "Wounded healer · core wound · teaching through suffering",
    "Ceres":   "Nurture · grief · cycles of loss and return · harvest",
    "Pallas":  "Wisdom · strategy · craft · pattern recognition · justice",
    "Juno":    "Partnership · commitment · equality · betrayal in union",
    "Vesta":   "Devotion · sacred flame · focus · sacrifice · the priestess",
    "N.Node":  "Soul's direction · karmic growth · the path forward",
    "S.Node":  "Past life gifts · karmic comfort zone · what must be released",
}

# Norse god correspondences for planets
NORSE_CORRESPONDENCES = {
    "Sun":     "Sól — the radiant one, light of the world-tree",
    "Moon":    "Máni — the moon-god, measurer of time and tides",
    "Mercury": "Oðinn — master of runes, speech, traveler between worlds",
    "Venus":   "Freyja — goddess of love, beauty, war, and seiðr",
    "Mars":    "Týr — god of justice, battle, and the sacred oath",
    "Jupiter": "Þórr — protector, law-giver, might of expansion",
    "Saturn":  "Oðinn in his Allfather aspect — time, fate, and hard wisdom",
    "Uranus":  "Loki — chaos-bringer, liberator, the trickster who reshapes",
    "Neptune": "Njörðr — god of sea, mist, dissolution, and the deep",
    "Pluto":   "Hel — ruler of Niflheim, death, transformation, the unseen",
    "Chiron":  "Mímir — the wounded sage whose severed head holds all wisdom",
    "N.Node":  "The Norns drawing wyrd-thread toward Urðarbrunnr",
    "S.Node":  "The wyrd already woven — what the Norns cut away",
}

# Rune correspondences for signs
SIGN_RUNES = {
    "Aries":       ("Tiwaz", "ᛏ", "Justice, sacrifice, directed will"),
    "Taurus":      ("Fehu",  "ᚠ", "Wealth, cattle, primal fire of creation"),
    "Gemini":      ("Ansuz", "ᚨ", "Divine breath, Oðinn's speech, inspiration"),
    "Cancer":      ("Berkano","ᛒ", "Birth, the birch, nurturing, the hidden"),
    "Leo":         ("Sowilo","ᛋ", "The sun, victory, life-force, wholeness"),
    "Virgo":       ("Jera",  "ᛃ", "Harvest, cycles, patience, right action"),
    "Libra":       ("Gebo",  "ᚷ", "Gift, exchange, sacred union, balance"),
    "Scorpio":     ("Hagalaz","ᚺ", "Hailstorm, disruption, radical transformation"),
    "Sagittarius": ("Raidho","ᚱ", "The ride, journey, cosmic order, the quest"),
    "Capricorn":   ("Isa",   "ᛁ", "Ice, stillness, ego-structure, frozen will"),
    "Aquarius":    ("Laguz", "ᛚ", "Water, flow, the unconscious, psychic depth"),
    "Pisces":      ("Perthro","ᛈ", "The dice cup, fate, mystery, the hidden well"),
}

# Aspects: name -> (angle, orb_for_luminaries, orb_for_others, glyph, quality)
ASPECTS = {
    "Conjunction":  (0,   10, 8,  "☌", "fusion"),
    "Opposition":   (180, 10, 8,  "☍", "polarity"),
    "Trine":        (120, 8,  7,  "△", "harmony"),
    "Square":       (90,  8,  7,  "□", "tension"),
    "Sextile":      (60,  6,  5,  "⚹", "opportunity"),
    "Quincunx":     (150, 3,  3,  "⚻", "adjustment"),
    "Semi-Square":  (45,  3,  2,  "∠", "friction"),
    "Sesquisquare": (135, 3,  2,  "⚼", "agitation"),
    "Semi-Sextile": (30,  2,  2,  "⌛", "subtle link"),
    "Quintile":     (72,  2,  2,  "Q", "creative"),
    "Bi-Quintile":  (144, 2,  2,  "bQ","creative"),
    "Septile":      (51.43, 1, 1, "S", "fated"),
    # --- the obscure harmonic family (tight orbs, as tradition demands) ---
    "Biseptile":    (102.86, 1.5, 1, "2S", "fated"),
    "Triseptile":   (154.29, 1.5, 1, "3S", "fated"),
    "Novile":       (40.0,  1.5, 1, "N",  "completion"),
    "Binovile":     (80.0,  1.5, 1, "2N", "completion"),
    "Quadnovile":   (160.0, 1.5, 1, "4N", "completion"),
    "Decile":       (36.0,  1.5, 1, "D",  "initiative"),
    "Undecile":     (32.73, 1.5, 1, "U",  "restlessness"),
    "Tredecile":    (108.0, 1.5, 1, "tD", "breakthrough"),
    "Quindecile":   (165.0, 1.5, 1, "qD", "obsession"),
    "Vigintile":    (18.0,  1.5, 1, "V",  "subtle link"),
}

# Aspect families for filtering ("obscure" = everything not major/minor).
ASPECT_FAMILIES = {
    "Conjunction": "major", "Sextile": "major", "Square": "major",
    "Trine": "major", "Opposition": "major",
    "Semi-Sextile": "minor", "Semi-Square": "minor",
    "Sesquisquare": "minor", "Quincunx": "minor",
    "Quintile": "quintile", "Bi-Quintile": "quintile",
    "Septile": "septile", "Biseptile": "septile", "Triseptile": "septile",
    "Novile": "novile", "Binovile": "novile", "Quadnovile": "novile",
    "Decile": "harmonic", "Undecile": "harmonic", "Tredecile": "harmonic",
    "Quindecile": "harmonic", "Vigintile": "harmonic",
}

OBSCURE_FAMILIES = {"quintile", "septile", "novile", "harmonic"}

# Names of the obscure harmonic aspects, kept out of the high-noise
# inline aspect loops (transit/synastry/predict/progressions) which
# deliberately show only stronger aspects; aspect-grid shows the full
# spectrum via calc_aspects().
OBSCURE_ASPECT_NAMES = ("Biseptile", "Triseptile", "Novile", "Binovile",
                        "Quadnovile", "Decile", "Undecile", "Tredecile",
                        "Quindecile", "Vigintile")

# Essential dignities
DOMICILE = {
    "Sun":     ["Leo"],
    "Moon":    ["Cancer"],
    "Mercury": ["Gemini", "Virgo"],
    "Venus":   ["Taurus", "Libra"],
    "Mars":    ["Aries", "Scorpio"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn":  ["Capricorn", "Aquarius"],
    "Uranus":  ["Aquarius"],
    "Neptune": ["Pisces"],
    "Pluto":   ["Scorpio"],
}
DETRIMENT = {
    "Sun":     ["Aquarius"],
    "Moon":    ["Capricorn"],
    "Mercury": ["Sagittarius", "Pisces"],
    "Venus":   ["Aries", "Scorpio"],
    "Mars":    ["Libra", "Taurus"],
    "Jupiter": ["Gemini", "Virgo"],
    "Saturn":  ["Cancer", "Leo"],
    "Uranus":  ["Leo"],
    "Neptune": ["Virgo"],
    "Pluto":   ["Taurus"],
}
EXALTATION = {
    "Sun":     "Aries",
    "Moon":    "Taurus",
    "Mercury": "Virgo",
    "Venus":   "Pisces",
    "Mars":    "Capricorn",
    "Jupiter": "Cancer",
    "Saturn":  "Libra",
    "Uranus":  "Scorpio",
    "Neptune": "Cancer",
    "Pluto":   "Aries",
    "N.Node":  "Gemini",
}
FALL = {v: k for k, v in EXALTATION.items() if isinstance(v, str)}
# Exaltation degrees (traditional)
EXALTATION_DEG = {
    "Sun": ("Aries", 19), "Moon": ("Taurus", 3),
    "Mercury": ("Virgo", 15), "Venus": ("Pisces", 27),
    "Mars": ("Capricorn", 28), "Jupiter": ("Cancer", 15),
    "Saturn": ("Libra", 21),
}

# Ptolemaic terms (Egyptian bounds)
TERMS = {
    "Aries":       [("Jupiter",0,6),("Venus",6,12),("Mercury",12,20),("Mars",20,25),("Saturn",25,30)],
    "Taurus":      [("Venus",0,8),("Mercury",8,14),("Jupiter",14,22),("Saturn",22,27),("Mars",27,30)],
    "Gemini":      [("Mercury",0,6),("Jupiter",6,12),("Venus",12,17),("Mars",17,24),("Saturn",24,30)],
    "Cancer":      [("Mars",0,7),("Venus",7,13),("Mercury",13,19),("Jupiter",19,26),("Saturn",26,30)],
    "Leo":         [("Jupiter",0,6),("Venus",6,11),("Saturn",11,18),("Mercury",18,24),("Mars",24,30)],
    "Virgo":       [("Mercury",0,7),("Venus",7,17),("Jupiter",17,21),("Mars",21,28),("Saturn",28,30)],
    "Libra":       [("Saturn",0,6),("Mercury",6,14),("Jupiter",14,21),("Venus",21,28),("Mars",28,30)],
    "Scorpio":     [("Mars",0,7),("Venus",7,11),("Mercury",11,19),("Jupiter",19,24),("Saturn",24,30)],
    "Sagittarius": [("Jupiter",0,12),("Venus",12,17),("Mercury",17,21),("Saturn",21,26),("Mars",26,30)],
    "Capricorn":   [("Mercury",0,7),("Jupiter",7,14),("Venus",14,22),("Saturn",22,26),("Mars",26,30)],
    "Aquarius":    [("Mercury",0,7),("Venus",7,13),("Jupiter",13,20),("Mars",20,25),("Saturn",25,30)],
    "Pisces":      [("Venus",0,12),("Jupiter",12,16),("Mercury",16,19),("Mars",19,28),("Saturn",28,30)],
}

# Decans / faces (each 10 degrees, traditional Chaldean order)
DECANS = {
    "Aries":       [("Mars",0),("Sun",10),("Venus",20)],
    "Taurus":      [("Mercury",0),("Moon",10),("Saturn",20)],
    "Gemini":      [("Jupiter",0),("Mars",10),("Sun",20)],
    "Cancer":      [("Venus",0),("Mercury",10),("Moon",20)],
    "Leo":         [("Saturn",0),("Jupiter",10),("Mars",20)],
    "Virgo":       [("Sun",0),("Venus",10),("Mercury",20)],
    "Libra":       [("Moon",0),("Saturn",10),("Jupiter",20)],
    "Scorpio":     [("Mars",0),("Sun",10),("Venus",20)],
    "Sagittarius": [("Mercury",0),("Moon",10),("Saturn",20)],
    "Capricorn":   [("Jupiter",0),("Mars",10),("Sun",20)],
    "Aquarius":    [("Venus",0),("Mercury",10),("Moon",20)],
    "Pisces":      [("Saturn",0),("Jupiter",10),("Mars",20)],
}

# Triplicity rulers (day / night / participating)
TRIPLICITY = {
    "Fire":  ("Sun",   "Jupiter", "Saturn"),
    "Earth": ("Venus", "Moon",    "Mars"),
    "Air":   ("Saturn","Mercury", "Jupiter"),
    "Water": ("Venus", "Mars",    "Moon"),
}

# Planetary joys by house (Hellenistic)
PLANETARY_JOY = {
    "Mercury": 1, "Moon": 3, "Venus": 5, "Mars": 6,
    "Sun": 9, "Jupiter": 11, "Saturn": 12,
}

# House meanings (brief)
HOUSE_KEYWORDS = [
    (1,  "Self · appearance · body · first impressions · the persona"),
    (2,  "Resources · money · possessions · self-worth · what sustains"),
    (3,  "Communication · siblings · local travel · early learning · the mind"),
    (4,  "Home · family · roots · ancestry · the foundation of the soul"),
    (5,  "Creativity · romance · children · pleasure · self-expression"),
    (6,  "Work · health · daily routine · service · the body as tool"),
    (7,  "Partnership · marriage · open enemies · projection · the other"),
    (8,  "Death · transformation · shared resources · occult · the shadow"),
    (9,  "Philosophy · religion · long travel · higher learning · the quest"),
    (10, "Career · public image · father · ambition · legacy · the peak"),
    (11, "Friends · community · hopes · ideals · the collective · the future"),
    (12, "Hidden enemies · karma · isolation · spirituality · the unconscious"),
]

# Planetary hours order (Chaldean sequence)
CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
DAY_RULERS = {
    0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
    4: "Venus", 5: "Saturn", 6: "Sun",
}  # Python date.weekday() (Mon=0) -> traditional planetary day ruler

# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------

def hr(char="─"):
    return char * W

def header(title, subtitle=None):
    print()
    print("╔" + "═" * (W - 2) + "╗")
    line = f"  ✦ {title} ✦"
    print("║" + line.center(W - 2) + "║")
    if subtitle:
        sub = f"  {subtitle}"
        print("║" + sub.center(W - 2) + "║")
    print("╚" + "═" * (W - 2) + "╝")
    print()

def section(title):
    print()
    print(f"  ┌─ {title} " + "─" * max(0, W - len(title) - 6) + "┐")

def wrap_print(text, indent=4):
    for line in textwrap.wrap(text, W - indent):
        print(" " * indent + line)

def deg_to_sign(deg):
    """Convert ecliptic longitude to sign, degree, minutes."""
    deg = deg % 360
    idx = int(deg // 30)
    d = int(deg % 30)
    m = int((deg % 1) * 60)
    return SIGNS[idx], idx, d, m

def sign_idx(sign_name):
    return SIGNS.index(sign_name)

def lon_from_sign_deg(sign, deg):
    return SIGNS.index(sign) * 30 + deg

def angle_diff(a, b):
    """Shortest arc between two longitudes."""
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d

def julian_day(year, month, day, hour=12.0):
    if SWE:
        return swe.julday(year, month, day, hour)
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return float(jdn) + (hour - 12.0) / 24.0

def parse_date_time(date_str: str, time_str: str | None = None) -> tuple[int, int, int, float]:
    """Validate a civil date/clock without timezone conversion; omitted time is noon."""
    civil = parse_civil(date_str, time_str)
    hour = (civil - civil.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600
    return civil.year, civil.month, civil.day, hour


def resolve_timezone(lat, lon):
    """Return IANA timezone name for a lat/lon, or None if unavailable."""
    tf = _tzf()
    if tf and lat is not None and lon is not None:
        try:
            return tf.timezone_at(lng=float(lon), lat=float(lat))
        except Exception:
            pass
    return None


def local_to_utc(year: int, month: int, day: int, local_hour: float,
                 tz_name: str) -> tuple[float, str]:
    """Strict UTC conversion, retaining signed hours relative to civil midnight."""
    return local_hour_to_utc(year, month, day, local_hour, tz_name)


def resolve_birth(date_str: str, time_str: str | None, city: str, nation: str = "",
                  lat_override: float | str | None = None, lon_override: float | str | None = None,
                  timezone_override: str | None = None) -> BirthTuple:
    """Resolve actual UTC date/clock in the unchanged ten-item legacy tuple.

    An explicit zone bypasses optional discovery. Unresolved locations/zones,
    invalid inputs and DST folds/gaps raise CalculationError. Unknown time stays
    a flagged local-noon surrogate. Houses/backend migration is owned by W09b2.
    """
    parse_civil(date_str, time_str)
    lat, lon, resolved = geocode_city(city, nation, lat_override, lon_override)
    if not resolved:
        raise CalculationError("Location unresolved; supply both --lat and --lon")
    coordinate_pair(lat, lon)
    zone = timezone_override if timezone_override is not None else resolve_timezone(lat, lon)
    if zone is None:
        raise CalculationError("Timezone unresolved; supply --timezone with an IANA zone or explicit UTC")
    return birth_tuple(ChartRequest(date_str, lat, lon, zone, time_str))


def geocode_city(city: str, nation: str = "", lat_override: float | str | None = None,
                 lon_override: float | str | None = None) -> tuple[float, float, bool]:
    """Resolve city → (lat, lon, city_resolved).
    
    city_resolved is True for explicit coordinates or a matched city (not defaulted).

    Priority:
      1. Explicit --lat / --lon flags
      2. Nominatim (OpenStreetMap, no API key, requires internet)
      3. kerykeion built-in geonames DB
      4. Hardcoded ~120-city fallback table
      5. Raise CalculationError when location is unresolved
    """
    pair = coordinate_pair(lat_override, lon_override)
    if pair is not None:
        return pair[0], pair[1], True
    if not isinstance(city, str) or not isinstance(nation, str):
        raise CalculationError("City and nation must be text; or supply explicit coordinates")

    # --- Nominatim (most accurate, works for any city worldwide) ---
    if city:
        geo = _geo()
        if geo:
            query = f"{city}, {nation}".strip(", ")
            try:
                loc = geo.geocode(query)
                if loc:
                    pair = coordinate_pair(loc.latitude, loc.longitude)
                    if pair is None:
                        raise CalculationError("Geocoder returned no coordinates")
                    return pair[0], pair[1], True
                # Retry without nation code in case nation is a 2-letter code that confuses it
                if nation and len(nation) == 2:
                    loc2 = geo.geocode(city)
                    if loc2:
                        pair = coordinate_pair(loc2.latitude, loc2.longitude)
                        if pair is None:
                            raise CalculationError("Geocoder returned no coordinates")
                        return pair[0], pair[1], True
            except CalculationError:
                raise
            except Exception:
                pass

    # --- kerykeion geonames ---
    if KK and city:
        try:
            import logging
            logging.disable(logging.CRITICAL)
            tmp = AstrologicalSubject("_", 2000, 1, 1, 12, 0, city, nation or "")
            logging.disable(logging.NOTSET)
            if tmp.lat is not None and tmp.lng is not None:
                pair = coordinate_pair(tmp.lat, tmp.lng)
                return pair[0], pair[1], True
        except CalculationError:
            raise
        except Exception:
            pass

    # --- hardcoded fallback (~400 cities: US state capitals, top US metros, major world) ---
    CITIES = {
        # ── US — Indiana region (home) ──
        "indianapolis": (39.7684, -86.1581),
        "angola": (41.6337, -84.9994),
        "fort wayne": (41.0793, -85.1394),
        "south bend": (41.6764, -86.2520),
        "elkhart": (41.6815, -85.9775),
        "gary": (41.5934, -87.3464),
        "lafayette": (40.4167, -86.8753),
        "west lafayette": (40.4259, -86.9081),
        "muncie": (40.1934, -85.3864),
        "terre haute": (39.4662, -87.3414),
        "bloomington": (39.1653, -86.5264),
        "evansville": (37.9715, -87.5698),
        "carmel": (39.9784, -86.1180),
        "fishers": (39.9517, -86.0197),
        "noblesville": (40.0496, -86.0086),
        # ── US — State Capitals (all 50) ──
        "montgomery": (32.3792, -86.3071),
        "juneau": (58.3019, -134.4197),
        "phoenix": (33.4484, -112.0740),
        "little rock": (34.7465, -92.2896),
        "sacramento": (38.5816, -121.4944),
        "denver": (39.7392, -104.9903),
        "hartford": (41.7658, -72.6734),
        "dover": (39.1582, -75.5244),
        "tallahassee": (30.4383, -84.2807),
        "atlanta": (33.7490, -84.3880),
        "honolulu": (21.3069, -157.8583),
        "boise": (43.6150, -116.2023),
        "springfield": (39.8017, -89.6437),
        "indianapolis": (39.7684, -86.1581),
        "des moines": (41.6005, -93.6091),
        "topeka": (39.0473, -95.6892),
        "frankfort": (38.1870, -84.8683),
        "baton rouge": (30.4583, -91.1403),
        "augusta": (44.3106, -69.7796),
        "annapolis": (38.9786, -76.4918),
        "boston": (42.3601, -71.0589),
        "lansing": (42.7325, -84.5555),
        "st. paul": (44.9537, -93.0900),
        "jackson": (32.2988, -90.1848),
        "jefferson city": (38.5721, -92.1893),
        "helena": (46.5927, -112.0361),
        "lincoln": (40.8081, -96.7003),
        "carson city": (39.1600, -119.7528),
        "concord": (43.2087, -71.5376),
        "trenton": (40.2206, -74.7566),
        "santa fe": (35.6872, -105.9378),
        "albany": (42.6526, -73.7562),
        "raleigh": (35.7796, -78.6382),
        "bismarck": (46.8083, -100.7837),
        "columbus": (39.9612, -82.9988),
        "oklahoma city": (35.4676, -97.5164),
        "salem": (44.9426, -123.0351),
        "harrisburg": (40.2698, -76.8756),
        "providence": (41.8240, -71.4128),
        "columbia": (34.0007, -81.0348),
        "pierre": (44.3683, -100.3512),
        "nashville": (36.1627, -86.7816),
        "austin": (30.2672, -97.7431),
        "salt lake city": (40.7608, -111.8910),
        "montpelier": (44.2601, -72.5806),
        "richmond": (37.5407, -77.4360),
        "olympia": (47.0379, -122.9007),
        "charleston": (38.3498, -81.6326),
        "madison": (43.0731, -89.4012),
        "cheyenne": (41.1400, -104.8197),
        # ── US — Northeast ──
        "new york": (40.7128, -74.0060),
        "new york city": (40.7128, -74.0060),
        "nyc": (40.7128, -74.0060),
        "manhattan": (40.7831, -73.9712),
        "brooklyn": (40.6782, -73.9442),
        "schenectady": (42.7603, -73.9334),
        "buffalo": (42.8864, -78.8784),
        "rochester": (43.1566, -77.6088),
        "philadelphia": (39.9526, -75.1652),
        "pittsburgh": (40.4406, -79.9959),
        "washington": (38.9072, -77.0369),
        "washington dc": (38.9072, -77.0369),
        "baltimore": (39.2904, -76.6122),
        "newark": (40.7357, -74.1724),
        "jersey city": (40.7178, -74.0436),
        "boston": (42.3601, -71.0589),
        "worcester": (42.2626, -71.8023),
        "springfield ma": (42.1015, -72.5898),
        "portland me": (43.6591, -70.2568),
        "burlington vt": (44.4759, -73.2121),
        "manchester nh": (42.9956, -71.4548),
        # ── US — Midwest ──
        "chicago": (41.8781, -87.6298),
        "detroit": (42.3314, -83.0458),
        "cincinnati": (39.1031, -84.5120),
        "cleveland": (41.4993, -81.6944),
        "minneapolis": (44.9778, -93.2650),
        "milwaukee": (43.0389, -87.9065),
        "kansas city": (39.0997, -94.5786),
        "st. louis": (38.6270, -90.1994),
        "st louis": (38.6270, -90.1994),
        "memphis": (35.1495, -90.0490),
        "louisville": (38.2527, -85.7585),
        "columbus": (39.9612, -82.9988),
        "indianapolis": (39.7684, -86.1581),
        "omaha": (41.2565, -95.9345),
        "wichita": (37.6889, -97.3360),
        "duluth": (46.7867, -92.1005),
        "fargo": (46.8772, -96.7898),
        "sioux falls": (43.5446, -96.7311),
        "grand rapids": (42.9634, -85.6681),
        "dayton": (39.7589, -84.1916),
        "akron": (41.0814, -81.5190),
        "toledo": (41.6639, -83.5552),
        "ann arbor": (42.2808, -83.7430),
        "madison": (43.0731, -89.4012),
        # ── US — South ──
        "houston": (29.7604, -95.3698),
        "dallas": (32.7767, -96.7970),
        "san antonio": (29.4241, -98.4936),
        "miami": (25.7617, -80.1918),
        "jacksonville": (30.3322, -81.6557),
        "charlotte": (35.2271, -80.8431),
        "new orleans": (29.9511, -90.0715),
        "orlando": (28.5384, -81.3792),
        "tampa": (27.9506, -82.4572),
        "nashville": (36.1627, -86.7816),
        "raleigh": (35.7796, -78.6382),
        "charleston": (32.7766, -79.9311),
        "savannah": (32.0809, -81.0912),
        "richmond": (37.5407, -77.4360),
        "virginia beach": (36.8529, -75.9780),
        "atlanta": (33.7490, -84.3880),
        "chattanooga": (35.0458, -85.3097),
        "birmingham al": (33.5186, -86.8104),
        "mobile": (30.6954, -88.0399),
        "jackson ms": (32.2988, -90.1848),
        "little rock": (34.7465, -92.2896),
        "baton rouge": (30.4583, -91.1403),
        "lexington": (38.0406, -84.5037),
        "knoxville": (35.9606, -83.9207),
        # ── US — Southwest ──
        "los angeles": (34.0522, -118.2437),
        "san francisco": (37.7749, -122.4194),
        "san diego": (32.7157, -117.1611),
        "las vegas": (36.1699, -115.1398),
        "phoenix": (33.4484, -112.0740),
        "albuquerque": (35.0844, -106.6504),
        "el paso": (31.7619, -106.4850),
        "tucson": (32.2226, -110.9747),
        "austin": (30.2672, -97.7431),
        "dallas": (32.7767, -96.7970),
        "fort worth": (32.7555, -97.3308),
        "oklahoma city": (35.4676, -97.5164),
        "santa fe": (35.6872, -105.9378),
        "reno": (39.5296, -119.8138),
        # ── US — Northwest / Mountain ──
        "seattle": (47.6062, -122.3321),
        "portland": (45.5051, -122.6750),
        "portland or": (45.5051, -122.6750),
        "denver": (39.7392, -104.9903),
        "salt lake city": (40.7608, -111.8910),
        "boise": (43.6150, -116.2023),
        "spokane": (47.6588, -117.4260),
        "tacoma": (47.2465, -122.4384),
        "eugene": (44.0521, -123.0868),
        "bend": (44.0582, -121.3153),
        "missoula": (46.8720, -113.9940),
        "billings": (45.7833, -108.5007),
        "anchorage": (61.2181, -149.9003),
        "fairbanks": (64.8378, -147.7164),
        # ── US — Mountain West ──
        "phoenix": (33.4484, -112.0740),
        "tucson": (32.2226, -110.9747),
        "mesa": (33.4152, -111.8314),
        "chandler": (33.3062, -111.8412),
        "scottsdale": (33.4942, -111.9260),
        "las vegas": (36.1699, -115.1398),
        "albuquerque": (35.0844, -106.6504),
        "denver": (39.7392, -104.9903),
        "colorado springs": (38.8339, -104.8214),
        "aurora": (39.7294, -104.8319),
        "salt lake city": (40.7608, -111.8910),
        "provo": (40.2338, -111.6585),
        "boise": (43.6150, -116.2023),
        "cheyenne": (41.1400, -104.8197),
        "casper": (42.8346, -106.3251),
        # ── Canada ──
        "toronto": (43.6532, -79.3832),
        "vancouver": (49.2827, -123.1207),
        "montreal": (45.5017, -73.5673),
        "ottawa": (45.4215, -75.6972),
        "calgary": (51.0447, -114.0719),
        "edmonton": (53.5461, -113.4938),
        "winnipeg": (49.8951, -97.1384),
        "halifax": (44.6488, -63.5752),
        "quebec city": (46.8139, -71.2080),
        "victoria": (48.4284, -123.3656),
        "regina": (50.4452, -104.6189),
        "saskatoon": (52.1294, -106.3469),
        "st. john's": (47.5615, -52.7126),
        # ── Nordic ──
        "oslo": (59.9139, 10.7522),
        "stockholm": (59.3293, 18.0686),
        "copenhagen": (55.6761, 12.5683),
        "helsinki": (60.1699, 24.9384),
        "reykjavik": (64.1355, -21.8954),
        "bergen": (60.3913, 5.3221),
        "tromso": (69.6496, 18.9560),
        "gothenburg": (57.7089, 11.9746),
        "malmo": (55.6050, 13.0000),
        "tampere": (61.4978, 23.7610),
        "oulu": (65.0121, 25.4681),
        "turku": (60.4518, 22.2666),
        "helsingoer": (56.0362, 12.6136),
        "stavanger": (58.9700, 5.7330),
        "trondheim": (63.4305, 10.3951),
        "uppsala": (59.8586, 17.6389),
        "lund": (55.7047, 13.1910),
        "umea": (63.8258, 20.2630),
        "tartu": (58.3782, 26.7147),
        "tallinn": (59.4370, 24.7536),
        "rikshospitalet": (59.9509, 10.7291),
        "odense": (55.4038, 10.3794),
        # ── British Isles ──
        "london": (51.5074, -0.1278),
        "dublin": (53.3498, -6.2603),
        "edinburgh": (55.9533, -3.1883),
        "manchester": (53.4808, -2.2426),
        "birmingham uk": (52.4862, -1.8904),
        "birmingham": (52.4862, -1.8904),
        "glasgow": (55.8642, -4.2518),
        "bristol": (51.4545, -2.5879),
        "cambridge": (52.2053, 0.1218),
        "oxford": (51.7520, -1.2577),
        "bath": (51.3803, -2.3580),
        "york": (53.9591, -1.0815),
        "cardiff": (51.4816, -3.1791),
        "liverpool": (53.4106, -2.9779),
        "leeds": (53.8008, -1.5491),
        "sheffield": (53.3811, -1.4701),
        "nottingham": (52.9548, -1.1581),
        "belfast": (54.5973, -5.9301),
        "cork": (51.8985, -8.4756),
        "galway": (53.2707, -9.0568),
        "limerick": (52.6680, -8.6305),
        "aberdeen": (57.1497, -2.0943),
        "inverness": (57.4778, -4.2247),
        "canterbury": (51.2766, 1.0735),
        "brighton": (50.8225, -0.1372),
        # ── Western Europe ──
        "paris": (48.8566, 2.3522),
        "lyon": (45.7640, 4.8357),
        "marseille": (43.2965, 5.3698),
        "toulouse": (43.6047, 1.4442),
        "nice": (43.7102, 7.2620),
        "bordeaux": (44.8378, -0.5792),
        "strasbourg": (48.5734, 7.7521),
        "berlin": (52.5200, 13.4050),
        "munich": (48.1351, 11.5820),
        "hamburg": (53.5511, 9.9937),
        "frankfurt": (50.1109, 8.6821),
        "cologne": (50.9375, 6.9603),
        "dresden": (51.0504, 13.7373),
        "dusseldorf": (51.2277, 6.7735),
        "stuttgart": (48.7758, 9.1829),
        "nuremberg": (49.4521, 11.0767),
        "heidelberg": (49.4126, 8.7538),
        "rome": (41.9028, 12.4964),
        "milan": (45.4642, 9.1900),
        "florence": (43.7696, 11.2558),
        "venice": (45.4408, 12.3155),
        "naples": (40.8518, 14.2681),
        "turin": (45.0703, 7.6869),
        "bologna": (44.4949, 11.3426),
        "madrid": (40.4168, -3.7038),
        "barcelona": (41.3874, 2.1686),
        "valencia": (39.4699, -0.3763),
        "seville": (37.3891, -5.9845),
        "bilbao": (43.2630, -2.9350),
        "amsterdam": (52.3676, 4.9041),
        "rotterdam": (51.9244, 4.4777),
        "the hague": (52.0705, 4.3007),
        "brussels": (50.8503, 4.3517),
        "antwerp": (51.2194, 4.4025),
        "luxembourg": (49.6117, 6.1300),
        "zurich": (47.3769, 8.5417),
        "geneva": (46.2044, 6.1432),
        "basel": (47.5596, 7.5886),
        "bern": (46.9480, 7.4474),
        "vienna": (48.2082, 16.3738),
        "salzburg": (47.8095, 13.0550),
        "innsbruck": (47.2692, 11.4041),
        # ── Southern & Eastern Europe ──
        "lisbon": (38.7223, -9.1393),
        "porto": (41.1579, -8.6291),
        "athens": (37.9838, 23.7275),
        "thessaloniki": (40.6401, 22.9444),
        "istanbul": (41.0082, 28.9784),
        "ankara": (39.9334, 32.8597),
        "prague": (50.0755, 14.4378),
        "budapest": (47.4979, 19.0402),
        "warsaw": (52.2297, 21.0122),
        "krakow": (50.0647, 19.9450),
        "bucharest": (44.4268, 26.1025),
        "sofia": (42.6977, 23.3219),
        "belgrade": (44.7866, 20.4489),
        "zagreb": (45.8150, 15.9819),
        "ljubljana": (46.0569, 14.5058),
        "bratislava": (48.1486, 17.1077),
        "moscow": (55.7558, 37.6173),
        "st. petersburg": (59.9343, 30.3351),
        "novosibirsk": (55.0084, 82.9357),
        "yekaterinburg": (56.8389, 60.6057),
        "kazan": (55.7887, 49.1221),
        "riga": (56.9496, 24.1052),
        "vilnius": (54.6872, 25.2797),
        "tallinn": (59.4370, 24.7536),
        # ── Middle East ──
        "dubai": (25.2048, 55.2708),
        "abu dhabi": (24.4539, 54.3773),
        "riyadh": (24.7136, 46.6753),
        "jeddah": (21.5433, 39.1728),
        "doha": (25.2854, 51.5310),
        "tehran": (35.6892, 51.3890),
        "istanbul": (41.0082, 28.9784),
        "tel aviv": (32.0853, 34.7818),
        "jerusalem": (31.7683, 35.2137),
        "beirut": (33.8938, 35.5018),
        "cairo": (30.0444, 31.2357),
        "alexandria": (31.2001, 29.9187),
        "amman": (31.9454, 35.9284),
        "muscat": (23.5880, 58.3829),
        "kuwait city": (29.3759, 47.9774),
        # ── Asia-Pacific ──
        "tokyo": (35.6762, 139.6503),
        "osaka": (34.6937, 135.5023),
        "kyoto": (35.0116, 135.7681),
        "yokohama": (35.4437, 139.6380),
        "nagoya": (35.1815, 136.9066),
        "sapporo": (43.0621, 141.3544),
        "fukuoka": (33.5904, 130.4017),
        "beijing": (39.9042, 116.4074),
        "shanghai": (31.2304, 121.4737),
        "guangzhou": (23.1291, 113.2644),
        "shenzhen": (22.5431, 114.0579),
        "chengdu": (30.5728, 104.0668),
        "hangzhou": (30.2741, 120.1551),
        "nanjing": (32.0603, 118.7969),
        "wuhan": (30.5928, 114.3055),
        "xian": (34.3416, 108.9398),
        "hong kong": (22.3193, 114.1694),
        "taipei": (25.0330, 121.5654),
        "seoul": (37.5665, 126.9780),
        "busan": (35.1796, 129.0756),
        "incheon": (37.4563, 126.7052),
        "pyongyang": (39.0392, 125.7625),
        "mumbai": (19.0760, 72.8777),
        "delhi": (28.6139, 77.2090),
        "new delhi": (28.6139, 77.2090),
        "kolkata": (22.5726, 88.3639),
        "chennai": (13.0827, 80.2707),
        "bangalore": (12.9716, 77.5946),
        "hyderabad": (17.3850, 78.4867),
        "pune": (18.5204, 73.8567),
        "jaipur": (26.9124, 75.7873),
        "bangkok": (13.7563, 100.5018),
        "chiang mai": (18.7883, 98.9853),
        "singapore": (1.3521, 103.8198),
        "jakarta": (-6.2088, 106.8456),
        "bali": (-8.3405, 115.0920),
        "manila": (14.5995, 120.9842),
        "ho chi minh city": (10.8231, 106.6297),
        "hanoi": (21.0278, 105.8342),
        "kuala lumpur": (3.1390, 101.6869),
        "phnom penh": (11.5564, 104.9282),
        "yangon": (16.8661, 96.1951),
        # ── East & Southeast Asia ──
        "sydney": (-33.8688, 151.2093),
        "melbourne": (-37.8136, 144.9631),
        "brisbane": (-27.4698, 153.0251),
        "perth": (-31.9505, 115.8605),
        "adelaide": (-34.9285, 138.6007),
        "auckland": (-36.8485, 174.7633),
        "wellington": (-41.2866, 174.7756),
        "christchurch": (-43.5321, 172.6362),
        # ── Latin America ──
        "mexico city": (19.4326, -99.1332),
        "guadalajara": (20.6597, -103.3496),
        "monterrey": (25.6866, -100.3161),
        "cancun": (21.1619, -86.8515),
        "tivat": (21.1619, -86.8515),
        "bogota": (4.7110, -74.0721),
        "medellin": (6.2442, -75.5812),
        "buenos aires": (-34.6037, -58.3816),
        "cordoba": (-31.4201, -64.1888),
        "santiago": (-33.4489, -70.6693),
        "valparaiso": (-33.0472, -71.6127),
        "lima": (-12.0464, -77.0428),
        "cusco": (-13.5320, -71.9675),
        "sao paulo": (-23.5505, -46.6333),
        "rio de janeiro": (-22.9068, -43.1729),
        "brasilia": (-15.7975, -47.8919),
        "salvador": (-12.9714, -38.5124),
        "recife": (-8.0476, -34.8770),
        "caracas": (10.4806, -66.9036),
        "havana": (23.1136, -82.3666),
        "quito": (-0.1807, -78.4678),
        "la paz": (-16.4897, -68.1193),
        "montevideo": (-34.9011, -56.1645),
        "asuncion": (-25.2637, -57.5759),
        # ── Africa ──
        "cairo": (30.0444, 31.2357),
        "alexandria": (31.2001, 29.9187),
        "lagos": (6.5244, 3.3792),
        "abuja": (9.0579, 7.4951),
        "nairobi": (-1.2921, 36.8219),
        "mombasa": (-4.0435, 39.6669),
        "johannesburg": (-26.2041, 28.0473),
        "cape town": (-33.9249, 18.4241),
        "durban": (-29.8587, 31.0218),
        "pretoria": (-25.7479, 28.2293),
        "casablanca": (33.5731, -7.5898),
        "marrakech": (31.6295, -7.9811),
        "tangier": (35.7595, -5.8340),
        "accra": (5.6037, -0.1870),
        "addis ababa": (9.0250, 38.7469),
        "dar es salaam": (-6.7924, 39.2083),
        "kampala": (0.3476, 32.5825),
        "kigali": (-1.9403, 29.8735),
        "maputo": (-25.9692, 32.5732),
        "algiers": (36.7538, 3.0588),
        "tunis": (36.8065, 10.1815),
        "dakar": (14.7167, -17.4677),
        "kinshasa": (-4.4419, 15.2663),
        "harare": (-17.8252, 31.0335),
        "lusaka": (-15.3875, 28.3228),
        # ── South/Central Asia ──
        "dhaka": (23.8103, 90.4125),
        "kathmandu": (27.7172, 85.3240),
        "karachi": (24.8607, 67.0011),
        "lahore": (31.5204, 74.3589),
        "islamabad": (33.6844, 73.0479),
        "colombo": (6.9271, 79.8612),
        "kabul": (34.5553, 69.2075),
        "tientSin": (39.1422, 117.1767),
        "ulaanbaatar": (47.8864, 106.9052),
    }
    result = CITIES.get(city.lower())
    if result:
        pair = coordinate_pair(*result)
        return pair[0], pair[1], True
    raise CalculationError(f"Location '{city}' unresolved; supply both --lat and --lon")

# ---------------------------------------------------------------------------
# CORE CALCULATION ENGINE
# ---------------------------------------------------------------------------

def calc_planet_positions(jd: float, tropical: bool = True) -> LegacyPositions:
    """Required bodies or an error; optional failures have named diagnostics."""
    if not SWE:
        raise CalculationError("pyswisseph is required for planetary calculations")
    return legacy_positions(jd, tropical)


def calc_houses(jd: float, lat: float, lon: float,
                system: bytes = b"P") -> tuple[list[float], float, float]:
    """Requested twelve-house cusps and angles; failed houses never fabricate."""
    if not SWE:
        raise CalculationError("pyswisseph is required for house calculations")
    return legacy_houses(jd, lat, lon, system)


def planet_house(planet_lon, cusps):
    """Determine which house a planet is in, given 12 cusp longitudes."""
    for i in range(12):
        cusp_start = cusps[i] % 360
        cusp_end = cusps[(i + 1) % 12] % 360
        lon = planet_lon % 360
        if cusp_start <= cusp_end:
            if cusp_start <= lon < cusp_end:
                return i + 1
        else:  # wraps 360
            if lon >= cusp_start or lon < cusp_end:
                return i + 1
    return 1

def is_applying(lon1, speed1, lon2, speed2, angle):
    """True if the aspect of `angle` degrees between two bodies is applying
    (moving toward exactness) rather than separating.

    sep  = signed longitude of body1 minus body2, wrapped to (-180, 180].
    x    = |sep| - angle        (signed distance from exactness)
    dx/dt = sign(sep) * (speed1 - speed2)
    Applying  <=>  x and dx/dt have opposite signs (distance shrinking).
    """
    sep = (lon1 - lon2 + 180.0) % 360.0 - 180.0
    x = abs(sep) - angle
    if x == 0:
        return False  # exact right now: parting, not approaching
    dxdt = math.copysign(1.0, sep) * (speed1 - speed2)
    return (x * dxdt) < 0


def calc_aspects(positions, luminaries=("Sun", "Moon"), families=None):
    """Return list of (p1, p2, aspect_name, orb, quality, glyph).

    families: None (all) or a collection like {"major"} or {"obscure"}.
    The pseudo-family "obscure" selects quintile/septile/novile/harmonic.
    """
    if families is not None:
        wanted = set(families)
        if "obscure" in wanted:
            wanted |= OBSCURE_FAMILIES
    planet_list = [p for p in positions if positions[p].get("longitude") is not None]
    results = []
    for i, p1 in enumerate(planet_list):
        for p2 in planet_list[i+1:]:
            lon1 = positions[p1]["longitude"]
            lon2 = positions[p2]["longitude"]
            diff = angle_diff(lon1, lon2)
            for asp_name, (angle, orb_lum, orb_other, glyph, quality) in ASPECTS.items():
                if families is not None and ASPECT_FAMILIES.get(asp_name) not in wanted:
                    continue
                orb = orb_lum if (p1 in luminaries or p2 in luminaries) else orb_other
                actual_orb = abs(diff - angle)
                if actual_orb <= orb:
                    # Applying or separating: is the pair moving toward exactness?
                    applying = is_applying(lon1, positions[p1]["speed"],
                                           lon2, positions[p2]["speed"], angle)
                    results.append((p1, p2, asp_name, round(actual_orb, 2), quality, glyph, applying))
    return sorted(results, key=lambda x: x[3])

def essential_dignity(planet, sign, degree):
    """Return dignity score and labels for a planet at a position."""
    labels = []
    score = 0

    if sign in DOMICILE.get(planet, []):
        labels.append("Domicile ★★★★★")
        score += 5
    elif sign in DETRIMENT.get(planet, []):
        labels.append("Detriment ✗✗")
        score -= 5

    if EXALTATION.get(planet) == sign:
        # Check for exact or near-exact exaltation degree (bonus +1 within 3°)
        ex_data = EXALTATION_DEG.get(planet)
        if ex_data and ex_data[0] == sign:
            deg_diff = abs(degree - ex_data[1])
            if deg_diff <= 1:
                labels.append(f"Exact Exaltation ★★★★★  (within {deg_diff:.0f}° of {ex_data[1]}° {sign})")
                score += 5
            elif deg_diff <= 3:
                labels.append(f"Exaltation ★★★★  (near exact: {deg_diff:.0f}° from {ex_data[1]}° {sign})")
                score += 4
            else:
                labels.append("Exaltation ★★★★")
                score += 4
        else:
            labels.append("Exaltation ★★★★")
            score += 4
    elif FALL.get(sign) == planet:
        labels.append("Fall ✗")
        score -= 4

    # Triplicity
    elem = ELEMENTS.get(sign, "")
    if elem in TRIPLICITY:
        trip = TRIPLICITY[elem]
        if planet in trip:
            idx = trip.index(planet)
            label = ["Triplicity Day ★★★", "Triplicity Night ★★★", "Triplicity Part ★"][idx]
            labels.append(label)
            score += 3

    # Terms (Egyptian)
    for term_planet, start, end in TERMS.get(sign, []):
        if start <= degree < end and term_planet == planet:
            labels.append(f"Terms ★★  ({start}°–{end}°)")
            score += 2
            break

    # Decan/Face
    for face_planet, start in DECANS.get(sign, []):
        end = start + 10
        if start <= degree < end and face_planet == planet:
            labels.append(f"Face/Decan ★  ({start}°–{end-1}°)")
            score += 1
            break

    if not labels:
        labels.append("Peregrine — no essential dignity")

    return score, labels

def mutual_reception(positions):
    """Find planets in each other's domicile (mutual reception)."""
    found = []
    for p1, d1 in positions.items():
        for p2, d2 in positions.items():
            if p1 >= p2:
                continue
            sign1 = d1.get("sign")
            sign2 = d2.get("sign")
            if sign1 in DOMICILE.get(p2, []) and sign2 in DOMICILE.get(p1, []):
                found.append((p1, p2, sign1, sign2))
    return found

def calc_antiscia(positions):
    """Antiscia: mirror across the Cancer/Capricorn axis (0° Cancer = 0° Cancer).
    Contra-antiscia: mirror across 0° Aries / 0° Libra."""
    results = {}
    for p, d in positions.items():
        lon = d.get("longitude")
        if lon is None:
            continue
        # Antiscia axis: 0 Cancer (90°) and 0 Capricorn (270°)
        # antiscia longitude = 180 - lon (mod 360)  ... standard formula
        antiscia_lon = (180 - lon) % 360
        # Contra-antiscia axis: 0 Aries / 0 Libra
        contra_lon = (360 - lon) % 360

        a_sign, _, a_deg, a_min = deg_to_sign(antiscia_lon)
        c_sign, _, c_deg, c_min = deg_to_sign(contra_lon)
        results[p] = {
            "antiscia_lon": antiscia_lon,
            "antiscia": f"{a_sign} {a_deg}°{a_min:02d}'",
            "contra_lon": contra_lon,
            "contra": f"{c_sign} {c_deg}°{c_min:02d}'",
        }
    return results

def is_day_chart(sun_lon, asc_lon):
    """Sun above horizon = day chart (Sun between Asc and Desc going via MC).

    Diurnal motion runs clockwise in a northern-hemisphere wheel, so the
    above-horizon half is the 180° of longitude just *before* the ASC:
    diff = (sun_lon - asc_lon) % 360 falls in (180, 360).
    """
    diff = (sun_lon - asc_lon) % 360
    return diff >= 180

def calc_lots(positions, asc_lon, day_chart):
    """Calculate Arabic Lots. Returns dict of lot_name -> longitude."""
    lots = {}
    fortune_lon = None

    def lot(from_p, to_p):
        try:
            f = positions[from_p]["longitude"]
            t = positions[to_p]["longitude"]
            if day_chart:
                return (asc_lon + t - f) % 360
            else:
                return (asc_lon + f - t) % 360
        except KeyError:
            return None

    # Fortune — day: ASC + Moon - Sun (project Sun→Moon from ASC);
    #          night: ASC + Sun - Moon. lot(from_p, to_p) computes
    #          ASC + to - from by day, so Fortune = lot("Sun", "Moon").
    fl = lot("Sun", "Moon")
    if fl is not None:
        lots["Lot of Fortune"] = fl
        fortune_lon = fl

    # Spirit (Daimon) — day: ASC + Sun - Moon; night: ASC + Moon - Sun.
    sl = lot("Moon", "Sun")
    if sl is not None:
        lots["Lot of Spirit"] = sl

    # Use computed Fortune for remaining lots
    if fortune_lon is not None and "Lot of Spirit" in lots:
        spirit_lon = lots["Lot of Spirit"]

        # Eros: ASC + Venus - Spirit (day) / ASC + Spirit - Venus (night)
        if "Venus" in positions:
            v = positions["Venus"]["longitude"]
            if day_chart:
                lots["Lot of Eros"] = (asc_lon + v - spirit_lon) % 360
            else:
                lots["Lot of Eros"] = (asc_lon + spirit_lon - v) % 360

        # Necessity: ASC + Fortune - Mercury (day) / reverse
        if "Mercury" in positions:
            merc = positions["Mercury"]["longitude"]
            if day_chart:
                lots["Lot of Necessity"] = (asc_lon + fortune_lon - merc) % 360
            else:
                lots["Lot of Necessity"] = (asc_lon + merc - fortune_lon) % 360

        # Courage: ASC + Mars - Fortune
        if "Mars" in positions:
            m = positions["Mars"]["longitude"]
            if day_chart:
                lots["Lot of Courage"] = (asc_lon + m - fortune_lon) % 360
            else:
                lots["Lot of Courage"] = (asc_lon + fortune_lon - m) % 360

        # Victory: ASC + Jupiter - Spirit
        if "Jupiter" in positions:
            j = positions["Jupiter"]["longitude"]
            if day_chart:
                lots["Lot of Victory"] = (asc_lon + j - spirit_lon) % 360
            else:
                lots["Lot of Victory"] = (asc_lon + spirit_lon - j) % 360

        # Nemesis: ASC + Saturn - Fortune
        if "Saturn" in positions:
            s = positions["Saturn"]["longitude"]
            if day_chart:
                lots["Lot of Nemesis"] = (asc_lon + s - fortune_lon) % 360
            else:
                lots["Lot of Nemesis"] = (asc_lon + fortune_lon - s) % 360

    return lots

def calc_lunar_phase(sun_lon, moon_lon):
    """Return lunar phase name and percentage illuminated."""
    diff = (moon_lon - sun_lon) % 360
    pct = diff / 360.0
    phases = [
        (0,   22.5,  "New Moon",         "🌑"),
        (22.5, 67.5, "Waxing Crescent",  "🌒"),
        (67.5, 112.5,"First Quarter",    "🌓"),
        (112.5,157.5,"Waxing Gibbous",   "🌔"),
        (157.5,202.5,"Full Moon",        "🌕"),
        (202.5,247.5,"Waning Gibbous",   "🌖"),
        (247.5,292.5,"Last Quarter",     "🌗"),
        (292.5,337.5,"Waning Crescent",  "🌘"),
        (337.5,360,  "Balsamic",         "🌑"),
    ]
    for start, end, name, glyph in phases:
        if start <= diff < end:
            illumination = round(50 * (1 - math.cos(math.radians(diff))))
            return name, glyph, diff, illumination
    return "Dark Moon", "🌑", diff, 0

def next_lunation(jd_start):
    """Find next New Moon (elongation 0°) and Full Moon (elongation 180°)
    from jd_start. Brackets the crossing in 1-day steps, then bisects."""
    if not SWE:
        return None, None

    def elongation(jd):
        sun = swe.calc_ut(jd, swe.SUN, 0)[0][0]
        moon = swe.calc_ut(jd, swe.MOON, 0)[0][0]
        return (moon - sun) % 360

    def signed_dist(e, target):
        d = (e - target) % 360
        return d if d <= 180 else d - 360

    def find_next(target):
        jd = jd_start
        d_prev = signed_dist(elongation(jd), target)
        for _ in range(40):  # more than one lunation
            jd_next = jd + 1.0
            d_curr = signed_dist(elongation(jd_next), target)
            if d_prev == 0:
                return jd
            # Sign change with small jump = genuine crossing (guards the
            # ±180° wrap of the signed distance, where |jump| ≈ 360°)
            if d_prev * d_curr < 0 and abs(d_prev - d_curr) < 90:
                lo, hi = jd, jd_next
                for _ in range(30):
                    mid = (lo + hi) / 2
                    if signed_dist(elongation(mid), target) * d_prev < 0:
                        hi = mid
                    else:
                        lo = mid
                return (lo + hi) / 2
            jd, d_prev = jd_next, d_curr
        return None

    return find_next(0.0), find_next(180.0)

def void_of_course(jd, moon_lon, positions):
    """Check if Moon is void of course — no applying major aspects before sign ingress.

    Uses exact aspect targeting: for each planet, compute the Moon longitude that would
    form an exact major aspect, then check if that longitude lies between now and ingress.
    Far more accurate and fast compared to step-scanning.
    """
    moon_sign_idx = int(moon_lon // 30)
    moon_sign_end = (moon_sign_idx + 1) * 30.0   # next sign boundary (tropical lon)
    moon_speed = positions.get("Moon", {}).get("speed", 13.2)
    degrees_to_ingress = (moon_sign_end - moon_lon) % 30
    hours_to_ingress = (degrees_to_ingress / moon_speed) * 24 if moon_speed > 0.01 else 999

    # Only check major aspects for VOC (classical definition)
    MAJOR_ASPECTS = {k: v for k, v in ASPECTS.items()
                     if k in ("Conjunction", "Opposition", "Trine", "Square", "Sextile")}

    next_aspect = None  # (planet, aspect_name, moon_lon_at_exact, orb_now)

    for pname, pdata in positions.items():
        if pname in ("Moon", "S.Node"):
            continue
        plon = pdata.get("longitude")
        if plon is None:
            continue
        pspeed = pdata.get("speed", 0.0)

        for asp_name, (angle, orb_l, orb_o, glyph, quality) in MAJOR_ASPECTS.items():
            # Target Moon longitude for exact aspect (two solutions per aspect type)
            for target_moon in [(plon + angle) % 360, (plon - angle) % 360]:
                # Is this target between moon_lon and moon_sign_end (going forward)?
                if moon_speed > 0:
                    # Forward motion: moon_lon → moon_sign_end
                    if moon_lon <= target_moon < moon_sign_end:
                        degrees_away = target_moon - moon_lon
                    elif moon_sign_end <= 360 and target_moon < moon_lon:
                        # wraps — not in this sign window
                        continue
                    else:
                        continue
                else:
                    continue  # retrograde Moon is extremely rare; skip

                # Confirm aspect is applying (Moon gaining on aspect point)
                # Moon is applying if current orb is decreasing:
                # relative speed of Moon vs planet in this aspect
                current_diff = angle_diff(moon_lon, plon)
                current_orb = abs(current_diff - angle)
                # planet will also move; approximate future planet lon
                hours_to_exact = (degrees_away / moon_speed) * 24 if moon_speed > 0 else 999
                future_plon = (plon + pspeed * hours_to_exact / 24) % 360
                future_diff = angle_diff(target_moon, future_plon)
                future_orb = abs(future_diff - angle)

                if future_orb < current_orb + 2:  # aspect is actually applying / within range
                    if next_aspect is None or degrees_away < next_aspect[3]:
                        next_aspect = (pname, asp_name, glyph, degrees_away, hours_to_exact)
                    return False, hours_to_ingress  # not VOC — found an applying aspect

    return True, hours_to_ingress

def planetary_hours(date, lat, lon):
    """Calculate planetary hours for a given date and location."""
    if not SWE:
        raise CalculationError("pyswisseph is required for planetary hours")
    jd = julian_day(date.year, date.month, date.day, 0.0)
    sunrise_jd, sunset_jd, next_sunrise_jd = solar_day_events(legacy_request(jd), lat, lon)

    day_len  = (sunset_jd - sunrise_jd) / 12.0   # length of one day planetary hour
    night_len = (next_sunrise_jd - sunset_jd) / 12.0  # one night hour

    weekday = date.weekday()  # 0=Mon
    day_ruler = DAY_RULERS[weekday]
    ruler_idx = CHALDEAN.index(day_ruler)

    hours = []
    for i in range(12):
        hour_start = sunrise_jd + i * day_len
        planet = CHALDEAN[(ruler_idx + i) % 7]
        hours.append(("day", i + 1, planet, hour_start, day_len * 24 * 60))

    night_ruler_idx = (ruler_idx + 12) % 7
    for i in range(12):
        hour_start = sunset_jd + i * night_len
        planet = CHALDEAN[(night_ruler_idx + i) % 7]
        hours.append(("night", i + 1, planet, hour_start, night_len * 24 * 60))

    return hours, day_ruler, sunrise_jd, sunset_jd

def jd_to_dt(jd):
    """Convert Julian day to datetime string."""
    if SWE:
        try:
            # gregflag=1 -> Gregorian calendar (0 would give Julian dates!)
            # returns (year, month, day, hour, minute, second)
            y, mo, d, hh, mi, _ss = swe.jdut1_to_utc(jd, 1)[:6]
            return (f"{int(y):04d}-{int(mo):02d}-{int(d):02d} "
                    f"{int(hh):02d}:{int(mi):02d} UTC")
        except Exception:
            pass
    return f"JD {jd:.4f}"

# ---------------------------------------------------------------------------
# COMPOSITE / SYNERGY / PREDICTION / GEOASTROLOGY ENGINE
# ---------------------------------------------------------------------------

def calc_composite(pos1, pos2):
    """Composite chart by midpoint method. Both charts must have same planet set."""
    composite = {}
    for planet in set(pos1.keys()) & set(pos2.keys()):
        lon1 = pos1[planet]["longitude"]
        lon2 = pos2[planet]["longitude"]
        # Shorter-arc midpoint
        diff = (lon2 - lon1) % 360
        mid = (lon1 + (diff / 2)) % 360 if diff <= 180 else (lon1 + (diff / 2) + 180) % 360
        sign, sidx, deg, mins = deg_to_sign(mid)
        composite[planet] = {
            "longitude": mid, "sign": sign, "sign_idx": sidx,
            "degree": deg, "minutes": mins,
            "latitude": 0.0, "speed": 0.0, "retrograde": False,
        }
    return composite

def calc_davison(jd1, jd2, lat1, lon1, lat2, lon2):
    """Davison relationship chart: average JD and average location."""
    jd_avg  = (jd1 + jd2) / 2.0
    lat_avg = (lat1 + lat2) / 2.0
    lon_avg = (lon1 + lon2) / 2.0
    return jd_avg, lat_avg, lon_avg

def calc_midpoints(positions):
    """Return all planet-pair midpoints sorted by longitude."""
    mps = []
    planet_list = sorted(positions.keys())
    for i, p1 in enumerate(planet_list):
        for p2 in planet_list[i+1:]:
            lon1 = positions[p1]["longitude"]
            lon2 = positions[p2]["longitude"]
            diff = (lon2 - lon1) % 360
            mid = (lon1 + diff / 2) % 360 if diff <= 180 else (lon1 + diff / 2 + 180) % 360
            sign, sidx, deg, mins = deg_to_sign(mid)
            mps.append((mid, p1, p2, sign, deg, mins))
    return sorted(mps)

def synergy_score(cross_aspects):
    """Score a list of (orb, p1, glyph, asp_name, p2, quality, applying) aspect rows."""
    WEIGHTS = {
        "Conjunction": 0,   # neutral — depends on planets
        "Trine":      +3,
        "Sextile":    +2,
        "Opposition": -1,   # awareness, not purely bad
        "Square":     -2,
        "Quincunx":   -1,
        "Semi-Square": -1,
        "Sesquisquare":-1,
    }
    PLANET_WEIGHTS = {
        "Sun":     3, "Moon":   3, "Venus": 2, "Mars": 2,
        "Mercury": 1, "Jupiter":2, "Saturn":1, "Chiron":1,
        "N.Node":  1, "Uranus": 1, "Neptune":1, "Pluto": 1,
    }
    categories = {"harmony": 0, "challenge": 0, "activation": 0, "neutral": 0}
    total = 0
    for row in cross_aspects:
        orb, p1, glyph, asp_name, p2, quality, applying = row
        w_asp = WEIGHTS.get(asp_name, 0)
        w_p   = (PLANET_WEIGHTS.get(p1, 1) + PLANET_WEIGHTS.get(p2, 1)) / 2
        tightness = max(0.1, 1 - orb / 10)  # closer = stronger
        score = w_asp * w_p * tightness

        # Conjunction: sign depends on planets involved
        if asp_name == "Conjunction":
            difficult_pair = {"Mars","Saturn","Pluto","Uranus","Neptune"}
            if p1 in difficult_pair or p2 in difficult_pair:
                score = -1 * w_p * tightness
            else:
                score = +2 * w_p * tightness

        if score > 0:
            categories["harmony"] += score
        elif score < 0:
            categories["challenge"] += abs(score)
        else:
            categories["neutral"] += 1
        total += score

    return total, categories

def find_exact_transit_dates(natal_pos, start_jd, end_jd, t_planets=None, n_planets=None, step=1.0):
    """Scan a date range for exact transit-to-natal major aspect dates.

    Returns list of (jd_exact, t_planet, asp_name, glyph, n_planet, quality).
    Uses bisection to find crossing to within 0.01° accuracy.
    """
    if not SWE:
        return []
    if t_planets is None:
        t_planets = ["Sun","Moon","Mercury","Venus","Mars",
                     "Jupiter","Saturn","Uranus","Neptune","Pluto","N.Node"]
    if n_planets is None:
        n_planets = ["Sun","Moon","Mercury","Venus","Mars","Asc","MC",
                     "Jupiter","Saturn","Chiron","N.Node"]

    MAJOR = {k: v for k, v in ASPECTS.items()
             if k in ("Conjunction","Opposition","Trine","Square","Sextile")}

    events = []

    for t_planet in t_planets:
        if t_planet not in PLANETS:
            continue
        pid = PLANETS[t_planet]

        for n_planet in n_planets:
            if n_planet not in natal_pos:
                continue
            n_lon = natal_pos[n_planet]["longitude"]

            for asp_name, (angle, orb_l, orb_o, glyph, quality) in MAJOR.items():
                # Two target longitudes (aspect from both sides)
                for target_lon in [(n_lon + angle) % 360, (n_lon - angle) % 360]:
                    jd = start_jd
                    try:
                        prev_lon = swe.calc_ut(jd, pid, swe.FLG_SPEED)[0][0]
                    except Exception:
                        continue

                    while jd < end_jd:
                        jd_next = min(jd + step, end_jd)
                        try:
                            curr_lon = swe.calc_ut(jd_next, pid, swe.FLG_SPEED)[0][0]
                        except Exception:
                            jd = jd_next
                            continue

                        # Check if transit planet crossed target_lon in this step
                        def dist_to_target(lon):
                            d = (lon - target_lon) % 360
                            return d if d <= 180 else d - 360

                        d_prev = dist_to_target(prev_lon)
                        d_curr = dist_to_target(curr_lon)

                        if d_prev * d_curr < 0 and abs(d_prev - d_curr) < 90:
                            # Sign change — bisect to find exact crossing
                            lo, hi = jd, jd_next
                            for _ in range(20):
                                mid_jd = (lo + hi) / 2
                                try:
                                    mid_lon = swe.calc_ut(mid_jd, pid, swe.FLG_SPEED)[0][0]
                                except Exception:
                                    break
                                if dist_to_target(mid_lon) * d_prev < 0:
                                    hi = mid_jd
                                else:
                                    lo = mid_jd
                            # Deduplicate: skip if same planet/aspect/natal combo within 5 days
                            duplicate = any(
                                abs(e[0] - (lo + hi) / 2) < 5
                                and e[1] == t_planet and e[2] == asp_name and e[3] == n_planet
                                for e in events
                            )
                            if not duplicate:
                                events.append(((lo + hi) / 2, t_planet, asp_name, glyph, n_planet, quality))

                        prev_lon = curr_lon
                        jd = jd_next

    return sorted(events)

def find_stations(start_jd, end_jd, step=1.0):
    """Find retrograde and direct station dates for all planets."""
    if not SWE:
        return []
    planets_to_check = ["Mercury","Venus","Mars","Jupiter","Saturn",
                        "Uranus","Neptune","Pluto","Chiron"]
    stations = []

    for planet in planets_to_check:
        pid = PLANETS[planet]
        jd = start_jd
        try:
            prev_speed = swe.calc_ut(jd, pid, swe.FLG_SPEED)[0][3]
        except Exception:
            continue

        while jd < end_jd:
            jd_next = min(jd + step, end_jd)
            try:
                curr = swe.calc_ut(jd_next, pid, swe.FLG_SPEED)[0]
                curr_speed = curr[3]
                curr_lon   = curr[0]
            except Exception:
                jd = jd_next
                continue

            if prev_speed * curr_speed < 0:
                # Speed sign change — bisect for exact station
                lo, hi = jd, jd_next
                for _ in range(20):
                    mid_jd = (lo + hi) / 2
                    try:
                        mid_spd = swe.calc_ut(mid_jd, pid, swe.FLG_SPEED)[0][3]
                    except Exception:
                        break
                    if mid_spd * prev_speed < 0:
                        hi = mid_jd
                    else:
                        lo = mid_jd
                exact_jd = (lo + hi) / 2
                try:
                    exact_lon = swe.calc_ut(exact_jd, pid, swe.FLG_SPEED)[0][0]
                except Exception:
                    exact_lon = curr_lon
                sign, sidx, deg, mins = deg_to_sign(exact_lon)
                kind = "Stations Retrograde ℞" if curr_speed < 0 else "Stations Direct  ℗"
                stations.append((exact_jd, planet, kind, sign, deg, mins))

            prev_speed = curr_speed
            jd = jd_next

    return sorted(stations)

def find_ingresses(start_jd, end_jd, planets=None, step=1.0):
    """Find sign ingresses for a list of planets."""
    if not SWE:
        return []
    if planets is None:
        planets = ["Sun","Mercury","Venus","Mars","Jupiter","Saturn",
                   "Uranus","Neptune","Pluto","N.Node"]
    ingresses = []

    for planet in planets:
        if planet not in PLANETS or PLANETS[planet] < 0:
            continue
        pid = PLANETS[planet]
        jd = start_jd
        try:
            prev_sign_idx = int(swe.calc_ut(jd, pid, swe.FLG_SPEED)[0][0] // 30) % 12
        except Exception:
            continue

        while jd < end_jd:
            jd_next = min(jd + step, end_jd)
            try:
                curr_lon = swe.calc_ut(jd_next, pid, swe.FLG_SPEED)[0][0]
                curr_sign_idx = int(curr_lon // 30) % 12
            except Exception:
                jd = jd_next
                continue

            if curr_sign_idx != prev_sign_idx:
                # Bisect to exact ingress
                lo, hi = jd, jd_next
                for _ in range(20):
                    mid_jd = (lo + hi) / 2
                    try:
                        mid_idx = int(swe.calc_ut(mid_jd, pid, swe.FLG_SPEED)[0][0] // 30) % 12
                    except Exception:
                        break
                    if mid_idx == prev_sign_idx:
                        lo = mid_jd
                    else:
                        hi = mid_jd
                ingresses.append(((lo + hi) / 2, planet,
                                   SIGNS[prev_sign_idx], SIGNS[curr_sign_idx]))
                prev_sign_idx = curr_sign_idx

            jd = jd_next

    return sorted(ingresses)

def find_eclipses(start_jd, end_jd):
    """Find solar and lunar eclipses using Swiss Ephemeris."""
    if not SWE:
        return []
    eclipses = []
    jd = start_jd

    while jd < end_jd:
        # Solar eclipse search
        try:
            ret, jd_sol = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, 0, False)
            if ret >= 0 and jd_sol[0] < end_jd:
                eclipse_type = {
                    swe.ECL_TOTAL:   "Total Solar Eclipse",
                    swe.ECL_ANNULAR: "Annular Solar Eclipse",
                    swe.ECL_PARTIAL: "Partial Solar Eclipse",
                    swe.ECL_ANNULAR_TOTAL: "Hybrid Solar Eclipse",
                }.get(ret & 0xFF, "Solar Eclipse")
                sun_lon = swe.calc_ut(jd_sol[0], swe.SUN, swe.FLG_SPEED)[0][0]
                sign, sidx, deg, mins = deg_to_sign(sun_lon)
                eclipses.append((jd_sol[0], eclipse_type, sign, deg, mins))
                jd = jd_sol[0] + 20  # skip past this eclipse
                continue
        except Exception:
            pass

        # Lunar eclipse search
        try:
            ret, jd_lun = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, 0, False)
            if ret >= 0 and jd_lun[0] < end_jd:
                eclipse_type = {
                    swe.ECL_TOTAL:    "Total Lunar Eclipse",
                    swe.ECL_PARTIAL:  "Partial Lunar Eclipse",
                    swe.ECL_PENUMBRAL:"Penumbral Lunar Eclipse",
                }.get(ret & 0xFF, "Lunar Eclipse")
                moon_lon = swe.calc_ut(jd_lun[0], swe.MOON, swe.FLG_SPEED)[0][0]
                sign, sidx, deg, mins = deg_to_sign(moon_lon)
                eclipses.append((jd_lun[0], eclipse_type, sign, deg, mins))
                jd = jd_lun[0] + 14
                continue
        except Exception:
            pass

        jd += 25  # jump roughly one lunation

    return sorted(eclipses)

def _obliquity(jd):
    """Return mean obliquity of ecliptic in degrees."""
    if SWE:
        try:
            return swe.calc_ut(jd, swe.ECL_NUT, 0)[0][0]
        except Exception:
            pass
    # IAU formula fallback
    T = (jd - 2451545.0) / 36525.0
    return 23.439291 - 0.013004 * T

def _ecl_to_eq(lon, lat, eps):
    """Convert ecliptic (lon, lat) to equatorial (RA, Dec) in degrees."""
    eps_r = math.radians(eps)
    lon_r = math.radians(lon)
    lat_r = math.radians(lat)
    dec = math.asin(math.sin(lat_r) * math.cos(eps_r) +
                    math.cos(lat_r) * math.sin(eps_r) * math.sin(lon_r))
    ra  = math.atan2(
        math.sin(lon_r) * math.cos(eps_r) - math.tan(lat_r) * math.sin(eps_r),
        math.cos(lon_r)
    )
    return math.degrees(ra) % 360, math.degrees(dec)

def _gmst(jd):
    """Greenwich Mean Sidereal Time in degrees."""
    if SWE:
        try:
            return swe.sidtime(jd) * 15.0  # hours -> degrees
        except Exception:
            pass
    T = (jd - 2451545.0) / 36525.0
    gmst_hours = 6.697374558 + 2400.0513369 * T + 0.0000258622 * T * T
    return (gmst_hours % 24) * 15.0

def calc_astrocartography(jd, positions):
    """Calculate astrocartography lines for all major planets.

    Returns dict of planet -> {
        "MC_lon": float,   # Earth longitude of MC line (planet on upper meridian)
        "IC_lon": float,   # Earth longitude of IC line
        "ASC_lons": [(lat, lon), ...],  # ASC line sampled every 10° of latitude
        "DSC_lons": [(lat, lon), ...],  # DSC line
        "ra": float, "dec": float,      # planet equatorial coords
    }
    """
    if not SWE:
        return {}

    eps = _obliquity(jd)
    gmst_deg = _gmst(jd)
    result = {}

    for planet, pid in PLANETS.items():
        if planet in ("S.Node",) or pid < 0:
            continue
        if planet not in positions:
            continue
        pdata = positions[planet]
        ecl_lon = pdata["longitude"]
        ecl_lat = pdata.get("latitude", 0.0)

        ra, dec = _ecl_to_eq(ecl_lon, ecl_lat, eps)

        # MC line: longitude on Earth where planet is on upper meridian
        # Local Sidereal Time = GMST + geographic_lon  →  geographic_lon = RA - GMST
        mc_earth_lon = (ra - gmst_deg) % 360
        if mc_earth_lon > 180:
            mc_earth_lon -= 360  # convert to -180..+180
        ic_earth_lon = mc_earth_lon + 180
        if ic_earth_lon > 180:
            ic_earth_lon -= 360

        # ASC/DSC lines: for each latitude, find the hour angle H where planet is on horizon
        # cos(H) = -tan(φ) * tan(δ)  → horizon condition
        asc_line = []
        dsc_line = []
        dec_r = math.radians(dec)

        for lat_deg in range(-60, 65, 5):
            phi_r = math.radians(lat_deg)
            cos_H = -math.tan(phi_r) * math.tan(dec_r)
            if abs(cos_H) > 1:
                continue  # circumpolar — no rising/setting
            H = math.degrees(math.acos(cos_H))  # 0..180°

            # Rising (ASC): RAMC = RA - H  →  geo_lon = RAMC - GMST
            ramc_asc = (ra - H) % 360
            geo_lon_asc = (ramc_asc - gmst_deg) % 360
            if geo_lon_asc > 180:
                geo_lon_asc -= 360
            asc_line.append((lat_deg, round(geo_lon_asc, 2)))

            # Setting (DSC): RAMC = RA + H
            ramc_dsc = (ra + H) % 360
            geo_lon_dsc = (ramc_dsc - gmst_deg) % 360
            if geo_lon_dsc > 180:
                geo_lon_dsc -= 360
            dsc_line.append((lat_deg, round(geo_lon_dsc, 2)))

        result[planet] = {
            "MC_lon": round(mc_earth_lon, 2),
            "IC_lon": round(ic_earth_lon, 2),
            "ASC_lons": asc_line,
            "DSC_lons": dsc_line,
            "ra": round(ra, 3),
            "dec": round(dec, 3),
        }

    return result

# Geographic region lookup (rough longitude bands for astrocartography)
_GEO_REGIONS = [
    (-180,-150,"Pacific Ocean / International Date Line"),
    (-150,-130,"Hawaii / Pacific Ocean"),
    (-130,-110,"Pacific Coast / British Columbia / Baja"),
    (-110, -90,"US Mountain West / Mexico"),
    ( -90, -70,"US Central / Mississippi / Caribbean"),
    ( -70, -50,"US East Coast / Eastern Canada"),
    ( -50, -30,"Atlantic Ocean / Eastern Brazil"),
    ( -30, -10,"Mid-Atlantic / West Africa"),
    ( -10,  10,"Western Europe / Central Africa"),
    (  10,  30,"Central Europe / East Africa"),
    (  30,  50,"Eastern Europe / Middle East"),
    (  50,  70,"Central Asia / Persian Gulf"),
    (  70,  90,"South Asia / India"),
    (  90, 110,"Southeast Asia / China"),
    ( 110, 130,"East Asia / Philippines / Japan"),
    ( 130, 150,"Japan / Oceania / Eastern Australia"),
    ( 150, 180,"Western Pacific / Eastern Australia"),
]

def geo_region(lon):
    for lo, hi, name in _GEO_REGIONS:
        if lo <= lon < hi:
            return name
    return "Unknown region"

# ---------------------------------------------------------------------------
# OUTPUT FORMATTERS
# ---------------------------------------------------------------------------

def fmt_position(p_data):
    sign = p_data["sign"]
    deg  = p_data["degree"]
    mins = p_data["minutes"]
    rx   = " ℞" if p_data.get("retrograde") else ""
    sym  = SIGN_SYMBOL[p_data["sign_idx"]]
    return f"{sign} {sym} {deg:2d}°{mins:02d}'{rx}"

def print_planet_table(positions, cusps=None, title="PLANETARY POSITIONS"):
    section(title)
    print(f"  │  {'Planet':<12} {'Symbol':<3} {'Position':<24} {'House':>5}  {'Lat':>7}  {'Speed':>8}")
    print(f"  │  {'─'*12} {'─'*3} {'─'*24} {'─'*5}  {'─'*7}  {'─'*8}")
    for name in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn",
                 "Uranus","Neptune","Pluto","Chiron","N.Node","S.Node",
                 "Ceres","Pallas","Juno","Vesta"]:
        if name not in positions:
            continue
        d = positions[name]
        sym = PLANET_SYMBOL.get(name, "?")
        pos = fmt_position(d)
        house = ""
        if cusps:
            h = planet_house(d["longitude"], cusps)
            house = f"H{h:2d}"
        lat = f"{d.get('latitude', 0.0):+.2f}°"
        spd = f"{d.get('speed', 0.0):+.4f}°/d"
        print(f"  │  {name:<12} {sym:<3} {pos:<24} {house:>5}  {lat:>7}  {spd:>8}")
    print()

def print_aspects(aspects, max_show=40):
    section("ASPECTS")
    print(f"  │  {'Planet 1':<12} {'Asp':<14} {'Glyph':<5} {'Planet 2':<12} {'Orb':>6}  {'Quality':<12} {'App/Sep'}")
    print(f"  │  {'─'*12} {'─'*14} {'─'*5} {'─'*12} {'─'*6}  {'─'*12} {'─'*8}")
    for a in aspects[:max_show]:
        p1, p2, asp, orb, quality, glyph, applying = a
        app = "Appl." if applying else "Sep."
        print(f"  │  {p1:<12} {asp:<14} {glyph:<5} {p2:<12} {orb:>5.2f}°  {quality:<12} {app}")
    if len(aspects) > max_show:
        print(f"  │  ... and {len(aspects) - max_show} more aspects")
    print()

def print_dignity_table(positions):
    section("ESSENTIAL DIGNITIES")
    print(f"  │  {'Planet':<12} {'Sign':<14} {'Score':>5}  Dignities")
    print(f"  │  {'─'*12} {'─'*14} {'─'*5}  {'─'*40}")
    for name in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]:
        if name not in positions:
            continue
        d = positions[name]
        score, labels = essential_dignity(name, d["sign"], d["degree"])
        score_str = f"{score:+d}"
        print(f"  │  {name:<12} {d['sign']:<14} {score_str:>5}  {labels[0]}")
        for lbl in labels[1:]:
            print(f"  │  {'':<12} {'':<14} {'':>5}  {lbl}")
    print()

def print_norse_layer(positions):
    section("NORSE MYTHIC CORRESPONDENCES")
    for name in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn",
                 "Uranus","Neptune","Pluto","Chiron","N.Node"]:
        if name not in positions:
            continue
        d = positions[name]
        norse = NORSE_CORRESPONDENCES.get(name, "")
        sign = d["sign"]
        rune_name, rune_sym, rune_meaning = SIGN_RUNES.get(sign, ("?", "?", "?"))
        print(f"  │  {PLANET_SYMBOL.get(name,'?')} {name} in {sign} {SIGN_SYMBOL[d['sign_idx']]}")
        print(f"  │    Norse: {norse}")
        print(f"  │    Rune:  {rune_sym} {rune_name} — {rune_meaning}")
        print(f"  │    Wyrd note: {name} carries the energy of {norse.split('—')[0].strip()} through the realm of {rune_name}.")
        print()

def print_lots(lots_dict, cusps=None):
    section("ARABIC LOTS / HERMETIC PARTS")
    print(f"  │  {'Lot':<24} {'Position':<28} {'House':>5}")
    print(f"  │  {'─'*24} {'─'*28} {'─'*5}")
    lot_meanings = {
        "Lot of Fortune":   "Material circumstances, the body, luck in external affairs",
        "Lot of Spirit":    "Soul's intention, agency, inner life, the mind-will",
        "Lot of Eros":      "Desire, erotic love, what the soul longs for",
        "Lot of Necessity": "What compels us, obligations, fate's grip",
        "Lot of Courage":   "Daring, risk, the hero's threshold",
        "Lot of Victory":   "Success, where Jupiter's grace manifests",
        "Lot of Nemesis":   "Retribution, hidden enemies, Saturn's reckoning",
    }
    for name, lon in lots_dict.items():
        sign, sidx, deg, mins = deg_to_sign(lon)
        sym = SIGN_SYMBOL[sidx]
        pos = f"{sign} {sym} {deg:2d}°{mins:02d}'"
        house = ""
        if cusps:
            h = planet_house(lon, cusps)
            house = f"H{h:2d}"
        print(f"  │  {name:<24} {pos:<28} {house:>5}")
        meaning = lot_meanings.get(name, "")
        wrap_print(meaning, indent=7)
    print()

def print_antiscia(antiscia_dict):
    section("ANTISCIA & CONTRA-ANTISCIA")
    print(f"  │  {'Planet':<12} {'Antiscia':<24} {'Contra-Antiscia':<24}")
    print(f"  │  {'─'*12} {'─'*24} {'─'*24}")
    for name in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn",
                 "Uranus","Neptune","Pluto"]:
        if name not in antiscia_dict:
            continue
        a = antiscia_dict[name]
        print(f"  │  {name:<12} {a['antiscia']:<24} {a['contra']:<24}")
    print()

def print_hellenistic(positions, cusps, asc_lon):
    section("HELLENISTIC ANALYSIS")

    # Sect
    sun_lon = positions.get("Sun", {}).get("longitude", 0)
    day = is_day_chart(sun_lon, asc_lon)
    sect_name = "Day Chart (Diurnal)" if day else "Night Chart (Nocturnal)"
    sect_light = "Sun" if day else "Moon"
    print(f"  │  Sect: {sect_name}")
    print(f"  │  Sect Light: {sect_light}")
    print()

    # Planetary joys
    print(f"  │  Planetary Joys:")
    for planet, house_num in sorted(PLANETARY_JOY.items(), key=lambda x: x[1]):
        if planet in positions and cusps:
            actual_house = planet_house(positions[planet]["longitude"], cusps)
            joy = "✦ IN JOY" if actual_house == house_num else f"(joy H{house_num}, in H{actual_house})"
        else:
            joy = f"(joy H{house_num})"
        print(f"  │    {planet:<12} rejoices in H{house_num}  {joy}")
    print()

    # Triplicity rulers for sect light sign
    sl_sign = positions.get(sect_light, {}).get("sign", "")
    elem = ELEMENTS.get(sl_sign, "")
    if elem in TRIPLICITY:
        day_r, night_r, part_r = TRIPLICITY[elem]
        print(f"  │  Triplicity Rulers of {sect_light} ({sl_sign} / {elem}):")
        print(f"  │    Day ruler:          {day_r}")
        print(f"  │    Night ruler:        {night_r}")
        print(f"  │    Participating:      {part_r}")
        active = day_r if day else night_r
        print(f"  │    Active sect ruler:  {active}")
    print()

    # Mutual receptions
    receps = mutual_reception(positions)
    if receps:
        print(f"  │  Mutual Receptions:")
        for p1, p2, s1, s2 in receps:
            print(f"  │    {p1} in {s1} ⇔ {p2} in {s2}")
    else:
        print(f"  │  Mutual Receptions: none")
    print()

    # Stelliums
    sign_counts = {}
    house_counts = {}
    for pname, pd in positions.items():
        if pname in ("S.Node","Ceres","Pallas","Juno","Vesta"):
            continue
        sg = pd.get("sign")
        if sg:
            sign_counts[sg] = sign_counts.get(sg, []) + [pname]
        if cusps:
            h = planet_house(pd["longitude"], cusps)
            house_counts[h] = house_counts.get(h, []) + [pname]

    stelliums = [(sg, ps) for sg, ps in sign_counts.items() if len(ps) >= 3]
    house_stelliums = [(h, ps) for h, ps in house_counts.items() if len(ps) >= 3]
    if stelliums:
        print(f"  │  Stelliums by Sign:")
        for sg, ps in stelliums:
            print(f"  │    {sg}: {', '.join(ps)}")
    if house_stelliums:
        print(f"  │  Stelliums by House:")
        for h, ps in house_stelliums:
            print(f"  │    House {h}: {', '.join(ps)}")
    print()

# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------------------------

def _paired_location_provided(args: argparse.Namespace, index: int) -> bool:
    return bool(getattr(args, f"city{index}", None)) or (
        getattr(args, f"lat{index}", None) is not None and
        getattr(args, f"lon{index}", None) is not None)


def _resolve_paired_birth(args: argparse.Namespace, index: int) -> BirthTuple:
    defaults = load_rules("profiles.json")["legacy_defaults"]
    city = getattr(args, f"city{index}", None)
    nation = getattr(args, f"nation{index}", None)
    coordinate_pair(getattr(args, f"lat{index}", None), getattr(args, f"lon{index}", None),
                    (f"--lat{index}", f"--lon{index}"))
    return resolve_birth(
        getattr(args, f"date{index}"), getattr(args, f"time{index}", None),
        city or defaults["city"], nation or (defaults["nation"] if not city else ""),
        getattr(args, f"lat{index}", None), getattr(args, f"lon{index}", None),
        getattr(args, f"timezone{index}", None))


def _print_pair_times(args: argparse.Namespace, first: str, second: str) -> None:
    defaults = load_rules("profiles.json")["legacy_defaults"]
    for index, label in ((1, first), (2, second)):
        assumption = "" if _paired_location_provided(args, index) else (
            f"  ·  default location: {defaults['city']}, {defaults['nation']}")
        print(f"  Time {index}: {label}{assumption}")
    print()


def _require_birth_time(known: bool, command: str) -> None:
    if not known:
        raise CalculationError(f"{command} requires a known birth time; supply --time")


def _print_house_system(args) -> None:
    """Name a non-default house system so output never misleads."""
    system = getattr(args, "houses", "placidus") or "placidus"
    if system != "placidus":
        print(f"  House system: {system}")


def _optional_houses(jd: float, latitude: float, longitude: float,
                     known: bool, system: str = "placidus"
                     ) -> tuple[list[float] | None, float | None, float | None]:
    if not known:
        return (None, None, None)
    from astroengine.houses import house_cusps
    return house_cusps(jd, latitude, longitude, system)


def _print_time_certainty(known: bool, label: str | None = None) -> None:
    if label:
        print(f"  Time: {label}")
    if not known:
        print("  Time unknown: planetary positions use a noon surrogate.")
        print("  Houses and angles unavailable without a known birth time.")
    print()


def _print_astronomy(positions: dict[str, dict[str, Any]], label: str = "Chart") -> None:
    provenance = getattr(positions, "provenance", None)
    if provenance:
        groups: dict[tuple[str, int], list[str]] = {}
        for name, position in positions.items():
            if "backend" in position:
                key = (position["backend"], position["returned_flags"])
                groups.setdefault(key, []).append(name)
        print(f"  {label} ephemeris: requested {provenance['requested_backend']} "
              f"(flags {provenance['requested_flags']}); actual returned results:")
        for (backend, flags), names in groups.items():
            print(f"    {backend} (flags {flags}): {', '.join(names)}")
        print(f"  Frame: {provenance['zodiac']} · Swiss version "
              f"{provenance['swiss_ephemeris_version']} · rule {provenance['rule_version']}")
        for name, reason in getattr(positions, "unavailable", {}).items():
            logging.getLogger(__name__).warning("%s optional body %s unavailable: %s", label, name, reason)
        print()


def _print_house_overview(positions: dict[str, dict[str, Any]], cusps: list[float]) -> None:
    section("HOUSE OVERVIEW")
    for h_num, h_key in HOUSE_KEYWORDS:
        c_sign, csidx, c_deg, c_min = deg_to_sign(cusps[h_num - 1])
        in_house = [p for p, pd in positions.items()
                    if planet_house(pd["longitude"], cusps) == h_num and p != "S.Node"]
        in_str = f"  [{', '.join(in_house)}]" if in_house else ""
        print(f"  │  H{h_num:2d} {c_sign} {SIGN_SYMBOL[csidx]} {c_deg:2d}°  {h_key}{in_str}")
    print()


def _print_overlay(positions: dict[str, dict[str, Any]], cusps: list[float] | None,
                   source: str, receiver: str) -> None:
    if cusps is None:
        print(f"  Overlay into {receiver}'s houses unavailable: known time and location required.")
        print()
        return
    section(f"HOUSE OVERLAYS — {source}'s planets in {receiver}'s houses")
    print(f"  │  {'Planet':<12} {'Position':<24} {receiver+' House':>10}  Theme")
    for pname in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                  "Uranus", "Neptune", "Pluto", "Chiron", "N.Node"]:
        if pname in positions:
            h = planet_house(positions[pname]["longitude"], cusps)
            _, kw = HOUSE_KEYWORDS[h - 1]
            print(f"  │  {pname:<12} {fmt_position(positions[pname]):<24} "
                  f"{'H'+str(h):>10}  {kw.split('·')[0].strip()}")
    print()


def _print_transit_houses(positions: dict[str, dict[str, Any]], cusps: list[float]) -> None:
    section("TRANSITING PLANETS IN NATAL HOUSES")
    print(f"  │  {'Planet':<12} {'Position':<24} {'Natal House':>12}  Natal house theme")
    for name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                 "Uranus", "Neptune", "Pluto", "N.Node"]:
        if name in positions:
            h = planet_house(positions[name]["longitude"], cusps)
            _, kw = HOUSE_KEYWORDS[h - 1]
            print(f"  │  {name:<12} {fmt_position(positions[name]):<24} "
                  f"{'H'+str(h):>12}  {kw.split('·')[0].strip()}")
    print()



# ---------------------------------------------------------------------------
# Chart library wiring (--save / --load on every chart-producing command)
# ---------------------------------------------------------------------------

_LOAD_FIELDS = ("date", "time", "city", "nation", "lat", "lon",
                "timezone", "houses")


def add_chart_lib(parser, two_person=False, with_load=True):
    """Add --save / --load / --chart-dir to a subparser."""
    parser.add_argument("--save", default=None, metavar="NAME",
                        help="Save this chart to the chart library under NAME")
    parser.add_argument("--chart-dir", default=None, dest="chart_dir",
                        help="Chart library directory (default ~/.astroengine/charts)")
    if not with_load:
        return
    if two_person:
        parser.add_argument("--load1", default=None, metavar="NAME",
                            help="Load person 1 birth data from a saved chart")
        parser.add_argument("--load2", default=None, metavar="NAME",
                            help="Load person 2 birth data from a saved chart")
    else:
        parser.add_argument("--load", default=None, metavar="NAME",
                            help="Load birth data from a saved chart")


def apply_chart_load(args, suffix=""):
    """Fill missing birth-data args from a saved chart (--load/--load1/--load2)."""
    from astroengine.charts import load_chart
    attr = f"load{suffix}" if suffix else "load"
    name = getattr(args, attr, None)
    if not name:
        return
    saved = load_chart(name, getattr(args, "chart_dir", None))
    req = saved.get("request", {}) or {}
    legacy_defaults = load_rules("profiles.json")["legacy_defaults"]
    filled = []
    for field in _LOAD_FIELDS:
        key = f"{field}{suffix}"
        if not hasattr(args, key):
            continue
        current = getattr(args, key)
        saved_val = req.get(field)
        if saved_val in (None, ""):
            continue
        # only fill defaulted fields: the user's explicit choices always win
        if field in ("city", "nation"):
            default = legacy_defaults.get(field)
        elif field == "houses":
            default = "placidus"
        else:
            default = None
        if default is not None:
            fill = current == default
        else:
            fill = current in (None, "")
        if fill:
            setattr(args, key, saved_val)
            filled.append(key)
    if filled:
        print(f"  Loaded chart '{name}' ({saved.get('chart_type', '?')}) -> "
              f"{', '.join(filled)}", file=sys.stderr)


def require_date(args, field="date"):
    if not getattr(args, field, None):
        raise CalculationError(
            f"--{field} is required (or use --load NAME to fill it from a saved chart)")


def maybe_save_chart(args, chart_type, result):
    """Save the chart when --save NAME was given."""
    name = getattr(args, "save", None)
    if not name:
        return
    from astroengine.charts import save_chart
    skip = {"save", "load", "load1", "load2", "chart_dir", "cmd", "func"}
    request = {k: v for k, v in vars(args).items() if k not in skip}
    path = save_chart(name, chart_type, request, result or {},
                      getattr(args, "chart_dir", None))
    print(f"  Saved chart '{name}' -> {path}")


def cmd_tarot(args):
    from astroengine.tarot import draw, spreads
    if args.list_spreads:
        header("TAROT SPREADS", f"{len(spreads())} layouts")
        for name, positions in sorted(spreads().items()):
            print(f"  {name:<14} {len(positions):>2} cards — {', '.join(positions[:4])}"
                  + ("…" if len(positions) > 4 else ""))
        print()
        return {"spreads": sorted(spreads())}
    result = draw(spread=args.spread, seed=args.seed,
                  reversals=not args.no_reversals, question=args.question)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return {"reading": result}
    header("TAROT", f"{result['spread']}  ·  {len(result['cards'])} cards"
           + (f"  ·  seed {args.seed}" if args.seed is not None else ""))
    if args.question:
        print(f"  Question: {args.question}\n")
    for c in result["cards"]:
        rev = " (reversed)" if c["reversed"] else ""
        print(f"  {c['position']}:")
        print(f"    {c['card']}{rev} — {', '.join(c['keywords'])}")
        print(f"    {c['meaning']}")
    print()
    print("  Interpretive — symbolic counsel, not computed fact.")
    return {"reading": result}


def cmd_reading(args):
    from astroengine.readings import reading as weave
    positions, asc_sign, mc_sign = None, None, None
    if args.load:
        from astroengine.charts import load_chart
        saved = load_chart(args.load, getattr(args, "chart_dir", None))
        result = saved.get("result") or {}
        positions = result.get("positions") or result.get("natal") or {}
        for _key, _var in (("asc", "asc_sign"), ("mc", "mc_sign")):
            _lon = result.get(_key)
            if isinstance(_lon, (int, float)):
                if _var == "asc_sign":
                    asc_sign = deg_to_sign(_lon)[0]
                else:
                    mc_sign = deg_to_sign(_lon)[0]
        print(f"  Reading from saved chart '{args.load}'")
    else:
        apply_chart_load(args)
        require_date(args)
        y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
            args.date, args.time, args.city, args.nation,
            getattr(args, "lat", None), getattr(args, "lon", None),
            getattr(args, "timezone", None))
        jd = julian_day(y, mo, d, utc_hour)
        positions = calc_planet_positions(jd)
        cusps, asc, mc = _optional_houses(jd, lat, lon, time_known,
                                          getattr(args, "houses", "placidus"))
        if asc is not None:
            asc_sign = deg_to_sign(asc)[0]
        if mc is not None:
            mc_sign = deg_to_sign(mc)[0]
    woven = weave(kind=args.kind, positions=positions,
                  asc_sign=asc_sign, mc_sign=mc_sign)
    if args.json:
        print(json.dumps(woven, ensure_ascii=False, sort_keys=True))
        return {"reading": woven}
    header("ASTROLOGY READING", args.kind.upper())
    _print_house_system(args)
    for para in woven["paragraphs"]:
        print(f"  {para['text']}\n")
    print(f"  {woven['label']}")
    return {"reading": woven}


def cmd_numerology(args):
    from astroengine.numerology import full_reading
    if not args.name:
        raise CalculationError("--name is required for numerology")
    result = full_reading(args.date, args.name, for_year=args.year)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return {"reading": result}
    header("NUMEROLOGY", f"{args.name}  ·  {args.date}")
    for key in ("life_path", "destiny", "soul_urge", "personality",
                "birthday", "personal_year"):
        n = result[key]
        master = " ★ master" if n["master_number"] else ""
        print(f"  {n['kind']:<13} {n['number']}{master} — {n['title']}")
        print(f"    {n['meaning']}")
    print()
    print("  Interpretive — symbolic counsel, not computed fact.")
    return {"reading": result}


_WHEEL_BODIES = ("Sun", "Moon", "Mercury", "Venus", "Mars",
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "N.Node")


def _loc_label(req: dict) -> str:
    """Truthful location label: explicit coordinates beat default city names."""
    lat, lon = req.get("lat"), req.get("lon")
    try:
        if lat is not None and lon is not None:
            la, lo = float(lat), float(lon)
            return (f"{abs(la):.2f}°{'N' if la >= 0 else 'S'} "
                    f"{abs(lo):.2f}°{'E' if lo >= 0 else 'W'}")
    except (TypeError, ValueError):
        pass
    city, nation = req.get("city"), req.get("nation")
    return " ".join(x for x in (city, nation) if x)


def cmd_stars(args):
    from astroengine.stars import load_stars, star_hits
    if args.list:
        # the catalog needs no birth data at all
        stars = load_stars()
        if args.json:
            print(json.dumps({"stars": stars}, ensure_ascii=False,
                             sort_keys=True))
            return {"stars": stars}
        header("FIXED STARS", "the bright ones")
        for st in stars:
            print(f"  {st['name']:<14} {st['constellation']:<16} "
                  f"{st['nature']:<14} mag {st['magnitude']}")
        return {"stars": stars}
    if args.load:
        from astroengine.charts import load_chart
        saved = load_chart(args.load, getattr(args, "chart_dir", None))
        req = saved.get("request", {}) or {}
        for k in ("date", "time", "lat", "lon", "timezone", "city", "nation"):
            if getattr(args, k, None) in (None, "") and req.get(k) not in (None, ""):
                setattr(args, k, req.get(k))
        title = saved.get("name", "Seeker")
        print(f"  Reading the fixed stars for saved chart '{args.load}'",
              file=sys.stderr if args.json else sys.stdout)
    else:
        apply_chart_load(args)
        title = "Seeker"
    require_date(args)
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None))
    jd = julian_day(y, mo, d, utc_hour)
    hits = star_hits(jd, lat, lon, orb=args.orb)
    if args.json:
        print(json.dumps({"title": title, "hits": hits},
                         ensure_ascii=False, sort_keys=True))
        return {"hits": hits}
    header("FIXED STARS", f"{title}")
    if not hits:
        print(f"  No star within {args.orb}° of a planet or angle.")
    for h in hits:
        print(f"  {h['star']:<14} conjunct {h['natal_point']:<8} "
              f"orb {h['orb']:.2f}°  [{h['nature']}]")
        print(f"      {h['meaning']}")
    print()
    print("  Traditional lore, held lightly; the planets do the talking.")
    return {"hits": hits}


def cmd_elect(args):
    from astroengine.electional import find_windows, score_moment
    if args.load:
        from astroengine.charts import load_chart
        saved = load_chart(args.load, getattr(args, "chart_dir", None))
        req = saved.get("request", {}) or {}
        for k in ("lat", "lon", "timezone", "city", "nation"):
            if getattr(args, k, None) in (None, "") and req.get(k) not in (None, ""):
                setattr(args, k, req.get(k))
        title = saved.get("name", "Seeker")
    else:
        apply_chart_load(args)
        title = "Seeker"
    if getattr(args, "lat", None) is None or getattr(args, "lon", None) is None:
        raise CalculationError("elections need a place: --lat/--lon or --load NAME")
    tz_name = getattr(args, "timezone", None) or "UTC"
    try:
        fy, fm, fd = (int(x) for x in (args.from_date or datetime.date.today().isoformat()).split("-"))
        ty, tm, td = (int(x) for x in (args.to_date or (datetime.date.today() + datetime.timedelta(days=7)).isoformat()).split("-"))
        jd_from = julian_day(fy, fm, fd, 12.0)
        jd_to = julian_day(ty, tm, td, 12.0)
    except (ValueError, TypeError):
        raise CalculationError("use YYYY-MM-DD for --from-date/--to-date")
    windows = find_windows(jd_from, jd_to, args.lat, args.lon,
                           step_hours=args.step_hours, timezone=tz_name)
    top = windows[:args.top]
    if args.json:
        print(json.dumps({"title": title, "windows": top},
                         ensure_ascii=False, sort_keys=True))
        return {"windows": top}
    header("ELECTIONAL WINDOWS", f"{title}")
    for w in top:
        print(f"  {w['datetime']}  score {w['score']:+d}  {w['verdict']:<11} Moon in {w['moon_sign']}")
        for n in w["notes"][:4]:
            print(f"      · {n}")
    print()
    print("  Symbolic timing, not prediction of events.")
    return {"windows": top}


def cmd_watch(args):
    from astroengine.watch import upcoming_transits
    if args.load:
        from astroengine.charts import load_chart
        saved = load_chart(args.load, getattr(args, "chart_dir", None))
        req = saved.get("request", {}) or {}
        for k in ("date", "time", "lat", "lon", "timezone", "city", "nation"):
            if getattr(args, k, None) in (None, "") and req.get(k) not in (None, ""):
                setattr(args, k, req.get(k))
        title = saved.get("name", "Seeker")
        print(f"  Watching transits for saved chart '{args.load}'",
              file=sys.stderr if args.json else sys.stdout)
    else:
        apply_chart_load(args)
        title = "Seeker"
    require_date(args)
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None))
    jd_natal = julian_day(y, mo, d, utc_hour)
    try:
        fy, fm, fd = (int(x) for x in (args.from_date or datetime.date.today().isoformat()).split("-"))
        ty, tm, td = (int(x) for x in (args.to_date or (datetime.date.today() + datetime.timedelta(days=365)).isoformat()).split("-"))
        jd_from = julian_day(fy, fm, fd, 12.0)
        jd_to = julian_day(ty, tm, td, 12.0)
    except (ValueError, TypeError):
        raise CalculationError("use YYYY-MM-DD for --from-date/--to-date")
    hits = upcoming_transits(jd_natal, jd_from, jd_to, lat, lon, orb=args.orb)
    if args.json:
        print(json.dumps({"title": title, "transits": hits},
                         ensure_ascii=False, sort_keys=True))
        return {"transits": hits}
    header("TRANSIT WATCH", f"{title}")
    if not hits:
        print(f"  No outer-planet transits within {args.orb}° in this window.")
    for h in hits:
        print(f"  {h['date']}  {h['transit_body']:<8} {h['aspect']:<12} "
              f"natal {h['natal_point']:<8} orb {h['orb']:.2f}°")
    print()
    print("  Symbolic timing, not prediction of events.")
    return {"transits": hits}


def cmd_profection(args):
    from astroengine.profections import profection
    if args.load:
        from astroengine.charts import load_chart
        saved = load_chart(args.load, getattr(args, "chart_dir", None))
        result = saved.get("result") or {}
        positions = result.get("positions") or result.get("natal") or {}
        req = saved.get("request", {}) or {}
        if not getattr(args, "date", None) and req.get("date"):
            args.date = req.get("date")
        title = saved.get("name", "Seeker")
        print(f"  Profections for saved chart '{args.load}'",
              file=sys.stderr if args.json else sys.stdout)
    else:
        apply_chart_load(args)
        positions = None
        title = "Seeker"
    if not getattr(args, "date", None):
        raise CalculationError("--date is required (or --load NAME)")
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None))
    jd_natal = julian_day(y, mo, d, utc_hour)
    if positions is None:
        positions = calc_planet_positions(jd_natal)
    houses_system = getattr(args, "houses", "placidus") or "placidus"
    cusps, asc, mc = _optional_houses(jd_natal, lat, lon, time_known,
                                      houses_system)
    if asc is None:
        raise CalculationError("profections need a known birth time for the Ascendant")
    target = args.target_date or datetime.date.today().isoformat()
    # the time lord's natal longitude, for its condition
    prof = profection(asc, args.date, target)
    lord_pos = positions.get(prof["time_lord"]) or {}
    lord_lon = lord_pos.get("longitude")
    prof = profection(asc, args.date, target, lord_longitude=lord_lon)
    _print_house_system(args)
    if args.json:
        print(json.dumps({"title": title, "target_date": target,
                          **prof}, ensure_ascii=False, sort_keys=True))
        return prof
    header("ANNUAL PROFECTION", f"{title}  →  {target}")
    print(f"  Age {prof['age']}: profected {prof['profected_sign']} "
          f"(house {prof['profected_house']})")
    print(f"  Lord of the year: {prof['time_lord']}", end="")
    if prof["lord_sign"]:
        print(f" — natal {prof['lord_sign']}, {prof['lord_dignity']}")
    else:
        print()
    print(f"  ({prof['method']})")
    print()
    return prof


def cmd_solar_arc(args):
    from astroengine.directions import solar_arc, directed_aspects
    if args.load:
        from astroengine.charts import load_chart
        saved = load_chart(args.load, getattr(args, "chart_dir", None))
        result = saved.get("result") or {}
        positions = result.get("positions") or result.get("natal") or {}
        req = saved.get("request", {}) or {}
        for k in ("date", "time", "lat", "lon", "timezone", "city", "nation"):
            if getattr(args, k, None) in (None, "") and req.get(k) not in (None, ""):
                setattr(args, k, req.get(k))
        title = saved.get("name", "Seeker")
        print(f"  Solar arcs for saved chart '{args.load}'",
              file=sys.stderr if args.json else sys.stdout)
    else:
        apply_chart_load(args)
        title = "Seeker"
    require_date(args)
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None))
    jd_natal = julian_day(y, mo, d, utc_hour)
    target = args.target_date or datetime.date.today().isoformat()
    try:
        ty, tm, td = (int(x) for x in target.split("-"))
        jd_target = julian_day(ty, tm, td, 12.0)
    except (ValueError, TypeError):
        raise CalculationError(f"invalid --target-date '{target}': use YYYY-MM-DD")
    houses_system = getattr(args, "houses", "placidus") or "placidus"
    positions = calc_planet_positions(jd_natal)
    arc = solar_arc(jd_natal, jd_target, lat, lon, houses_system)
    natal_lon = {b: (positions[b]["longitude"] % 360.0) for b in arc["directed"]
                 if b in positions and positions[b].get("longitude") is not None}
    hits = directed_aspects(arc["directed"], natal_lon, orb=args.orb,
                              arc=arc["arc"])
    _print_house_system(args)
    if args.json:
        print(json.dumps({"title": title, "target_date": target,
                          "arc": arc["arc"], "years": arc["years"],
                          "aspects": hits}, ensure_ascii=False, sort_keys=True))
        return {"arc": arc, "aspects": hits}
    header("SOLAR ARC DIRECTIONS", f"{title}  →  {target}")
    print(f"  Solar arc: {arc['arc']:.2f}° over {arc['years']:.2f} years\n")
    if not hits:
        print(f"  No directed-to-natal aspects within {args.orb}°.")
    for h in hits:
        flag = "  ★ EXACT" if h["exact"] else ""
        print(f"  d.{h['directed']:<8} {h['aspect']:<12} n.{h['natal']:<8} "
              f"orb {h['orb']:>5.2f}°  {'applying' if h['applying'] else 'separating'}{flag}")
    print()
    return {"arc": arc, "aspects": hits}


def cmd_wheel(args):
    from astroengine.wheel import wheel_svg, PLANET_GLYPHS
    houses_system = getattr(args, "houses", "placidus") or "placidus"
    saved = None
    if args.load:
        from astroengine.charts import load_chart
        saved = load_chart(args.load, getattr(args, "chart_dir", None))
    if saved is not None and houses_system == "placidus":
        result = saved.get("result") or {}
        positions = result.get("positions") or result.get("natal") or {}
        cusps = result.get("cusps")
        asc = result.get("asc")
        mc = result.get("mc")
        title = saved.get("name", "Natal Chart")
        req = saved.get("request", {}) or {}
        subtitle = " ".join(x for x in (
            req.get("date"), req.get("time"),
            _loc_label(req)) if x)
        print(f"  Wheel for saved chart '{args.load}'")
    else:
        # Fresh computation; --load fills birth data via dispatch, and a
        # non-default --houses recomputes cusps in the requested system.
        apply_chart_load(args)
        require_date(args)
        y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
            args.date, args.time, args.city, args.nation,
            getattr(args, "lat", None), getattr(args, "lon", None),
            getattr(args, "timezone", None))
        jd = julian_day(y, mo, d, utc_hour)
        positions = calc_planet_positions(jd)
        cusps, asc, mc = _optional_houses(jd, lat, lon, time_known,
                                          houses_system)
        title = (saved.get("name", "Natal Chart") if saved
                 else "Natal Chart")
        if houses_system != "placidus":
            title += f" ({houses_system})"
            print(f"  Wheel for saved chart '{args.load}' "
                  f"with {houses_system} houses")
        subtitle = f"{args.date} {args.time or ''} {_loc_label(vars(args))}".strip()
    planets = []
    for body in _WHEEL_BODIES:
        p = positions.get(body) or {}
        if p.get("longitude") is None:
            continue
        planets.append({"name": body,
                        "glyph": PLANET_GLYPHS.get(body, "?"),
                        "longitude": p["longitude"]})
    aspects = []
    for p1, p2, name, _orb, _q, _g, _app in calc_aspects(
            positions, families={"major", "minor"}):
        if p1 in _WHEEL_BODIES and p2 in _WHEEL_BODIES:
            aspects.append({"a": p1, "b": p2, "kind": name.lower()})
    svg = wheel_svg(planets, cusps or [], aspects,
                    {"title": title, "subtitle": subtitle,
                     "asc": asc, "mc": mc})
    out = args.output or "wheel.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  Wheel written to {out} "
          f"({len(planets)} bodies, {len(aspects)} aspects)")
    return {"output": out, "bodies": len(planets), "aspects": len(aspects)}


def cmd_runecast(args):
    from astroengine.runecast import cast, layouts
    if args.list_layouts:
        header("RUNE LAYOUTS", f"{len(layouts())} casts")
        for name, positions in sorted(layouts().items()):
            print(f"  {name:<12} {len(positions):>2} runes — {', '.join(positions[:3])}"
                  + ("…" if len(positions) > 3 else ""))
        print()
        return {"layouts": sorted(layouts())}
    result = cast(layout=args.layout, seed=args.seed,
                  merkstave=not args.no_merkstave, blank=args.blank,
                  question=args.question)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return {"reading": result}
    header("RUNE CAST", f"{result['layout']}  ·  {len(result['runes'])} runes"
           + (f"  ·  seed {args.seed}" if args.seed is not None else ""))
    if args.question:
        print(f"  Question: {args.question}\n")
    for r in result["runes"]:
        murk = " (merkstave)" if r["merkstave"] else ""
        modern = " — modern invention" if r["modern_invention"] else ""
        print(f"  {r['position']}:")
        print(f"    {r['glyph']} {r['rune']}{murk}{modern} — {', '.join(r['keywords'])}")
        print(f"    {r['meaning']}")
    print()
    print("  Interpretive — symbolic counsel, not computed fact.")
    return {"reading": result}


def cmd_iching(args):
    from astroengine.iching import cast
    result = cast(question=args.question, method=args.method, seed=args.seed)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return {"reading": result}
    header("I-CHING", f"{result['method']}"
           + (f"  ·  seed {args.seed}" if args.seed is not None else ""))
    if args.question:
        print(f"  Question: {args.question}\n")
    p = result["primary"]
    print(f"  Primary — #{p['number']} {p['name']} ({p['chinese']})")
    print(f"    {p['judgment']}")
    if result["changing_lines"]:
        print(f"\n  Changing lines: {', '.join(map(str, result['changing_lines']))}")
        r = result["relating"]
        print(f"  Relating — #{r['number']} {r['name']} ({r['chinese']})")
        print(f"    {r['judgment']}")
    else:
        print("\n  No changing lines — the oracle stands as cast.")
    print()
    print("  Interpretive — symbolic counsel, not computed fact.")
    return {"reading": result}


def cmd_charts(args):
    from astroengine.charts import list_charts, chart_dir
    rows = list_charts(getattr(args, "chart_dir", None))
    header("CHART LIBRARY", str(chart_dir(getattr(args, "chart_dir", None))))
    if not rows:
        print("  (empty — save a chart with --save NAME)")
        print()
        return
    print(f"  │  {'Name':<24} {'Type':<16} {'Saved':<20}")
    print(f"  │  {'─'*24} {'─'*16} {'─'*20}")
    for r in rows:
        print(f"  │  {r['name']:<24} {r['chart_type']:<16} {r['saved_at']:<20}")
    print()


def cmd_chart_show(args):
    from astroengine.charts import load_chart
    c = load_chart(args.name, getattr(args, "chart_dir", None))
    header("CHART", f"{c['name']}  ·  {c['chart_type']}  ·  saved {c['saved_at']}")
    section("REQUEST")
    for k, v in sorted((c.get("request") or {}).items()):
        print(f"  │  {k:<14} {v}")
    section("RESULT (headline keys)")
    result = c.get("result") or {}
    if isinstance(result, dict):
        for k in sorted(result.keys())[:20]:
            v = result[k]
            preview = str(v)[:60]
            print(f"  │  {k:<14} {preview}")
    else:
        print(f"  │  {str(result)[:80]}")
    print()


def cmd_chart_delete(args):
    from astroengine.charts import delete_chart
    delete_chart(args.name, getattr(args, "chart_dir", None))
    print(f"  Deleted chart '{args.name}'")


def cmd_natal(args):
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, city_default_used = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    jd = julian_day(y, mo, d, utc_hour)
    name = args.name or "Seeker"

    # Determine display label for location
    loc_label = f"{args.city}, {args.nation}"
    if getattr(args, "lat", None) is not None and getattr(args, "lon", None) is not None:
        # When explicit coords are given, use them in the label
        lat_dir_co = 'N' if lat >= 0 else 'S'
        lon_dir_co = 'E' if lon >= 0 else 'W'
        loc_label = f"{abs(lat):.4f}°{lat_dir_co} {abs(lon):.4f}°{lon_dir_co}"

    positions = calc_planet_positions(jd)
    cusps, asc, mc = _optional_houses(jd, lat, lon, time_known,
                                          getattr(args, "houses", "placidus"))

    header(
        f"NATAL CHART — {name.upper()}",
        f"{args.date}  ·  {loc_label}"
    )
    _print_house_system(args)
    _print_time_certainty(time_known, tz_label)
    _print_astronomy(positions)
    sun_sign, moon_sign = positions["Sun"]["sign"], positions["Moon"]["sign"]
    print(f"  Sun: {sun_sign}  ·  Moon: {moon_sign}")
    if cusps is not None:
        asc_sign, asidx, asc_deg, asc_min = deg_to_sign(asc)
        mc_sign, msidx, mc_deg, mc_min = deg_to_sign(mc)
        print(f"  ASC (Rising): {asc_sign} {SIGN_SYMBOL[asidx]} {asc_deg}°{asc_min:02d}'")
        print(f"  MC  (Midheaven): {mc_sign} {SIGN_SYMBOL[msidx]} {mc_deg}°{mc_min:02d}'")
        day = is_day_chart(positions["Sun"]["longitude"], asc)
        print(f"  Chart Type: {'Day (Diurnal)' if day else 'Night (Nocturnal)'}")
    else:
        print("  Sect, lots and house interpretations unavailable without a known birth time.")
    print()

    print_planet_table(positions, cusps)
    print_aspects(calc_aspects(positions))
    print_dignity_table(positions)

    # Lots
    if cusps is not None:
        lots = calc_lots(positions, asc, day)
        print_lots(lots, cusps)

    # Antiscia
    print_antiscia(calc_antiscia(positions))

    # Hellenistic
    if cusps is not None:
        print_hellenistic(positions, cusps, asc)

    # Norse layer
    print_norse_layer(positions)

    if cusps is not None:
        _print_house_overview(positions, cusps)

    print(f"  {hr()}")
    lat_dir = 'N' if lat >= 0 else 'S'
    lon_dir = 'E' if lon >= 0 else 'W'
    print(f"  Latitude: {abs(lat):.4f}°{lat_dir}  ·  Longitude: {abs(lon):.4f}°{lon_dir}  ·  JD: {jd:.4f}")


    return {"positions": positions, "cusps": cusps, "asc": asc, "mc": mc}
def cmd_transit(args):
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    jd_natal = julian_day(y, mo, d, utc_hour)

    # Gap 2 fix: --transit-date overrides "now"
    transit_date_str = getattr(args, "transit_date", None)
    if transit_date_str is not None:
        ty, tmo, td, thour = parse_date_time(transit_date_str,
                                              getattr(args, "transit_time", None))
        jd_sky = julian_day(ty, tmo, td, thour)
        ttime = getattr(args, "transit_time", None) or "12:00"
        sky_label = f"{transit_date_str} {ttime} UTC"
    else:
        if getattr(args, "transit_time", None) is not None:
            raise CalculationError("Supply --transit-date with --transit-time")
        now = datetime.datetime.utcnow()
        jd_sky = julian_day(now.year, now.month, now.day,
                             now.hour + now.minute / 60.0)
        sky_label = now.strftime("%Y-%m-%d %H:%M UTC")

    natal_pos   = calc_planet_positions(jd_natal)
    transit_pos = calc_planet_positions(jd_sky)
    cusps, asc, mc = _optional_houses(jd_natal, lat, lon, time_known,
                                          getattr(args, "houses", "placidus"))

    header("TRANSIT CHART", f"Natal: {args.date}  ·  Sky: {sky_label}")
    _print_house_system(args)

    _print_time_certainty(time_known, tz_label)
    _print_astronomy(natal_pos, "Natal")
    _print_astronomy(transit_pos, "Sky")
    print_planet_table(transit_pos, title=f"SKY POSITIONS  ({sky_label})")

    if cusps is not None:
        _print_transit_houses(transit_pos, cusps)

    # Transit-to-natal aspects
    section("TRANSIT-TO-NATAL ASPECTS")
    print(f"  │  {'Transit Planet':<14} {'Glyph+Aspect':<16} {'Natal Planet':<14} {'Orb':>6}  {'Quality':<12} App/Sep")
    print(f"  │  {'─'*14} {'─'*16} {'─'*14} {'─'*6}  {'─'*12} {'─'*6}")
    rows = []
    for t_name, t_data in transit_pos.items():
        if t_name in ("S.Node", "Ceres","Pallas","Juno","Vesta"):
            continue
        t_lon = t_data["longitude"]
        for n_name, n_data in natal_pos.items():
            if n_name in ("S.Node", "Ceres","Pallas","Juno","Vesta"):
                continue
            n_lon = n_data["longitude"]
            diff = angle_diff(t_lon, n_lon)
            for asp_name, (angle, orb_l, orb_o, glyph, quality) in ASPECTS.items():
                if asp_name in ("Quintile","Bi-Quintile","Septile","Semi-Sextile") \
                        or asp_name in OBSCURE_ASPECT_NAMES:
                    continue
                orb = orb_l if t_name in ("Sun","Moon") or n_name in ("Sun","Moon") else orb_o
                actual_orb = abs(diff - angle)
                if actual_orb <= orb:
                    # Natal point is fixed: applying = transit moving toward exactness
                    applying = is_applying(t_lon, t_data["speed"], n_lon, 0.0, angle)
                    rows.append((actual_orb, t_name, glyph, asp_name, n_name, quality, applying))
    for actual_orb, t_name, glyph, asp_name, n_name, quality, applying in sorted(rows):
        app = "Appl." if applying else "Sep."
        print(f"  │  {t_name:<14} {glyph} {asp_name:<14} {n_name:<14} {actual_orb:>5.2f}°  {quality:<12} {app}")
    print()


    return {"natal": natal_pos, "transit": transit_pos}
def cmd_synastry(args):
    y1, mo1, d1, h1, lat1, lon1, tz1, tzl1, known1, _ = _resolve_paired_birth(args, 1)
    y2, mo2, d2, h2, lat2, lon2, tz2, tzl2, known2, _ = _resolve_paired_birth(args, 2)
    jd1 = julian_day(y1, mo1, d1, h1)
    jd2 = julian_day(y2, mo2, d2, h2)

    pos1 = calc_planet_positions(jd1)
    pos2 = calc_planet_positions(jd2)

    n1 = getattr(args, "name1", "Person A")
    n2 = getattr(args, "name2", "Person B")

    cusps1, _, _ = _optional_houses(jd1, lat1, lon1, known1 and _paired_location_provided(args, 1),
                                        getattr(args, "houses", "placidus"))
    cusps2, _, _ = _optional_houses(jd2, lat2, lon2, known2 and _paired_location_provided(args, 2),
                                        getattr(args, "houses", "placidus"))
    header("SYNASTRY CHART", f"{n1}  ×  {n2}")
    _print_house_system(args)
    _print_pair_times(args, tzl1, tzl2)
    _print_time_certainty(known1)
    _print_time_certainty(known2)
    _print_astronomy(pos1, n1)
    _print_astronomy(pos2, n2)

    print_planet_table(pos1, cusps1, title=f"CHART 1 — {n1}")
    print_planet_table(pos2, cusps2, title=f"CHART 2 — {n2}")

    _print_overlay(pos1, cusps2, n1, n2)
    _print_overlay(pos2, cusps1, n2, n1)

    # Cross-aspects
    section(f"CROSS-ASPECTS  {n1} → {n2}")
    print(f"  │  {n1+' Planet':<16} {'Asp':<16} {n2+' Planet':<16} {'Orb':>6}  {'Quality':<12} App/Sep")
    print(f"  │  {'─'*16} {'─'*16} {'─'*16} {'─'*6}  {'─'*12} {'─'*6}")

    rows = []
    for p1, d1_data in pos1.items():
        if p1 not in ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn",
                       "Uranus","Neptune","Pluto","Chiron","N.Node"):
            continue
        for p2, d2_data in pos2.items():
            if p2 not in ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn",
                           "Uranus","Neptune","Pluto","Chiron","N.Node"):
                continue
            diff = angle_diff(d1_data["longitude"], d2_data["longitude"])
            for asp_name, (angle, orb_l, orb_o, glyph, quality) in ASPECTS.items():
                if asp_name in ("Quintile","Bi-Quintile","Septile","Semi-Sextile") \
                        or asp_name in OBSCURE_ASPECT_NAMES:
                    continue
                orb = orb_l if p1 in ("Sun","Moon") or p2 in ("Sun","Moon") else orb_o
                actual_orb = abs(diff - angle)
                if actual_orb <= orb:
                    applying = is_applying(d1_data["longitude"], d1_data["speed"],
                                           d2_data["longitude"], d2_data["speed"], angle)
                    rows.append((actual_orb, p1, glyph, asp_name, p2, quality, applying))
    for actual_orb, p1, glyph, asp_name, p2, quality, applying in sorted(rows):
        app = "Appl." if applying else "Sep."
        print(f"  │  {p1:<16} {glyph} {asp_name:<14} {p2:<16} {actual_orb:>5.2f}°  {quality:<12} {app}")
    print()


    return {"person1": pos1, "person2": pos2}
def cmd_solar_return(args):
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    jd_natal = julian_day(y, mo, d, utc_hour)
    target_year = return_year(getattr(args, "year", None))
    _require_birth_time(time_known, "solar-return")

    if not SWE:
        raise CalculationError("pyswisseph is required for solar return calculation")

    # Find exact moment when Sun returns to natal Sun position
    natal_pos = calc_planet_positions(jd_natal)
    natal_sun_lon = natal_pos.get("Sun", {}).get("longitude", 0)

    # Start searching from ~1 month before the birthday in the target year
    # (for January birthdays, December of the previous year).
    start_yr = target_year if mo > 1 else target_year - 1
    start_mo = mo - 1 if mo > 1 else 12
    jd_search = julian_day(start_yr, start_mo, min(d, 28), 0)
    # Refine iteratively: the Sun moves ~0.986°/day, so each degree of
    # remaining longitude error corresponds to ~1/0.986 days of time.
    for _ in range(50):
        pos = calc_planet_positions(jd_search)
        sun_lon = pos.get("Sun", {}).get("longitude", natal_sun_lon)
        diff = (natal_sun_lon - sun_lon) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < 0.001:
            break
        jd_search += diff / 0.9856

    sr_pos = calc_planet_positions(jd_search)
    from astroengine.houses import house_cusps as _hc
    sr_cusps, sr_asc, sr_mc = _hc(jd_search, lat, lon,
                                     getattr(args, "houses", "placidus"))

    sr_dt = jd_to_dt(jd_search)
    header("SOLAR RETURN CHART", f"Year {target_year}  ·  {sr_dt}  ·  {args.city}, {args.nation}")
    _print_house_system(args)
    _print_astronomy(natal_pos, "Natal")
    _print_astronomy(sr_pos, "Solar return")
    print_planet_table(sr_pos, sr_cusps)
    print_aspects(calc_aspects(sr_pos))
    sr_asc_sign, saidx, sa_deg, sa_min = deg_to_sign(sr_asc)
    print(f"  SR ASC: {sr_asc_sign} {SIGN_SYMBOL[saidx]} {sa_deg}°{sa_min:02d}'")
    print()


    return {"natal": natal_pos, "solar_return": sr_pos}
def cmd_progressions(args):
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    jd_natal = julian_day(y, mo, d, utc_hour)

    prog_date_str = getattr(args, "prog_date", None)
    if prog_date_str is None:
        prog_date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    py, pmo, pd, _ = parse_date_time(prog_date_str)
    jd_prog_target = julian_day(py, pmo, pd, 12.0)

    # Secondary progressions: 1 day = 1 year
    years_elapsed = (jd_prog_target - jd_natal) / 365.25
    jd_prog = jd_natal + years_elapsed  # 1 day per year

    prog_pos = calc_planet_positions(jd_prog)
    prog_cusps, prog_asc, prog_mc = _optional_houses(jd_prog, lat, lon, time_known)
    natal_pos = calc_planet_positions(jd_natal)

    header(
        "SECONDARY PROGRESSIONS",
        f"Natal: {args.date}  ·  Progressed to: {prog_date_str}  ({years_elapsed:.1f} years)"
    )
    _print_time_certainty(time_known, tz_label)
    _print_astronomy(natal_pos, "Natal")
    _print_astronomy(prog_pos, "Progressed")
    print_planet_table(prog_pos, prog_cusps, title="PROGRESSED PLANETS")

    # Aspects: progressed to natal
    section("PROGRESSED-TO-NATAL ASPECTS")
    print(f"  │  {'Prog Planet':<14} {'Aspect':<14} {'Natal Planet':<14} {'Orb':>6}")
    print(f"  │  {'─'*14} {'─'*14} {'─'*14} {'─'*6}")
    for pp, pd_data in prog_pos.items():
        if pp in ("S.Node","Ceres","Pallas","Juno","Vesta","Uranus","Neptune","Pluto"):
            continue
        for np, nd_data in natal_pos.items():
            if np in ("S.Node","Ceres","Pallas","Juno","Vesta"):
                continue
            diff = angle_diff(pd_data["longitude"], nd_data["longitude"])
            for asp_name, (angle, orb_l, orb_o, glyph, quality) in ASPECTS.items():
                if asp_name in ("Quintile","Bi-Quintile","Septile","Semi-Sextile","Semi-Square","Sesquisquare") \
                        or asp_name in OBSCURE_ASPECT_NAMES:
                    continue
                orb = 1.5  # tight orbs for progressions
                if abs(diff - angle) <= orb:
                    print(f"  │  {pp:<14} {glyph} {asp_name:<12} {np:<14} {abs(diff-angle):>5.2f}°")
    print()


    return {"progressed": prog_pos}
def cmd_lunar(args):
    if not SWE:
        raise CalculationError("pyswisseph is required for lunar calculations")

    now = datetime.datetime.utcnow()
    jd_now = julian_day(now.year, now.month, now.day,
                         now.hour + now.minute / 60.0)
    pos = calc_planet_positions(jd_now)

    sun_lon  = pos.get("Sun",  {}).get("longitude", 0)
    moon_lon = pos.get("Moon", {}).get("longitude", 0)

    phase_name, phase_glyph, elongation, illumination = calc_lunar_phase(sun_lon, moon_lon)
    moon_sign, msidx, m_deg, m_min = deg_to_sign(moon_lon)
    sun_sign,  ssidx, s_deg, s_min = deg_to_sign(sun_lon)

    header("LUNAR INTELLIGENCE", now.strftime("%Y-%m-%d  %H:%M UTC"))

    _print_astronomy(pos)
    print(f"  Current Phase:    {phase_glyph}  {phase_name}")
    print(f"  Moon Position:    {moon_sign} {SIGN_SYMBOL[msidx]} {m_deg}°{m_min:02d}'")
    print(f"  Sun Position:     {sun_sign}  {SIGN_SYMBOL[ssidx]} {s_deg}°{s_min:02d}'")
    print(f"  Elongation:       {elongation:.2f}°")
    print(f"  Illumination:     {illumination}%")
    print()

    # Void of course
    voc, hours_remaining = void_of_course(jd_now, moon_lon, pos)
    print(f"  Void of Course:   {'YES — Moon casts no more aspects in {moon_sign}' if voc else f'No  (ingress in ~{hours_remaining:.1f}h)'}")
    print()

    # Rune of current Moon sign
    rune_name, rune_sym, rune_meaning = SIGN_RUNES.get(moon_sign, ("?", "?", "?"))
    print(f"  Moon Rune:        {rune_sym} {rune_name} — {rune_meaning}")
    print()

    # Next lunations
    try:
        new_jd, full_jd = next_lunation(jd_now)
        if new_jd:
            print(f"  Next New Moon:    {jd_to_dt(new_jd)}")
        if full_jd:
            print(f"  Next Full Moon:   {jd_to_dt(full_jd)}")
    except Exception:
        pass
    print()

    # Moon aspects to current sky
    section("MOON ASPECTS (NOW)")
    moon_aspects = [(p1, p2, asp, orb, q, g, app)
                    for p1, p2, asp, orb, q, g, app in calc_aspects(pos)
                    if "Moon" in (p1, p2)]
    for p1, p2, asp, orb, q, g, app in moon_aspects:
        other = p2 if p1 == "Moon" else p1
        print(f"  │  Moon {g} {asp:<14} {other:<12}  orb {orb:.2f}°  {'Appl.' if app else 'Sep.'}")
    print()


    return {"positions": pos}
def cmd_planet_hours(args):
    date = parse_civil(args.date).date() if args.date is not None else datetime.date.today()
    pair = coordinate_pair(getattr(args, "lat", None), getattr(args, "lon", None))
    if pair is not None:
        lat, lon = pair
    elif getattr(args, "city", None):
        lat, lon, _ = geocode_city(args.city, args.nation or "")
    elif getattr(args, "nation", None):
        raise CalculationError("Supply a city with --nation, or both --lat and --lon")
    else:
        defaults = load_rules("profiles.json")["legacy_defaults"]
        lat, lon = defaults["planet_hours_latitude"], defaults["planet_hours_longitude"]

    hours_data, day_ruler, sunrise_jd, sunset_jd = planetary_hours(date, lat, lon)

    header("PLANETARY HOURS", f"{date}  ·  Day Ruler: {day_ruler}  ·  Lat {lat:.2f}° Lon {lon:.2f}°")

    print(f"  Sunrise: {jd_to_dt(sunrise_jd)}")
    print(f"  Sunset:  {jd_to_dt(sunset_jd)}")
    print()

    section("DAY HOURS")
    print(f"  │  {'Hour':>4}  {'Planet':<12} {'Norse':<40}")
    print(f"  │  {'─'*4}  {'─'*12} {'─'*40}")
    for period, num, planet, jd_start, dur_min in hours_data:
        if period == "day":
            norse = NORSE_CORRESPONDENCES.get(planet, "").split("—")[0].strip()
            time_str = jd_to_dt(jd_start).split(" ")[1] if SWE else ""
            print(f"  │  D{num:>2}.  {planet:<12} {norse}")

    section("NIGHT HOURS")
    print(f"  │  {'Hour':>4}  {'Planet':<12} {'Norse'}")
    print(f"  │  {'─'*4}  {'─'*12} {'─'*40}")
    for period, num, planet, jd_start, dur_min in hours_data:
        if period == "night":
            norse = NORSE_CORRESPONDENCES.get(planet, "").split("—")[0].strip()
            print(f"  │  N{num:>2}.  {planet:<12} {norse}")
    print()


    return {"hours": hours_data, "day_ruler": day_ruler}
def cmd_lots(args):
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    jd = julian_day(y, mo, d, utc_hour)
    _require_birth_time(time_known, "lots")
    positions = calc_planet_positions(jd)
    cusps, asc, mc = calc_houses(jd, lat, lon)
    sun_lon = positions.get("Sun", {}).get("longitude", 0)
    day = is_day_chart(sun_lon, asc)

    header("ARABIC LOTS / HERMETIC PARTS", f"{args.date}  ·  {'Day' if day else 'Night'} Chart")
    _print_astronomy(positions)
    lots = calc_lots(positions, asc, day)
    print_lots(lots, cusps)


    return {"lots": lots, "positions": positions}
def cmd_hellenistic(args):
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    jd = julian_day(y, mo, d, utc_hour)
    _require_birth_time(time_known, "hellenistic")
    positions = calc_planet_positions(jd)
    cusps, asc, mc = calc_houses(jd, lat, lon)

    header("HELLENISTIC ASTROLOGY ANALYSIS", f"{args.date}  {args.time or ''}")
    _print_astronomy(positions)
    print_hellenistic(positions, cusps, asc)
    print_dignity_table(positions)
    print_antiscia(calc_antiscia(positions))


    return {"positions": positions}
def cmd_aspect_grid(args):
    y, mo, d, hour = parse_date_time(args.date, args.time)
    jd = julian_day(y, mo, d, hour)  # aspect-grid has no location so no TZ conversion
    positions = calc_planet_positions(jd)

    header("FULL ASPECT GRID", args.date)
    _print_time_certainty(args.time is not None)
    _print_astronomy(positions)
    fams = None if args.aspects == "all" else {args.aspects}
    print_aspects(calc_aspects(positions, families=fams), max_show=200)


    return {"aspects": calc_aspects(positions), "positions": positions}
def cmd_runic(args):
    """The runic star-program: Pennick's runic astrology as one command."""
    from astroengine.runic import runic_reading
    flag_map = [("half_month", "half_month"), ("hour", "hour"),
                ("tide", "tide"), ("station", "station"),
                ("weekday", "weekday"), ("mansion", "mansion"),
                ("life_period", "life_period"), ("name", "name"),
                ("reading", "reading")]
    layers = [layer for layer, dest in flag_map
              if getattr(args, dest, False)]
    if args.full or not layers:
        layers = ["half_month", "hour", "tide", "station", "weekday",
                  "mansion", "life_period", "name", "reading"]
    reading = runic_reading(
        args.datetime, args.lon, args.timezone,
        age_years=args.age,
        moon_sidereal_longitude=args.moon_lon)
    if args.json:
        keep = set(layers)
        if "hour" in layers:
            keep |= {"sele", "planetary_hour"}
        out = {"computation":
               {k: v for k, v in reading["computation"].items()
                if k in keep},
               "provenance": {"source": "Pennick (2023)",
                              "historical_claim": "modern synthesis"}}
        if "reading" in layers:
            out["interpretation"] = reading["interpretation"]
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return {"reading": reading}

    comp = reading["computation"]
    header("RUNIC STAR-PROGRAM",
           f"{args.datetime}  ·  Lon {args.lon}°  ·  {args.timezone}")
    if "half_month" in layers:
        h = comp["half_month"]
        section("HALF-MONTH RUNE")
        print(f"  {h['rune']} — half-month from {h['half_month_start']} "
              f"({h['correspondences'].get('deity', '')})")
    if "hour" in layers:
        hr, ph = comp["hour"], comp["planetary_hour"]
        section("RUNIC HOUR")
        print(f"  Hour rune {hr['rune']} (LAT window {hr['window']})")
        print(f"  Planetary hour: {ph['deity']} (clock hour {ph['clock_hour']})"
              + ("  ·  SELE — especially powerful" if comp["sele"] else ""))
    if "tide" in layers:
        t = comp["tide"]
        section("TIDE OF DAY")
        print(f"  {t['english']} ({t['old_norse']})")
    if "station" in layers:
        st = comp["station"]
        section("STATION OF THE MYSTIC YEAR")
        print(f"  {st['name']} ({st['runes']}): {st['symbolic_event']}")
    if "weekday" in layers:
        w = comp["weekday"]
        section("WEEKDAY")
        print(f"  {w['weekday']} — {w['deity']} — rune {w['rune']}")
    if "mansion" in layers and "mansion" in comp:
        m = comp["mansion"]
        section("LUNAR MANSION")
        print(f"  {m['mansion']}. {m['northern_name']} ({m['star']}) — "
              f"rune {m['rune']}")
    if "life_period" in layers and "life_period" in comp:
        lp = comp["life_period"]
        section("LIFE PERIOD")
        print(f"  {lp['deity']} ({lp['planet']}) — "
              f"{lp['years_elapsed']:.1f} years in, "
              f"{lp['years_remaining']:.1f} remaining")
    if "name" in layers:
        n = comp["name"]
        section("RUNIC NAME")
        print(f"  {n['pair']}  (half-month {n['half_month_rune']} + "
              f"hour {n['hour_rune']})")
    if "reading" in layers:
        section("READING — INTERPRETIVE (Ch. 8)")
        for s in reading["interpretation"]["statements"]:
            print(f"  · {s['statement']}")
    print()
    print("  Provenance: Pennick (2023) · modern synthesis · computation "
          "and interpretation labeled separately")


    return {"reading": reading}
def cmd_dignity(args):
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    jd = julian_day(y, mo, d, utc_hour)
    positions = calc_planet_positions(jd)

    header("ESSENTIAL DIGNITIES", f"{args.date}  {args.time or ''}")
    _print_time_certainty(time_known, tz_label)
    _print_astronomy(positions)
    print_dignity_table(positions)

    # Mutual receptions
    receps = mutual_reception(positions)
    section("MUTUAL RECEPTIONS")
    if receps:
        for p1, p2, s1, s2 in receps:
            print(f"  │  {p1} in {s1}  ⇔  {p2} in {s2}")
            print(f"  │    Both planets swap homes — strong cooperative bond, dignity by mutual reception")
    else:
        print(f"  │  None detected")
    print()

    # Scoring summary
    section("DIGNITY SCORE SUMMARY")
    scores = []
    for name in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]:
        if name not in positions:
            continue
        d_data = positions[name]
        score, _ = essential_dignity(name, d_data["sign"], d_data["degree"])
        scores.append((score, name))
    scores.sort(reverse=True)
    print(f"  │  {'Rank':<5} {'Planet':<12} {'Score':>6}  {'Status'}")
    print(f"  │  {'─'*5} {'─'*12} {'─'*6}  {'─'*20}")
    for i, (score, name) in enumerate(scores, 1):
        if score >= 5:   status = "Highly dignified"
        elif score >= 3: status = "Dignified"
        elif score >= 1: status = "Moderate"
        elif score == 0: status = "Peregrine"
        elif score >= -3:status = "Weakened"
        else:            status = "Debilitated"
        print(f"  │  {i:<5} {name:<12} {score:>+6}  {status}")
    print()


    return {"positions": positions}
def cmd_antiscia(args):
    """Gap 1 fix: standalone antiscia subcommand."""
    y, mo, d, hour = parse_date_time(args.date, args.time)
    jd = julian_day(y, mo, d, hour)
    positions = calc_planet_positions(jd)

    header("ANTISCIA & CONTRA-ANTISCIA", f"{args.date}  {args.time or ''}")

    print("  Antiscia mirror: solstice axis (0° Cancer / 0° Capricorn)")
    print("  Contra-antiscia: equinox axis (0° Aries / 0° Libra)")
    print()

    antiscia_data = calc_antiscia(positions)
    _print_time_certainty(args.time is not None)
    _print_astronomy(positions)
    print_antiscia(antiscia_data)

    # Check for antiscia conjunctions between planets
    section("ANTISCIA CONNECTIONS (within 1°)")
    print(f"  │  {'Planet A':<12} {'Antiscia of A':<24} {'Planet B':<12} {'Position of B':<24} {'Orb':>6}")
    print(f"  │  {'─'*12} {'─'*24} {'─'*12} {'─'*24} {'─'*6}")
    planet_list = [p for p in antiscia_data]
    found_any = False
    for i, p1 in enumerate(planet_list):
        for p2 in planet_list[i+1:]:
            if p2 not in positions:
                continue
            a_lon  = antiscia_data[p1]["antiscia_lon"]
            p2_lon = positions[p2]["longitude"]
            orb = angle_diff(a_lon, p2_lon)
            if orb <= 1.0:
                found_any = True
                print(f"  │  {p1:<12} {antiscia_data[p1]['antiscia']:<24} {p2:<12} {fmt_position(positions[p2]):<24} {orb:>5.2f}°")
            # Also check contra-antiscia
            c_lon = antiscia_data[p1]["contra_lon"]
            c_orb = angle_diff(c_lon, p2_lon)
            if c_orb <= 1.0:
                found_any = True
                print(f"  │  {p1:<12} contra: {antiscia_data[p1]['contra']:<18} {p2:<12} {fmt_position(positions[p2]):<24} {c_orb:>5.2f}°  [contra]")
    if not found_any:
        print(f"  │  No antiscia connections within 1° orb")
    print()


    return {"antiscia": antiscia_data, "positions": positions}
def cmd_composite(args):
    """Composite chart (midpoint method) for two people. Optionally show Davison chart too."""
    y1, mo1, d1, h1, _lat1, _lon1, _, tzl1, known1, _ = _resolve_paired_birth(args, 1)
    y2, mo2, d2, h2, _lat2, _lon2, _, tzl2, known2, _ = _resolve_paired_birth(args, 2)
    jd1 = julian_day(y1, mo1, d1, h1)
    jd2 = julian_day(y2, mo2, d2, h2)
    n1 = getattr(args, "name1", "Person A")
    n2 = getattr(args, "name2", "Person B")

    pos1 = calc_planet_positions(jd1)
    pos2 = calc_planet_positions(jd2)
    comp = calc_composite(pos1, pos2)

    davison_available = (known1 and known2 and _paired_location_provided(args, 1)
                         and _paired_location_provided(args, 2))
    if davison_available:
        jd_dav, lat_dav, lon_dav = calc_davison(jd1, jd2, _lat1, _lon1, _lat2, _lon2)
        dav_pos = calc_planet_positions(jd_dav)
        from astroengine.houses import house_cusps as _hc2
        dav_cusps, dav_asc, dav_mc = _hc2(jd_dav, lat_dav, lon_dav,
                                             getattr(args, "houses", "placidus"))

    header("COMPOSITE CHART", f"{n1}  +  {n2}  (Midpoint Method)")
    _print_house_system(args)
    _print_pair_times(args, tzl1, tzl2)
    _print_astronomy(pos1, n1)
    _print_astronomy(pos2, n2)
    print("  Composite positions are symbolic midpoints, with no physical houses or ephemeris backend.")
    print_planet_table(comp, title="COMPOSITE PLANETS")
    print_aspects(calc_aspects(comp))
    print_dignity_table(comp)

    if davison_available:
        _print_astronomy(dav_pos, "Davison")
        dav_dt   = jd_to_dt(jd_dav)
        section(f"DAVISON RELATIONSHIP CHART  ({dav_dt}  ·  {lat_dav:.2f}°N {lon_dav:.2f}°E)")
        print_planet_table(dav_pos, dav_cusps, title="DAVISON PLANETS")
        asc_sign, asidx, asc_deg, asc_min = deg_to_sign(dav_asc)
        mc_sign,  msidx, mc_deg,  mc_min  = deg_to_sign(dav_mc)
        print(f"  Davison ASC: {asc_sign} {SIGN_SYMBOL[asidx]} {asc_deg}°{asc_min:02d}'")
        print(f"  Davison MC:  {mc_sign}  {SIGN_SYMBOL[msidx]} {mc_deg}°{mc_min:02d}'")
        print()
    else:
        print("  Davison chart unavailable: both known birth times and actual locations required.")
        print()


    return {"composite": comp}
def cmd_synergy(args):
    """Full relationship analysis: synastry + composite + synergy score + midpoints."""
    y1, mo1, d1, h1, _la1, _lo1, _, tzl1, _, _ = _resolve_paired_birth(args, 1)
    y2, mo2, d2, h2, _la2, _lo2, _, tzl2, _, _ = _resolve_paired_birth(args, 2)
    jd1 = julian_day(y1, mo1, d1, h1)
    jd2 = julian_day(y2, mo2, d2, h2)
    n1 = getattr(args, "name1", "Person A")
    n2 = getattr(args, "name2", "Person B")

    pos1 = calc_planet_positions(jd1)
    pos2 = calc_planet_positions(jd2)
    comp = calc_composite(pos1, pos2)

    header("SYNERGY ANALYSIS", f"{n1}  ×  {n2}")
    _print_pair_times(args, tzl1, tzl2)

    _print_astronomy(pos1, n1)
    _print_astronomy(pos2, n2)

    # Cross-aspects and score
    core = ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Chiron","N.Node")
    cross_rows = []
    for p1, d1d in pos1.items():
        if p1 not in core:
            continue
        for p2, d2d in pos2.items():
            if p2 not in core:
                continue
            diff = angle_diff(d1d["longitude"], d2d["longitude"])
            for asp_name, (angle, orb_l, orb_o, glyph, quality) in ASPECTS.items():
                if asp_name in ("Quintile","Bi-Quintile","Septile","Semi-Sextile") \
                        or asp_name in OBSCURE_ASPECT_NAMES:
                    continue
                orb = orb_l if p1 in ("Sun","Moon") or p2 in ("Sun","Moon") else orb_o
                actual_orb = abs(diff - angle)
                if actual_orb <= orb:
                    applying = is_applying(d1d["longitude"], d1d["speed"],
                                           d2d["longitude"], d2d["speed"], angle)
                    cross_rows.append((actual_orb, p1, glyph, asp_name, p2, quality, applying))
    cross_rows.sort()

    total_score, cats = synergy_score(cross_rows)
    pct_harmony = cats["harmony"] / max(0.1, cats["harmony"] + cats["challenge"]) * 100

    section("SYNERGY SCORE")
    bar_len = 40
    h_bars = int(pct_harmony / 100 * bar_len)
    c_bars = bar_len - h_bars
    bar = "█" * h_bars + "░" * c_bars
    print(f"  │  Harmony:   {cats['harmony']:.1f}  ·  Challenge: {cats['challenge']:.1f}")
    print(f"  │  Net score: {total_score:+.1f}")
    print(f"  │  [{bar}] {pct_harmony:.0f}% harmony")
    if pct_harmony >= 70:
        verdict = "Highly harmonious — strong natural flow and ease"
    elif pct_harmony >= 55:
        verdict = "Mostly harmonious — supportive with productive friction"
    elif pct_harmony >= 40:
        verdict = "Mixed — significant growth potential, requires conscious effort"
    else:
        verdict = "Challenging — high activation energy, powerful transformation possible"
    print(f"  │  {verdict}")
    print()

    # Top aspects by significance
    section(f"KEY CROSS-ASPECTS  {n1} → {n2}")
    print(f"  │  {n1+' Planet':<14} {'Asp':<16} {n2+' Planet':<14} {'Orb':>6}  {'Quality':<12} App/Sep")
    print(f"  │  {'─'*14} {'─'*16} {'─'*14} {'─'*6}  {'─'*12} {'─'*6}")
    for actual_orb, p1, glyph, asp_name, p2, quality, applying in cross_rows[:30]:
        app = "Appl." if applying else "Sep."
        print(f"  │  {p1:<14} {glyph} {asp_name:<14} {p2:<14} {actual_orb:>5.2f}°  {quality:<12} {app}")
    print()

    # Composite chart
    section(f"COMPOSITE CHART (Midpoints)")
    print_planet_table(comp, title=f"COMPOSITE PLANETS — {n1} + {n2}")
    comp_aspects = calc_aspects(comp)
    print_aspects(comp_aspects, max_show=20)

    # Composite dignity highlights
    section("COMPOSITE DIGNITY HIGHLIGHTS")
    for name in ["Sun","Moon","Venus","Mars","Jupiter","Saturn"]:
        if name not in comp:
            continue
        cd = comp[name]
        score, labels = essential_dignity(name, cd["sign"], cd["degree"])
        if score != 0:
            print(f"  │  {name} in {cd['sign']}: {labels[0]}  (score {score:+d})")
    print()

    # Shared midpoints between charts (within 2°)
    section("CROSS-MIDPOINTS  (planet of A at midpoint of B pair, within 2°)")
    mps2 = calc_midpoints(pos2)
    hits = []
    for p1, d1d in pos1.items():
        if p1 not in core:
            continue
        for mp_lon, pa, pb, mp_sign, mp_deg, mp_min in mps2:
            orb = angle_diff(d1d["longitude"], mp_lon)
            if orb <= 2.0:
                hits.append((orb, p1, pa, pb, mp_sign, mp_deg, mp_min))
    hits.sort()
    if hits:
        print(f"  │  {n1+' Planet':<14} {'Midpoint of '+n2:<32} {'Position':<20} {'Orb':>5}")
        print(f"  │  {'─'*14} {'─'*32} {'─'*20} {'─'*5}")
        for orb, p1, pa, pb, mp_sign, mp_deg, mp_min in hits[:20]:
            mp_str = f"{mp_sign} {mp_deg}°{mp_min:02d}'"
            pair = f"{pa}/{pb}"
            print(f"  │  {p1:<14} {pair:<32} {mp_str:<20} {orb:>4.2f}°")
    else:
        print(f"  │  No cross-midpoint hits within 2°")
    print()


    return {"composite": comp, "aspects": comp_aspects}
def cmd_predict(args):
    """Event prediction: exact transit dates, stations, ingresses, eclipses."""
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time, args.city, args.nation,
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    start_str = getattr(args, "start", None)
    if start_str is None:
        start_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    start_date, end_date = date_window(start_str, getattr(args, "end", None))
    start_str, end_str = start_date.isoformat(), end_date.isoformat()
    _require_birth_time(time_known, "predict")
    sy, smo, sd = start_date.year, start_date.month, start_date.day
    ey, emo, ed = end_date.year, end_date.month, end_date.day
    start_jd = julian_day(sy, smo, sd, 0.0)
    end_jd   = julian_day(ey, emo, ed, 23.9)

    t_planets = (getattr(args, "transit_planets", None) or
                 "Jupiter,Saturn,Uranus,Neptune,Pluto,Chiron,N.Node,Mars,Sun,Venus,Mercury").split(",")
    n_planets = (getattr(args, "natal_planets",   None) or
                 "Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Chiron,N.Node,Asc,MC").split(",")

    jd_natal = julian_day(y, mo, d, utc_hour)
    natal_pos = calc_planet_positions(jd_natal)
    cusps, asc, mc = calc_houses(jd_natal, lat, lon)

    # Add Asc and MC to natal positions for aspect targets
    asc_sign, asidx, asc_deg, asc_min = deg_to_sign(asc)
    mc_sign,  msidx, mc_deg,  mc_min  = deg_to_sign(mc)
    natal_pos["Asc"] = {"longitude": asc, "sign": asc_sign, "sign_idx": asidx,
                        "degree": asc_deg, "minutes": asc_min,
                        "latitude": 0, "speed": 0, "retrograde": False}
    natal_pos["MC"]  = {"longitude": mc,  "sign": mc_sign,  "sign_idx": msidx,
                        "degree": mc_deg,  "minutes": mc_min,
                        "latitude": 0, "speed": 0, "retrograde": False}

    header("EVENT PREDICTION", f"Natal: {args.date}  ·  Window: {start_str} → {end_str}")

    _print_astronomy(natal_pos, "Natal")

    # Step size: fine for inner planets, coarse for outer
    step = 0.5 if "Sun" in t_planets or "Moon" in t_planets or "Mercury" in t_planets else 1.0

    # Exact transit-to-natal aspects
    section("EXACT TRANSIT-TO-NATAL ASPECTS")
    print("  Computing... (this may take a few seconds)", flush=True)
    events = find_exact_transit_dates(natal_pos, start_jd, end_jd, t_planets, n_planets, step=step)
    print(f"\r  Found {len(events)} exact aspects in window.                    ")
    if events:
        print(f"  │  {'Date':<12} {'Transit':<12} {'Asp':<14} {'Natal':<12} {'Quality'}")
        print(f"  │  {'─'*12} {'─'*12} {'─'*14} {'─'*12} {'─'*14}")
        for jd_e, t_p, asp, glyph, n_p, quality in events:
            dt_str = jd_to_dt(jd_e).split(" ")[0]
            print(f"  │  {dt_str:<12} {t_p:<12} {glyph} {asp:<12} {n_p:<12} {quality}")
    print()

    # Stations
    section("PLANETARY STATIONS (Retrograde / Direct)")
    stations = find_stations(start_jd, end_jd)
    if stations:
        print(f"  │  {'Date':<12} {'Planet':<12} {'Event':<26} {'Position'}")
        print(f"  │  {'─'*12} {'─'*12} {'─'*26} {'─'*20}")
        for jd_s, planet, kind, sign, deg, mins in stations:
            dt_str = jd_to_dt(jd_s).split(" ")[0]
            pos_str = f"{sign} {deg}°{mins:02d}'"
            print(f"  │  {dt_str:<12} {planet:<12} {kind:<26} {pos_str}")
    else:
        print(f"  │  No stations found in window")
    print()

    # Ingresses
    section("SIGN INGRESSES")
    ingresses = find_ingresses(start_jd, end_jd)
    if ingresses:
        print(f"  │  {'Date':<12} {'Planet':<12} {'From':<14} → {'Into':<14}")
        print(f"  │  {'─'*12} {'─'*12} {'─'*14}   {'─'*14}")
        for jd_i, planet, from_sign, into_sign in ingresses:
            dt_str = jd_to_dt(jd_i).split(" ")[0]
            print(f"  │  {dt_str:<12} {planet:<12} {from_sign:<14} → {into_sign}")
    else:
        print(f"  │  No ingresses found in window")
    print()

    # Eclipses
    section("ECLIPSES")
    eclipses = find_eclipses(start_jd, end_jd)
    if eclipses:
        print(f"  │  {'Date':<12} {'Type':<32} {'Position'}")
        print(f"  │  {'─'*12} {'─'*32} {'─'*20}")
        for jd_ec, etype, sign, deg, mins in eclipses:
            dt_str = jd_to_dt(jd_ec).split(" ")[0]
            pos_str = f"{sign} {deg}°{mins:02d}'"
            print(f"  │  {dt_str:<12} {etype:<32} {pos_str}")
    else:
        print(f"  │  No eclipses found in window (or swe eclipse functions unavailable)")
    print()


    return {"events": events}
def cmd_geoastrology(args):
    """Astrocartography: MC, IC, ASC, DSC lines for a natal chart."""
    query = coordinate_pair(getattr(args, "query_lat", None), getattr(args, "query_lon", None),
                            ("--query-lat", "--query-lon"))
    defaults = load_rules("profiles.json")["legacy_defaults"]
    y, mo, d, utc_hour, lat, lon, tz_name, tz_label, time_known, _ = resolve_birth(
        args.date, args.time,
        getattr(args, "city", None) or defaults["city"],
        getattr(args, "nation", None) or defaults["nation"],
        getattr(args, "lat", None), getattr(args, "lon", None),
        getattr(args, "timezone", None)
    )
    _require_birth_time(time_known, "geoastrology")
    jd = julian_day(y, mo, d, utc_hour)
    positions = calc_planet_positions(jd)
    name = args.name or "Seeker"

    lines = calc_astrocartography(jd, positions)
    header("GEOASTROLOGY — ASTROCARTOGRAPHY", f"{name}  ·  {args.date}  ·  {tz_label}")

    _print_astronomy(positions)

    # MC / IC lines table
    section("MC AND IC LINES  (planet on upper/lower meridian)")
    print(f"  │  {'Planet':<12} {'RA':>7}  {'Dec':>7}  {'MC Lon':>8}  MC Region")
    print(f"  │  {'':24}{'IC Lon':>8}  IC Region")
    print(f"  │  {'─'*12} {'─'*7}  {'─'*7}  {'─'*8}  {'─'*30}")
    for planet in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn",
                   "Uranus","Neptune","Pluto","Chiron","N.Node"]:
        if planet not in lines:
            continue
        L = lines[planet]
        mc = L["MC_lon"]
        ic = L["IC_lon"]
        ra = L["ra"]
        dec = L["dec"]
        mc_dir = "E" if mc >= 0 else "W"
        ic_dir = "E" if ic >= 0 else "W"
        mc_region = geo_region(mc)
        ic_region = geo_region(ic)
        sym = PLANET_SYMBOL.get(planet, "?")
        print(f"  │  {sym} {planet:<10} {ra:>7.2f}°  {dec:>+7.2f}°  MC {abs(mc):>5.1f}°{mc_dir:<2}  {mc_region}")
        print(f"  │  {'':12}                        IC {abs(ic):>5.1f}°{ic_dir:<2}  {ic_region}")
    print()

    # ASC line table — show latitudes where ASC line passes through notable longitudes
    section("ASC LINES  (planet on eastern horizon — power locations)")
    print(f"  ASC line crossings by latitude (planet rises at these Earth longitudes):")
    print()
    for planet in ["Sun","Moon","Venus","Jupiter","Saturn","Mars","Mercury"]:
        if planet not in lines:
            continue
        L = lines[planet]
        sym = PLANET_SYMBOL.get(planet, "?")
        print(f"  │  {sym} {planet} ASC line:")
        print(f"  │    {'Lat':>5}  {'Lon':>8}  Region")
        print(f"  │    {'─'*5}  {'─'*8}  {'─'*34}")
        for lat_deg, geo_lon in L["ASC_lons"]:
            dir_c = "N" if lat_deg >= 0 else "S"
            dir_l = "E" if geo_lon >= 0 else "W"
            region = geo_region(geo_lon)
            print(f"  │    {abs(lat_deg):>4}°{dir_c}  {abs(geo_lon):>6.1f}°{dir_l}  {region}")
        print()

    # DSC line summary (briefer)
    section("DSC LINES  (planet on western horizon — relationship/other locations)")
    print(f"  │  {'Planet':<12} {'Lat 0°':<16} {'Lat 40°N':<16} {'Lat 40°S':<16}")
    print(f"  │  {'─'*12} {'─'*16} {'─'*16} {'─'*16}")
    for planet in ["Sun","Moon","Venus","Mars","Jupiter","Saturn"]:
        if planet not in lines:
            continue
        L = lines[planet]
        lons_by_lat = {lat: lon for lat, lon in L["DSC_lons"]}
        l0  = f"{abs(lons_by_lat.get(0,  999)):>5.1f}°{'E' if lons_by_lat.get(0,0)  >= 0 else 'W'}" if 0   in lons_by_lat else "n/a"
        l40n= f"{abs(lons_by_lat.get(40, 999)):>5.1f}°{'E' if lons_by_lat.get(40,0) >= 0 else 'W'}" if 40  in lons_by_lat else "n/a"
        l40s= f"{abs(lons_by_lat.get(-40,999)):>5.1f}°{'E' if lons_by_lat.get(-40,0)>= 0 else 'W'}" if -40 in lons_by_lat else "n/a"
        sym = PLANET_SYMBOL.get(planet, "?")
        print(f"  │  {sym} {planet:<10} {l0:<16} {l40n:<16} {l40s:<16}")
    print()

    # Power spot finder: where is a user-specified location relative to chart lines?
    if query is not None:
        qlat, qlon = query
        section(f"POWER SPOT ANALYSIS  ({qlat:.2f}°N, {qlon:.2f}°E)")
        print(f"  Nearest astrocartography lines to this location:")
        print()
        hits = []
        for planet, L in lines.items():
            if planet in ("S.Node","Ceres","Pallas","Juno","Vesta"):
                continue
            # MC line distance
            mc_dist = abs(angle_diff(qlon, L["MC_lon"]))
            if mc_dist <= 15:
                hits.append((mc_dist, planet, "MC line", L["MC_lon"]))
            ic_dist = abs(angle_diff(qlon, L["IC_lon"]))
            if ic_dist <= 15:
                hits.append((ic_dist, planet, "IC line", L["IC_lon"]))
            # ASC/DSC: find closest latitude
            for lat_a, lon_a in L["ASC_lons"]:
                combo_dist = math.sqrt((lat_a - qlat)**2 + angle_diff(lon_a, qlon)**2)
                if combo_dist <= 10:
                    hits.append((combo_dist, planet, "ASC line", lon_a))
                    break
            for lat_d, lon_d in L["DSC_lons"]:
                combo_dist = math.sqrt((lat_d - qlat)**2 + angle_diff(lon_d, qlon)**2)
                if combo_dist <= 10:
                    hits.append((combo_dist, planet, "DSC line", lon_d))
                    break
        hits.sort()
        if hits:
            for dist, planet, line_type, line_lon in hits[:10]:
                kw = PLANET_KEYWORDS.get(planet, "").split("·")[0].strip()
                norse = NORSE_CORRESPONDENCES.get(planet, "").split("—")[0].strip()
                print(f"  │  {PLANET_SYMBOL.get(planet,'?')} {planet} {line_type}  (dist {dist:.1f}°)")
                print(f"  │    Energy: {kw}")
                print(f"  │    Norse:  {norse}")
                print()
        else:
            print(f"  │  No major lines within 15° of this location")
        print()


    return {"lines": lines}
# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        prog="astrology_engine",
        description="Advanced Astrology Engine — Volmarr's Longhall / Hermes Divination Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd")

    def add_geo(parser: argparse.ArgumentParser, city_default: str | None = None,
                nation_default: str | None = None) -> None:
        """Add legacy location and explicit IANA timezone controls."""
        defaults = load_rules("profiles.json")["legacy_defaults"]
        parser.add_argument("--city", default=city_default or defaults["city"],
                            help=f"Birth city (legacy default: {defaults['city']})")
        parser.add_argument("--nation", default=nation_default or defaults["nation"])
        parser.add_argument("--lat", default=None, help="Override latitude (decimal)")
        parser.add_argument("--lon", default=None, help="Override longitude (decimal)")
        parser.add_argument("--timezone", default=None,
                            help="Explicit IANA zone, bypassing optional discovery; UTC for known UTC input")

    def add_houses(parser: argparse.ArgumentParser) -> None:
        """Add the --houses flag: placidus (default), whole-sign, equal, koch, regiomontanus."""
        from astroengine.houses import SYSTEMS
        parser.add_argument("--houses", default="placidus", choices=SYSTEMS,
                            help="House system (default: placidus)")

    def add_pair_geo(parser: argparse.ArgumentParser) -> None:
        for index in (1, 2):
            parser.add_argument(f"--city{index}", default=None, help=f"Person {index} birth city")
            parser.add_argument(f"--nation{index}", default=None)
            parser.add_argument(f"--lat{index}", default=None)
            parser.add_argument(f"--lon{index}", default=None)
            parser.add_argument(f"--timezone{index}", default=None, help=f"Person {index} explicit IANA zone")

    # natal
    natal = sub.add_parser("natal", help="Full natal chart")
    natal.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    natal.add_argument("--time", default=None,  help="HH:MM (24h)")
    natal.add_argument("--name", default=None)
    add_geo(natal)
    add_houses(natal)
    add_chart_lib(natal)

    # transit  (gap 2: --transit-date / --transit-time)
    transit = sub.add_parser("transit", help="Transits to natal (default: now; use --transit-date to forecast)")
    transit.add_argument("--date",         required=False, help="Natal birth date YYYY-MM-DD (or --load NAME)")
    transit.add_argument("--time",         default=None,  help="Natal birth time HH:MM")
    transit.add_argument("--transit-date", default=None,  dest="transit_date",
                         help="Sky date to compare (default: now) YYYY-MM-DD")
    transit.add_argument("--transit-time", default=None,  dest="transit_time",
                         help="Sky time HH:MM (default: noon if transit-date given)")
    add_geo(transit)
    add_houses(transit)
    add_chart_lib(transit)

    # synastry  (gap 6: --city1/2 --nation1/2 --lat1/2 --lon1/2)
    syn = sub.add_parser("synastry", help="Two-chart synastry with optional house overlays")
    syn.add_argument("--date1",    required=False, help="Person 1 date (or --load1 NAME)")
    syn.add_argument("--date2",    required=False, help="Person 2 date (or --load2 NAME)")
    syn.add_argument("--time1",    default=None)
    syn.add_argument("--time2",    default=None)
    syn.add_argument("--name1",    default="Person A")
    syn.add_argument("--name2",    default="Person B")
    add_pair_geo(syn)
    add_houses(syn)
    add_chart_lib(syn, two_person=True)

    # solar return
    sr = sub.add_parser("solar-return", help="Solar return chart")
    sr.add_argument("--date",  required=False, help="YYYY-MM-DD (or --load NAME)")
    sr.add_argument("--time",  default=None)
    sr.add_argument("--year",  default=None)
    add_geo(sr)
    add_houses(sr)
    add_chart_lib(sr)

    # progressions
    prog = sub.add_parser("progressions", help="Secondary progressions")
    prog.add_argument("--date",      required=False, help="YYYY-MM-DD (or --load NAME)")
    prog.add_argument("--time",      default=None)
    prog.add_argument("--prog-date", default=None, dest="prog_date", help="Target date YYYY-MM-DD")
    add_geo(prog)
    add_chart_lib(prog)

    # lunar
    lunar_p = sub.add_parser("lunar", help="Lunar intelligence — phase, VOC, next lunations")
    add_chart_lib(lunar_p, with_load=False)

    # planet-hours
    ph = sub.add_parser("planet-hours", help="Planetary hours for a date and location")
    ph.add_argument("--date", default=None, help="YYYY-MM-DD (default today)")
    ph.add_argument("--lat",  default=None, help="Latitude decimal")
    ph.add_argument("--lon",  default=None, help="Longitude decimal")
    ph.add_argument("--city",   default=None)
    ph.add_argument("--nation", default=None)
    add_chart_lib(ph)

    # lots
    lots_p = sub.add_parser("lots", help="Arabic Lots / Hermetic Parts")
    lots_p.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    lots_p.add_argument("--time", default=None)
    add_geo(lots_p)
    add_chart_lib(lots_p)

    # hellenistic
    hell = sub.add_parser("hellenistic", help="Hellenistic analysis — sect, bonification, joys")
    hell.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    hell.add_argument("--time", default=None)
    add_geo(hell)
    add_chart_lib(hell)

    # dignity  (gap 1: new standalone command)
    dig = sub.add_parser("dignity", help="Essential dignities table with scoring and mutual receptions")
    dig.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    dig.add_argument("--time", default=None)
    add_geo(dig)
    add_chart_lib(dig)

    # antiscia  (gap 1: new standalone command)
    ant = sub.add_parser("antiscia", help="Antiscia and contra-antiscia with connection detection")
    ant.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    ant.add_argument("--time", default=None)
    add_chart_lib(ant)

    # composite
    comp_p = sub.add_parser("composite", help="Composite chart (midpoints) + optional Davison chart")
    comp_p.add_argument("--date1",   required=False, help="Person 1 date (or --load1 NAME)")
    comp_p.add_argument("--date2",   required=False, help="Person 2 date (or --load2 NAME)")
    comp_p.add_argument("--time1",   default=None)
    comp_p.add_argument("--time2",   default=None)
    comp_p.add_argument("--name1",   default="Person A")
    comp_p.add_argument("--name2",   default="Person B")
    add_pair_geo(comp_p)
    add_houses(comp_p)
    add_chart_lib(comp_p, two_person=True)

    # synergy
    syne = sub.add_parser("synergy", help="Full relationship analysis: aspects + composite + score + midpoints")
    syne.add_argument("--date1",   required=False, help="Person 1 date (or --load1 NAME)")
    syne.add_argument("--date2",   required=False, help="Person 2 date (or --load2 NAME)")
    syne.add_argument("--time1",   default=None)
    syne.add_argument("--time2",   default=None)
    syne.add_argument("--name1",   default="Person A")
    syne.add_argument("--name2",   default="Person B")
    add_pair_geo(syne)
    add_chart_lib(syne, two_person=True)

    # predict
    pred = sub.add_parser("predict",
        help="Exact transit dates, stations, ingresses, eclipses within a window")
    pred.add_argument("--date",   required=False, help="Natal birth date YYYY-MM-DD (or --load NAME)")
    pred.add_argument("--time",   default=None)
    pred.add_argument("--start",  default=None,  help="Window start YYYY-MM-DD (default: today)")
    pred.add_argument("--end",    default=None,  help="Window end   YYYY-MM-DD (default: 1 year)")
    pred.add_argument("--transit-planets", default=None, dest="transit_planets",
                      help="Comma-separated transit planets (default: all)")
    pred.add_argument("--natal-planets",   default=None, dest="natal_planets",
                      help="Comma-separated natal points (default: all)")
    add_geo(pred)
    add_chart_lib(pred)

    # geoastrology
    geo_p = sub.add_parser("geoastrology",
        help="Astrocartography MC/IC/ASC/DSC lines; add --query-lat/--query-lon for power-spot analysis")
    geo_p.add_argument("--date",       required=False, help="YYYY-MM-DD (or --load NAME)")
    geo_p.add_argument("--time",       default=None)
    geo_p.add_argument("--name",       default=None)
    add_geo(geo_p)
    add_chart_lib(geo_p)
    geo_p.add_argument("--query-lat",  default=None, dest="query_lat",
                       help="Latitude to analyse proximity of lines")
    geo_p.add_argument("--query-lon",  default=None, dest="query_lon",
                       help="Longitude to analyse proximity of lines")

    # aspect-grid
    ag = sub.add_parser("aspect-grid", help="Full aspect matrix")
    ag.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    ag.add_argument("--time", default=None)
    ag.add_argument("--aspects", default="all",
                    choices=("all", "major", "minor", "obscure"),
                    help="Aspect family filter (default: all)")
    add_chart_lib(ag)

    # runic — the runic star-program (Pennick 2023)
    runic = sub.add_parser("runic", help="Runic astrology layers and readings (Pennick 2023)")
    runic.add_argument("--datetime", required=True, help="ISO datetime, e.g. 2026-05-16T16:45")
    runic.add_argument("--lon", type=float, required=True, help="Longitude in degrees east")
    runic.add_argument("--timezone", required=True, help="IANA timezone, e.g. UTC")
    runic.add_argument("--age", type=float, default=None, help="Age in years (enables --life-period)")
    runic.add_argument("--moon-lon", type=float, default=None, dest="moon_lon",
                       help="Moon's sidereal longitude in degrees (enables --mansion)")
    runic.add_argument("--half-month", action="store_true", dest="half_month")
    runic.add_argument("--hour", action="store_true")
    runic.add_argument("--tide", action="store_true")
    runic.add_argument("--station", action="store_true")
    runic.add_argument("--weekday", action="store_true")
    runic.add_argument("--mansion", action="store_true")
    runic.add_argument("--life-period", action="store_true", dest="life_period")
    runic.add_argument("--name", action="store_true")
    runic.add_argument("--reading", action="store_true",
                       help="Include the Ch. 8 interpretive statements")
    runic.add_argument("--full", action="store_true", help="All layers (default when no layer flag is given)")
    runic.add_argument("--json", action="store_true", help="JSON output instead of text")
    add_chart_lib(runic, with_load=False)

    trt = sub.add_parser("tarot", help="Tarot reading with classic spreads")
    trt.add_argument("--spread", default="three",
                     help="Spread name (see --list-spreads)")
    trt.add_argument("--list-spreads", action="store_true", dest="list_spreads")
    trt.add_argument("--seed", type=int, default=None)
    trt.add_argument("--no-reversals", action="store_true", dest="no_reversals")
    trt.add_argument("--question", default=None)
    trt.add_argument("--json", action="store_true")
    add_chart_lib(trt, with_load=False)

    rdg = sub.add_parser("reading", help="Interpretive astrology reading (general/love/career)")
    rdg.add_argument("--kind", default="general", choices=("general", "love", "career"))
    rdg.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    rdg.add_argument("--time", default=None, help="HH:MM (24h)")
    rdg.add_argument("--json", action="store_true")
    add_geo(rdg)
    add_houses(rdg)
    add_chart_lib(rdg)

    num = sub.add_parser("numerology", help="Pythagorean numerology reading")
    num.add_argument("--date", required=True, help="Birth date YYYY-MM-DD")
    num.add_argument("--name", required=True, help="Full birth name")
    num.add_argument("--year", type=int, default=None, help="Year for the Personal Year number")
    num.add_argument("--json", action="store_true")
    add_chart_lib(num, with_load=False)

    stc = sub.add_parser("stars", help="Fixed stars: the bright ones and their contacts to the chart")
    stc.add_argument("--date", required=False, help="Birth date YYYY-MM-DD (or --load NAME)")
    stc.add_argument("--time", default=None, help="HH:MM (24h)")
    stc.add_argument("--orb", type=float, default=1.0)
    stc.add_argument("--list", action="store_true", help="List the star catalog")
    stc.add_argument("--json", action="store_true")
    add_geo(stc)
    add_chart_lib(stc)

    elc = sub.add_parser("elect", help="Electional astrology: find the most fortunate windows")
    elc.add_argument("--from-date", default=None, dest="from_date", help="Search start YYYY-MM-DD (default: today)")
    elc.add_argument("--to-date", default=None, dest="to_date", help="Search end YYYY-MM-DD (default: +7 days)")
    elc.add_argument("--lat", type=float, default=None)
    elc.add_argument("--lon", type=float, default=None)
    elc.add_argument("--timezone", default=None)
    elc.add_argument("--step-hours", type=float, default=6.0)
    elc.add_argument("--top", type=int, default=10)
    elc.add_argument("--json", action="store_true")
    add_chart_lib(elc)

    wtc = sub.add_parser("watch", help="Watch for coming outer-planet transits to natal points")
    wtc.add_argument("--date", required=False, help="Birth date YYYY-MM-DD (or --load NAME)")
    wtc.add_argument("--time", default=None, help="HH:MM (24h)")
    wtc.add_argument("--from-date", default=None, dest="from_date", help="Window start YYYY-MM-DD (default: today)")
    wtc.add_argument("--to-date", default=None, dest="to_date", help="Window end YYYY-MM-DD (default: +1 year)")
    wtc.add_argument("--orb", type=float, default=1.0)
    wtc.add_argument("--json", action="store_true")
    add_geo(wtc)
    add_chart_lib(wtc)

    prf = sub.add_parser("profection", help="Annual profections: the Hellenistic time-lord wheel")
    prf.add_argument("--date", required=False, help="Birth date YYYY-MM-DD (or --load NAME)")
    prf.add_argument("--time", default=None, help="HH:MM (24h)")
    prf.add_argument("--target-date", default=None, help="Target date YYYY-MM-DD (default: today)")
    prf.add_argument("--json", action="store_true")
    add_geo(prf)
    add_houses(prf)
    add_chart_lib(prf)

    sar = sub.add_parser("solar-arc", help="Solar arc directions to a target date")
    sar.add_argument("--date", required=False, help="Birth date YYYY-MM-DD (or --load NAME)")
    sar.add_argument("--time", default=None, help="HH:MM (24h)")
    sar.add_argument("--target-date", default=None, help="Target date YYYY-MM-DD (default: today)")
    sar.add_argument("--orb", type=float, default=1.0)
    sar.add_argument("--json", action="store_true")
    add_geo(sar)
    add_houses(sar)
    add_chart_lib(sar)

    whl = sub.add_parser("wheel", help="Render a natal chart wheel as SVG")
    whl.add_argument("--date", required=False, help="YYYY-MM-DD (or --load NAME)")
    whl.add_argument("--time", default=None, help="HH:MM (24h)")
    whl.add_argument("-o", "--output", default="wheel.svg")
    add_geo(whl)
    add_houses(whl)
    add_chart_lib(whl)

    rnc = sub.add_parser("runecast", help="Rune casting: Elder Futhark readings in many layouts")
    rnc.add_argument("--layout", default="norns", help="Layout name (see --list-layouts)")
    rnc.add_argument("--list-layouts", action="store_true", dest="list_layouts")
    rnc.add_argument("--seed", type=int, default=None)
    rnc.add_argument("--no-merkstave", action="store_true", dest="no_merkstave")
    rnc.add_argument("--blank", action="store_true",
                     help="Include the modern blank rune")
    rnc.add_argument("--question", default=None)
    rnc.add_argument("--json", action="store_true")
    add_chart_lib(rnc, with_load=False)

    ich = sub.add_parser("iching", help="I-Ching oracle: cast a hexagram")
    ich.add_argument("--question", default=None)
    ich.add_argument("--method", default="coins", choices=("coins", "yarrow"))
    ich.add_argument("--seed", type=int, default=None)
    ich.add_argument("--json", action="store_true")
    add_chart_lib(ich, with_load=False)

    mgmt = sub.add_parser("charts", help="List saved charts in the chart library")
    mgmt.add_argument("--chart-dir", default=None, dest="chart_dir")
    mgmt.set_defaults(_mgmt="charts")

    show = sub.add_parser("chart-show", help="Show a saved chart")
    show.add_argument("name", help="Chart name")
    show.add_argument("--chart-dir", default=None, dest="chart_dir")
    show.set_defaults(_mgmt="chart-show")

    dele = sub.add_parser("chart-delete", help="Delete a saved chart")
    dele.add_argument("name", help="Chart name")
    dele.add_argument("--chart-dir", default=None, dest="chart_dir")
    dele.set_defaults(_mgmt="chart-delete")

    from astroengine.cli import register_commands, run_command
    register_commands(sub)
    args = p.parse_args()
    if hasattr(args, "modern_handler"):
        raise SystemExit(run_command(args))
    dispatch = {
        "natal":        cmd_natal,
        "transit":      cmd_transit,
        "synastry":     cmd_synastry,
        "solar-return": cmd_solar_return,
        "progressions": cmd_progressions,
        "lunar":        cmd_lunar,
        "planet-hours": cmd_planet_hours,
        "lots":         cmd_lots,
        "hellenistic":  cmd_hellenistic,
        "dignity":      cmd_dignity,
        "antiscia":     cmd_antiscia,
        "composite":    cmd_composite,
        "synergy":      cmd_synergy,
        "predict":      cmd_predict,
        "geoastrology": cmd_geoastrology,
        "aspect-grid":  cmd_aspect_grid,
        "runic":        cmd_runic,
        "charts":       cmd_charts,
        "chart-show":   cmd_chart_show,
        "chart-delete": cmd_chart_delete,
        "tarot":        cmd_tarot,
        "reading":      cmd_reading,
        "numerology":   cmd_numerology,
        "iching":       cmd_iching,
        "runecast":     cmd_runecast,
        "wheel":        cmd_wheel,
        "solar-arc":    cmd_solar_arc,
        "profection":   cmd_profection,
        "watch":        cmd_watch,
        "elect":        cmd_elect,
        "stars":        cmd_stars,
    }
    _TWO_PERSON = {"synastry", "composite", "synergy"}
    _DATE_FIELDS = {
        "natal": ("date",), "transit": ("date",),
        "synastry": ("date1", "date2"), "solar-return": ("date",),
        "progressions": ("date",), "lots": ("date",),
        "hellenistic": ("date",), "dignity": ("date",),
        "antiscia": ("date",), "composite": ("date1", "date2"),
        "synergy": ("date1", "date2"), "predict": ("date",),
        "geoastrology": ("date",), "aspect-grid": ("date",),
    }
    fn = dispatch.get(args.cmd)
    if fn:
        try:
            if args.cmd in _TWO_PERSON:
                apply_chart_load(args, "1")
                apply_chart_load(args, "2")
            elif hasattr(args, "load"):
                apply_chart_load(args)
            for _field in _DATE_FIELDS.get(args.cmd, ()):
                require_date(args, _field)
            result = fn(args)
            if result is not None:
                maybe_save_chart(args, args.cmd, result)
        except CalculationError as exc:
            print(f"Calculation error: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
    else:
        p.print_help()


if __name__ == "__main__":
    main()
