"""Legacy entry point regressions with explicit dates and offline IANA zones."""

import subprocess
import sys
from types import SimpleNamespace

import pytest
import swisseph as swe

import astrology_engine as legacy


CASES = [
    ('2000-01-01', '00:15', 'Asia/Kolkata', (1999, 12, 31, 18.75), -5.25),
    ('2000-01-01', '23:45', 'America/New_York', (2000, 1, 2, 4.75), 28.75),
    ('2000-01-01', '12:00', 'Pacific/Kiritimati', (1999, 12, 31, 22.0), -2.0),
    ('2024-03-01', '00:15', 'Asia/Kolkata', (2024, 2, 29, 18.75), -5.25),
    ('1975-11-22', '14:30', 'America/Indiana/Indianapolis', (1975, 11, 22, 19.5), 19.5),
]


@pytest.mark.parametrize('day,clock,zone,expected,relative_hour', CASES)
def test_legacy_utc_date_and_direct_julian_day(monkeypatch, day, clock, zone, expected, relative_hour):
    monkeypatch.setattr(legacy, 'resolve_timezone', lambda lat, lon: zone)
    parsed = legacy.parse_date_time(day, clock)
    converted, offset = legacy.local_to_utc(*parsed, zone)
    assert converted == pytest.approx(relative_hour)
    assert offset.startswith('UTC') and '?' not in offset
    expected_jd = swe.julday(*expected)
    assert legacy.julian_day(*parsed[:3], converted) == pytest.approx(expected_jd, abs=1e-9, rel=0)
    resolved = legacy.resolve_birth(day, clock, '', lat_override=0, lon_override=0)
    assert len(resolved) == 10
    assert resolved[:4] == expected
    assert legacy.julian_day(*resolved[:4]) == pytest.approx(expected_jd, abs=1e-9, rel=0)
    assert resolved[-1] is False
    if day != f'{expected[0]:04d}-{expected[1]:02d}-{expected[2]:02d}':
        assert f'{expected[0]:04d}-{expected[1]:02d}-{expected[2]:02d}' in resolved[7]
    monkeypatch.setattr(legacy, 'SWE', False)
    assert legacy.julian_day(*parsed[:3], converted) == pytest.approx(expected_jd, abs=1e-9, rel=0)


def test_historical_same_day_display_remains(monkeypatch):
    monkeypatch.setattr(legacy, 'resolve_timezone', lambda lat, lon: 'America/Indiana/Indianapolis')
    result = legacy.resolve_birth('1975-11-22', '14:30', '', lat_override=0, lon_override=0)
    assert result[7] == '14:30 LT  →  19:30 UTC  (UTC-05:00  America/Indiana/Indianapolis)'


@pytest.mark.parametrize('zone,expected', [
    ('Asia/Kolkata', (2000, 1, 1, 6.5)),
    ('Pacific/Kiritimati', (1999, 12, 31, 22.0)),
])
def test_legacy_unknown_time_uses_local_noon(monkeypatch, zone, expected):
    monkeypatch.setattr(legacy, 'resolve_timezone', lambda lat, lon: zone)
    result = legacy.resolve_birth('2000-01-01', None, '', lat_override=0, lon_override=0)
    assert result[:4] == expected
    assert result[8] is False
    assert 'Time unknown' in result[7] and '12:00 noon' in result[7]
    assert legacy.julian_day(*result[:4]) == pytest.approx(swe.julday(*expected), abs=1e-9, rel=0)


@pytest.mark.parametrize('coords', [(0, 0), (0, 30), (-10, 0)])
def test_explicit_coordinates_are_resolved_without_geocoding(monkeypatch, coords):
    def unexpected_network():
        pytest.fail('explicit coordinates must bypass geocoding')
    monkeypatch.setattr(legacy, '_geo', unexpected_network)
    assert legacy.geocode_city('unrelated city', '', *coords) == (*coords, True)


def test_zero_coordinate_synastry_overlays_use_actual_julian_days(monkeypatch, capsys):
    monkeypatch.setattr(legacy, 'resolve_timezone', lambda lat, lon: 'Asia/Kolkata')
    import astroengine.houses as houses_mod
    original = houses_mod.house_cusps
    calls = []
    def recorded_houses(jd, lat, lon, system="placidus"):
        calls.append((jd, lat, lon))
        return original(jd, lat, lon, system)
    monkeypatch.setattr(houses_mod, 'house_cusps', recorded_houses)
    args = SimpleNamespace(date1='2000-01-01', time1='00:15', date2='2000-01-01',
                           time2='12:00', lat1=0, lon1=0, lat2=0, lon2=30,
                           city1=None, nation1=None, city2=None, nation2=None,
                           name1='A', name2='B')
    legacy.cmd_synastry(args)
    assert calls == [(swe.julday(1999, 12, 31, 18.75), 0, 0),
                     (swe.julday(2000, 1, 1, 6.5), 0, 30)]
    assert 'HOUSE OVERLAYS' in capsys.readouterr().out


@pytest.mark.parametrize('command', ['natal', 'geoastrology'])
def test_legacy_cli_offline_rollover(command):
    script = "import astrology_engine as e; e.resolve_timezone=lambda lat,lon:'Asia/Kolkata'; e.main()"
    # Imported main does not install the script's stdout wrapper; set child UTF-8.
    result = subprocess.run([sys.executable, '-X', 'utf8', '-c', script, command, '--date', '2000-01-01',
                             '--time', '00:15', '--lat', '0', '--lon', '0'],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert '1999-12-31 18:45 UTC' in result.stdout
    if command == 'natal':
        assert f'JD: {swe.julday(1999, 12, 31, 18.75):.4f}' in result.stdout
        assert '0.0000°N 0.0000°E' in result.stdout
