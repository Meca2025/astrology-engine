"""All nominal boundaries and their neighboring representable floats."""

import math

from astroengine.partitions import uniform_partition
from astroengine.vedic import nakshatra
from astroengine.vargas import varga_position
from astroengine.rules import load_rules


def test_all_pada_exact_boundaries_and_adjacent_float():
    for index in range(108):
        boundary = index * 360 / 108
        found = nakshatra(boundary)
        assert found['index'] == index // 4 + 1
        assert found['pada'] == index % 4 + 1
        if index:
            previous = nakshatra(math.nextafter(boundary, -math.inf))
            assert previous['index'] == (index - 1) // 4 + 1
            assert previous['pada'] == (index - 1) % 4 + 1
        following = nakshatra(math.nextafter(boundary, math.inf))
        assert following['index'] == index // 4 + 1
        assert following['pada'] == index % 4 + 1


def test_equal_varga_boundaries_across_all_signs():
    for division, rule in load_rules('vargas.json')['divisions'].items():
        if rule['mode'] == 'unequal-parity':
            continue
        count = int(division)
        for sign in range(12):
            for index in range(count):
                boundary = sign * 30 + index * 30 / count
                found = varga_position(boundary, count)
                assert found['source_subdivision'] == index + 1
                if index:
                    previous = varga_position(math.nextafter(boundary, -math.inf), count)
                    assert previous['source_subdivision'] == index


def test_all_tithi_karana_and_yoga_partition_boundaries():
    for count in (30, 60, 27):
        for index in range(count):
            boundary = index * 360 / count
            assert uniform_partition(boundary, count) == (index, 0)
            if index:
                assert uniform_partition(math.nextafter(boundary, -math.inf), count)[0] == index - 1
