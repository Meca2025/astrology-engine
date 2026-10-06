"""Circular invariants, separate civil time and explainable relationship output."""

import json
import subprocess
import sys
from dataclasses import replace

import pytest

from astroengine import CalculationError, ChartRequest
from astroengine.aspects import circular_midpoint, cross_aspects, house_of
from astroengine.relationships import compute_relationship, synergy


@pytest.mark.parametrize(('first', 'second', 'expected'), [(350, 10, 0), (10, 50, 30), (0, 180, None)])
def test_midpoint_wrap_swap_and_ambiguity(first, second, expected):
    assert circular_midpoint(first, second) == expected
    assert circular_midpoint(second, first) == expected


def test_house_boundaries_wrap():
    cusps = [(350 + i * 30) % 360 for i in range(12)]
    assert house_of(350, cusps) == 1
    assert house_of(19.99, cusps) == 1
    assert house_of(20, cusps) == 2


def test_static_aspects_threshold_and_score_trace():
    first = {'Sun': {'longitude': 350}}
    second = {'Moon': {'longitude': 110}}
    aspects = cross_aspects(first, second)
    assert aspects[0]['aspect'] == 'Trine'
    assert aspects[0]['motion_status'] is None
    assert synergy(aspects)['total'] == 9  # trine 3 * luminary mean weight 3
    assert synergy(aspects)['total'] == sum(item['contribution'] for item in synergy(aspects)['contributions'])
    assert cross_aspects(first, {'Moon': {'longitude': 116.001}}) == []


def test_two_zones_and_unknown_receiver_houses():
    first = ChartRequest('2000-01-01', 40, -74, 'America/New_York', '00:15')
    second = ChartRequest('2000-01-01', 28, 77, 'Asia/Kolkata', None)
    report = compute_relationship(first, second)
    assert report['charts'][0]['utc'] == '2000-01-01T05:15:00+00:00'
    assert report['charts'][1]['utc'] == '2000-01-01T06:30:00+00:00'
    assert report['house_overlays']['first_in_second'] is None
    assert report['house_overlays']['second_in_first'] is not None
    reverse = compute_relationship(second, first)
    assert reverse['synergy']['total'] == pytest.approx(report['synergy']['total'])
    assert reverse['composite'] == report['composite']
    with pytest.raises(CalculationError, match='zodiac'):
        compute_relationship(first, replace(second, zodiac='sidereal'))


def test_relationship_cli():
    command = [sys.executable, '-m', 'astroengine', 'synergy-json']
    for suffix in ('1', '2'):
        command += [f'--date{suffix}', '2000-01-01', f'--time{suffix}', '12:00',
                    f'--lat{suffix}', '0', f'--lon{suffix}', '0', f'--timezone{suffix}', 'UTC']
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['synergy']['contributions']
