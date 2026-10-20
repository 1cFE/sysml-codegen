"""The read-only half of ``generate`` cannot reach the writing half (Item 2b D1, Invariant 1).

``cli/prepare.py`` holds what runs before the first write; ``cli/emit.py`` holds everything
that writes under the destination. ``emit`` may import ``prepare``; ``prepare`` must never
import ``emit`` or the CLI package that composes them, at module level or inside a function.
Read from source, so a function-local import counts too.
"""

from __future__ import annotations

import ast
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen" / "cli"


def _imported_modules(path: Path) -> set[str]:
    """Every module an ``import`` or ``from … import`` anywhere in the file names."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            found.add(node.module)
            found.update(f"{node.module}.{alias.name}" for alias in node.names)
    return found


def test_prepare_imports_nothing_that_writes():
    imported = _imported_modules(CLI / "prepare.py")
    assert "sysml_codegen.cli.emit" not in imported
    assert not {name for name in imported if name == "sysml_codegen.cli"}, (
        "prepare.py imports the CLI package, which imports emit"
    )


def test_emit_holds_every_destination_writer():
    """The writer and clearing functions are defined in emit.py and nowhere else in cli/."""
    writers = {
        "_clear_output_directory",
        "_setup_output_directories",
        "_generate_primitives",
        "_generate_schemas",
        "_generate_modules",
        "_generate_stencils",
        "_generate_pipeline",
        "_generate_registry",
        "_generate_entry_points",
        "_generate_backlog",
        "_generate_tests",
        "_seal_package",
    }
    defined: dict[str, set[str]] = {}
    for path in CLI.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        defined[path.name] = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert writers <= defined["emit.py"]
    for name, functions in defined.items():
        if name != "emit.py":
            assert not writers & functions, (name, writers & functions)


def test_the_screen_imports_no_cli_module_at_run_time():
    """``subset_screen.py`` may name ``cli.prepare`` for type checking only (Invariant 1).

    Importing any ``sysml_codegen.cli`` module runs the package, which imports ``emit``.
    """
    tree = ast.parse((CLI.parent / "subset_screen.py").read_text(encoding="utf-8"))
    type_only = {
        id(node)
        for block in ast.walk(tree)
        if isinstance(block, ast.If)
        and isinstance(block.test, ast.Name)
        and block.test.id == "TYPE_CHECKING"
        for node in ast.walk(block)
    }
    runtime = {
        name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom)) and id(node) not in type_only
        for name in (
            [alias.name for alias in node.names]
            if isinstance(node, ast.Import)
            else [node.module or ""]
        )
    }
    assert not {name for name in runtime if name.startswith("sysml_codegen.cli")}, runtime
