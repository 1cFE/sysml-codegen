"""Canonical SysML-to-Python type mapping.

Single source of truth for mapping SysML types to Python types across all
generators (REQ-GEN-06). Replaces 5 divergent copies in modules.py,
entry_point.py, schemas.py, stencils.py, and registry.py.

Two public functions:
- map_sysml_type_to_python(): SysML type -> Python primitive ("float", "int", etc.)
- map_sysml_type_to_rootmodel_wrapper(): SysML type -> RootModel wrapper ("Float", "Int", etc.)
"""

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

PYTHON_TO_ROOTMODEL_WRAPPER: dict[str, str] = {
    "float": "Float",
    "int": "Int",
    "str": "String",
    "bool": "Bool",
}


def map_sysml_type_to_python(sysml_type: str) -> str:
    """Map a SysML type to a Python primitive type string.

    Handles both bare forms ("Real") and prefixed forms ("ScalarValues::Real").
    Unknown types pass through unchanged with a warning.

    Args:
        sysml_type: SysML type reference (e.g., "Real", "ScalarValues::Integer")

    Returns:
        Python type string (e.g., "float", "int", "bool", "str")
    """
    result = SYSML_TO_PYTHON.get(sysml_type)
    if result is not None:
        return result
    log.warning(
        "Unknown SysML type %r — passing through unchanged. "
        "Consider adding explicit mapping.",
        sysml_type,
    )
    return sysml_type


def map_sysml_type_to_rootmodel_wrapper(sysml_type: str) -> str:
    """Map a SysML type to a RootModel wrapper type name.

    First resolves to Python primitive via map_sysml_type_to_python(),
    then maps to the RootModel wrapper name (Float, Int, Bool, String).
    Unknown types pass through unchanged.

    Args:
        sysml_type: SysML type reference (e.g., "Real", "ScalarValues::Integer")

    Returns:
        RootModel wrapper type name (e.g., "Float", "Int", "Bool", "String")
    """
    python_type = map_sysml_type_to_python(sysml_type)
    return PYTHON_TO_ROOTMODEL_WRAPPER.get(python_type, python_type)


__all__ = [
    "SYSML_TO_PYTHON",
    "PYTHON_TO_ROOTMODEL_WRAPPER",
    "map_sysml_type_to_python",
    "map_sysml_type_to_rootmodel_wrapper",
]
