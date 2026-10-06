"""Machine schemas match whitelisted calculations and reject invented inputs."""

import copy
import json
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator

from astroengine import CalculationError, capabilities
from astroengine.agent import run_tool, tool_catalog

REQUEST = {'date': '2000-01-01', 'time': '12:00', 'latitude': 0, 'longitude': 0, 'timezone': 'UTC'}


def test_catalog_schema_and_capability_parity():
    available = {item['id'] for item in capabilities()['capabilities'] if item['status'] == 'available'}
    catalog = tool_catalog()
    assert {item['name'] for item in catalog['tools']} == available
    for tool in catalog['tools']:
        Draft202012Validator.check_schema(tool['input_schema'])


def test_vedic_defaults_and_no_mutation():
    parameters = {'request': copy.deepcopy(REQUEST)}
    before = copy.deepcopy(parameters)
    result = run_tool('vedic', parameters)
    assert result['chart']['request']['zodiac'] == 'sidereal'
    assert result['chart']['request']['node_type'] == 'mean'
    assert parameters == before


def test_two_birth_tool_routing():
    result = run_tool('relationship', {'first': REQUEST, 'second': {**REQUEST, 'timezone': 'Asia/Kolkata'}})
    assert result['charts'][0]['utc'] != result['charts'][1]['utc']
    assert result['synergy']['contributions']


@pytest.mark.parametrize('parameters', [
    {'request': {**REQUEST, 'made_up_field': 42}},
    {'request': REQUEST, 'muhurta': True},
    {'request': {**REQUEST, 'latitude': True}},
    {'request': {**REQUEST, 'time': 12}},
    {'request': {**REQUEST, 'latitude': float('nan')}},
    {'request': {**REQUEST, 'date': '2000-99-99'}},
    {},
])
def test_invalid_tool_inputs(parameters):
    with pytest.raises(CalculationError):
        run_tool('chart', parameters)


def test_unsupported_tool_and_tool_cli():
    with pytest.raises(CalculationError, match='Unsupported'):
        run_tool('all-vedic-yogas', {'request': REQUEST})
    result = subprocess.run([sys.executable, '-m', 'astroengine', 'tools'],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert len(json.loads(result.stdout)['tools']) == 9
