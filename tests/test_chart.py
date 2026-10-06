"""Input, astronomy and process boundaries with independent expected cases."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime

import pytest
import swisseph as swe

from astroengine import CalculationError, ChartRequest, capabilities, compute_chart
from astroengine.inputs import resolve_utc


def request(**updates):
    base = ChartRequest('2000-01-01', 0.0, 0.0, 'UTC', '12:00')
    return replace(base, **updates)


@pytest.mark.parametrize(('zone', 'clock', 'expected'), [
    ('Asia/Kolkata', '00:15', '1999-12-31T18:45:00+00:00'),
    ('America/New_York', '23:45', '2000-01-02T04:45:00+00:00'),
    ('Pacific/Kiritimati', '12:00', '1999-12-31T22:00:00+00:00'),
])
def test_date_rollover(zone, clock, expected):
    assert resolve_utc(request(timezone=zone, time=clock)).isoformat() == expected


@pytest.mark.parametrize('updates', [
    {'date': '2000-02-30'}, {'time': '24:00'}, {'timezone': 'unknown/zone'},
    {'latitude': float('nan')}, {'longitude': 181}, {'latitude': True},
    {'zodiac': 'imaginary'}, {'ayanamsa': 'unknown'}, {'house_system': 'unknown'},
    {'node_type': 'unknown'}, {'time': '12:00+02:00'},
])
def test_invalid_requests(updates):
    with pytest.raises(CalculationError):
        compute_chart(request(**updates))


@pytest.mark.parametrize(('day', 'clock'), [('2024-11-03', '01:30'), ('2024-03-10', '02:30')])
def test_dst_fold_and_gap_reject(day, clock):
    with pytest.raises(CalculationError, match='ambiguous|nonexistent'):
        resolve_utc(request(date=day, time=clock, timezone='America/New_York'))


def test_unknown_time_converts_local_noon_and_suppresses_houses():
    result = compute_chart(request(time=None, timezone='Asia/Kolkata'))
    assert result['utc'] == '2000-01-01T06:30:00+00:00'
    assert result['houses'] is None
    assert result['time_known'] is False
    assert 'surrogate' in result['warnings'][0]


def test_positions_houses_and_j2000():
    result = compute_chart(request())
    assert result['julian_day_ut'] == 2451545.0
    expected, flags = swe.calc_ut(2451545.0, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
    sun = result['positions']['Sun']
    assert sun['longitude'] == pytest.approx(expected[0], abs=1e-9)
    # Independent approximate astronomical fixture, not the historical README chart.
    assert sun['longitude'] == pytest.approx(280.36892, abs=0.001)
    cusps, angles = swe.houses_ex(2451545.0, 0, 0, b'P')
    assert result['houses']['cusps'] == pytest.approx(cusps)
    assert result['houses']['ascendant'] == pytest.approx(angles[0])
    assert sun['returned_flags'] == flags
    north, south = (result['positions'][key] for key in ('North Node', 'South Node'))
    assert (south['longitude'] - north['longitude']) % 360 == pytest.approx(180)
    assert south['speed'] == north['speed']


def test_no_fabricated_polar_houses():
    with pytest.raises(CalculationError, match='Swiss Ephemeris'):
        compute_chart(request(latitude=80))


def test_sidereal_settings_are_isolated_across_threads():
    profiles = [request(zodiac='sidereal', ayanamsa='lahiri'),
                request(zodiac='sidereal', ayanamsa='raman'), request()]
    expected = [compute_chart(p)['positions']['Moon']['longitude'] for p in profiles]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(compute_chart, profiles * 4))
    assert [r['positions']['Moon']['longitude'] for r in results] == pytest.approx(expected * 4)
    assert abs(expected[0] - expected[1]) > 1


def test_missing_ephemeris_path_is_error(tmp_path):
    with pytest.raises(CalculationError, match='directory'):
        compute_chart(request(ephemeris_path=str(tmp_path / 'absent')))


def test_discovery_is_not_mutable_global_state():
    first = capabilities()
    first['capabilities'][0]['status'] = 'tampered'
    assert capabilities()['capabilities'][0]['status'] == 'available'


def test_cli_success_and_error_contract():
    args = [sys.executable, '-m', 'astroengine', 'chart', '--date', '2000-01-01',
            '--time', '12:00', '--timezone', 'UTC', '--lat', '0', '--lon', '0']
    good = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    assert good.returncode == 0, good.stderr
    assert json.loads(good.stdout)['schema_version'] == '1.0'
    args[args.index('0')] = 'nan'
    bad = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    assert bad.returncode == 2
    assert bad.stdout == ''
    assert 'latitude' in json.loads(bad.stderr)['error']['message']


def test_legacy_import_and_cli_remain_usable():
    command = [sys.executable, '-c',
               "import sys; old=sys.stdout; import astrology_engine; assert sys.stdout is old"]
    imported = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    assert imported.returncode == 0, imported.stderr
    help_result = subprocess.run([sys.executable, 'astrology_engine.py', '--help'],
                                 capture_output=True, text=True, encoding="utf-8")
    assert help_result.returncode == 0
    assert all(key in help_result.stdout for key in ('natal', 'geoastrology', 'synergy', 'chart'))
    lunar = subprocess.run([sys.executable, 'astrology_engine.py', 'lunar'],
                           capture_output=True, text=True, encoding="utf-8")
    assert lunar.returncode == 0, lunar.stderr
    assert 'MOON' in lunar.stdout.upper()
