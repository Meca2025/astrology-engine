"""Independent spherical fixtures, birth-instant preservation and zodiac invariance."""

import json
import math
import subprocess
import sys
from dataclasses import replace

import pytest
import swisseph as swe

from astroengine import CalculationError, ChartRequest
from astroengine.locations import angular_lines, compute_location


def test_equatorial_zero_declination_geometry():
    lines = angular_lines(100, 0, 20, 0)
    assert lines == {'MC': 80, 'IC': -100, 'ASC': -10, 'DSC': 170, 'horizon_status': 'crossing'}
    assert angular_lines(350, 0, 0, 0)['MC'] == -10


def test_synthetic_horizon_residual_is_zero():
    latitude, declination = 45, 20
    lines = angular_lines(100, declination, 20, latitude)
    for label in ('ASC', 'DSC'):
        hour_angle = math.radians(20 + lines[label] - 100)
        phi, delta = math.radians(latitude), math.radians(declination)
        altitude_sine = math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.cos(hour_angle)
        assert altitude_sine == pytest.approx(0, abs=1e-12)
    assert lines['ASC'] < lines['MC']


def test_circumpolar_and_pole_geometry():
    assert angular_lines(0, 30, 0, 80)['horizon_status'] == 'always-above'
    assert angular_lines(0, -30, 0, 80)['horizon_status'] == 'always-below'
    assert angular_lines(0, 0, 0, 90)['horizon_status'] == 'on-horizon-all-longitudes'
    assert angular_lines(0, 45, 0, 45)['horizon_status'] == 'grazing'


def test_relocation_keeps_instant_and_zodiac_independent_lines():
    request = ChartRequest('2000-01-01', 28, 77, 'Asia/Kolkata', '00:15', house_system='whole-sign')
    result = compute_location(request, 40, -74)
    natal, relocated = result['natal'], result['relocated']
    assert relocated['utc'] == natal['utc'] == '1999-12-31T18:45:00+00:00'
    assert relocated['positions'] == natal['positions']
    expected, angles = swe.houses_ex(natal['julian_day_ut'], 40, -74, b'W')
    assert relocated['houses']['cusps'] == pytest.approx(expected)
    assert relocated['houses']['ascendant'] == pytest.approx(angles[0])
    sidereal = compute_location(replace(request, zodiac='sidereal'), 40, -74)
    assert sidereal['lines'] == result['lines']
    for line in result['lines'].values():
        for value in line['line_longitudes'].values():
            if isinstance(value, float):
                assert -180 <= value < 180
    with pytest.raises(CalculationError, match='known birth time'):
        compute_location(replace(request, time=None), 40, -74)


def test_location_cli():
    result = subprocess.run([sys.executable, '-m', 'astroengine', 'location',
                             '--date', '2000-01-01', '--time', '12:00', '--lat', '0', '--lon', '0',
                             '--timezone', 'UTC', '--query-lat', '40', '--query-lon', '-74'],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['lines']['Sun']['line_longitudes']['MC'] is not None
