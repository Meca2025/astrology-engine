"""Angular and fixed/moving karana boundaries, with local civil-day contract."""

import json
import subprocess
import sys

import pytest

from astroengine import ChartRequest
from astroengine.panchanga import compute_panchanga, panchanga_elements


@pytest.mark.parametrize(('moon', 'tithi', 'paksha', 'karana'), [
    (0, 1, 'Shukla', 'Kimstughna'), (6, 1, 'Shukla', 'Bava'),
    (12, 2, 'Shukla', 'Balava'), (42, 4, 'Shukla', 'Vishti'),
    (48, 5, 'Shukla', 'Bava'), (168, 15, 'Shukla', 'Vishti'),
    (180, 16, 'Krishna', 'Balava'), (342, 29, 'Krishna', 'Shakuni'),
    (348, 30, 'Krishna', 'Chatushpada'), (354, 30, 'Krishna', 'Naga'),
    (360, 1, 'Shukla', 'Kimstughna'),
])
def test_partitions(moon, tithi, paksha, karana):
    result = panchanga_elements(0, moon)
    assert (result['tithi']['index'], result['tithi']['paksha'], result['karana']['name']) == (tithi, paksha, karana)


def test_yoga_and_elongation_wrap():
    result = panchanga_elements(350, 10)
    assert result['elongation_degrees'] == 20
    assert result['yoga']['name'] == 'Vishkambha'
    assert panchanga_elements(0, 359.99)['yoga']['name'] == 'Vaidhriti'
    assert panchanga_elements(0, 168)['tithi']['name'] == 'Purnima'
    assert panchanga_elements(0, 348)['tithi']['name'] == 'Amavasya'


def test_civil_weekday_is_not_sunrise_vara():
    request = ChartRequest('2000-01-01', 0, 0, 'Pacific/Kiritimati', '00:10',
                           zodiac='sidereal', house_system='whole-sign')
    result = compute_panchanga(request)
    assert result['local_date'] == '2000-01-01'
    assert result['civil_weekday'] == 'Saturday'
    assert result['vara'] is None
    assert result['d1']['chart']['utc'].startswith('1999-12-31')


def test_panchanga_cli():
    result = subprocess.run([sys.executable, '-m', 'astroengine', 'panchanga',
                             '--date', '2000-01-01', '--lat', '0', '--lon', '0', '--timezone', 'UTC'],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['kind'] == 'panchanga-snapshot'
