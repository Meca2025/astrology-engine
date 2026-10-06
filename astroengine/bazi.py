"""Four Pillars / BaZi: year, month, day, hour pillars.

Year pillar turns at Lichun (not Lunar New Year); month branches
follow the twelve jie (solar terms) via Swiss Ephemeris Sun
longitude; month stems by the Five Tigers rule; day ganzhi from the
Julian Day Number (offsets derived from the verified anchor
1939-01-17 = Jia-Yin, cross-checked on three published charts);
hour stems by the Five Rats rule.

Conventions (disclosed): the calendar day changes at local
midnight; the hour branch uses the given local clock time as-is
(no true-solar-time correction); the traditional early/late Zi
refinement is not applied.
"""

import datetime as _datetime
import json as _json
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path
from zoneinfo import ZoneInfo

import swisseph as _swe

from .models import CalculationError

# The twelve jie (solar-term month openers): Sun longitude -> branch.
# Lichun 315° opens Yin month, Jingzhe 345° Mao, ... Xiaohan 285° Chou.
JIE = [
    (315.0, "Yin"), (345.0, "Mao"), (15.0, "Chen"), (45.0, "Si"),
    (75.0, "Wu"), (105.0, "Wei"), (135.0, "Shen"), (165.0, "You"),
    (195.0, "Xu"), (225.0, "Hai"), (255.0, "Zi"), (285.0, "Chou"),
]
JIE_NAMES = ["Lichun", "Jingzhe", "Qingming", "Lixia", "Mangzhong",
             "Xiazhi", "Liqiu", "Bailu", "Hanlu", "Lidong", "Daxue",
             "Xiaohan"]

# Five Tigers: year stem -> stem of the Yin (first) month.
FIVE_TIGERS = {"Jia": "Bing", "Yi": "Wu", "Bing": "Geng", "Ding": "Ren",
               "Wu": "Jia", "Ji": "Bing", "Geng": "Wu", "Xin": "Geng",
               "Ren": "Ren", "Gui": "Jia"}
# Five Rats: day stem -> stem of the Zi (first) hour.
FIVE_RATS = {"Jia": "Jia", "Yi": "Bing", "Bing": "Wu", "Ding": "Geng",
             "Wu": "Ren", "Ji": "Jia", "Geng": "Bing", "Xin": "Wu",
             "Ren": "Geng", "Gui": "Ren"}

_BRANCH_ORDER = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei",
                 "Shen", "You", "Xu", "Hai"]


@_lru_cache(maxsize=1)
def _corpus() -> dict:
    return _json.loads((_Path(__file__).parent.parent / "data" /
                        "chinese_zodiac.json").read_text(encoding="utf-8"))


def _stems() -> list[dict]:
    return _corpus()["stems"]


def _branches() -> list[dict]:
    return _corpus()["branches"]


def _stem_idx(name: str) -> int:
    return next(i for i, s in enumerate(_stems()) if s["name"] == name)


def _branch_idx(name: str) -> int:
    return next(i for i, b in enumerate(_branches()) if b["name"] == name)


def ganzhi_index(stem: str, branch: str) -> int:
    """Position in the 60-cycle for a stem+branch pair."""
    si, bi = _stem_idx(stem), _branch_idx(branch)
    for n in range(60):
        if n % 10 == si and n % 12 == bi:
            return n
    raise CalculationError(f"impossible ganzhi {stem}-{branch}")


def nayin(stem: str, branch: str) -> str:
    """NaYin element-image for a pillar."""
    return _corpus()["nayin"][ganzhi_index(stem, branch) // 2]


def _sun_lon(jd_ut: float) -> float:
    xx, _ = _swe.calc_ut(jd_ut, _swe.SUN, _swe.FLG_SWIEPH)
    return xx[0] % 360.0


def _crossing(jd_from: float, target: float,
              max_days: float = 20.0) -> float:
    """Julian day (UT) of the Sun's next crossing of `target` longitude.

    Used only for Lichun (315°) scanning forward from Feb 1, where the
    Sun moves steadily forward with no longitude wrap in range.
    """
    step = 1.0 / 24.0
    prev = _sun_lon(jd_from)
    jd = jd_from
    while jd - jd_from < max_days:
        jd += step
        lon = _sun_lon(jd)
        if prev < target <= lon:
            lo, hi = jd - step, jd
            for _ in range(42):
                mid = (lo + hi) / 2
                if _sun_lon(mid) < target:
                    lo = mid
                else:
                    hi = mid
            return (lo + hi) / 2
        prev = lon
    raise CalculationError(
        f"solar term at {target}° not found within {max_days} days")


def lichun_moment(year: int) -> _datetime.datetime:
    """The instant of Lichun (Sun at 315°) opening BaZi year `year`, UTC."""
    jd = _crossing(_swe.julday(year, 2, 1, 0.0), 315.0)
    y, mo, d, h, mi, sec = _swe.jdut1_to_utc(jd, 1)[:6]
    return _datetime.datetime(y, mo, d, h, mi, int(sec),
                             tzinfo=_datetime.timezone.utc)


def _jie_index(lon: float) -> int:
    """Which jie interval contains this Sun longitude."""
    for i, (start, _branch) in enumerate(JIE):
        end = JIE[(i + 1) % 12][0]
        if start < end:
            inside = start <= lon < end
        else:
            inside = lon >= start or lon < end
        if inside:
            return i
    raise CalculationError("Sun longitude outside all jie intervals")


def _jdn(y: int, m: int, d: int) -> int:
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return (d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4
            - y2 // 100 + y2 // 400 - 32045)


def pillars(iso_date: str, time: str = "12:00",
            timezone: str = "UTC") -> dict:
    """The four pillars for a birth moment.

    `time` is "HH:MM" (24h); `timezone` an IANA zone. Raises
    CalculationError on bad date/time/zone.
    """
    try:
        zone = ZoneInfo(timezone)
    except Exception as exc:
        raise CalculationError(
            f"unknown timezone '{timezone}'") from exc
    try:
        d = _datetime.date.fromisoformat(iso_date)
    except ValueError as exc:
        raise CalculationError(
            f"bad date '{iso_date}'; use ISO YYYY-MM-DD") from exc
    try:
        t = _datetime.time.fromisoformat(time)
    except ValueError as exc:
        raise CalculationError(
            f"bad time '{time}'; use HH:MM") from exc
    local = _datetime.datetime.combine(d, t, tzinfo=zone)
    jd_ut = _swe.julday(local.astimezone(_datetime.timezone.utc).year,
                        local.astimezone(_datetime.timezone.utc).month,
                        local.astimezone(_datetime.timezone.utc).day,
                        local.astimezone(_datetime.timezone.utc).hour
                        + local.astimezone(_datetime.timezone.utc).minute / 60.0)

    # Year pillar: the BaZi year turns at Lichun.
    lichun_utc = lichun_moment(local.year)
    moment_utc = local.astimezone(_datetime.timezone.utc).replace(tzinfo=None)
    bazi_year = (local.year if moment_utc >= lichun_utc.replace(tzinfo=None)
                 else local.year - 1)
    y_stem = _stems()[(bazi_year - 4) % 10]["name"]
    y_branch = _branches()[(bazi_year - 4) % 12]["name"]

    # Month pillar: branch from the current jie, stem by Five Tigers.
    jie = _jie_index(_sun_lon(jd_ut))
    m_branch = JIE[jie][1]
    m_stem = _stems()[(_stem_idx(FIVE_TIGERS[y_stem]) + jie) % 10]["name"]

    # Day pillar: from the Julian Day Number of the local calendar date.
    jdn = _jdn(local.year, local.month, local.day)
    d_stem = _stems()[(jdn + 9) % 10]["name"]
    d_branch = _branches()[(jdn + 1) % 12]["name"]

    # Hour pillar: branch from the two-hour period, stem by Five Rats.
    h_branch = _BRANCH_ORDER[((local.hour + 1) % 24) // 2]
    h_stem = _stems()[(_stem_idx(FIVE_RATS[d_stem])
                       + _BRANCH_ORDER.index(h_branch)) % 10]["name"]

    def pillar(stem: str, branch: str) -> dict:
        b = _branches()[_branch_idx(branch)]
        s = _stems()[_stem_idx(stem)]
        return {"stem": stem, "branch": branch,
                "ganzhi": f"{stem}-{branch}",
                "stem_element": s["element"], "branch_element": b["element"],
                "nayin": nayin(stem, branch)}

    return {
        "date": iso_date, "time": time, "timezone": timezone,
        "year": pillar(y_stem, y_branch),
        "month": pillar(m_stem, m_branch),
        "day": pillar(d_stem, d_branch),
        "hour": pillar(h_stem, h_branch),
        "day_master": d_stem,
        "day_master_element": _stems()[_stem_idx(d_stem)]["element"],
        "solar_term": JIE_NAMES[jie],
        "lichun": lichun_utc.isoformat(),
        "kind": "computed",
        "conventions": ("day changes at local midnight; hour branch from "
                        "local clock time as given (no true-solar-time "
                        "correction); early/late Zi refinement not applied"),
    }


__all__ = ["pillars", "lichun_moment", "nayin", "ganzhi_index",
           "JIE_NAMES", "FIVE_TIGERS", "FIVE_RATS"]
