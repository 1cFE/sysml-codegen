"""Core shared utilities for sysml-codegen.

This module contains utilities and types that are used across multiple layers
(extraction, analysis, resolution, generation) without introducing circular
dependencies.

Layer dependencies should follow:
    extraction → core
    analysis → extraction, core
    resolution → extraction, analysis, core
    generation → extraction, resolution, analysis, core
    cli → all layers

By placing shared utilities here, we avoid layer violations like extraction
importing from analysis or analysis importing from resolution.
"""

from sysml_codegen.core.identifier_types import (
    ElementQualifiedName,
    ModuleType,
    PythonModulePath,
    SysMLQualifiedName,
    derive_module_type,
    derive_python_path,
)
from sysml_codegen.core.models import (
    BindingResolution,
    BindingResolutionType,
    ChannelAlias,
)
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
    # identifier_types
    "ElementQualifiedName",
    "ModuleType",
    "PythonModulePath",
    "SysMLQualifiedName",
    "derive_module_type",
    "derive_python_path",
    # models
    "BindingResolution",
    "BindingResolutionType",
    "ChannelAlias",
    # qualified_names
    "build_element_qualified_name",
    "build_parameter_qualified_name",
    "extract_simple_name",
    "get_channel_name",
    "get_module_name",
    "python_to_sysml_qualified_name",
    "sanitize_name",
    "sysml_to_python_qualified_name",
]
