"""Portable agent tool routing with data-owned request schemas."""

import math
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .models import CalculationError, ChartRequest
from .rules import load_rules


def tool_catalog() -> dict[str, Any]:
    return load_rules('tool_schemas.json')


def _validate(parameters: Any, schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    error = next(validator.iter_errors(parameters), None)
    if error is not None:
        raise CalculationError(f'Invalid tool parameters: {error.message}')
    _reject_nonfinite(parameters)


def _reject_nonfinite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise CalculationError('Tool parameters cannot contain non-finite numbers')
    if isinstance(value, dict):
        for item in value.values():
            _reject_nonfinite(item)
    if isinstance(value, list):
        for item in value:
            _reject_nonfinite(item)


def _dispatch(name: str, parameters: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    from .service import compute_chart
    from .vedic import compute_vedic
    from .vargas import compute_vargas
    from .dashas import compute_dashas
    from .panchanga import compute_panchanga
    from .relationships import compute_relationship
    from .locations import compute_location
    from .western import compute_western
    if name == 'relationship':
        return compute_relationship(ChartRequest(**parameters['first']), ChartRequest(**parameters['second']))
    request = ChartRequest(**{**defaults, **parameters['request']})
    options = {key: value for key, value in parameters.items() if key != 'request'}
    services = {'chart': compute_chart, 'vedic': compute_vedic, 'vargas': compute_vargas,
                'dashas': compute_dashas, 'panchanga': compute_panchanga,
                'location': compute_location, 'western': compute_western}
    return services[name](request, **options)


def run_tool(name: str, parameters: dict[str, Any]) -> dict[str, Any]:
    tool = next((item for item in tool_catalog()['tools'] if item['name'] == name), None)
    if tool is None:
        raise CalculationError(f'Unsupported tool: {name}')
    available = load_rules('capabilities.json')['capabilities']
    if not any(item['id'] == tool['capability_id'] and item['status'] == 'available' for item in available):
        raise CalculationError(f'Tool is not available: {name}')
    _validate(parameters, tool['input_schema'])
    return _dispatch(name, parameters, tool['request_defaults'])
