"""Single source of truth for qualified name construction.

All identifier construction MUST use these functions.
Do NOT construct qualified names via inline f-strings.

Per ADR-003: Signal Identifier Architecture, this module provides
the authoritative implementation for building qualified names.
"""

import re


def sanitize_name(name: str | None) -> str:
    """Sanitize SysML name for Python.

    Args:
        name: Raw SysML name (may contain quotes, spaces, reserved words,
              special characters like &, $, @, -)

    Returns:
        Python-safe identifier string
    """
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    # Replace non-alphanumeric, non-underscore chars with underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Collapse runs of underscores (safe: operates on individual segments,
    # not qualified names — the __ ADR-003 separator is applied later)
    name = re.sub(r"_+", "_", name)
    # Strip leading/trailing underscores
    name = name.strip("_") or "unnamed"
    if name in {"class", "def", "import", "from", "return", "yield"}:
        name = f"{name}_"
    return name


def build_element_qualified_name(elem: object, use_double_underscore: bool = True) -> str:
    """Build fully qualified name for any SysML element.

    Traverses AST ownership hierarchy to build full path.
    Uses `__` (double underscore) as hierarchy separator.

    Args:
        elem: SysML element to build qualified name for
        use_double_underscore: If True, use `__` separator; if False, use `::`

    Returns:
        Fully qualified name (e.g., "CATFMFEPhysics__catf_physics__net_electric")
    """
    separator = "__" if use_double_underscore else "::"
    chain = _build_owner_chain_with_packages(elem)
    elem_name = getattr(elem, "name", None)

    if elem_name:
        elem_name = sanitize_name(elem_name)
        if chain:
            return separator.join(chain + [elem_name])
        return elem_name

    return ""


def _build_owner_chain_with_packages(elem: object) -> list[str]:
    """Build ownership chain including packages for element."""
    chain: list[str] = []
    current = elem

    while hasattr(current, "owner") and current.owner:
        owner = current.owner

        if hasattr(owner, "owning_related_element"):
            owning_elem = owner.owning_related_element
            if owning_elem and hasattr(owning_elem, "name") and owning_elem.name:
                chain.insert(0, sanitize_name(owning_elem.name))
        elif hasattr(owner, "name") and owner.name:
            chain.insert(0, sanitize_name(owner.name))

        current = owner

        if len(chain) >= 50:
            break

    return chain


def build_parameter_qualified_name(usage_qualified_name: str, param_name: str) -> str:
    """Build qualified name for a parameter scoped to a usage."""
    return f"{usage_qualified_name}__{param_name}"


def get_module_name(usage_qualified_name: str) -> str:
    """Get YAML module name from usage qualified name."""
    return usage_qualified_name.lower()


def get_channel_name(usage_qualified_name: str, output_attr_name: str) -> str:
    """Get output channel name (which is just the output's PQN)."""
    return f"{usage_qualified_name}__{output_attr_name}"


def sysml_to_python_qualified_name(sysml_qname: str) -> str:
    """Convert SysML qualified name ('::' separator) to Python-safe ('__' separator)."""
    return sysml_qname.replace("::", "__")


def python_to_sysml_qualified_name(python_qname: str) -> str:
    """Convert Python-safe qualified name ('__' separator) to SysML ('::' separator)."""
    return python_qname.replace("__", "::")


def extract_simple_name(qualified_path: str) -> str:
    """Extract the simple name from a qualified path."""
    if "::" in qualified_path:
        return qualified_path.split("::")[-1]
    if "__" in qualified_path:
        return qualified_path.split("__")[-1]
    if "." in qualified_path:
        return qualified_path.split(".")[-1]
    return qualified_path


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
