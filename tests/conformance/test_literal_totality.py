"""Offline totality guard for expression reconstruction fidelity (SC-6).

The buggy reconstructor stringified literals as ``LiteralRationalEvaluation()``
because the invocation catch-all dispatched before the literal branches, and it
never emitted parentheses. Item 6 fixed both. These guards pin the regenerated
corpus so a regression (or a stale re-capture) cannot land silently:

- **INV-2**: no ``Literal*Evaluation`` string survives anywhere in the committed
  extraction snapshots or pipeline baselines.
- **M1**: the source-verified paren-restorer expressions are present verbatim.
  A *missing* restorer is as much a failure as a surprise one — a polarity bug
  in ``needs_parens`` would silently drop exactly these groups. (The design's
  fourth restorer, catf_mfe's constraint expression, is not snapshot-captured —
  recorded as an erratum in the Item 6 design appendix.)

REQ-AST-08: literal branches dispatch before the invocation catch-all.
REQ-AST-09: operator expressions parenthesize by KerML precedence.
"""

from __future__ import annotations

import re
from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"

LITERAL_EVALUATION = re.compile(r"Literal\w*Evaluation")

# Source-verified paren restorers (Item 6 design, Appendix A) and the snapshot
# each must appear in.
PAREN_RESTORERS = [
    ("attr_expr_probe/extraction_snapshot.json", "(r_inner + r_outer) / 2.0"),
    ("attr_expr_probe/extraction_snapshot.json", "(f_pump * eta_pump + f_subsystem)"),
    ("expression_binding_probe/extraction_snapshot.json", "(1.0 + tax_rate)"),
]


def _corpus_files():
    yield from FIXTURES.glob("*/extraction_snapshot.json")
    yield from FIXTURES.glob("baseline_outputs/**/*.json")


def test_no_literal_evaluation_strings_survive():
    offenders = {
        str(path.relative_to(FIXTURES)): len(LITERAL_EVALUATION.findall(path.read_text()))
        for path in _corpus_files()
        if LITERAL_EVALUATION.search(path.read_text())
    }
    assert not offenders, (
        f"Literal*Evaluation strings found in committed fixtures: {offenders}. "
        "The reconstructor's literal branches must dispatch before the "
        "invocation catch-all (REQ-AST-08); re-run the Item 6 regen."
    )


def test_paren_restorers_present():
    missing = [
        (rel, expr)
        for rel, expr in PAREN_RESTORERS
        if expr not in (FIXTURES / rel).read_text()
    ]
    assert not missing, (
        f"Expected paren-restored expressions absent from snapshots: {missing}. "
        "A missing restorer means needs_parens dropped a meaning-bearing group "
        "(REQ-AST-09 polarity bug) or the snapshot predates the Item 6 regen."
    )
