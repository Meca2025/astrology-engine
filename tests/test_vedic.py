"""Lunar-mansion boundaries and consistent sidereal frames."""

import json
import subprocess
import sys
from dataclasses import replace

import pytest
import swisseph as swe

from astroengine import CalculationError, ChartRequest
from astroengine.vedic import compute_vedic, nakshatra


def vedic_request(**changes):
    return replace(ChartRequest('2000-01-01', 0, 0, 'UTC', '12:00',
                                'sidereal', 'lahiri', 'whole-sign', 'mean'), **changes)


@pytest.mark.parametrize(('longitude', 'name', 'lord', 'pada'), [
    (0, 'Ashwini', 'Ketu', 1), (10 / 3, 'Ashwini', 'Ketu', 2),
    (40 / 3, 'Bharani', 'Venus', 1), (30, 'Krittika', 'Sun', 2),
    (359.999, 'Revati', 'Mercury', 4), (360, 'Ashwini', 'Ketu', 1),
])
def test_known_partitions(longitude, name, lord, pada):
    found = nakshatra(longitude)
    assert (found['name'], found['lord'], found['pada']) == (name, lord, pada)


def test_all_mansion_and_pada_interiors():
    for index in range(108):
        found = nakshatra((index + 0.5) * 360 / 108)
        assert found['index'] == index // 4 + 1
        assert found['pada'] == index % 4 + 1


def test_direct_lahiri_frame_for_planets_and_houses():
    chart = compute_vedic(vedic_request())
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon = swe.calc_ut(2451545, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
    cusps, angles = swe.houses_ex(2451545, 0, 0, b'W', swe.FLG_SIDEREAL)
    assert chart['grahas']['Moon']['longitude'] == pytest.approx(moon)
    assert chart['lagna']['longitude'] == pytest.approx(angles[0])
    assert chart['chart']['houses']['cusps'] == pytest.approx(cusps)
    assert chart['grahas']['Rahu']['speed'] == chart['grahas']['Ketu']['speed']
    assert (chart['grahas']['Ketu']['longitude'] - chart['grahas']['Rahu']['longitude']) % 360 == pytest.approx(180)


def test_alternatives_and_missing_time():
    mean = compute_vedic(vedic_request())
    true = compute_vedic(vedic_request(node_type='true', ayanamsa='raman'))
    assert mean['grahas']['Rahu']['longitude'] != true['grahas']['Rahu']['longitude']
    assert compute_vedic(vedic_request(time=None))['lagna'] is None
    with pytest.raises(CalculationError, match='sidereal'):
        compute_vedic(vedic_request(zodiac='tropical'))


def test_vedic_cli_defaults_are_explicit():
    result = subprocess.run([sys.executable, 'astrology_engine.py', 'vedic',
                             '--date', '2000-01-01', '--time', '12:00',
                             '--lat', '0', '--lon', '0', '--timezone', 'UTC'],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    chart = json.loads(result.stdout)['chart']
    assert chart['request']['zodiac'] == 'sidereal'
    assert chart['request']['house_system'] == 'whole-sign'
