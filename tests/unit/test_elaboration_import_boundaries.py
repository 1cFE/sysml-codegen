"""The exact-ID front end cannot depend on legacy/string identity machinery."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[2] / "src/sysml_codegen/elaboration"


def test_exact_front_end_has_no_legacy_or_first_match_identity_route() -> None:
    sources = {
        name: (ROOT / name).read_text() for name in ("identity.py", "occurrence.py", "elaborate.py")
    }
    banned = (
        "PartInstanceIndex",
        "InstanceOccurrence",
        "PathStep",
        "analysis.part_instance_index",
        "sanitize_name",
        "sanitize_qualified_name",
        "instance_path",
        "next(iter",
    )
    for name, source in sources.items():
        found = [token for token in banned if token in source]
        assert found == [], f"{name} imports or reconstructs legacy identity: {found}"


def test_display_rendering_is_an_explicit_metadata_only_boundary() -> None:
    source = (ROOT / "display.py").read_text()
    assert "sanitize_name" in source
    assert "sanitize_qualified_name" in source
    assert "identity" not in source
    assert "NodeId" not in source


def test_leaf_resolution_never_reads_display_or_qualified_name_metadata() -> None:
    source = (ROOT / "elaborate.py").read_text()
    module = ast.parse(source)
    [resolver] = [
        node
        for node in ast.walk(module)
        if isinstance(node, ast.FunctionDef) and node.name == "_resolve_leaf"
    ]
    forbidden = {
        node.attr
        for node in ast.walk(resolver)
        if isinstance(node, ast.Attribute)
        and node.attr in {"display_path", "qualified_name", "startswith", "endswith"}
    }
    called_names = {
        node.func.id
        for node in ast.walk(resolver)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert forbidden == set()
    assert "display_qualified_name" not in called_names
