"""Source-anchored guard for expression parenthesization fidelity."""

from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"

# Source-verified paren restorers (Item 6 design, Appendix A).
PAREN_RESTORERS = [
    ("attr_expr_probe/design.sysml", "(r_inner + r_outer) / 2.0"),
    ("attr_expr_probe/design.sysml", "(f_pump * eta_pump + f_subsystem)"),
    ("expression_binding_probe/library.sysml", "(1.0 + tax_rate)"),
]


def test_paren_restorers_present() -> None:
    missing = [
        (relative_path, expression)
        for relative_path, expression in PAREN_RESTORERS
        if expression not in (FIXTURES / relative_path).read_text()
    ]
    assert not missing, f"Expected parenthesized source expressions are absent: {missing}"
