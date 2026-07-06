"""Shared AST-to-text reconstruction utilities for SysML expressions.

Common AST traversal and text reconstruction logic used across extraction —
notably the expression compiler and the hierarchy resolver.
"""

from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter


# Operator mapping for expression reconstruction (SysML text output)
OPERATOR_MAP = {
    "and": " and ",
    "or": " or ",
    "==": " == ",
    "!=": " != ",
    ">": " > ",
    "<": " < ",
    ">=": " >= ",
    "<=": " <= ",
    "+": " + ",
    "-": " - ",
    "*": " * ",
    "/": " / ",
    "**": " ** ",
    "^": " ^ ",
    "implies": " implies ",
    "not": "not ",
}


def reconstruct_expression(expr_node: Any) -> str:
    """Reconstruct expression text from AST nodes."""
    if isinstance(expr_node, str):
        return expr_node

    if expr_node is None:
        return ""

    # FeatureChainExpression MUST be before OperatorExpression — FCE is a
    # subtype of OE in SysIDE's type system. Without this, FCE nodes enter
    # reconstruct_operator_expression() and produce ".(name)" instead of
    # "name.attr".
    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return extract_feature_chain_name(expr_node)

    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(expr_node)

    # Literal/null branches MUST dispatch before the invocation catch-all
    # (REQ-AST-08). Every SysIDE node carries a derived KerML `.function`, so a
    # literal placed after the catch-all is dead code and stringifies to
    # `LiteralRationalEvaluation()`. Detect via is_instance (D2), consistent
    # with the FCE/OE/FRE branches and is_literal_expression.
    if (
        SysideAdapter.is_instance(expr_node, "LiteralInteger")
        or SysideAdapter.is_instance(expr_node, "LiteralRational")
    ):
        if hasattr(expr_node, "value"):
            return str(expr_node.value)

    if SysideAdapter.is_instance(expr_node, "LiteralBoolean"):
        if hasattr(expr_node, "value"):
            return "true" if expr_node.value else "false"

    if SysideAdapter.is_instance(expr_node, "LiteralString"):
        if hasattr(expr_node, "value"):
            return f'"{expr_node.value}"'

    if SysideAdapter.is_instance(expr_node, "LiteralInfinity"):
        return "*"  # KerML textual notation for an unbounded literal (D3)

    if SysideAdapter.is_instance(expr_node, "NullExpression"):
        return "null"

    if hasattr(expr_node, "function") and hasattr(expr_node.function, "name"):
        # InvocationExpression (e.g., sum(), sqrt()) — catch-all, now last.
        func_name = expr_node.function.name
        operands = list(getattr(expr_node, "operands", []))
        args = ", ".join(reconstruct_expression(op) for op in operands)
        return f"{func_name}({args})"

    return str(expr_node)


# Binary-operator precedence ranks from KerML Table 6 (§8.2.5.8.1),
# authoritative over the grammar. Smaller rank = binds tighter (the C2
# polarity convention: comparisons are written against the rank directly, so
# "child binds looser than parent" is RANK[child] > RANK[parent]). Unary
# operators are not keyed here — they share operator strings with binary "-"
# but bind at UNARY_RANK regardless.
RANK = {
    "**": 3,
    "^": 3,
    "*": 4,
    "/": 4,
    "+": 5,
    "-": 5,
    "<": 7,
    ">": 7,
    "<=": 7,
    ">=": 7,
    "==": 9,
    "!=": 9,
    "and": 10,
    "or": 12,
    "implies": 13,
}
# Unary -/not bind tighter than every binary operator, including power (KerML
# rank 2). So any binary operand of a unary node needs wrapping.
UNARY_RANK = 2
# Right-associative operators: the *left* child at equal precedence is the
# unfavored side (the mirror of the left-associative rule).
RIGHT_ASSOC = frozenset({"**", "^"})


def binary_op_of(child: Any) -> str | None:
    """Return a child's operator iff it is a 2-operand binary OperatorExpression.

    Returns None for literals, FRE, FCE, invocations, and unary operator
    expressions — anything that renders atomically and never needs wrapping.
    The RANK-membership clause makes FeatureChainExpression (operator ".") and
    invocations fall through to None without a separate guard.
    """
    if not SysideAdapter.is_instance(child, "OperatorExpression"):
        return None
    # `.operands` is a LazyIterator on real SysIDE nodes — materialize before len().
    if len(list(getattr(child, "operands", []))) != 2:
        return None
    operator = getattr(child, "operator", None)
    if operator is None:
        return None
    # `.operator` is an Operator enum on real nodes (a plain str in unit stubs);
    # str() yields the SysML symbol either way.
    op_sym = str(operator)
    return op_sym if op_sym in RANK else None


def needs_parens(parent_rank: int, parent_right_assoc: bool, child: Any, side: str) -> bool:
    """True iff `child` must be wrapped when it sits on `side` of a parent.

    `side` is "left"/"right" for a binary parent, or "operand" for a unary one.
    A child wraps iff it binds looser than the parent, or equal and on the
    associativity-unfavored side.
    """
    cop = binary_op_of(child)
    if cop is None:
        return False  # atomic / unary child → never wrap
    cr = RANK[cop]
    if cr > parent_rank:
        return True  # child binds looser → must group
    if cr < parent_rank:
        return False  # child binds tighter → safe
    unfavored = "left" if parent_right_assoc else "right"
    return side == unfavored  # equal precedence → wrap the unfavored side


def reconstruct_operator_expression(expr_node: Any) -> str:
    """Reconstruct operator expression from AST, parenthesizing where grouping
    changes meaning (precedence-aware, REQ-AST-09)."""
    operator = ""
    if hasattr(expr_node, "operator") and expr_node.operator:
        # `.operator` is an Operator enum on real nodes (str in unit stubs);
        # normalize to the SysML symbol so RANK / RIGHT_ASSOC / OPERATOR_MAP and
        # the "-"/"not" checks all key off the same string.
        operator = str(expr_node.operator)

    operands = []
    if hasattr(expr_node, "operands"):
        operands = list(expr_node.operands)

    if len(operands) == 2:
        parent_rank = RANK.get(operator)
        right_assoc = operator in RIGHT_ASSOC
        left = reconstruct_expression(operands[0])
        right = reconstruct_expression(operands[1])
        if parent_rank is not None:
            if needs_parens(parent_rank, right_assoc, operands[0], "left"):
                left = f"({left})"
            if needs_parens(parent_rank, right_assoc, operands[1], "right"):
                right = f"({right})"
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        return f"{left}{op_str}{right}"

    if len(operands) == 1:
        operand = reconstruct_expression(operands[0])
        # Unary -/not bind tighter than every binary, so a binary operand needs
        # wrapping (C3): -(a + b), not (a and b). A nested unary operand is
        # atomic (binary_op_of → None) so it stays flat: - -a.
        if needs_parens(UNARY_RANK, False, operands[0], "operand"):
            operand = f"({operand})"
        if operator == "-":
            return f"-{operand}"
        if operator == "not":
            return f"not {operand}"
        return f"{operator}({operand})"

    if len(operands) > 2:
        # n-ary: left fold. A same-operator child is part of the same
        # associative chain and never wraps; a looser-precedence child still
        # does.
        parent_rank = RANK.get(operator)
        right_assoc = operator in RIGHT_ASSOC
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        parts = []
        for i, op in enumerate(operands):
            text = reconstruct_expression(op)
            side = "left" if i == 0 else "right"
            if (
                parent_rank is not None
                and binary_op_of(op) != operator
                and needs_parens(parent_rank, right_assoc, op, side)
            ):
                text = f"({text})"
            parts.append(text)
        return op_str.join(parts)

    return operator


def extract_feature_reference_name(expr_node: Any) -> str:
    """Extract name from FeatureReferenceExpression."""
    if hasattr(expr_node, "referent") and expr_node.referent:
        referent = expr_node.referent
        if hasattr(referent, "name") and referent.name:
            return referent.name

    if hasattr(expr_node, "memberships"):
        for membership in expr_node.memberships:
            if type(membership).__name__ == "Membership":
                if hasattr(membership, "member_element"):
                    elem = membership.member_element
                    if elem and hasattr(elem, "name") and elem.name:
                        return elem.name

    if hasattr(expr_node, "declared_name") and expr_node.declared_name:
        return expr_node.declared_name
    if hasattr(expr_node, "name") and expr_node.name:
        return expr_node.name

    return str(expr_node)


def extract_feature_chain_name(expr_node: Any) -> str:
    """Extract name from FeatureChainExpression (a.b.c paths)."""
    path_parts = []

    if hasattr(expr_node, "operands"):
        operands = list(expr_node.operands)
        if operands:
            operand_expr = operands[0]
            operand_name = reconstruct_expression(operand_expr)
            if operand_name:
                path_parts.append(operand_name)

    if hasattr(expr_node, "target_feature") and expr_node.target_feature:
        target = expr_node.target_feature
        if hasattr(target, "name") and target.name:
            path_parts.append(target.name)

    if not path_parts and hasattr(expr_node, "memberships"):
        for membership in expr_node.memberships:
            if type(membership).__name__ == "Membership":
                if hasattr(membership, "member_element"):
                    elem = membership.member_element
                    if elem and hasattr(elem, "name") and elem.name:
                        path_parts.append(elem.name)

    if path_parts:
        return ".".join(path_parts)

    return str(expr_node)


def extract_feature_chain_segments(expr_node: Any) -> list[str]:
    """Return the full dotted-path segments of a FeatureChainExpression.

    The segment-list analog of extract_feature_chain_name (Item 10, D9). Unlike
    that helper — which reads ``operands[0]`` + ``target_feature.name`` and joins
    to a string — this expands ``target_feature.chaining_features`` so a 3+-deep
    chain yields every segment instead of truncating.

    Concretely, ``tf_coil.volume_calc.volume`` parses to a FeatureChainExpression
    whose ``target_feature`` is an anonymous Feature with ``name is None`` and
    ``chaining_features == [volume_calc, volume]``. Reading ``.name`` alone yields
    ``["tf_coil"]``; expanding ``chaining_features`` yields the full
    ``["tf_coil", "volume_calc", "volume"]`` the multi-hop confirm walk needs.

    Returns an empty list for a non-FeatureChainExpression node.
    """
    if not SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return []

    segments: list[str] = []

    operands = list(getattr(expr_node, "operands", []) or [])
    if operands:
        root = operands[0]
        if SysideAdapter.is_instance(root, "FeatureChainExpression"):
            segments.extend(extract_feature_chain_segments(root))
        else:
            name = reconstruct_expression(root)
            if name:
                segments.append(name)

    target = getattr(expr_node, "target_feature", None)
    if target is not None:
        chaining = list(getattr(target, "chaining_features", []) or [])
        if chaining:
            segments.extend(c.name for c in chaining if getattr(c, "name", None))
        elif getattr(target, "name", None):
            segments.append(target.name)

    return segments


def is_literal_expression(expr: Any) -> bool:
    """Check if a syside AST node is a literal value expression.

    Handles the four SysML literal types (LiteralInteger, LiteralRational,
    LiteralBoolean, LiteralString) plus LiteralInfinity and NullExpression,
    keeping this consistent with the dispatch set in reconstruct_expression.
    """
    return (
        SysideAdapter.is_instance(expr, "LiteralInteger")
        or SysideAdapter.is_instance(expr, "LiteralRational")
        or SysideAdapter.is_instance(expr, "LiteralBoolean")
        or SysideAdapter.is_instance(expr, "LiteralString")
        or SysideAdapter.is_instance(expr, "LiteralInfinity")
        or SysideAdapter.is_instance(expr, "NullExpression")
    )


def extract_literal_value(expr: Any) -> float | int | str | bool | None:
    """Extract the Python value from a literal AST node.

    Returns None if the node has no ``value`` attribute.
    """
    if hasattr(expr, "value"):
        return expr.value
    return None


__all__ = [
    "OPERATOR_MAP",
    "reconstruct_expression",
    "reconstruct_operator_expression",
    "extract_feature_reference_name",
    "extract_feature_chain_name",
    "is_literal_expression",
    "extract_literal_value",
]
