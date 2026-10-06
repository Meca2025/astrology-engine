"""Civil birthdays, traditional rulers, harmonics and midpoint sensitivity."""

import json
import subprocess
import sys
from datetime import date

import pytest

from astroengine import CalculationError, ChartRequest
from astroengine.western import annual_profection, compute_western, harmonic_positions, sensitive_midpoints


@pytest.mark.parametrize(('target', 'age', 'house', 'sign', 'lord'), [
    ('2000-01-01', 0, 1, 'Libra', 'Venus'),
    ('2011-12-31', 11, 12, 'Virgo', 'Mercury'),
    ('2012-01-01', 12, 1, 'Libra', 'Venus'),
    ('2013-01-01', 13, 2, 'Scorpio', 'Mars'),
])
def test_annual_profection_boundary(target, age, house, sign, lord):
    found = annual_profection(date(2000, 1, 1), date.fromisoformat(target), 181)
    assert (found['completed_age'], found['activated_house'], found['sign'], found['lord_of_year']) == (age, house, sign, lord)


def test_leap_birthday_policy():
    assert annual_profection(date(2000, 2, 29), date(2023, 2, 27), 0)['completed_age'] == 22
    assert annual_profection(date(2000, 2, 29), date(2023, 2, 28), 0)['completed_age'] == 23
    with pytest.raises(CalculationError):
        annual_profection(date(2000, 1, 1), date(1999, 12, 31), 0)


def test_harmonic_wrap_and_invalid_factor():
    assert harmonic_positions({'Sun': {'longitude': 350}}, 2)['Sun']['longitude'] == 340
    with pytest.raises(CalculationError):
        harmonic_positions({}, 0)
    with pytest.raises(CalculationError):
        harmonic_positions({}, 2.5)


def test_third_body_sensitive_midpoint_and_antipode():
    positions = {'Sun': {'longitude': 350}, 'Moon': {'longitude': 10}, 'Mars': {'longitude': 0.5}}
    pair = next(item for item in sensitive_midpoints(positions, 1) if set(item['bodies']) == {'Sun', 'Moon'})
    assert pair['longitude'] == 0
    assert pair['hits'] == [{'body': 'Mars', 'orb': 0.5}]
    positions['Moon']['longitude'] = 170
    pair = next(item for item in sensitive_midpoints(positions, 1) if set(item['bodies']) == {'Sun', 'Moon'})
    assert pair['ambiguity'] == 'antipodal'
    assert pair['hits'] == []


def test_missing_birth_time_suppresses_profection_only():
    request = ChartRequest('2000-01-01', 0, 0, 'UTC')
    result = compute_western(request, '2026-01-01')
    assert result['profection'] is None
    assert result['chart']['warnings']
    assert result['harmonic']['positions']


def test_western_cli_and_command_registry():
    result = subprocess.run([sys.executable, '-m', 'astroengine', 'western', '--date', '2000-01-01',
                             '--time', '12:00', '--lat', '0', '--lon', '0', '--timezone', 'UTC',
                             '--as-of', '2026-01-01', '--harmonic', '7'],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['harmonic']['factor'] == 7
    from astroengine.cli import main, register_commands
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_commands(sub)
    assert set(sub.choices) == {'chart', 'capabilities', 'tools', 'vedic', 'vargas', 'dashas', 'panchanga',
                                 'relationship', 'synergy-json', 'location', 'western'}
