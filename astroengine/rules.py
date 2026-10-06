"""Load fresh rule snapshots from source or installed package resources."""

import json
from importlib.resources import files
from pathlib import Path
from typing import Any


def load_rules(name: str) -> dict[str, Any]:
    """Internal resource names are never taken directly from user input."""
    source = Path(__file__).resolve().parent.parent / "data" / name
    if source.is_file():
        return json.loads(source.read_text(encoding="utf-8"))
    resource = files("astroengine_data").joinpath(name)
    return json.loads(resource.read_text(encoding="utf-8"))
