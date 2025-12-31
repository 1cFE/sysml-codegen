"""Qualified name utilities - re-exported from core.

This module is kept for backward compatibility.
New code should import from sysml_codegen.core.qualified_names.
"""

from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    build_parameter_qualified_name,
    extract_simple_name,
    get_channel_name,
    get_module_name,
    python_to_sysml_qualified_name,
    sanitize_name,
    sysml_to_python_qualified_name,
)

__all__ = [
    "sanitize_name",
    "build_element_qualified_name",
    "build_parameter_qualified_name",
    "get_module_name",
    "get_channel_name",
    "sysml_to_python_qualified_name",
    "python_to_sysml_qualified_name",
    "extract_simple_name",
]
