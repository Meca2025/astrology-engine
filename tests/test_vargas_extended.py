"""V01: extended divisional charts D5/D6/D8/D11.

Fixtures are hand-worked from the documented JHora Traditional rules:
- D5: 6-degree parts; odd signs use [Aries, Aquarius, Sagittarius, Gemini, Libra],
  even signs use [Taurus, Virgo, Pisces, Capricorn, Scorpio] (0-indexed).
- D6: 5-degree parts; odd signs count from Aries, even from Libra.
- D8: 3.75-degree parts; movable from Aries, fixed from Sagittarius, dual from Leo.
- D11: 30/11-degree parts; target = (sign*11 + part) mod 12 (0-indexed signs).
"""

import pytest

from astroengine.vargas import compute_vargas, varga_position
from astroengine.models import CalculationError, ChartRequest


CASES = [
    # (division, longitude, expected sign, note)
    (5, 261.0, 'Gemini', '21 Sagittarius, odd, 4th part -> Gemini (hora-prakash example)'),
    (5, 40.0, 'Virgo', '10 Taurus, even, 2nd part -> Virgo'),
    (5, 0.0, 'Aries', '0 Aries, odd, 1st part -> Aries'),
    (5, 359.9, 'Scorpio', '29.9 Pisces, even, 5th part -> Scorpio'),
    (6, 12.0, 'Gemini', '12 Aries, odd from Aries, 3rd part -> Gemini'),
    (6, 42.0, 'Sagittarius', '12 Taurus, even from Libra, 3rd part -> Sagittarius'),
    (6, 120.0, 'Aries', '0 Leo, odd from Aries, 1st part -> Aries'),
    (8, 10.0, 'Gemini', '10 Aries movable from Aries, 3rd part -> Gemini'),
    (8, 40.0, 'Aquarius', '10 Taurus fixed from Sagittarius, 3rd part -> Aquarius'),
    (8, 70.0, 'Libra', '10 Gemini dual from Leo, 3rd part -> Libra'),
    (11, 10.0, 'Cancer', '10 Aries: (0*11+3)%12 -> Cancer'),
    (11, 30.0, 'Pisces', '0 Taurus: (1*11+0)%12 -> Pisces'),
    (11, 359.0, 'Pisces', '29 Pisces: (11*11+10)%12 -> Pisces'),
]


@pytest.mark.parametrize('division,longitude,expected,note', CASES)
def test_extended_varga_positions(division, longitude, expected, note):
    assert varga_position(longitude, division)['sign'] == expected, note


def test_extended_divisions_in_compute():
    request = ChartRequest(date='1972-09-01', time='08:18', latitude=42.8142,
                           longitude=-73.9396, timezone='America/New_York',
                           zodiac='sidereal', house_system='whole-sign')
    result = compute_vargas(request, divisions=[5, 6, 8, 11])
    assert set(result['divisions']) == {'D5', 'D6', 'D8', 'D11'}
    assert result['divisions']['D5']['name'] == 'Panchamsha'
    assert result['divisions']['D6']['name'] == 'Shashthamsha'
    assert result['divisions']['D8']['name'] == 'Ashtamsha'
    assert result['divisions']['D11']['name'] == 'Rudramsha'
    assert result['rule_version'] == '1.1'


def test_default_includes_extended():
    request = ChartRequest(date='1972-09-01', time='08:18', latitude=42.8142,
                           longitude=-73.9396, timezone='America/New_York',
                           zodiac='sidereal', house_system='whole-sign')
    result = compute_vargas(request)
    assert len(result['divisions']) == 20


def test_unsupported_division_still_rejected():
    with pytest.raises(CalculationError):
        varga_position(10.0, 13)
