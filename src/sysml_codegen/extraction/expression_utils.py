"""Shared AST-to-text reconstruction utilities for SysML expressions.

Extracted from constraint_extractor.py to provide common AST traversal
and text reconstruction logic used by both the constraint extractor and
the expression compiler.
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

    node_type = type(expr_node).__name__

    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return extract_feature_chain_name(expr_node)

    if node_type in ("LiteralInteger", "LiteralReal", "LiteralRational"):
        if hasattr(expr_node, "value"):
            return str(expr_node.value)

    if node_type == "LiteralBoolean":
        if hasattr(expr_node, "value"):
            return "true" if expr_node.value else "false"

    if node_type == "LiteralString":
        if hasattr(expr_node, "value"):
            return f'"{expr_node.value}"'

    if node_type == "NullExpression":
        return "null"

    return str(expr_node)


def reconstruct_operator_expression(expr_node: Any) -> str:
    """Reconstruct operator expression from AST."""
    operator = ""
    if hasattr(expr_node, "operator") and expr_node.operator:
        operator = expr_node.operator

    operands = []
    if hasattr(expr_node, "operands"):
        operands = list(expr_node.operands)

    if len(operands) == 2:
        left = reconstruct_expression(operands[0])
        right = reconstruct_expression(operands[1])
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        return f"{left}{op_str}{right}"

    if len(operands) == 1:
        operand = reconstruct_expression(operands[0])
        if operator == "-":
            return f"-{operand}"
        if operator == "not":
            return f"not {operand}"
        return f"{operator}({operand})"

    if len(operands) > 2:
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        parts = [reconstruct_expression(op) for op in operands]
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


__all__ = [
    "OPERATOR_MAP",
    "reconstruct_expression",
    "reconstruct_operator_expression",
    "extract_feature_reference_name",
    "extract_feature_chain_name",
]
