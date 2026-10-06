"""Failure, uncertainty, node motion and real ephemeris provenance contracts."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
import swisseph as swe

import astrology_engine as legacy
from astroengine import CalculationError, ChartRequest, EphemerisRequest, compute_chart
from astroengine.ephemeris import houses_at_jd, positions_at_jd, solar_day_events
from astroengine.rules import load_rules

JD = 2451545.0
SINGLE = ['--date', '2000-01-01', '--lat', '0', '--lon', '0', '--timezone', 'UTC']
PAIR = ['--date1', '2000-01-01', '--lat1', '0', '--lon1', '0', '--timezone1', 'UTC',
        '--date2', '2000-01-02', '--lat2', '0', '--lon2', '30', '--timezone2', 'UTC',
        '--name1', 'A', '--name2', 'B']


def cli(command: str, *flags: str, setup: str | None = None) -> subprocess.CompletedProcess[str]:
    prefix = [sys.executable, '-X', 'utf8']
    prefix += (['astrology_engine.py'] if setup is None else
               ['-c', f'import astrology_engine as e; {setup}; e.main()'])
    return subprocess.run(prefix + [command, *flags], capture_output=True,
                          text=True, encoding='utf-8')


@pytest.mark.parametrize('system', [b'P', b'W', b'E', b'K', b'R', b'C', b'O'])
def test_legacy_houses_match_direct_requested_system(system):
    expected, angles = swe.houses(JD, 39.7684, -86.1581, system)
    cusps, asc, mc = legacy.calc_houses(JD, 39.7684, -86.1581, system)
    assert cusps == pytest.approx(expected, rel=0, abs=1e-10)
    assert (asc, mc) == pytest.approx((angles[0], angles[1]), rel=0, abs=1e-10)


def test_polar_placidus_never_returns_substitute_cusps():
    with pytest.raises(swe.Error):
        swe.houses(JD, 80, 0, b'P')
    with pytest.raises(CalculationError, match='House calculation failed'):
        legacy.calc_houses(JD, 80, 0)
    with pytest.raises(CalculationError, match='Swiss Ephemeris'):
        compute_chart(ChartRequest('2000-01-01', 80, 0, 'UTC', '12:00'))
    assert len(legacy.calc_houses(JD, 80, 0, b'W')[0]) == 12


@pytest.mark.parametrize('command', ['natal', 'transit', 'lots', 'hellenistic', 'progressions', 'solar-return'])
def test_known_polar_cli_fails_before_chart(command):
    result = cli(command, '--date', '2000-01-01', '--time', '12:00',
                 '--lat', '80', '--lon', '0', '--timezone', 'UTC')
    assert result.returncode == 2 and result.stdout == ''
    assert 'House calculation failed' in result.stderr and 'Traceback' not in result.stderr


@pytest.mark.parametrize('command', ['synastry', 'composite'])
def test_paired_house_failure_is_preflighted_before_any_header(command):
    flags = list(PAIR)
    flags[flags.index('--lat2') + 1] = '89'
    if command == 'composite':
        flags[flags.index('--lat1') + 1] = '89'
    result = cli(command, *flags, '--time1', '12:00', '--time2', '12:00')
    assert result.returncode == 2 and result.stdout == ''
    assert 'House calculation failed' in result.stderr


def test_unknown_polar_natal_has_positions_without_house_conclusions():
    result = cli('natal', '--date', '2000-01-01', '--lat', '80', '--lon', '0', '--timezone', 'UTC')
    assert result.returncode == 0, result.stderr
    assert 'noon surrogate' in result.stdout and 'PLANETARY POSITIONS' in result.stdout
    for forbidden in ['ASC (Rising)', 'MC  (Midheaven)', 'Chart Type:', 'HOUSE OVERVIEW',
                      'ARABIC LOTS', 'HELLENISTIC']:
        assert forbidden not in result.stdout
    chart = compute_chart(ChartRequest('2000-01-01', 80, 0, 'UTC'))
    assert chart['houses'] is None and chart['warnings']


@pytest.mark.parametrize('command', ['transit', 'progressions', 'dignity'])
def test_unknown_time_partial_analysis_does_not_call_houses(command):
    setup = "e.calc_houses=lambda *args:(_ for _ in ()).throw(AssertionError('noon houses called'))"
    result = cli(command, *SINGLE, setup=setup)
    assert result.returncode == 0, result.stderr
    assert 'noon surrogate' in result.stdout
    assert 'TRANSITING PLANETS IN NATAL HOUSES' not in result.stdout
    assert 'actual returned results' in result.stdout


def test_dignity_does_not_require_polar_houses_even_with_known_time():
    result = cli('dignity', '--date', '2000-01-01', '--time', '12:00',
                 '--lat', '80', '--lon', '0', '--timezone', 'UTC')
    assert result.returncode == 0 and 'DIGNITY SCORE SUMMARY' in result.stdout


@pytest.mark.parametrize('command', ['lots', 'hellenistic', 'solar-return', 'predict', 'geoastrology'])
def test_unknown_time_house_dependent_commands_reject(command):
    result = cli(command, *SINGLE)
    assert result.returncode == 2 and result.stdout == ''
    assert 'requires a known birth time' in result.stderr and 'Traceback' not in result.stderr


@pytest.mark.parametrize('known_person', [1, 2])
def test_synastry_independently_preserves_known_receiving_overlay(known_person):
    result = cli('synastry', *PAIR, f'--time{known_person}', '12:00')
    assert result.returncode == 0, result.stderr
    receiver, source = ('A', 'B') if known_person == 1 else ('B', 'A')
    assert f"HOUSE OVERLAYS — {source}'s planets in {receiver}'s houses" in result.stdout
    assert f"Overlay into {source}'s houses unavailable" in result.stdout
    assert f"HOUSE OVERLAYS — {receiver}'s planets in {source}'s houses" not in result.stdout
    assert 'Time unknown' in result.stdout and 'noon surrogate' in result.stdout


def test_composite_unknown_time_preserves_symbolic_planets_without_davison():
    setup = "e.calc_houses=lambda *args:(_ for _ in ()).throw(AssertionError('noon houses called'))"
    result = cli('composite', *PAIR, '--time2', '12:00', setup=setup)
    assert result.returncode == 0, result.stderr
    assert 'COMPOSITE PLANETS' in result.stdout and 'symbolic midpoints' in result.stdout
    assert 'Davison chart unavailable' in result.stdout
    assert 'DAVISON RELATIONSHIP CHART' not in result.stdout and 'Davison ASC:' not in result.stdout


@pytest.mark.parametrize('command', ['aspect-grid', 'antiscia'])
def test_utc_date_only_charts_label_noon_surrogate(command):
    result = cli(command, '--date', '2000-01-01')
    assert result.returncode == 0 and 'noon surrogate' in result.stdout
    assert 'actual returned results' in result.stdout


def test_missing_optional_files_have_named_diagnostics_without_fake_positions(tmp_path, monkeypatch):
    monkeypatch.delenv('SE_EPHE_PATH', raising=False)
    rules = load_rules('legacy_astronomy.json')
    result = positions_at_jd(EphemerisRequest(JD, ephemeris_path=str(tmp_path)),
                             rules['required_bodies'], rules['optional_bodies'])
    assert set(result['positions']) == set(rules['required_bodies'])
    assert set(result['unavailable']) == set(rules['optional_bodies'])
    assert all(reason for reason in result['unavailable'].values())
    sun = result['positions']['Sun']
    assert sun['backend'] == 'moshier'
    assert sun['returned_flags'] & swe.FLG_MOSEPH
    assert not sun['returned_flags'] & swe.FLG_SWIEPH
    assert sun['requested_flags'] & swe.FLG_SWIEPH
    assert result['provenance']['requested_backend'] == 'swiss'


def test_dict_keys_stay_planets_and_cli_reports_optional_failure(monkeypatch, caplog, capsys):
    original = swe.calc_ut
    def missing(jd: float, body: int, flags: int):
        if body == swe.CHIRON:
            raise swe.Error('missing optional Chiron fixture')
        return original(jd, body, flags)
    monkeypatch.setattr(swe, 'calc_ut', missing)
    result = legacy.calc_planet_positions(JD)
    assert 'Chiron' not in result and 'Chiron' in result.unavailable
    assert 'provenance' not in result and 'unavailable' not in result
    legacy.calc_aspects(result)
    legacy._print_astronomy(result)
    assert 'optional body Chiron unavailable' in caplog.text
    assert 'missing optional Chiron fixture' in caplog.text
    assert 'flags' in capsys.readouterr().out


@pytest.mark.parametrize('body', [swe.SUN, swe.MOON, swe.TRUE_NODE])
def test_required_body_failure_rejects_entire_snapshot(monkeypatch, body):
    original = swe.calc_ut
    def broken(jd: float, identifier: int, flags: int):
        if identifier == body:
            raise swe.Error('required failure fixture')
        return original(jd, identifier, flags)
    monkeypatch.setattr(swe, 'calc_ut', broken)
    with pytest.raises(CalculationError, match='Required body .* unavailable'):
        legacy.calc_planet_positions(JD)
    with pytest.raises(CalculationError, match='Swiss Ephemeris'):
        compute_chart(ChartRequest('2000-01-01', 0, 0, 'UTC', '12:00'))


def test_required_body_cli_failure_emits_only_stderr():
    setup = "e.swe.calc_ut=lambda *args:(_ for _ in ()).throw(e.swe.Error('major fixture'))"
    result = cli('natal', *SINGLE, '--time', '12:00', setup=setup)
    assert result.returncode == 2 and result.stdout == ''
    assert 'Required body Sun unavailable' in result.stderr and 'major fixture' in result.stderr
    assert 'Traceback' not in result.stderr


@pytest.mark.parametrize('body', [swe.SUN, swe.CHIRON])
def test_unexpected_programming_errors_are_never_silenced(monkeypatch, body):
    original = swe.calc_ut
    def broken(jd: float, identifier: int, flags: int):
        if identifier == body:
            raise RuntimeError('programming fixture')
        return original(jd, identifier, flags)
    monkeypatch.setattr(swe, 'calc_ut', broken)
    with pytest.raises(RuntimeError, match='programming fixture'):
        legacy.calc_planet_positions(JD)


@pytest.mark.parametrize('speed', [-0.05, 0.05])
def test_south_node_antipode_preserves_motion_and_mirrors_latitude(monkeypatch, speed):
    original = swe.calc_ut
    def node(jd: float, identifier: int, flags: int):
        if identifier == swe.TRUE_NODE:
            return (359.5, 1.25, 0, speed, 0, 0), swe.FLG_SPEED | swe.FLG_MOSEPH
        return original(jd, identifier, flags)
    monkeypatch.setattr(swe, 'calc_ut', node)
    result = legacy.calc_planet_positions(JD)
    north, south = result['N.Node'], result['S.Node']
    assert south['longitude'] == 179.5 and south['latitude'] == -1.25
    assert south['speed'] == north['speed'] == speed
    assert south['retrograde'] is north['retrograde'] is (speed < 0)
    assert south['returned_flags'] == north['returned_flags']
    assert south['derived_from'] == 'N.Node'


def test_legacy_fagan_and_core_lahiri_settings_are_isolated_under_mixed_calls():
    swe.set_ephe_path('')
    swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
    expected = swe.calc_ut(JD, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL)[0][0]
    request = ChartRequest('2000-01-01', 0, 0, 'UTC', '12:00', 'sidereal', 'lahiri', 'whole-sign')
    lahiri = compute_chart(request)['positions']['Sun']['longitude']
    def mixed(index: int) -> float:
        return (legacy.calc_planet_positions(JD, False)['Sun']['longitude'] if index % 2
                else compute_chart(request)['positions']['Sun']['longitude'])
    with ThreadPoolExecutor(max_workers=4) as pool:
        values = list(pool.map(mixed, range(20)))
    for index, value in enumerate(values):
        assert value == pytest.approx(expected if index % 2 else lahiri, rel=0, abs=1e-10)


def test_planetary_hours_use_real_ordered_rise_set_instants():
    sunrise, sunset, following = solar_day_events(EphemerisRequest(JD - 0.5), 0, 0)
    status, values = swe.rise_trans(JD - 0.5, swe.SUN,
                                  swe.CALC_RISE | swe.BIT_DISC_CENTER, (0, 0, 0))
    assert status == 0 and sunrise == pytest.approx(values[0], rel=0, abs=1e-10)
    assert sunrise < sunset < following
    hours, ruler, first, second = legacy.planetary_hours(date(2000, 1, 1), 0, 0)
    assert len(hours) == 24 and ruler == 'Saturn'
    assert (first, second) == (sunrise, sunset)
    assert sum(hour[4] for hour in hours) == pytest.approx((following - sunrise) * 1440)


@pytest.mark.parametrize('status,event', [(-2, JD), (0, 0.0), (0, float('nan'))])
def test_missing_or_invalid_solar_events_never_become_clock_fallbacks(monkeypatch, status, event):
    monkeypatch.setattr(swe, 'rise_trans', lambda *args, **kwargs: (status, (event,) * 10))
    with pytest.raises(CalculationError, match='Solar sunrise'):
        legacy.planetary_hours(date(2000, 1, 1), 0, 0)


def test_later_sunset_failure_cannot_make_a_partial_day(monkeypatch):
    results = iter([(0, (JD,)), (-2, (0.0,))])
    monkeypatch.setattr(swe, 'rise_trans', lambda *args, **kwargs: next(results))
    with pytest.raises(CalculationError, match='Solar sunset unavailable'):
        solar_day_events(EphemerisRequest(JD - 0.5), 0, 0)


def test_real_polar_solar_event_cli_is_nonzero_without_fabricated_hours():
    result = cli('planet-hours', '--date', '2000-06-21', '--lat', '89', '--lon', '0')
    assert result.returncode == 2 and result.stdout == ''
    assert 'Solar sunrise unavailable' in result.stderr and 'status -2' in result.stderr


@pytest.mark.parametrize('function,args', [('calc_houses', (JD, 0, 0)),
                                         ('calc_planet_positions', (JD,)),
                                         ('planetary_hours', (date(2000, 1, 1), 0, 0))])
def test_missing_swiss_dependency_is_explicit(monkeypatch, function, args):
    monkeypatch.setattr(legacy, 'SWE', False)
    with pytest.raises(CalculationError, match='pyswisseph is required'):
        getattr(legacy, function)(*args)


@pytest.mark.parametrize('jd', [float('nan'), float('inf'), True, 'bad', 10 ** 1000])
def test_ephemeris_request_rejects_invalid_julian_days(jd):
    with pytest.raises(CalculationError, match='finite UT'):
        legacy.calc_planet_positions(jd)


def test_json_chart_unknown_time_keeps_null_houses_without_optional_registry_leak():
    result = cli('chart', *SINGLE)
    assert result.returncode == 0, result.stderr
    chart = json.loads(result.stdout)
    assert chart['houses'] is None and chart['warnings']
    assert 'unavailable' not in chart['positions']


def test_invalid_house_result_and_body_result_reject(monkeypatch):
    monkeypatch.setattr(swe, 'houses_ex', lambda *args: ((float('nan'),) * 12, (0.0,) * 8))
    with pytest.raises(CalculationError, match='invalid cusps'):
        legacy.calc_houses(JD, 0, 0)
    monkeypatch.setattr(swe, 'calc_ut', lambda *args: ((float('nan'),) * 6, swe.FLG_MOSEPH))
    with pytest.raises(CalculationError, match='invalid body coordinates'):
        legacy.calc_planet_positions(JD)


def test_solar_swiss_error_is_a_known_calculation_failure(monkeypatch):
    def failed(*args, **kwargs):
        raise swe.Error('rise/set fixture')
    monkeypatch.setattr(swe, 'rise_trans', failed)
    with pytest.raises(CalculationError, match='Solar rise/set calculation failed'):
        solar_day_events(EphemerisRequest(JD), 0, 0)


def test_legacy_zodiac_choice_cannot_be_coerced_from_text():
    with pytest.raises(CalculationError, match='explicit boolean'):
        legacy.calc_planet_positions(JD, 'false')
