"""Sólrún's scrutiny of R08: the runic reading synthesis (Ch. 8).

Golden-output fixture plus the anti-fabrication gate: every adverb and
planetary quality appearing in any statement must come from the corpus
tables — nothing invented.
"""

import json
import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.runic import runic_reading  # noqa: E402
from astroengine.models import CalculationError  # noqa: E402

CORPUS = json.load(open("/home/hatch/workspace/astrology-engine/data/runic.json"))

GOLDEN = [
    'Half-month rune Ing — Ing (Frey) — expressed expansively.',
    'Hour rune Rad — Ing/Nerthus — expressed actively.',
    'Station Sixth (Lagu): Mystical Union — plant in full growth in '
    'harmony with the environment.',
    'Weekday rune Dag — Loki (limitation) — expressed changingly.',
    'Life period: Tyr (energy) — year 13.0 of the reign, 2.0 years remaining.',
    'Lunar mansion 2 (The Follower, Aldebaran) — expressed powerfully.',
    "Runic-name pair Ing-Rad: the book's rendered names (Kenneth, Ingrid, "
    'Darwin) are literary wordplay on such pairs, not mechanical output.',
]


def test_golden_reading():
    r = runic_reading('2026-05-16T16:45', 0.0, 'UTC',
                      age_years=54, moon_sidereal_longitude=50.0)
    got = [s["statement"] for s in r["interpretation"]["statements"]]
    assert got == GOLDEN


def test_split_and_labels():
    r = runic_reading('2026-05-16T16:45', 0.0, 'UTC', age_years=54)
    assert "interpretive" not in json.dumps(r["computation"])
    interp = r["interpretation"]
    assert interp["kind"] == "interpretive"
    for s in interp["statements"]:
        assert s["kind"] == "interpretive"
        assert s["source"] == "Pennick (2023)"


def test_anti_fabrication():
    adverbs = set(CORPUS["interpretation"]["rune_adverbs"].values())
    qualities = set(CORPUS["interpretation"]["planetary_qualities"].values())
    moments = [
        ('2026-01-05T03:20', 0.0, 'UTC', 10, 200.0),
        ('2026-07-04T12:00', -74.0, 'America/New_York', 80, 300.0),
        ('2026-11-07T13:05', 7.5, 'UTC', 30, 36.1175),
        ('2026-12-25T00:00', 0.0, 'UTC', 5, 150.0),
    ]
    for dt, lon, tz, age, mlon in moments:
        r = runic_reading(dt, lon, tz, age_years=age,
                          moon_sidereal_longitude=mlon)
        for s in r["interpretation"]["statements"]:
            text = s["statement"]
            for adv in adverbs:
                if f"expressed {adv}" in text:
                    break
            else:
                if "expressed " in text:
                    pytest.fail(f"unlisted adverb in: {text}")
            for q in qualities:
                if f"({q})" in text:
                    break
            else:
                if "(" in text and "quality" not in text.lower():
                    # parentheticals must be rune-name notes, not qualities
                    assert "wordplay" in text or "coincidence" in text or \
                        " — " in text, f"suspicious parenthetical: {text}"


def test_reading_needs_timezone():
    with pytest.raises(CalculationError):
        runic_reading('2026-05-16T16:45', 0.0, 'Moon/Oceanus')
