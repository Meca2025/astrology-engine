"""Vimshottari periods anchored before birth, then clipped for reporting."""

import math
from datetime import UTC, datetime, timedelta
from typing import Any

from .models import CalculationError, ChartRequest
from .rules import load_rules
from .vedic import compute_vedic, nakshatra


def _period(lord: str, start: datetime, end: datetime,
            window_start: datetime, window_end: datetime) -> dict[str, Any]:
    return {'lord': lord, 'full_start': start.isoformat(), 'full_end': end.isoformat(),
            'start': max(start, window_start).isoformat(),
            'end': min(end, window_end).isoformat(),
            'full_duration_days': (end - start).total_seconds() / 86400,
            'clipped': start < window_start or end > window_end}


def _antars(index: int, start: datetime, end: datetime, birth: datetime,
            horizon: datetime, sequence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cursor = start
    result = []
    cycle_years = sum(item['years'] for item in sequence)
    cumulative = 0
    for offset in range(len(sequence)):
        lord = sequence[(index + offset) % len(sequence)]
        cumulative += lord['years']
        next_time = end if offset == len(sequence) - 1 else start + (end - start) * (cumulative / cycle_years)
        if next_time > birth and cursor < horizon:
            result.append(_period(lord['lord'], cursor, next_time, birth, horizon))
        cursor = next_time
    return result


def vimshottari_timeline(birth: datetime, moon_longitude: float,
                        years: float, year_days: float) -> dict[str, Any]:
    if birth.tzinfo is None:
        raise CalculationError('Dasha birth instant must be timezone-aware')
    if not all(math.isfinite(value) and value > 0 for value in (years, year_days)):
        raise CalculationError('Dasha horizon and year length must be positive and finite')
    birth = birth.astimezone(UTC)
    sequence = load_rules('vedic.json')['vimshottari']
    mansion = nakshatra(moon_longitude)
    index = next(i for i, item in enumerate(sequence) if item['lord'] == mansion['lord'])
    first_years = sequence[index]['years']
    start = birth - timedelta(days=first_years * year_days * mansion['fraction_elapsed'])
    horizon = birth + timedelta(days=years * year_days)
    periods = []
    while start < horizon:
        lord = sequence[index]
        end = start + timedelta(days=lord['years'] * year_days)
        periods.append({**_period(lord['lord'], start, end, birth, horizon),
                        'antardashas': _antars(index, start, end, birth, horizon, sequence)})
        start, index = end, (index + 1) % len(sequence)
    return {'balance_at_birth_years': first_years * (1 - mansion['fraction_elapsed']),
            'birth_nakshatra': mansion, 'year_days': year_days,
            'window_start': birth.isoformat(), 'window_end': horizon.isoformat(),
            'mahadasas': periods}


def active_period(timeline: dict[str, Any], instant: datetime) -> dict[str, str] | None:
    if instant.tzinfo is None:
        raise CalculationError('As-of instant must include a UTC offset')
    utc = instant.astimezone(UTC)
    for maha in timeline['mahadasas']:
        if datetime.fromisoformat(maha['start']) <= utc < datetime.fromisoformat(maha['end']):
            antar = next(item for item in maha['antardashas']
                         if datetime.fromisoformat(item['start']) <= utc < datetime.fromisoformat(item['end']))
            return {'mahadasa': maha['lord'], 'antardasha': antar['lord']}
    return None


def compute_dashas(request: ChartRequest, years: float | None = None,
                   year_model: str | None = None, as_of: str | None = None) -> dict[str, Any]:
    rules = load_rules('timing.json')
    model = year_model or rules['default_year_model']
    if model not in rules['year_models']:
        raise CalculationError(f'Unknown year model: {model}')
    d1 = compute_vedic(request)
    birth = datetime.fromisoformat(d1['chart']['utc'])
    try:
        timeline = vimshottari_timeline(birth, d1['grahas']['Moon']['longitude'],
                                       years if years is not None else rules['default_horizon_years'],
                                       rules['year_models'][model])
        active = active_period(timeline, datetime.fromisoformat(as_of)) if as_of else None
    except (OverflowError, ValueError) as exc:
        raise CalculationError(f'Invalid dasha window or as-of instant: {exc}') from exc
    return {'schema_version': '1.0', 'kind': 'vimshottari', 'd1': d1,
            'year_model': model, 'interval_convention': '[start, end)',
            'source': rules['source'], 'timeline': timeline, 'as_of': as_of,
            'active': active}
