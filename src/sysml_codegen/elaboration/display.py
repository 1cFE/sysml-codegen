"""Display-only rendering for exact elaboration identities."""

from sysml_codegen.core.qualified_names import sanitize_name, sanitize_qualified_name

__all__ = ["display_name", "display_qualified_name"]


def display_name(name: str) -> str:
    return sanitize_name(name)


def display_qualified_name(qualified_name: str) -> str:
    return sanitize_qualified_name(qualified_name)
