"""Real-AST regression test for expression reconstruction fidelity (SC-6, INV-3).

Parses a live fixture (no mocks) so the reconstructor runs on real
`.function`-bearing SysIDE nodes — the exact class of node whose derived
`.function` sent every literal to the invocation catch-all. Mocks masked that
dispatch bug, so this proof must use a real parse.

License-gated: skips cleanly without a live syside license (the offline
hand-trace unit tests in test_expression_paren_helper.py still carry C2/C3
coverage when it does).

Requirements: REQ-AST-08 (literal-before-invocation dispatch), REQ-AST-09
(precedence-aware parenthesization).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import REPO_ROOT, requires_license

FIXTURE = REPO_ROOT / "tests/fixtures/expr_paren_probe"


def _calc_expressions(fixture: Path) -> list[str]:
    """Reconstructed `name = expr` strings from a live parse of `fixture`."""
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models(), f"fixture failed to parse: {fixture}"
    out: list[str] = []
    for calc in extractor.extract_calculation_definitions():
        out.extend(calc.calc_expressions)
    return out


@requires_license
@pytest.mark.req("REQ-AST-08")
@pytest.mark.req("REQ-AST-09")
def test_repro_and_all_branch_shapes_render_exactly() -> None:
    got = _calc_expressions(FIXTURE)

    # INV-3 repro: equal-precedence, associativity-unfavored group preserved,
    # every literal as its value.
    assert "repro = capacity * rate + capacity * (rate / 2.0) * 3.0" in got

    # C2: unequal precedence, looser child on each side.
    assert "add_left = (a + b) * c" in got
    assert "add_right = a * (b + c)" in got

    # C3: unary over binary wraps.
    assert "neg_group = -(a + b)" in got
    assert "bool_group = not (flag_x and flag_y)" in got

    # Power right-associativity: natural nesting flat, forced left nesting wrapped.
    assert "pow_flat = a ** b ** c" in got
    assert "pow_forced = (a ** b) ** c" in got

    # Literal totality on a live AST: no dead-branch Literal*Evaluation leaks.
    assert "Evaluation()" not in "".join(got)
