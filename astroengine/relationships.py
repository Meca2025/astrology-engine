"""Two-profile relationships with fully traceable symbolic weights."""

from typing import Any

from .aspects import circular_midpoint, cross_aspects, house_of
from .ephemeris import zodiac_position
from .models import CalculationError, ChartRequest
from .rules import load_rules
from .service import compute_chart


def synergy(aspects: list[dict[str, Any]]) -> dict[str, Any]:
    rules = load_rules('western.json')
    definitions = {item['name']: item for item in rules['aspects']}
    contributions = []
    for aspect in aspects:
        names = (aspect['body1'], aspect['body2'])
        weights = [rules['body_weights'].get(name, rules['default_body_weight']) for name in names]
        weight = definitions[aspect['aspect']]['weight']
        if aspect['aspect'] == 'Conjunction' and any(name in rules['conjunction_challenge_bodies'] for name in names):
            weight = rules['conjunction_challenge_weight']
        tightness = max(0, 1 - aspect['orb'] / aspect['maximum_orb'])
        score = weight * sum(weights) / len(weights) * tightness
        contributions.append({**aspect, 'aspect_weight': weight,
                              'body_weight': sum(weights) / len(weights),
                              'tightness': tightness, 'contribution': score})
    return {'method': rules['synergy_method'], 'total': sum(item['contribution'] for item in contributions),
            'harmony': sum(max(0, item['contribution']) for item in contributions),
            'challenge': sum(max(0, -item['contribution']) for item in contributions),
            'contributions': contributions, 'meaning': 'Symbolic heuristic; not an empirical probability or relationship verdict'}


def _overlays(source: dict[str, Any], receiver: dict[str, Any]) -> dict[str, int] | None:
    if receiver['houses'] is None:
        return None
    return {name: house_of(position['longitude'], receiver['houses']['cusps'])
            for name, position in source['positions'].items()}


def compute_relationship(first: ChartRequest, second: ChartRequest) -> dict[str, Any]:
    if first.zodiac != second.zodiac or (first.zodiac == 'sidereal' and first.ayanamsa != second.ayanamsa):
        raise CalculationError('Relationship charts require the same zodiac and ayanamsa')
    if first.node_type != second.node_type:
        raise CalculationError('Relationship charts require the same node model')
    chart1, chart2 = compute_chart(first), compute_chart(second)
    aspects = cross_aspects(chart1['positions'], chart2['positions'])
    composite = {}
    for name in sorted(chart1['positions'].keys() & chart2['positions'].keys()):
        midpoint = circular_midpoint(chart1['positions'][name]['longitude'], chart2['positions'][name]['longitude'])
        composite[name] = (zodiac_position(midpoint) if midpoint is not None
                           else {'longitude': None, 'ambiguity': 'Exactly antipodal: two equivalent midpoints'})
    return {'schema_version': '1.0', 'kind': 'relationship', 'charts': [chart1, chart2],
            'cross_aspects': aspects, 'house_overlays': {'first_in_second': _overlays(chart1, chart2),
                                                      'second_in_first': _overlays(chart2, chart1)},
            'composite': {'method': 'shorter-arc midpoint', 'positions': composite, 'houses': None},
            'synergy': synergy(aspects),
            'conventions': ['Static synastry has no applying/separating motion across birth epochs',
                            'Composite positions are mathematical midpoints; no astronomical instant or house angles inferred']}
