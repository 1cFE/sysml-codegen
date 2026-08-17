"""One canonical SysML scalar-to-Python type table."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

SYSML_TO_PYTHON: dict[str, str] = {
    "Real": "float",
    "ScalarValues::Real": "float",
    "Integer": "int",
    "ScalarValues::Integer": "int",
    "String": "str",
    "ScalarValues::String": "str",
    "Boolean": "bool",
    "ScalarValues::Boolean": "bool",
}


def map_sysml_type_to_python(sysml_type: str) -> str:
    """Map the established bare or qualified spelling for legacy consumers."""
    result = SYSML_TO_PYTHON.get(sysml_type)
    if result is not None:
        return result
    log.warning(
        "Unknown SysML type %r — passing through unchanged. "
        "Consider adding explicit mapping.",
        sysml_type,
    )
    return sysml_type


__all__ = ["SYSML_TO_PYTHON", "map_sysml_type_to_python"]
