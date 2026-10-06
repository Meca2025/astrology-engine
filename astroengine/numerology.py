"""Pythagorean numerology: life path, destiny, soul urge, and cycles."""

import json as _json
import re as _re
import unicodedata as _unicodedata
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

from .models import CalculationError

_VALUES = {}
for _i, _ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    _VALUES[_ch] = (_i % 9) + 1  # A=1..I=9, J=1..R=9, S=1..Z=9

_VOWELS = set("AEIOU")
_MASTERS = (11, 22, 33)


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "numerology.json").read_text(encoding="utf-8"))


def _strip_accents(text: str) -> str:
    # transliterate runic-ish letters before stripping
    text = (text.replace("ð", "d").replace("Ð", "D")
                .replace("þ", "th").replace("Þ", "TH")
                .replace("æ", "ae").replace("Æ", "AE")
                .replace("ø", "o").replace("Ø", "O")
                .replace("å", "a").replace("Å", "A"))
    return "".join(c for c in _unicodedata.normalize("NFKD", text)
                   if not _unicodedata.combining(c))


def _clean_name(name: str) -> str:
    cleaned = _re.sub(r"[^A-Za-z]", "", _strip_accents(name or "").upper())
    if not cleaned:
        raise CalculationError("a name with letters is required")
    return cleaned


def reduce_number(total: int, keep_masters: bool = True):
    """Reduce to a single digit, holding 11/22/33 when keep_masters."""
    n = int(total)
    while n > 9 and not (keep_masters and n in _MASTERS):
        n = sum(int(d) for d in str(n))
    return n


def _check_date(iso_date: str):
    import datetime as _dt
    try:
        return _dt.date.fromisoformat(iso_date)
    except ValueError:
        raise CalculationError(
            f"invalid date '{iso_date}': use YYYY-MM-DD")


def life_path(iso_date: str) -> dict:
    """Life Path number from the birth date (masters held)."""
    d = _check_date(iso_date)
    total = sum(int(c) for c in f"{d.year:04d}{d.month:02d}{d.day:02d}")
    number = reduce_number(total)
    return _number_result("Life Path", number, total)


def destiny(full_name: str) -> dict:
    """Destiny/Expression number from all letters of the name."""
    cleaned = _clean_name(full_name)
    total = sum(_VALUES[c] for c in cleaned)
    return _number_result("Destiny", reduce_number(total), total)


def _vowel_pool(cleaned: str) -> list[str]:
    """Vowels; Y counts as a vowel only when no A/E/I/O/U is present."""
    if any(c in _VOWELS for c in cleaned):
        return [c for c in cleaned if c in _VOWELS]
    return [c for c in cleaned if c == "Y"]


def soul_urge(full_name: str) -> dict:
    """Soul Urge from the vowels (Y counts when no other vowel present)."""
    cleaned = _clean_name(full_name)
    pool = _vowel_pool(cleaned)
    if not pool:
        raise CalculationError("no vowels found for the Soul Urge")
    total = sum(_VALUES[c] for c in pool)
    return _number_result("Soul Urge", reduce_number(total), total)


def personality(full_name: str) -> dict:
    """Personality number from the consonants."""
    cleaned = _clean_name(full_name)
    vowels = set(_vowel_pool(cleaned))
    consonants = [c for c in cleaned if c not in vowels]
    if not consonants:
        raise CalculationError("no consonants found for the Personality")
    total = sum(_VALUES[c] for c in consonants)
    return _number_result("Personality", reduce_number(total), total)


def birthday(iso_date: str) -> dict:
    """Birthday number from the day of birth (masters held)."""
    d = _check_date(iso_date)
    return _number_result("Birthday", reduce_number(d.day), d.day)


def personal_year(iso_date: str, for_year: int | None = None) -> dict:
    """Personal Year number for the given calendar year."""
    d = _check_date(iso_date)
    import datetime as _dt
    year = int(for_year) if for_year is not None else _dt.date.today().year
    total = (sum(int(c) for c in str(d.month)) +
             sum(int(c) for c in str(d.day)) +
             sum(int(c) for c in str(year)))
    number = reduce_number(total)
    out = _number_result("Personal Year", number, total)
    out["year"] = year
    return out


def _number_result(kind: str, number: int, total: int) -> dict:
    entry = _corpus()["numbers"].get(str(number), {})
    return {
        "kind": kind,
        "number": number,
        "digit_sum": total,
        "master_number": number in _MASTERS,
        "title": entry.get("title", ""),
        "keywords": entry.get("keywords", []),
        "meaning": entry.get("meaning", ""),
        "source": "Pythagorean numerology",
        "historical_claim": "modern synthesis",
    }


def full_reading(iso_date: str, full_name: str,
                 for_year: int | None = None) -> dict:
    """All core numbers in one reading."""
    return {
        "date": iso_date,
        "name": full_name,
        "life_path": life_path(iso_date),
        "destiny": destiny(full_name),
        "soul_urge": soul_urge(full_name),
        "personality": personality(full_name),
        "birthday": birthday(iso_date),
        "personal_year": personal_year(iso_date, for_year),
        "kind": "interpretive",
        "source": "Pythagorean numerology",
        "historical_claim": "modern synthesis",
    }


__all__ = ["reduce_number", "life_path", "destiny", "soul_urge",
           "personality", "birthday", "personal_year", "full_reading"]
