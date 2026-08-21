"""Canonical SysML-to-Python type mapping.

Single source of truth for mapping SysML types to Python types across all
generators (REQ-GEN-06). Replaces 5 divergent copies in modules.py,
entry_point.py, schemas.py, stencils.py, and registry.py.

One public function:
- map_sysml_type_to_python(): SysML type -> Python primitive ("float", "int", etc.)
"""

from sysml_codegen.core.type_mapping import (
    SYSML_TO_PYTHON,
    map_sysml_type_to_python,
)

__all__ = [
    "SYSML_TO_PYTHON",
    "map_sysml_type_to_python",
]
