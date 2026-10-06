"""Relocation and geometric angular-line solutions at an exact latitude."""

import math
from dataclasses import replace
from datetime import datetime
from typing import Any

from .aspects import signed_arc
from .ephemeris import equatorial_positions
from .inputs import validate_coordinates
from .models import CalculationError, ChartRequest
from .rules import load_rules
from .service import compute_chart


def _earth_longitude(value: float) -> float:
    return (value + 180) % 360 - 180


def angular_lines(right_ascension: float, declination: float, sidereal_degrees: float,
                  latitude: float) -> dict[str, Any]:
    validate_coordinates(latitude, 0)
    if not all(math.isfinite(value) for value in (right_ascension, declination, sidereal_degrees)) or abs(declination) > 90:
        raise CalculationError('Equatorial coordinates must be finite with declination in [-90,90]')
    mc = _earth_longitude(right_ascension - sidereal_degrees)
    result = {'MC': mc, 'IC': _earth_longitude(mc + 180), 'ASC': None, 'DSC': None}
    phi, delta = math.radians(latitude), math.radians(declination)
    constant = math.sin(phi) * math.sin(delta)
    amplitude = math.cos(phi) * math.cos(delta)
    tolerance = load_rules('locations.json')['geometric_tolerance']
    if abs(amplitude) <= tolerance:
        result['horizon_status'] = ('on-horizon-all-longitudes' if abs(constant) <= tolerance
                                    else 'always-above' if constant > 0 else 'always-below')
        return result
    cosine = -constant / amplitude
    if abs(cosine) > 1 + tolerance:
        result['horizon_status'] = 'always-above' if constant > 0 else 'always-below'
        return result
    angle = math.degrees(math.acos(max(-1, min(1, cosine))))
    result.update({'ASC': _earth_longitude(mc - angle), 'DSC': _earth_longitude(mc + angle),
                   'horizon_status': 'grazing' if abs(abs(cosine) - 1) <= tolerance else 'crossing'})
    return result


def compute_location(request: ChartRequest, latitude: float, longitude: float) -> dict[str, Any]:
    validate_coordinates(latitude, longitude)
    if request.time is None:
        raise CalculationError('Location astrology requires a known birth time')
    natal = compute_chart(request)
    utc = datetime.fromisoformat(natal['utc'])
    relocated_request = replace(request, date=utc.date().isoformat(), time=utc.time().isoformat(),
                                timezone='UTC', latitude=latitude, longitude=longitude)
    relocated = compute_chart(relocated_request)
    equatorial = equatorial_positions(natal['julian_day_ut'], request)
    lines = {}
    for body, position in equatorial['positions'].items():
        solved = angular_lines(position['right_ascension'], position['declination'],
                               equatorial['greenwich_sidereal_degrees'], latitude)
        residuals = {angle: signed_arc(value, longitude) if value is not None else None
                     for angle, value in solved.items() if angle != 'horizon_status'}
        lines[body] = {'equatorial': position, 'line_longitudes': solved,
                       'query_longitude_residuals': residuals}
    rules = load_rules('locations.json')
    return {'schema_version': '1.0', 'kind': 'location', 'natal': natal, 'relocated': relocated,
            'query': {'latitude': latitude, 'longitude': longitude}, 'lines': lines,
            'method': rules['method'], 'residual_units': rules['residual_units'],
            'greenwich_sidereal_degrees': equatorial['greenwich_sidereal_degrees'],
            'limitations': ['No refraction, geodesic distance, parans, local-space or map sampling']}
