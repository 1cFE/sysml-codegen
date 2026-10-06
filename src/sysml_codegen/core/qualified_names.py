"""Compatibility surface for qualified name construction.

Shared SysML-general name helpers live in ``agentic_mbse.sysml.qualified_names``.
Codegen-specific ADR-003 builders stay local in this module.

All sysml-codegen identifier construction MUST use these functions.
Do NOT construct qualified names via inline f-strings.
"""

from agentic_mbse.sysml.qualified_names import (
    build_element_qualified_name,
    extract_simple_name,
    python_to_sysml_qualified_name,
    sanitize_name,
    sanitize_qualified_name,
    sysml_to_python_qualified_name,
)


def build_parameter_qualified_name(usage_qualified_name: str, param_name: str) -> str:
    """Build qualified name for a parameter scoped to a usage."""
    return f"{usage_qualified_name}__{param_name}"


def get_module_name(usage_qualified_name: str) -> str:
    """Get YAML module name from usage qualified name."""
    return usage_qualified_name.lower()


def get_channel_name(usage_qualified_name: str, output_attr_name: str) -> str:
    """Get output channel name (which is just the output's PQN)."""
    return f"{usage_qualified_name}__{output_attr_name}"


def params_field_name(entry_point_key: str) -> str:
    """The Python attribute name a params key is carried by.

    A modelled finite multiplicity mints keys carrying an occurrence index
    (``…__caster[0]__load_rating``). The key is the JSON surface and does not
    move, but a Python class body cannot declare a field by that name, so the
    generated schema declares the sanitized name and keeps the exact key as the
    field's alias. Everything that reads the field through the *package* — the
    pipeline YAML's field path — must use this name; everything that reads the
    *JSON* keeps using the key.

    Keys without an index are already identifiers and pass through unchanged, so
    every package that has no multiplicity is byte-identical to before.
    """
    return entry_point_key.replace("[", "_").replace("]", "")


__all__ = [
    "sanitize_name",
    "params_field_name",
    "build_element_qualified_name",
    "build_parameter_qualified_name",
    "get_module_name",
    "get_channel_name",
    "sysml_to_python_qualified_name",
    "sanitize_qualified_name",
    "python_to_sysml_qualified_name",
    "extract_simple_name",
]
