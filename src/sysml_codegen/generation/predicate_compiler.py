"""Kleene predicate compiler (Item 7 / D2).

Turns one definition's ``predicate_ir`` (a landed ``expression_ir.ExpressionIR`` tree) into
readable Python implementing three-valued (Kleene) predicate semantics: a non-finite leaf
comparison is ``unknown`` (``None``), and ``unknown`` propagates only where a connective needs
it (``true or unknown -> true``, ``false and unknown -> false``, ``not unknown -> unknown``).

This is a rewrite of the spike's ``s2_ir.compile_predicate`` against Item 2's landed node
algebra (`agentic_mbse.sysml.expression_ir`) — the spike's ``IRNode`` and the landed
``ExpressionIR`` have different node kinds/fields, so the tree-walk is rebuilt while the emitted
Python (leaf ``_cmp``, ``_and``/``_or``/``_not``, margin) matches the spike's proven form. Units
are strip-rendered (B2) — the compiler is not a unit safety net; Item 3's profile gate already
excludes a unit-mismatched comparison before this module ever sees the IR.
"""

from __future__ import annotations

import keyword
import math
from typing import Any

from agentic_mbse.sysml.expression_facts import OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
)

__all__ = [
    "KLEENE_RUNTIME_SOURCE",
    "PredicateCompileError",
    "compile_predicate",
    "function_source_only",
    "load_predicate",
    "margin_expression",
]

COMPARISON_OPS = {"<", "<=", ">", ">=", "==", "!="}
_BOUNDARY_COMPARISON_OPS = {"<", "<=", ">", ">="}
ARITHMETIC_OPS = {"+", "-", "*", "/", "**", "^"}

# The Kleene runtime block, emitted once per compiled function. Kept a plain string (not a
# shared import) so each generated predicates.py module is self-contained (D4: a sealed
# per-package artifact cannot depend on codegen-side runtime definitions).
_KLEENE_RUNTIME = '''
import math
from typing import NamedTuple


class _PredicateResult(NamedTuple):
    actual_value: object  # True/False/None (None = indeterminate)
    status: str           # satisfied | violated | indeterminate
    margin: object         # signed float or None (simple-inequality roots only)


def _fin(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def _cmp(op, a, b):
    """Leaf comparison: unknown (None) if either operand is non-finite."""
    if not _fin(a) or not _fin(b):
        return None
    if op == "<=": return a <= b
    if op == ">=": return a >= b
    if op == "<":  return a < b
    if op == ">":  return a > b
    raise ValueError(f"not a comparison: {op}")


def _and(*vals):
    if any(v is False for v in vals): return False
    if any(v is None for v in vals): return None
    return True


def _or(*vals):
    if any(v is True for v in vals): return True
    if any(v is None for v in vals): return None
    return False


def _not(v):
    return None if v is None else (not v)


def _norm0(x):
    """Normalize an exact-boundary signed zero (-0.0) to 0.0 (`[HARD]`)."""
    return 0.0 if x == 0.0 else x
'''


KLEENE_RUNTIME_SOURCE = _KLEENE_RUNTIME


class PredicateCompileError(Exception):
    """The IR contains a construct the compiler does not (yet) render."""


def _required_operand_type(n: ExpressionIR) -> OperandTypeFact:
    if not isinstance(n, (LiteralNode, FeatureReferenceNode, UnitAnnotationNode)):
        raise PredicateCompileError(f"{n.kind} does not carry an operand_type")
    operand_type = n.operand_type
    if operand_type is None:
        raise PredicateCompileError(f"{n.kind} is missing operand_type")
    return operand_type


def _compile_reference(n: FeatureReferenceNode) -> str:
    if n.reference.chain_segments:
        raise PredicateCompileError("feature chain not supported in executable-profile/v3")
    if not n.reference.source_name:
        raise PredicateCompileError("nameless feature reference")
    return n.reference.source_name


def _compile_numeric_operator(n: OperatorNode) -> str:
    if n.operator not in ARITHMETIC_OPS:
        raise PredicateCompileError(f"operator {n.operator!r} in numeric position")
    if not n.operands:
        raise PredicateCompileError(f"operator {n.operator!r} with no operands")
    if len(n.operands) == 1:
        if n.operator not in ("+", "-"):
            raise PredicateCompileError(f"unsupported unary operator: {n.operator!r}")
        return f"({n.operator}{_compile_numeric(n.operands[0])})"

    py_operator = "**" if n.operator in ("**", "^") else n.operator
    parts = [_compile_numeric(operand) for operand in n.operands]
    expression = parts[0]
    for part in parts[1:]:
        expression = f"({expression} {py_operator} {part})"
    return expression


def _compile_numeric(n: ExpressionIR) -> str:
    """Numeric (float-valued) subtree -> plain Python expression."""
    if isinstance(n, LiteralNode):
        operand_type = _required_operand_type(n)
        if operand_type.category in ("real", "integer"):
            return repr(n.literal.value)
        raise PredicateCompileError(
            f"non-numeric literal in numeric position: category={operand_type.category!r}"
        )
    if isinstance(n, FeatureReferenceNode):
        operand_type = _required_operand_type(n)
        if operand_type.category not in ("real", "integer", "quantity"):
            raise PredicateCompileError(
                "non-numeric feature reference in numeric position: "
                f"category={operand_type.category!r}"
            )
        return _compile_reference(n)
    if isinstance(n, UnitAnnotationNode):
        _required_operand_type(n)
        return _compile_numeric(n.value)
    if isinstance(n, OperatorNode):
        return _compile_numeric_operator(n)
    raise PredicateCompileError(f"{n.kind} in numeric position")


def _compile_equality(n: OperatorNode) -> str:
    raise PredicateCompileError(
        f"{n.operator!r} is not admitted by executable-profile/v3; profile preflight must "
        "exclude every equality expression"
    )


def _compile_boolean(n: ExpressionIR) -> str:
    """Boolean-valued subtree -> three-valued Python expression."""
    if isinstance(n, OperatorNode) and n.operator in COMPARISON_OPS:
        if n.operator in ("==", "!="):
            return _compile_equality(n)
        if len(n.operands) != 2:
            raise PredicateCompileError(
                f"comparison {n.operator!r} needs 2 operands, got {len(n.operands)}"
            )
        a = _compile_numeric(n.operands[0])
        b = _compile_numeric(n.operands[1])
        return f"_cmp({n.operator!r}, {a}, {b})"
    if isinstance(n, OperatorNode) and n.operator in ("and", "or"):
        if len(n.operands) < 2:
            raise PredicateCompileError(
                f"{n.operator!r} needs at least 2 operands, got {len(n.operands)}"
            )
        fn = "_and" if n.operator == "and" else "_or"
        parts = ", ".join(_compile_boolean(o) for o in n.operands)
        return f"{fn}({parts})"
    if isinstance(n, OperatorNode) and n.operator == "not":
        if len(n.operands) != 1:
            raise PredicateCompileError(f"'not' needs exactly 1 operand, got {len(n.operands)}")
        return f"_not({_compile_boolean(n.operands[0])})"
    if isinstance(n, LiteralNode):
        operand_type = _required_operand_type(n)
        if operand_type.category == "boolean":
            return repr(n.literal.value)
    operator = n.operator if isinstance(n, OperatorNode) else None
    raise PredicateCompileError(f"unsupported boolean node: {n.kind}/{operator}")


def _leaf_ref_names(n: ExpressionIR, acc: list[str]) -> None:
    """Collect ``FeatureReferenceNode`` source names, first-occurrence order, deduped."""
    if isinstance(n, FeatureReferenceNode):
        name = n.reference.source_name
        if name and name not in acc:
            acc.append(name)
        return
    if isinstance(n, OperatorNode):
        for child in n.operands:
            _leaf_ref_names(child, acc)
    elif isinstance(n, UnitAnnotationNode):
        _leaf_ref_names(n.value, acc)
    elif isinstance(n, InvocationNode):
        for child in n.arguments:
            _leaf_ref_names(child, acc)
    # LiteralNode / UnsupportedNode carry no leaf references.


def margin_expression(n: ExpressionIR, negated: bool) -> str | None:
    """Signed margin for a simple-inequality root; ``None`` for compound shapes.

    Sign convention: positive margin <=> assertion satisfied. A negated assertion flips the
    sign. The exact boundary (``margin == 0``) is normalized so it never reads as a signed
    near-miss (``-0.0``) — `[HARD]`.
    """
    if not (isinstance(n, OperatorNode) and n.operator in _BOUNDARY_COMPARISON_OPS):
        return None
    if len(n.operands) != 2:
        raise PredicateCompileError(
            f"comparison {n.operator!r} needs 2 operands, got {len(n.operands)}"
        )
    a = _compile_numeric(n.operands[0])
    b = _compile_numeric(n.operands[1])
    raw = f"({b} - {a})" if n.operator in ("<", "<=") else f"({a} - {b})"
    body = f"(-{raw})" if negated else raw
    return f"(_norm0({body}) if (_fin({a}) and _fin({b})) else None)"


def compile_predicate(
    ir: ExpressionIR, fn_name: str, negated: bool = False
) -> tuple[str, list[str]]:
    """Generate Python source for one predicate.

    Returns ``(source, arg_names)``. The emitted function returns a ``_PredicateResult``
    namedtuple: ``actual_value`` (``True``/``False``/``None``), ``status``
    (``satisfied``/``violated``/``indeterminate``, polarity applied), and ``margin`` (signed
    float or ``None``) — the field names match :class:`ConstraintEvaluation` directly.
    """
    if not fn_name.isidentifier() or keyword.iskeyword(fn_name):
        raise PredicateCompileError(f"function name {fn_name!r} is not a Python identifier")
    args: list[str] = []
    _leaf_ref_names(ir, args)
    for arg in args:
        if not arg.isidentifier() or keyword.iskeyword(arg):
            raise PredicateCompileError(f"leaf reference {arg!r} is not a safe Python identifier")
    body = _compile_boolean(ir)
    margin = margin_expression(ir, negated) or "None"
    expected = "False" if negated else "True"
    src = f"""{_KLEENE_RUNTIME}

def {fn_name}({", ".join(args)}):
    value = {body}
    if value is None:
        status = "indeterminate"
    elif value == {expected}:
        status = "satisfied"
    else:
        status = "violated"
    return _PredicateResult(actual_value=value, status=status, margin={margin})
"""
    return src, args


def function_source_only(full_source: str) -> str:
    """Strip the leading ``_KLEENE_RUNTIME`` prelude from one `compile_predicate` output.

    D3: the shared predicates module emits the runtime block once, then each definition's
    function body — never one runtime block per function. ``full_source`` must be a string
    `compile_predicate` produced (it always starts with the runtime prelude).
    """
    if not full_source.startswith(_KLEENE_RUNTIME):
        raise PredicateCompileError(
            "function_source_only expects a compile_predicate() output (runtime-prelude "
            "prefixed source)"
        )
    return full_source[len(_KLEENE_RUNTIME) :]


def load_predicate(src: str, fn_name: str) -> Any:
    """Exec emitted source in a fresh namespace and return the compiled function.

    Test/debug convenience — production generation embeds ``src`` directly into the shared
    predicates module template (D3); it never execs at generation time.
    """
    ns: dict[str, Any] = {"math": math}
    exec(src, ns)  # noqa: S102 — controlled codegen-emitted source, not external input
    return ns[fn_name]
