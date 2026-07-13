"""INV-4: ExpressionAST and its two compile functions are gone from src/.

The last gate of CONSTRAINT-EXEC Item 13 (calc-seam cutover): after the seam and
computed-attribute flips (Phases 1-2) and the deletion (Phase 4), the three retired symbols
must appear nowhere in `sysml_codegen/src` -- no silent third representation, no
half-migrated caller left calling a symbol that's actually gone from behind an alias.
"""

from __future__ import annotations

import re
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen"

BANNED = ("ExpressionAST", "build_expression_ast", "compile_expression")


def test_expression_ast_symbols_deleted():
    banned_pattern = re.compile("|".join(re.escape(name) for name in BANNED))
    hits: list[str] = []
    for path in SRC_DIR.rglob("*.py"):
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            if banned_pattern.search(line):
                hits.append(f"{path.relative_to(SRC_DIR)}:{lineno}: {line.strip()}")
    assert hits == [], "ExpressionAST not fully retired:\n" + "\n".join(hits)
