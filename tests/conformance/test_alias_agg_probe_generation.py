"""SC #1 lock: quoted CalcUsage names generate an importable package (Item 5).

``alias_agg_probe`` owns quoted calc defs (``'Margin Calc'``, ``'Report Calc'``,
``'Unit Cost Calc'``). It has ``computed_attributes: []`` and has never flowed
through registry + module generation, so the CalcUsage class-name / module-path
leak (``ModuleType.from_sysml`` / ``PythonModulePath.from_sysml`` building
identifiers straight from the raw quoted QN) was only code-inferred until now.

This drives the committed snapshot through full generation (license-free) and
asserts the two properties the leak breaks:
  1. every generated ``.py`` file parses (no ``'margin calc'.py`` / ``class
     'Margin Calc'Module`` garbage), and
  2. each class name the registry imports is declared by the module file it
     imports from (the registry never imports a name its module lacks).

Requirement: REQ-NC-08.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.conftest import snapshot_fixture


def _module_class_imports(
    registry_init: Path, package_name: str
) -> list[tuple[str, str]]:
    """(imported_class, module_file_relpath) for each module-class import.

    Parses the generated registry ``__init__.py`` and keeps only
    ``from {package}.modules.<path> import <Class>[ as Alias]`` statements. The
    *imported* name (before ``as``) is what the module file must declare; the
    alias is the registry's local rename and is irrelevant to declaration.
    """
    prefix = f"{package_name}.modules."
    tree = ast.parse(registry_init.read_text())
    out: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(prefix):
            rel = node.module[len(prefix):].replace(".", "/") + ".py"
            for alias in node.names:
                out.append((alias.name, rel))
    return out


def _classes_declared_in(module_file: Path) -> set[str]:
    """All class names declared at any level in a module file."""
    tree = ast.parse(module_file.read_text())
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}


@pytest.mark.req("REQ-NC-08")
def test_alias_agg_probe_generates_importable_package(tmp_path) -> None:
    """Quoted CalcUsage names generate a parseable, internally-consistent package."""
    from sysml_codegen.cli import GenerationConfig, run_codegen

    config = GenerationConfig(
        output_path=tmp_path,
        from_snapshot=snapshot_fixture("alias_agg_probe"),
        package_name="aap",
        overwrite=True,
    )
    assert run_codegen(config) is True

    # (1) every generated file parses.
    py_files = list(tmp_path.rglob("*.py"))
    assert py_files, "generation produced no Python files"
    for py in py_files:
        ast.parse(py.read_text())  # raises SyntaxError on a leaked quoted identifier

    # (2) each class the registry imports is declared by the module it imports from.
    modules_dir = tmp_path / "modules"
    for cls, rel in _module_class_imports(tmp_path / "__init__.py", "aap"):
        module_file = modules_dir / rel
        assert module_file.exists(), f"registry imports from missing module {rel}"
        declared = _classes_declared_in(module_file)
        assert cls in declared, (
            f"registry imports {cls!r} from {rel} but that module declares {sorted(declared)}"
        )
