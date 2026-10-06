"""Sólrún's scrutiny of the chart wheel."""

import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
from astroengine.wheel import wheel_svg, _assign_rings  # noqa: E402


def _fixture():
    planets = [
        {"name": "Sun", "glyph": "☉", "longitude": 159.0},
        {"name": "Moon", "glyph": "☽", "longitude": 58.5},
        {"name": "Mars", "glyph": "♂", "longitude": 160.2},
    ]
    cusps = [181.0, 211.0, 241.0, 271.0, 301.0, 331.0,
             1.0, 31.0, 61.0, 91.0, 121.0, 151.0]
    aspects = [
        {"a": "Sun", "b": "Moon", "kind": "trine"},
        {"a": "Sun", "b": "Mars", "kind": "conjunction"},
    ]
    meta = {"title": "Seeker", "subtitle": "1972-09-01",
            "asc": 181.0, "mc": 91.0}
    return planets, cusps, aspects, meta


def test_valid_xml():
    svg = wheel_svg(*_fixture())
    ET.fromstring(svg)  # raises if malformed


def test_planet_glyphs_present():
    svg = wheel_svg(*_fixture())
    for glyph in ("☉", "☽", "♂"):
        assert glyph in svg


def test_aspect_lines_match():
    planets, cusps, aspects, meta = _fixture()
    svg = wheel_svg(planets, cusps, aspects, meta)
    assert svg.count('stroke="#3e9bff"') == 1  # trine
    assert svg.count('stroke="#f5f2e8"') == 1  # conjunction


def test_deterministic():
    assert wheel_svg(*_fixture()) == wheel_svg(*_fixture())


def test_empty_aspects_valid():
    planets, cusps, _, meta = _fixture()
    svg = wheel_svg(planets, cusps, [], meta)
    ET.fromstring(svg)
    assert 'opacity="0.85"' not in svg


def test_meta_escaping():
    planets, cusps, aspects, _ = _fixture()
    svg = wheel_svg(planets, cusps, aspects,
                    {"title": "A & B <C>", "subtitle": ""})
    assert "A &amp; B &lt;C&gt;" in svg
    assert "<C>" not in svg


def test_asc_at_nine_oclock():
    svg = wheel_svg(*_fixture())
    m = re.search(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>ASC</text>', svg)
    assert m, "ASC label missing"
    assert float(m.group(1)) < 150  # left half of the 600-wide wheel


def test_houses_numbered():
    svg = wheel_svg(*_fixture())
    for n in range(1, 13):
        assert f">{n}</text>" in svg


def test_unknown_aspect_kind_gray_and_skipped_bodies():
    planets, cusps, _, meta = _fixture()
    svg = wheel_svg(planets, cusps, [
        {"a": "Sun", "b": "Moon", "kind": "quindecile"},
        {"a": "Sun", "b": "Ceres", "kind": "trine"},  # not on wheel
    ], meta)
    assert svg.count('stroke="#8a8f9e"') == 1
    assert svg.count('stroke="#3e9bff"') == 0
    ET.fromstring(svg)


def test_no_houses_still_renders():
    planets, _, aspects, meta = _fixture()
    svg = wheel_svg(planets, [], aspects, {"title": "No houses"})
    ET.fromstring(svg)


def test_assign_rings_no_reconflict():
    # Sólrún D1: three planets inside 6° must all land on distinct rings
    assert _assign_rings([0.0, 3.0, 5.0]) == [140.0, 116.0, 164.0]
    assert _assign_rings([0.0, 90.0, 180.0]) == [140.0, 140.0, 140.0]
    # wraparound adjacency also conflicts
    assert _assign_rings([359.0, 1.0]) == [140.0, 116.0]
