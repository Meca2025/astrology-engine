"""Published worked sign placements independent of implementation tables."""

import json
import subprocess
import sys

import pytest

from astroengine import CalculationError, ChartRequest
from astroengine.vargas import compute_vargas, varga_position


@pytest.mark.parametrize(('division', 'longitude', 'expected'), [
    (3, 63, 'Gemini'), (3, 79, 'Libra'), (3, 81, 'Aquarius'),
    (4, 33, 'Taurus'), (4, 44, 'Leo'), (4, 53, 'Aquarius'),
    (7, 70, 'Leo'), (7, 169, 'Cancer'),
    (9, 71, 'Capricorn'), (9, 229, 'Sagittarius'),
    (10, 70, 'Virgo'), (10, 229, 'Capricorn'),
    (12, 71, 'Libra'), (12, 229, 'Gemini'),
    (16, 71, 'Taurus'), (16, 229, 'Gemini'),
    (20, 71, 'Pisces'), (20, 229, 'Sagittarius'),
    (24, 71, 'Aries'), (24, 229, 'Libra'),
    (27, 71, 'Cancer'), (27, 229, 'Gemini'),
    (40, 71, 'Gemini'), (40, 229, 'Scorpio'),
    (45, 71, 'Aries'), (45, 229, 'Sagittarius'),
    (60, 222 + 58 / 60, 'Sagittarius'),
])
# D27 Example 23 says Leo, but its rule gives the 10th from Libra = Cancer.
# Expected value follows the independently counted rule, recorded in source notes.
def test_rao_published_examples(division, longitude, expected):
    assert varga_position(longitude, division)['sign'] == expected


@pytest.mark.parametrize(('longitude', 'expected'), [
    (0, 'Leo'), (14.999, 'Leo'), (15, 'Cancer'), (30, 'Cancer'), (45, 'Leo'),
])
def test_hora_is_not_second_harmonic(longitude, expected):
    assert varga_position(longitude, 2)['sign'] == expected


@pytest.mark.parametrize(('longitude', 'expected'), [
    (0, 'Aries'), (5, 'Aquarius'), (10, 'Sagittarius'), (18, 'Gemini'), (25, 'Libra'),
    (30, 'Taurus'), (35, 'Virgo'), (42, 'Pisces'), (50, 'Capricorn'), (55, 'Scorpio'),
])
def test_unequal_trimsamsa_boundaries(longitude, expected):
    assert varga_position(longitude, 30)['sign'] == expected


def test_entire_classical_set_and_missing_lagna():
    request = ChartRequest('2000-01-01', 0, 0, 'UTC', zodiac='sidereal', house_system='whole-sign')
    report = compute_vargas(request)
    assert len(report['divisions']) == 20  # 16 classical + D5/D6/D8/D11 (V01)
    for chart in report['divisions'].values():
        assert chart['lagna'] is None
        assert len(chart['placements']) == 9
    with pytest.raises(CalculationError, match='Unsupported'):
        varga_position(0, 150)
    with pytest.raises(CalculationError):
        varga_position(float('nan'), 9)
    with pytest.raises(CalculationError):
        compute_vargas(request, [])


def test_vargas_cli_is_wired():
    result = subprocess.run([sys.executable, '-m', 'astroengine', 'vargas',
                             '--date', '2000-01-01', '--lat', '0', '--lon', '0',
                             '--timezone', 'UTC', '--divisions', '9', '30'],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert set(json.loads(result.stdout)['divisions']) == {'D9', 'D30'}
