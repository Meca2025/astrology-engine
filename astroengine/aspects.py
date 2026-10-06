"""Circular geometry and static aspect/house contracts."""

import math
from typing import Any

from .models import CalculationError
from .rules import load_rules


def signed_arc(first: float, second: float) -> float:
    return (second - first + 180) % 360 - 180


def circular_midpoint(first: float, second: float) -> float | None:
    if not all(math.isfinite(value) for value in (first, second)):
        raise CalculationError('Midpoint longitudes must be finite')
    lower, upper = sorted((first % 360, second % 360))
    delta = upper - lower
    if math.isclose(delta, 180, abs_tol=1e-10, rel_tol=0):
        return None
    return ((lower + upper) / 2 + (180 if delta > 180 else 0)) % 360


def house_of(longitude: float, cusps: list[float]) -> int:
    if len(cusps) != 12 or not all(math.isfinite(value) for value in cusps):
        raise CalculationError('House assignment requires twelve finite cusps')
    for index, start in enumerate(cusps):
        span = (cusps[(index + 1) % 12] - start) % 360
        if (longitude - start) % 360 < span:
            return index + 1
    raise CalculationError('Longitude cannot be assigned to these cusps')


def cross_aspects(first: dict[str, Any], second: dict[str, Any]) -> list[dict[str, Any]]:
    rules = load_rules('western.json')
    results = []
    for name1 in rules['relationship_bodies']:
        for name2 in rules['relationship_bodies']:
            if name1 not in first or name2 not in second:
                continue
            separation = abs(signed_arc(first[name1]['longitude'], second[name2]['longitude']))
            for aspect in rules['aspects']:
                orb = abs(separation - aspect['angle'])
                if orb <= aspect['orb']:
                    results.append({'body1': name1, 'body2': name2,
                                    'aspect': aspect['name'], 'angle': aspect['angle'],
                                    'orb': orb, 'maximum_orb': aspect['orb'],
                                    'motion_status': None})
    return sorted(results, key=lambda item: (item['orb'], item['body1'], item['body2'], item['aspect']))
