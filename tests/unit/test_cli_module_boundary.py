"""The read-only modules cannot reach the writing half, nor the screen (Item 2b D1, D17).

``cli/prepare.py`` holds what runs before the first write; ``cli/emit.py`` holds everything
that writes under the destination. ``emit`` may import ``prepare``; ``prepare`` and
``readiness`` must never import ``emit`` or the CLI package that composes them, at module level
or inside a function. Read from source, so a function-local import counts too.

Nothing ``generate`` runs before the seal may import agentic-mbse's subset screen (audit B1).
So no module the CLI loads imports it at module level, and loading every CLI module, the
screen's own wrapper included, leaves the screen's vocabulary module unimported.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

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


SCREEN_MODULES = frozenset(
    {
        "agentic_mbse.sysml.subset_profile",
        "agentic_mbse.sysml.subset_extraction",
        "sysml_codegen.subset_profile_adapter",
    }
)


def _module_level_imports(path: Path) -> set[str]:
    """The modules imported at module level, outside ``if TYPE_CHECKING:`` blocks."""
    found: set[str] = set()
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            found.add(node.module)
            found.update(f"{node.module}.{alias.name}" for alias in node.names)
    return found


@pytest.mark.parametrize("module", ["prepare.py", "readiness.py", "destination.py"])
def test_a_read_only_module_imports_nothing_that_writes(module):
    imported = _imported_modules(CLI / module)
    assert "sysml_codegen.cli.emit" not in imported
    assert not {name for name in imported if name == "sysml_codegen.cli"}, (
        f"{module} imports the CLI package, which imports emit"
    )


@pytest.mark.parametrize("module", ["__init__.py", "prepare.py", "destination.py", "readiness.py"])
def test_no_cli_module_imports_the_screen_at_module_level(module):
    assert not _module_level_imports(CLI / module) & SCREEN_MODULES


def test_loading_every_cli_module_leaves_the_screen_unimported():
    """A fresh interpreter, so nothing else has imported the screen first."""
    probe = (
        "import sys\n"
        "import sysml_codegen.cli, sysml_codegen.cli.prepare, sysml_codegen.cli.emit\n"
        "import sysml_codegen.cli.destination, sysml_codegen.cli.readiness\n"
        "import sysml_codegen.subset_screen\n"
        f"print(sorted(set(sys.modules) & set({sorted(SCREEN_MODULES)!r})))\n"
    )
    run = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, check=True)
    assert run.stdout.strip() == "[]", run.stdout + run.stderr


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


def _imports_emit(node: ast.AST) -> bool:
    return any(
        isinstance(n, ast.ImportFrom)
        and (
            n.module == "sysml_codegen.cli.emit"
            or (n.module == "sysml_codegen.cli" and "emit" in {a.name for a in n.names})
        )
        for n in ast.walk(node)
    )


def test_the_cli_imports_emit_only_inside_run_codegen():
    """So ``check``, which lives in the same package, never loads the writing module."""
    tree = ast.parse((CLI / "__init__.py").read_text(encoding="utf-8"))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert not any(_imports_emit(n) for n in tree.body if n not in functions)
    assert [f.name for f in functions if _imports_emit(f)] == ["run_codegen"]
