"""Whole-sign profections, mathematical harmonics and midpoint sensitivity."""

import calendar
import math
from datetime import date
from itertools import combinations
from typing import Any

from .aspects import circular_midpoint, signed_arc
from .ephemeris import zodiac_position
from .models import CalculationError, ChartRequest
from .rules import load_rules
from .service import compute_chart


def annual_profection(birth: date, as_of: date, ascendant: float) -> dict[str, Any]:
    if as_of < birth:
        raise CalculationError('Profection target must not precede birth')
    if not math.isfinite(ascendant):
        raise CalculationError('Profection requires a finite natal Ascendant')
    birthday = date(as_of.year, birth.month, min(birth.day, calendar.monthrange(as_of.year, birth.month)[1]))
    age = as_of.year - birth.year - (as_of < birthday)
    sign = (int((ascendant % 360) // 30) + age) % 12
    rules = load_rules('western.json')
    return {'completed_age': age, 'activated_house': age % 12 + 1,
            'sign': load_rules('profiles.json')['signs'][sign], 'sign_index': sign,
            'lord_of_year': rules['traditional_rulers'][sign],
            'method': 'whole-sign, civil birthday age; traditional rulers',
            'leap_birthday_policy': rules['leap_birthday_policy']}


def harmonic_positions(positions: dict[str, Any], harmonic: int) -> dict[str, Any]:
    if isinstance(harmonic, bool) or not isinstance(harmonic, int) or harmonic <= 0:
        raise CalculationError('Harmonic factor must be a positive integer')
    return {name: zodiac_position(position['longitude'] * harmonic)
            for name, position in positions.items()}


def sensitive_midpoints(positions: dict[str, Any], orb: float) -> list[dict[str, Any]]:
    if not math.isfinite(orb) or not 0 <= orb <= 180:
        raise CalculationError('Midpoint orb must be finite and between 0 and 180 degrees')
    rules = load_rules('western.json')
    bodies = sorted(set(rules['relationship_bodies']) & positions.keys())
    results = []
    for first, second in combinations(bodies, 2):
        midpoint = circular_midpoint(positions[first]['longitude'], positions[second]['longitude'])
        hits = []
        if midpoint is not None:
            for target in bodies:
                separation = abs(signed_arc(midpoint, positions[target]['longitude']))
                if target not in (first, second) and separation <= orb:
                    hits.append({'body': target, 'orb': separation})
        results.append({'bodies': [first, second], 'longitude': midpoint,
                        'ambiguity': 'antipodal' if midpoint is None else None,
                        'hits': sorted(hits, key=lambda item: (item['orb'], item['body']))})
    return results


def compute_western(request: ChartRequest, as_of: str, harmonic: int | None = None,
                    midpoint_orb: float | None = None) -> dict[str, Any]:
    target = date.fromisoformat(as_of)
    birth = date.fromisoformat(request.date)
    if target < birth:
        raise CalculationError('Western target must not precede birth')
    chart = compute_chart(request)
    rules = load_rules('western.json')
    factor = harmonic if harmonic is not None else rules['default_harmonic']
    orb = midpoint_orb if midpoint_orb is not None else rules['default_midpoint_orb']
    profection = annual_profection(birth, target, chart['houses']['ascendant']) if chart['houses'] else None
    return {'schema_version': '1.0', 'kind': 'western-techniques', 'chart': chart,
            'as_of': as_of, 'profection': profection,
            'harmonic': {'factor': factor, 'positions': harmonic_positions(chart['positions'], factor),
                         'coordinate_type': 'mathematical harmonic; no physical instant or houses'},
            'midpoints': {'orb': orb, 'pairs': sensitive_midpoints(chart['positions'], orb)},
            'limitations': ['Profection birthday is civil-calendar based, not exact solar-return timing',
                            'Missing birth time suppresses profection; other positions retain surrogate warnings']}
