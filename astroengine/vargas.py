"""Classical sign mappings, preserving source subdivision information."""

import math
from typing import Any

from .models import CalculationError, ChartRequest
from .rules import load_rules
from .partitions import uniform_partition
from .vedic import compute_vedic


def _target(sign: int, part: int, rule: dict[str, Any]) -> int:
    mode = rule['mode']
    if mode == 'relative':
        return (sign + part * rule['step']) % 12
    if mode == 'relative-parity':
        return (sign + rule['offsets'][sign % 2] + part) % 12
    if mode == 'parity-table':
        return rule['table'][sign % 2][part]
    group = {'element': sign % 4, 'modality': sign % 3, 'parity': sign % 2}[mode]
    return (rule['starts'][group] + part) % 12


def varga_position(longitude: float, division: int) -> dict[str, Any]:
    rules = load_rules('vargas.json')
    if isinstance(division, bool) or not isinstance(division, int) or str(division) not in rules['divisions']:
        raise CalculationError(f'Unsupported classical division: {division}')
    if not math.isfinite(longitude):
        raise CalculationError('Varga longitude must be finite')
    rule = rules['divisions'][str(division)]
    sign = int((longitude % 360) // 30)
    degree = longitude % 30
    part, fraction = uniform_partition(longitude % 360, division, span=30, origin=sign * 30)
    if rule['mode'] == 'unequal-parity':
        segments = rule['segments'][sign % 2]
        part, (start, end, target) = next((i, segment) for i, segment in enumerate(segments)
                                        if segment[0] <= degree < segment[1])
        fraction = (degree - start) / (end - start)
    else:
        target = _target(sign, part, rule)
    return {'sign_index': target, 'sign': load_rules('profiles.json')['signs'][target],
            'source_subdivision': part + 1, 'fraction_within_subdivision': fraction}


def compute_vargas(request: ChartRequest, divisions: list[int] | None = None) -> dict[str, Any]:
    d1 = compute_vedic(request)
    rules = load_rules('vargas.json')
    selected = list(dict.fromkeys(divisions if divisions is not None
                                 else map(int, rules['divisions'])))
    if not selected:
        raise CalculationError('Select at least one divisional chart')
    results = {}
    for division in selected:
        placements = {name: varga_position(position['longitude'], division)
                      for name, position in d1['grahas'].items()}
        lagna = varga_position(d1['lagna']['longitude'], division) if d1['lagna'] else None
        results[f'D{division}'] = {'name': rules['divisions'][str(division)]['name'],
                                  'placements': placements, 'lagna': lagna}
    return {'schema_version': '1.0', 'kind': 'vargas', 'd1': d1,
            'method': rules['method'], 'source': rules['source'],
            'rule_version': rules['version'], 'divisions': results,
            'coordinate_convention': 'Sign mapping with source fraction; not observed astronomical longitudes'}
