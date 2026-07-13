"""Additive-guard test for the part-instance index (Item 4, INV-1).

License-free. Asserts no production module imports ``part_instance_index`` —
the item is a standalone analysis, wired in by nothing until Item 5, so an
accidental import (and its import-time side effects) would violate the
additive boundary the design and plan both require.
"""

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen"
MODULE_NAME = "part_instance_index"


def _imports_part_instance_index(source_path: Path) -> bool:
    tree = ast.parse(source_path.read_text(), filename=str(source_path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[-1] == MODULE_NAME for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[-1] == MODULE_NAME:
                return True
    return False


def test_no_production_module_imports_part_instance_index() -> None:
    offenders = [
        str(path.relative_to(SRC_ROOT))
        for path in sorted(SRC_ROOT.rglob("*.py"))
        if path.stem != MODULE_NAME and _imports_part_instance_index(path)
    ]
    assert offenders == [], (
        f"part_instance_index is additive this item (INV-1) — no production module "
        f"should import it yet, but found: {offenders}"
    )
