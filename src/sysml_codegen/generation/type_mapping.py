"""Canonical SysML-to-Python type mapping.

Single source of truth for mapping SysML types to Python types across all
generators (REQ-GEN-06). Replaces 5 divergent copies in modules.py,
entry_point.py, schemas.py, stencils.py, and registry.py.

One public function:
- map_sysml_type_to_python(): SysML type -> Python primitive ("float", "int", etc.)
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


__all__ = [
    "SYSML_TO_PYTHON",
    "map_sysml_type_to_python",
]
