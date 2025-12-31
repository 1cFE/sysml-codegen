"""Identifier type transformations - re-exported from core.

This module is kept for backward compatibility.
New code should import from sysml_codegen.core.identifier_types.
"""

from sysml_codegen.core.identifier_types import (
    ElementQualifiedName,
    ModuleType,
    PythonModulePath,
    SysMLQualifiedName,
    derive_module_type,
    derive_python_path,
)

__all__ = [
    "SysMLQualifiedName",
    "ModuleType",
    "PythonModulePath",
    "ElementQualifiedName",
    "derive_module_type",
    "derive_python_path",
]
