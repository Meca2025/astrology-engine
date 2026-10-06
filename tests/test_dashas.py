"""Independent period balances, chronology and subperiod clipping."""

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta

import pytest

from astroengine import CalculationError
from astroengine.dashas import active_period, vimshottari_timeline

BIRTH = datetime(2000, 1, 1, tzinfo=UTC)


def test_published_example_50_balance():
    timeline = vimshottari_timeline(BIRTH, 302 + 23 / 60, 120, 360)
    assert timeline['birth_nakshatra']['name'] == 'Dhanishtha'
    assert timeline['balance_at_birth_years'] == pytest.approx(2.24875)
    assert timeline['mahadasas'][0]['lord'] == 'Mars'
    end = datetime.fromisoformat(timeline['mahadasas'][0]['end'])
    assert (end - BIRTH).total_seconds() / 86400 == pytest.approx(809.55)


def test_full_cycle_and_antars_sum():
    result = vimshottari_timeline(BIRTH, 0, 120, 360)
    periods = result['mahadasas']
    assert [p['lord'] for p in periods] == ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
    assert sum(p['full_duration_days'] for p in periods) == 120 * 360
    for period in periods:
        assert sum(a['full_duration_days'] for a in period['antardashas']) == pytest.approx(period['full_duration_days'])
        assert period['antardashas'][0]['lord'] == period['lord']
        assert period['antardashas'][-1]['end'] == period['end']


def test_antars_do_not_restart_at_birth():
    result = vimshottari_timeline(BIRTH, 20 / 3, 2, 360)  # half of Ashwini elapsed
    first = result['mahadasas'][0]['antardashas'][0]
    assert first['lord'] == 'Rahu'  # Ketu/Venus/Sun/Moon/Mars already elapsed
    assert first['start'] == BIRTH.isoformat()
    assert first['full_start'] < first['start']
    assert first['clipped']


def test_exact_boundary_belongs_to_next_period():
    result = vimshottari_timeline(BIRTH, 0, 120, 360)
    boundary = datetime.fromisoformat(result['mahadasas'][0]['end'])
    assert active_period(result, boundary)['mahadasa'] == 'Venus'
    assert active_period(result, boundary - timedelta(microseconds=1))['mahadasa'] == 'Ketu'
    assert active_period(result, datetime.fromisoformat(result['window_end'])) is None


@pytest.mark.parametrize('years', [0, -1, float('nan'), float('inf')])
def test_invalid_horizon(years):
    with pytest.raises(CalculationError):
        vimshottari_timeline(BIRTH, 0, years, 360)


def test_cli_year_model_and_active():
    result = subprocess.run([sys.executable, '-m', 'astroengine', 'dashas',
                             '--date', '2000-01-01', '--time', '12:00', '--lat', '0',
                             '--lon', '0', '--timezone', 'UTC', '--years', '10',
                             '--year-model', 'savana', '--as-of', '2001-01-01T00:00:00Z'],
                            capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['timeline']['year_days'] == 360
    assert report['active'] is not None
