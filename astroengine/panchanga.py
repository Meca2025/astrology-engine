"""Instant lunar/solar partitions, distinct from a sunrise-based calendar."""

import math
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from .models import CalculationError, ChartRequest
from .rules import load_rules
from .vedic import compute_vedic, nakshatra


def panchanga_elements(sun: float, moon: float) -> dict[str, Any]:
    if not all(math.isfinite(value) for value in (sun, moon)):
        raise CalculationError('Panchanga longitudes must be finite')
    rules = load_rules('panchanga.json')
    elongation = (moon - sun) % 360
    tithi_index = int(elongation / 12)
    fortnight_index = tithi_index % 15
    terminal = rules['full_moon_tithi'] if tithi_index == 14 else rules['new_moon_tithi']
    name = rules['tithis'][fortnight_index] if fortnight_index < 14 else terminal
    karana_index = int(elongation / 6)
    karana = rules['karanas_fixed'].get(str(karana_index))
    if karana is None:
        karana = rules['karanas_repeating'][(karana_index - 1) % len(rules['karanas_repeating'])]
    yoga_coordinate = ((sun + moon) % 360) * len(rules['yogas']) / 360
    yoga_index = int(yoga_coordinate)
    return {'elongation_degrees': elongation,
            'tithi': {'index': tithi_index + 1, 'name': name,
                      'paksha': rules['pakshas'][tithi_index // 15],
                      'fraction_elapsed': elongation / 12 - tithi_index},
            'karana': {'half_tithi_index': karana_index + 1, 'name': karana,
                       'fraction_elapsed': elongation / 6 - karana_index},
            'nakshatra': nakshatra(moon),
            'yoga': {'index': yoga_index + 1, 'name': rules['yogas'][yoga_index],
                     'fraction_elapsed': yoga_coordinate - yoga_index}}


def compute_panchanga(request: ChartRequest) -> dict[str, Any]:
    d1 = compute_vedic(request)
    positions = d1['grahas']
    elements = panchanga_elements(positions['Sun']['longitude'], positions['Moon']['longitude'])
    local = datetime.fromisoformat(d1['chart']['utc']).astimezone(ZoneInfo(request.timezone))
    rules = load_rules('panchanga.json')
    return {'schema_version': '1.0', 'kind': 'panchanga-snapshot', 'd1': d1,
            'elements': elements, 'local_date': local.date().isoformat(),
            'civil_weekday': rules['civil_weekdays'][local.weekday()],
            'vara': None, 'method': rules['method'], 'source': rules['source'],
            'limitations': ['Sunrise vara, transition times, festivals and muhurta require the calendar slice']}
