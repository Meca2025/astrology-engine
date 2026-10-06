"""Strict legacy API/CLI inputs, complete propagation and paired UTC evidence."""

import subprocess
import sys
from types import SimpleNamespace

import pytest
import swisseph as swe

import astrology_engine as legacy
from astroengine import CalculationError, ChartRequest
from astroengine.inputs import resolve_utc
from astroengine.legacy_inputs import date_window, return_year


def cli(command, *flags, setup=None):
    prefix = [sys.executable, '-X', 'utf8']
    if setup is None:
        prefix += ['astrology_engine.py']
    else:
        prefix += ['-c', f'import astrology_engine as e; {setup}; e.main()']
    return subprocess.run(prefix + [command, *flags], capture_output=True,
                          text=True, encoding='utf-8')


@pytest.mark.parametrize('day,clock', [
    ('2024-02-30', '12:00'), ('2000-01-01', '24:00'), ('2000-01-01', '12:60'),
    ('2000-01-01', ''), ('2000-01-01', '12:00+02:00'),
    ('20240101', '12:00'), ('2000-01-01', '1200'),
])
def test_shared_civil_validation(day, clock):
    with pytest.raises(CalculationError, match='Invalid'):
        legacy.parse_date_time(day, clock)
    with pytest.raises(CalculationError, match='Invalid'):
        resolve_utc(ChartRequest(day, 0, 0, 'UTC', clock))


@pytest.mark.parametrize('day,clock,message', [
    ((2024, 11, 3), 1.5, 'ambiguous'), ((2024, 3, 10), 2.5, 'nonexistent'),
])
def test_legacy_dst_folds_and_gaps_reject(day, clock, message):
    with pytest.raises(CalculationError, match=message):
        legacy.local_to_utc(*day, clock, 'America/New_York')


@pytest.mark.parametrize('hour', [float('nan'), float('inf'), True, 24, -1, '12'])
def test_direct_local_hour_validation(hour):
    with pytest.raises(CalculationError, match='clock hour'):
        legacy.local_to_utc(2000, 1, 1, hour, 'UTC')


def test_timezone_override_bypasses_discovery(monkeypatch):
    def unexpected(*args):
        pytest.fail('explicit coordinates and zone must bypass optional backends')
    monkeypatch.setattr(legacy, '_geo', unexpected)
    monkeypatch.setattr(legacy, '_tzf', unexpected)
    result = legacy.resolve_birth('2000-01-01', '00:15', 'unrelated city',
                                   lat_override=0, lon_override=0,
                                   timezone_override='Asia/Kolkata')
    assert result[:4] == (1999, 12, 31, 18.75)
    assert result[6] == 'Asia/Kolkata' and result[9] is False
    assert legacy.julian_day(*result[:4]) == pytest.approx(swe.julday(1999, 12, 31, 18.75), rel=0, abs=1e-9)


def test_unresolved_zone_and_invalid_override_reject(monkeypatch):
    monkeypatch.setattr(legacy, 'resolve_timezone', lambda lat, lon: None)
    with pytest.raises(CalculationError, match='--timezone'):
        legacy.resolve_birth('2000-01-01', '12:00', '', lat_override=0, lon_override=0)
    for zone in ('unknown/zone', ''):
        with pytest.raises(CalculationError, match='timezone'):
            legacy.resolve_birth('2000-01-01', '12:00', '', lat_override=0, lon_override=0,
                                  timezone_override=zone)


@pytest.mark.parametrize('coords', [(None, 0), (0, None), (float('nan'), 0),
                                  (91, 0), (0, 181), (True, 0), ('bad', 0), (10 ** 1000, 0)])
def test_invalid_coordinates_reject_before_network(monkeypatch, coords):
    monkeypatch.setattr(legacy, '_geo', lambda: pytest.fail('invalid flags reached geocoding'))
    with pytest.raises(CalculationError):
        legacy.geocode_city('London', 'GB', *coords)


def test_unresolved_and_invalid_geocoder_locations_reject(monkeypatch):
    monkeypatch.setattr(legacy, 'KK', False)
    monkeypatch.setattr(legacy, '_geo', lambda: None)
    with pytest.raises(CalculationError, match='Location.*unresolved'):
        legacy.geocode_city('__unknown_input_fixture__')
    fake = SimpleNamespace(geocode=lambda query: SimpleNamespace(latitude=float('nan'), longitude=0))
    monkeypatch.setattr(legacy, '_geo', lambda: fake)
    with pytest.raises(CalculationError, match='latitude'):
        legacy.geocode_city('London')


@pytest.mark.parametrize('flags,message', [
    (['--date', '2000-02-30', '--time', '12:00', '--lat', '0', '--lon', '0', '--timezone', 'UTC'], 'Invalid date'),
    (['--date', '2000-01-01', '--time', '', '--lat', '0', '--lon', '0', '--timezone', 'UTC'], 'Invalid time'),
    (['--date', '2000-01-01', '--time', '12:00', '--lat', '0', '--timezone', 'UTC'], 'both --lat and --lon'),
    (['--date', '2000-01-01', '--time', '12:00', '--lat', 'nan', '--lon', '0', '--timezone', 'UTC'], 'latitude'),
    (['--date', '2024-11-03', '--time', '01:30', '--lat', '0', '--lon', '0', '--timezone', 'America/New_York'], 'ambiguous'),
    (['--date', '2024-03-10', '--time', '02:30', '--lat', '0', '--lon', '0', '--timezone', 'America/New_York'], 'nonexistent'),
    (['--date', '2000-01-01', '--time', '12:00', '--lat', '0', '--lon', '0', '--timezone', 'unknown/zone'], 'timezone'),
])
def test_cli_input_error_has_no_chart(flags, message):
    result = cli('natal', *flags)
    assert result.returncode == 2
    assert result.stdout == ''
    assert message in result.stderr and 'Traceback' not in result.stderr


def test_missing_discovery_is_not_assumed_utc_cli():
    result = cli('natal', '--date', '2000-01-01', '--time', '12:00', '--lat', '0', '--lon', '0',
                 setup='e.resolve_timezone=lambda lat,lon:None')
    assert result.returncode == 2 and result.stdout == ''
    assert '--timezone' in result.stderr


def test_unresolved_city_cli_has_no_chart():
    result = cli('natal', '--date', '2000-01-01', '--city', '__unknown_input_fixture__',
                 '--timezone', 'UTC', setup='e._geo=lambda:None; e.KK=False')
    assert result.returncode == 2 and result.stdout == ''
    assert 'Location' in result.stderr and '--lat' in result.stderr


SINGLE_HANDLERS = ['natal', 'transit', 'solar-return', 'progressions', 'lots',
                   'hellenistic', 'dignity', 'predict', 'geoastrology']


@pytest.mark.parametrize('command', SINGLE_HANDLERS)
def test_every_birth_handler_and_help_propagates_timezone(monkeypatch, command):
    class StopAfterInput(Exception):
        pass
    received = []
    def capture(*args):
        received.append(args)
        raise StopAfterInput
    monkeypatch.setattr(legacy, 'resolve_birth', capture)
    args = SimpleNamespace(date='2000-01-01', time='12:00', city='London', nation='GB',
                           lat=0, lon=0, timezone='Asia/Kolkata')
    with pytest.raises(StopAfterInput):
        getattr(legacy, f"cmd_{command.replace('-', '_')}")(args)
    assert received[0][-1] == 'Asia/Kolkata'
    help_result = cli(command, '--help')
    assert help_result.returncode == 0 and '--timezone' in help_result.stdout


@pytest.mark.parametrize('command', ['synastry', 'composite', 'synergy'])
def test_paired_cli_has_independent_zones_and_no_discovery(command):
    result = cli(command, '--date1', '2000-01-01', '--time1', '00:15', '--lat1', '0', '--lon1', '0',
                 '--timezone1', 'Asia/Kolkata', '--date2', '2000-01-01', '--time2', '23:45',
                 '--lat2', '0', '--lon2', '30', '--timezone2', 'America/New_York',
                 setup="e._geo=lambda:(_ for _ in ()).throw(AssertionError('geocoding called')); e._tzf=lambda:(_ for _ in ()).throw(AssertionError('zone discovery called'))")
    assert result.returncode == 0, result.stderr
    assert '1999-12-31 18:45 UTC' in result.stdout
    assert '2000-01-02 04:45 UTC' in result.stdout
    assert 'default location' not in result.stdout
    if command == 'composite':
        assert 'DAVISON RELATIONSHIP CHART' in result.stdout


@pytest.mark.parametrize('command', ['synastry', 'composite', 'synergy'])
def test_paired_calculations_use_exact_independent_julian_days(monkeypatch, capsys, command):
    original = legacy.calc_planet_positions
    dates = []
    def record(jd, *args, **kwargs):
        dates.append(jd)
        return original(jd, *args, **kwargs)
    monkeypatch.setattr(legacy, 'calc_planet_positions', record)
    args = SimpleNamespace(date1='2000-01-01', time1='00:15', lat1=0, lon1=0,
                           timezone1='Asia/Kolkata', date2='2000-01-01', time2='23:45',
                           lat2=0, lon2=30, timezone2='America/New_York', name1='A', name2='B')
    getattr(legacy, f'cmd_{command}')(args)
    assert dates[:2] == [swe.julday(1999, 12, 31, 18.75), swe.julday(2000, 1, 2, 4.75)]
    assert 'default location' not in capsys.readouterr().out


def test_second_person_invalid_fails_before_any_chart():
    result = cli('synergy', '--date1', '2000-01-01', '--lat1', '0', '--lon1', '0', '--timezone1', 'UTC',
                 '--date2', '2000-01-01', '--lat2', '0', '--lon2', '0', '--timezone2', 'unknown/zone')
    assert result.returncode == 2 and result.stdout == ''
    assert 'timezone' in result.stderr


def test_default_pair_location_is_exposed_and_no_partial_davison(monkeypatch, capsys):
    monkeypatch.setattr(legacy, '_geo', lambda: None)
    monkeypatch.setattr(legacy, 'KK', False)
    args = SimpleNamespace(date1='2000-01-01', timezone1='UTC', lat1=0, lon1=0,
                           date2='2000-01-01', timezone2='UTC', name1='A', name2='B')
    # Optional backends are bypassed while the existing default city resolves offline.
    legacy.cmd_composite(args)
    out = capsys.readouterr().out
    assert 'default location: London, GB' in out
    assert 'DAVISON RELATIONSHIP CHART' not in out


def test_planet_hours_accepts_zero_pair_and_rejects_partial(monkeypatch):
    class StopBeforeAstronomy(Exception):
        pass
    received = []
    def capture(day, lat, lon):
        received.append((day.isoformat(), lat, lon))
        raise StopBeforeAstronomy
    monkeypatch.setattr(legacy, 'planetary_hours', capture)
    # W09b2 preserves admission and lets unexpected astronomy errors propagate.
    with pytest.raises(StopBeforeAstronomy):
        legacy.cmd_planet_hours(SimpleNamespace(date='2000-01-01', lat=0, lon=0, city=None, nation=None))
    assert received == [('2000-01-01', 0, 0)]
    with pytest.raises(CalculationError, match='both'):
        legacy.cmd_planet_hours(SimpleNamespace(date='2000-01-01', lat=0, lon=None, city=None, nation=None))


def test_typed_cli_empty_time_is_invalid():
    result = cli('chart', '--date', '2000-01-01', '--time', '', '--lat', '0', '--lon', '0', '--timezone', 'UTC')
    assert result.returncode == 2 and result.stdout == '' and 'Invalid time' in result.stderr


def test_historical_iana_seconds_and_civil_second_precision():
    # IANA tzdb europe: Paris uses +00:09:21 through 1911; 12:00 - offset = 11:50:39.
    # https://data.iana.org/time-zones/tzdb/europe
    result = legacy.resolve_birth('1890-01-01', '12:00', '', lat_override=0, lon_override=0,
                                   timezone_override='Europe/Paris')
    assert result[3] == pytest.approx(11 + 50 / 60 + 39 / 3600, rel=0, abs=1e-12)
    assert '11:50:39 UTC' in result[7] and 'UTC+00:09:21' in result[7]
    assert legacy.local_to_utc(1890, 1, 1, 12, 'Europe/Paris')[0] == result[3]
    seconds = legacy.resolve_birth('2000-01-01', '00:15:30.125', '', lat_override=0, lon_override=0,
                                    timezone_override='Asia/Kolkata')
    assert seconds[:3] == (1999, 12, 31)
    assert seconds[3] == pytest.approx(18 + 45 / 60 + 30.125 / 3600, rel=0, abs=1e-12)
    assert '18:45:30.125000 UTC' in seconds[7]


def test_huge_integer_coordinates_reject_as_domain_error():
    with pytest.raises(CalculationError, match='latitude'):
        resolve_utc(ChartRequest('2000-01-01', 10 ** 1000, 0, 'UTC', '12:00'))


@pytest.mark.parametrize('command,extra,message', [
    ('progressions', ['--prog-date', '2024-02-30'], 'Invalid date'),
    ('transit', ['--transit-time', '12:00'], '--transit-date'),
    ('transit', ['--transit-date', '2024-02-30'], 'Invalid date'),
    ('solar-return', ['--year', 'bad'], 'Invalid return year'),
    ('predict', ['--start', '2000-01-02', '--end', '2000-01-01'], 'after --start'),
    ('predict', ['--start', '2024-02-30'], 'Invalid date'),
    ('geoastrology', ['--query-lat', '0'], 'both --query-lat and --query-lon'),
    ('geoastrology', ['--query-lat', '0', '--query-lon', '181'], 'longitude'),
])
def test_secondary_inputs_fail_before_chart_output(command, extra, message):
    result = cli(command, '--date', '2000-01-01', '--time', '12:00', '--lat', '0', '--lon', '0',
                 '--timezone', 'UTC', *extra)
    assert result.returncode == 2 and result.stdout == ''
    assert message in result.stderr and 'Traceback' not in result.stderr


def test_zero_location_query_is_present():
    result = cli('geoastrology', '--date', '2000-01-01', '--time', '12:00', '--lat', '0', '--lon', '0',
                 '--timezone', 'UTC', '--query-lat', '0', '--query-lon', '0')
    assert result.returncode == 0, result.stderr
    assert 'POWER SPOT ANALYSIS  (0.00°N, 0.00°E)' in result.stdout


def test_prediction_default_window_and_leap_day():
    first, second = date_window('2024-02-29')
    assert (first.isoformat(), second.isoformat()) == ('2024-02-29', '2025-02-28')
    first, second = date_window('2000-01-01', '2000-01-02')
    assert (second - first).days == 1
    with pytest.raises(CalculationError, match='--end'):
        date_window('9999-12-31')


@pytest.mark.parametrize('value', [0, 10000, True, 'bad', 2024.5])
def test_return_year_is_a_real_integer_year(value):
    with pytest.raises(CalculationError, match='Invalid return year'):
        return_year(value)


@pytest.mark.parametrize('day,clock,zone', [
    ('0001-01-01', '00:00', 'Asia/Tokyo'),
    ('9999-12-31', '23:00', 'America/New_York'),
])
def test_utc_calendar_overflow_is_domain_error(day, clock, zone):
    with pytest.raises(CalculationError, match='supported civil calendar'):
        legacy.resolve_birth(day, clock, '', lat_override=0, lon_override=0, timezone_override=zone)
