"""Named Jyotisha D1 adapter and equal lunar-mansion arithmetic."""

import math
from typing import Any

from .models import CalculationError, ChartRequest
from .rules import load_rules
from .service import compute_chart


def nakshatra(longitude: float) -> dict[str, Any]:
    if not math.isfinite(longitude):
        raise CalculationError('Nakshatra longitude must be finite')
    rules = load_rules('vedic.json')
    # Multiply first, avoiding repeated subtraction across exact 13°20' boundaries.
    coordinate = (longitude % 360) * len(rules['nakshatras']) / 360
    index = int(coordinate)
    fraction = coordinate - index
    return {'index': index + 1, 'name': rules['nakshatras'][index],
            'lord': rules['vimshottari'][index % len(rules['vimshottari'])]['lord'],
            'pada': min(4, int(fraction * 4) + 1), 'fraction_elapsed': fraction,
            'degrees_elapsed': fraction * 360 / len(rules['nakshatras'])}


def require_sidereal(request: ChartRequest) -> None:
    if request.zodiac != 'sidereal':
        raise CalculationError('Jyotisha requires an explicit sidereal chart profile')


def compute_vedic(request: ChartRequest) -> dict[str, Any]:
    require_sidereal(request)
    chart = compute_chart(request)
    rules = load_rules('vedic.json')
    grahas = {name: {**chart['positions'][body],
                     'nakshatra': nakshatra(chart['positions'][body]['longitude'])}
              for name, body in rules['grahas'].items()}
    lagna = None
    if chart['houses'] is not None:
        ascendant = chart['houses']['ascendant']
        lagna = {'longitude': ascendant, 'nakshatra': nakshatra(ascendant)}
        asc_sign = int(ascendant // 30)
        for position in grahas.values():
            position['rasi_house'] = (position['sign_index'] - asc_sign) % 12 + 1
    return {'schema_version': '1.0', 'kind': 'vedic-d1', 'chart': chart,
            'method': rules['profile'], 'rule_version': rules['version'],
            'grahas': grahas, 'lagna': lagna,
            'moon_nakshatra': grahas['Moon']['nakshatra']}
