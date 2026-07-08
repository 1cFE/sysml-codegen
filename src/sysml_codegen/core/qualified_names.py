"""Compatibility surface for qualified name construction.

Shared SysML-general name helpers live in ``agentic_mbse.sysml.qualified_names``.
Codegen-specific ADR-003 builders stay local in this module.

All sysml-codegen identifier construction MUST use these functions.
Do NOT construct qualified names via inline f-strings.
"""

from agentic_mbse.sysml.qualified_names import (  # type: ignore[import-untyped]
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


def owning_part_leaf(owning_part_qn: str) -> str:
    """Return the leaf (last segment) of a PartDef/PartUsage qualified name.

    Handles both separator forms an ``owning_part_qn`` can carry: SysML ``::``
    (e.g. ``"AttrExprProbeDesign::probe_design"``) and Python ``__`` (e.g.
    ``"SolarBatteryLibrary__Solar_Array"``). A ``::``-form QN splits on ``::``
    only — a ``__`` inside a sanitized segment must not be mistaken for the
    separator, which is why this is not ``split`` on both at once. Unlike
    ``extract_simple_name`` it never splits on ``.``, so a dotted nested scope
    stays intact where the caller passes one.

    Single rule for the three sites that derive an instance scope from an
    ``owning_part_qn``: the two EXPOSE_PURE alias registrations in
    ``output_registry_builder`` and ``_build_output_aliases`` — so shape A and
    shape B can never drift on a ``::``-form QN.
    """
    if "::" in owning_part_qn:
        return owning_part_qn.rsplit("::", 1)[-1]
    return owning_part_qn.split("__")[-1]


__all__ = [
    "sanitize_name",
    "build_element_qualified_name",
    "build_parameter_qualified_name",
    "get_module_name",
    "get_channel_name",
    "sysml_to_python_qualified_name",
    "sanitize_qualified_name",
    "python_to_sysml_qualified_name",
    "extract_simple_name",
    "owning_part_leaf",
]
