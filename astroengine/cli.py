"""Versioned JSON transport for computation services."""

import argparse
import json
import logging
import sys
from dataclasses import fields
from typing import Any

from .models import CalculationError, ChartRequest
from .rules import load_rules
from .service import capabilities, compute_chart

_LOG = logging.getLogger(__name__)


def add_chart_arguments(parser: argparse.ArgumentParser, suffix: str = "") -> None:
    rules = load_rules("profiles.json")
    parser.add_argument(f"--date{suffix}", required=True)
    parser.add_argument(f"--time{suffix}")
    parser.add_argument(f"--lat{suffix}", dest=f"latitude{suffix}", type=float, required=True)
    parser.add_argument(f"--lon{suffix}", dest=f"longitude{suffix}", type=float, required=True)
    parser.add_argument(f"--timezone{suffix}", required=True)
    if suffix:
        return
    add_profile_arguments(parser)


def add_profile_arguments(parser: argparse.ArgumentParser) -> None:
    rules = load_rules("profiles.json")
    parser.add_argument("--zodiac", choices=("tropical", "sidereal"), default=rules["defaults"]["zodiac"])
    parser.add_argument("--ayanamsa", choices=rules["ayanamsas"], default=rules["defaults"]["ayanamsa"])
    parser.add_argument("--house-system", choices=rules["houses"], default=rules["defaults"]["house_system"])
    parser.add_argument("--node-type", choices=rules["nodes"], default=rules["defaults"]["node_type"])
    parser.add_argument("--ephemeris-path")


def register_commands(subparsers: Any) -> None:
    chart = subparsers.add_parser("chart", help="Reproducible chart as JSON (explicit location/zone)")
    add_chart_arguments(chart)
    chart.set_defaults(modern_handler=lambda args: compute_chart(request_from_args(args)))
    from .vedic import compute_vedic
    vedic = subparsers.add_parser("vedic", help="Jyotisha D1, navagraha and nakshatras as JSON")
    add_chart_arguments(vedic)
    vedic.set_defaults(**load_rules("vedic.json")["defaults"],
                       modern_handler=lambda args: compute_vedic(request_from_args(args)))
    from .vargas import compute_vargas
    vargas = subparsers.add_parser("vargas", help="Sixteen named classical divisional charts")
    add_chart_arguments(vargas)
    vargas.add_argument("--divisions", type=int, nargs="+")
    vargas.set_defaults(**load_rules("vedic.json")["defaults"],
                        modern_handler=lambda args: compute_vargas(request_from_args(args), args.divisions))
    from .dashas import compute_dashas
    dashas = subparsers.add_parser("dashas", help="Vimshottari maha/antar timeline and birth balance")
    add_chart_arguments(dashas)
    dashas.add_argument("--years", type=float)
    dashas.add_argument("--year-model", choices=load_rules("timing.json")["year_models"])
    dashas.add_argument("--as-of", help="ISO timestamp with explicit UTC offset")
    dashas.set_defaults(**load_rules("vedic.json")["defaults"],
                        modern_handler=lambda args: compute_dashas(request_from_args(args), args.years, args.year_model, args.as_of))
    from .panchanga import compute_panchanga
    panchanga = subparsers.add_parser("panchanga", help="Instant panchanga angular elements and civil weekday")
    add_chart_arguments(panchanga)
    panchanga.set_defaults(**load_rules("vedic.json")["defaults"],
                          modern_handler=lambda args: compute_panchanga(request_from_args(args)))
    from .relationships import compute_relationship
    relationship = subparsers.add_parser("relationship", aliases=["synergy-json"],
                                         help="Synastry, overlays, composite and explainable synergy")
    add_chart_arguments(relationship, "1")
    add_chart_arguments(relationship, "2")
    add_profile_arguments(relationship)
    relationship.set_defaults(modern_handler=lambda args: compute_relationship(
        request_from_args(args, "1"), request_from_args(args, "2")))
    from .locations import compute_location
    location = subparsers.add_parser("location", help="Relocation and geometric angular lines at destination latitude")
    add_chart_arguments(location)
    location.add_argument("--query-lat", type=float, required=True)
    location.add_argument("--query-lon", type=float, required=True)
    location.set_defaults(modern_handler=lambda args: compute_location(
        request_from_args(args), args.query_lat, args.query_lon))
    discovery = subparsers.add_parser("capabilities", help="Technique availability and scope as JSON")
    discovery.set_defaults(modern_handler=lambda args: capabilities())


def request_from_args(args: argparse.Namespace, suffix: str = "") -> ChartRequest:
    values = {field.name: getattr(args, field.name + suffix)
              for field in fields(ChartRequest) if hasattr(args, field.name + suffix)}
    if suffix:
        for field in fields(ChartRequest):
            if field.name not in values and hasattr(args, field.name):
                values[field.name] = getattr(args, field.name)
    return ChartRequest(**values)


def run_command(args: argparse.Namespace) -> int:
    try:
        result = args.modern_handler(args)
        sys.stdout.write(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True) + "\n")
        return 0
    except (CalculationError, OSError, ValueError) as exc:
        _LOG.debug("Calculation failed", exc_info=True)
        sys.stderr.write(json.dumps({"schema_version": "1.0", "error": {
            "type": "calculation_error", "message": str(exc)}}) + "\n")
        return 2


def main() -> int:
    parser = argparse.ArgumentParser(prog="astroengine")
    register_commands(parser.add_subparsers(dest="cmd", required=True))
    return run_command(parser.parse_args())
