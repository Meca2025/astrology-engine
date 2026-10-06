"""Sólrún's scrutiny of the full aspect spectrum.

Every obscure aspect fires at exact separation; the orb boundary is
respected; the family filter selects only its family.
"""

import sys
import pytest

sys.path.insert(0, "/home/hatch/workspace/astrology-engine")
import astrology_engine as ae  # noqa: E402

OBSCURE = {
    "Biseptile": 102.86, "Triseptile": 154.29,
    "Novile": 40.0, "Binovile": 80.0, "Quadnovile": 160.0,
    "Decile": 36.0, "Undecile": 32.73, "Tredecile": 108.0,
    "Quindecile": 165.0, "Vigintile": 18.0,
}


def _positions(separation):
    return {
        "Sun": {"longitude": 0.0, "speed": 1.0},
        "Mars": {"longitude": separation % 360.0, "speed": 0.5},
    }


@pytest.mark.parametrize("name,angle", sorted(OBSCURE.items()))
def test_obscure_aspect_fires_at_exact(name, angle):
    hits = ae.calc_aspects(_positions(angle))
    names = [h[2] for h in hits]
    assert name in names, f"{name} not found in {names}"


def test_orb_boundary_respected():
    # Vigintile orb is 1.5 (luminary) — 1.6° off must not fire
    hits = ae.calc_aspects(_positions(18.0 + 1.6))
    assert "Vigintile" not in [h[2] for h in hits]
    # non-luminary pair orb is 1.0 — 1.1° off must not fire
    pos = {"Mars": {"longitude": 0.0, "speed": 0.5},
           "Venus": {"longitude": 41.1, "speed": 1.0}}
    hits = ae.calc_aspects(pos)
    assert "Novile" not in [h[2] for h in hits]


def test_family_filter():
    pos = _positions(40.0)  # Novile
    assert {h[2] for h in ae.calc_aspects(pos, families={"major"})} == set()
    assert "Novile" in {h[2] for h in
                        ae.calc_aspects(pos, families={"obscure"})}
    assert "Novile" in {h[2] for h in
                        ae.calc_aspects(pos, families={"novile"})}
    assert "Novile" not in {h[2] for h in
                            ae.calc_aspects(pos, families={"septile"})}


def test_major_minor_untouched():
    pos = _positions(90.0)  # Square
    assert "Square" in {h[2] for h in ae.calc_aspects(pos)}
    assert "Square" in {h[2] for h in
                        ae.calc_aspects(pos, families={"major"})}
    assert ae.ASPECT_FAMILIES["Square"] == "major"
    assert ae.ASPECT_FAMILIES["Quincunx"] == "minor"


def test_western_json_mirror():
    import json
    d = json.load(open("/home/hatch/workspace/astrology-engine/data/western.json"))
    names = {a["name"] for a in d["aspects"]}
    for name in OBSCURE:
        assert name in names, name
    # new weights are neutral so synergy scoring does not shift
    assert sum(a["weight"] for a in d["aspects"]
               if a["name"] in OBSCURE) == 0
