"""Constraint Extractor for SysML Models.

Extracts all constraint blocks from SysML AST and reconstructs expressions
as human-readable strings. Supports constraint, assert constraint, and
require constraint syntax.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# CRITICAL: Import syside adapter from agentic-mbse, NOT direct syside import
from agentic_mbse.sysml.syside_adapter import SysideAdapter


@dataclass
class ConstraintData:
    """Extracted constraint with full metadata."""

    name: str
    expression: str
    doc_comment: str
    owner_name: str
    owner_type: str
    owner_qualified_name: str
    referenced_variables: list[str]
    source_file: Path
    source_line: int


# Operator mapping for expression reconstruction
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

# Keywords to exclude from variable extraction
KEYWORDS = {"and", "or", "not", "true", "false", "implies", "if", "then", "else"}


def extract_all_constraints(model: Any) -> dict[str, list[ConstraintData]]:
    """Extract all constraints from model, keyed by owner qualified name.

    Args:
        model: Parsed SysIDE model

    Returns:
        Dict mapping owner qualified name to list of constraints
    """
    constraints_by_owner: dict[str, list[ConstraintData]] = {}

    for constraint_elem in SysideAdapter.elements_of_type(model, "ConstraintUsage"):
        try:
            constraint_data = _extract_constraint(constraint_elem)
            if constraint_data:
                owner_key = constraint_data.owner_qualified_name
                if owner_key not in constraints_by_owner:
                    constraints_by_owner[owner_key] = []
                constraints_by_owner[owner_key].append(constraint_data)
        except Exception as e:
            name = _safe_get_name(constraint_elem)
            print(f"Warning: Failed to extract constraint '{name}': {e}")
            continue

    return constraints_by_owner


def _extract_constraint(constraint_elem: Any) -> ConstraintData | None:
    """Extract single constraint from SysIDE element."""
    name = ""
    if hasattr(constraint_elem, "declared_name") and constraint_elem.declared_name:
        name = constraint_elem.declared_name
    elif hasattr(constraint_elem, "name") and constraint_elem.name:
        name = constraint_elem.name

    expression = _extract_constraint_expression(constraint_elem)
    if not expression:
        expression = str(constraint_elem) if constraint_elem else ""

    doc_comment = _extract_doc_comment(constraint_elem)
    owner_name, owner_type, owner_qualified_name = _find_owner(constraint_elem)
    referenced_variables = _extract_referenced_variables(expression)
    source_file, source_line = _get_source_location(constraint_elem)

    return ConstraintData(
        name=name,
        expression=expression,
        doc_comment=doc_comment,
        owner_name=owner_name,
        owner_type=owner_type,
        owner_qualified_name=owner_qualified_name,
        referenced_variables=referenced_variables,
        source_file=source_file,
        source_line=source_line,
    )


def _extract_constraint_expression(constraint_elem: Any) -> str:
    """Extract constraint expression as string."""
    if hasattr(constraint_elem, "result_expression") and constraint_elem.result_expression:
        expr = constraint_elem.result_expression
        return _reconstruct_expression(expr)

    if hasattr(constraint_elem, "owned_memberships"):
        for membership in constraint_elem.owned_memberships:
            membership_type = type(membership).__name__
            if membership_type == "FeatureValue":
                if hasattr(membership, "value") and membership.value:
                    return _reconstruct_expression(membership.value)

    if hasattr(constraint_elem, "feature_value_expression") and constraint_elem.feature_value_expression:
        return _reconstruct_expression(constraint_elem.feature_value_expression)

    if hasattr(constraint_elem, "owned_features"):
        for feature in constraint_elem.owned_features:
            if hasattr(feature, "feature_value_expression") and feature.feature_value_expression:
                return _reconstruct_expression(feature.feature_value_expression)

    return ""


def _reconstruct_expression(expr_node: Any) -> str:
    """Reconstruct expression text from AST nodes."""
    if isinstance(expr_node, str):
        return expr_node

    if expr_node is None:
        return ""

    node_type = type(expr_node).__name__

    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return _reconstruct_operator_expression(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return _extract_feature_reference_name(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return _extract_feature_chain_name(expr_node)

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


def _reconstruct_operator_expression(expr_node: Any) -> str:
    """Reconstruct operator expression from AST."""
    operator = ""
    if hasattr(expr_node, "operator") and expr_node.operator:
        operator = expr_node.operator

    operands = []
    if hasattr(expr_node, "operands"):
        operands = list(expr_node.operands)

    if len(operands) == 2:
        left = _reconstruct_expression(operands[0])
        right = _reconstruct_expression(operands[1])
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        return f"{left}{op_str}{right}"

    if len(operands) == 1:
        operand = _reconstruct_expression(operands[0])
        if operator == "-":
            return f"-{operand}"
        if operator == "not":
            return f"not {operand}"
        return f"{operator}({operand})"

    if len(operands) > 2:
        op_str = OPERATOR_MAP.get(operator, f" {operator} ")
        parts = [_reconstruct_expression(op) for op in operands]
        return op_str.join(parts)

    return operator


def _extract_feature_reference_name(expr_node: Any) -> str:
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


def _extract_feature_chain_name(expr_node: Any) -> str:
    """Extract name from FeatureChainExpression (a.b.c paths)."""
    path_parts = []

    if hasattr(expr_node, "operands"):
        operands = list(expr_node.operands)
        if operands:
            operand_expr = operands[0]
            operand_name = _reconstruct_expression(operand_expr)
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


def _extract_referenced_variables(expression: str) -> list[str]:
    """Extract variable names from expression string."""
    if not expression:
        return []

    identifiers = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", expression)

    variables = []
    for ident in identifiers:
        ident_lower = ident.lower()
        if ident_lower not in KEYWORDS:
            if not ident.isdigit():
                variables.append(ident)

    seen = set()
    unique_vars = []
    for var in variables:
        if var not in seen:
            seen.add(var)
            unique_vars.append(var)

    return unique_vars


def _find_owner(constraint_elem: Any) -> tuple[str, str, str]:
    """Find owning element (name, type, qualified_name)."""
    owner_name = ""
    owner_type = "unknown"
    owner_qualified_name = ""

    if not hasattr(constraint_elem, "owner"):
        return owner_name, owner_type, owner_qualified_name

    current = constraint_elem.owner

    while current is not None:
        if SysideAdapter.is_instance(current, "CalculationDefinition"):
            owner_type = "calc_def"
            owner_name = _safe_get_name(current)
            owner_qualified_name = _get_qualified_name(current)
            break

        if SysideAdapter.is_instance(current, "PartDefinition"):
            owner_type = "part_def"
            owner_name = _safe_get_name(current)
            owner_qualified_name = _get_qualified_name(current)
            break

        if SysideAdapter.is_instance(current, "PartUsage"):
            owner_type = "part_usage"
            owner_name = _safe_get_name(current)
            owner_qualified_name = _get_qualified_name(current)
            break

        if SysideAdapter.is_instance(current, "RequirementDefinition"):
            owner_type = "requirement"
            owner_name = _safe_get_name(current)
            owner_qualified_name = _get_qualified_name(current)
            break

        if hasattr(current, "owner"):
            current = current.owner
        else:
            break

    if not owner_name and hasattr(constraint_elem, "owner"):
        owner = constraint_elem.owner
        owner_name = _safe_get_name(owner)
        owner_qualified_name = _get_qualified_name(owner)

    return owner_name, owner_type, owner_qualified_name


def _get_qualified_name(elem: Any) -> str:
    """Get qualified name for an element."""
    if hasattr(elem, "qualified_name") and elem.qualified_name:
        return str(elem.qualified_name)

    parts = []
    current = elem
    while current is not None:
        name = _safe_get_name(current)
        if name:
            parts.insert(0, name)
        if hasattr(current, "owner"):
            current = current.owner
        else:
            break
        if len(parts) > 10:
            break

    return "::".join(parts) if parts else ""


def _safe_get_name(elem: Any) -> str:
    """Safely get name from element."""
    if elem is None:
        return ""
    if hasattr(elem, "declared_name") and elem.declared_name:
        return elem.declared_name
    if hasattr(elem, "name") and elem.name:
        return elem.name
    return ""


def _extract_doc_comment(constraint_elem: Any) -> str:
    """Extract documentation comment from constraint."""
    if hasattr(constraint_elem, "documentation") and constraint_elem.documentation:
        docs = list(constraint_elem.documentation)
        if docs:
            doc = docs[0]
            if hasattr(doc, "body") and doc.body:
                return doc.body.strip()
    return ""


def _get_source_location(constraint_elem: Any) -> tuple[Path, int]:
    """Get source file and line for constraint."""
    source_file = Path("unknown")
    source_line = 0

    if hasattr(constraint_elem, "source") and constraint_elem.source:
        source = constraint_elem.source
        if hasattr(source, "file") and source.file:
            source_file = Path(source.file)
        if hasattr(source, "line") and source.line:
            source_line = source.line

    if hasattr(constraint_elem, "text_position") and constraint_elem.text_position:
        pos = constraint_elem.text_position
        if hasattr(pos, "file") and pos.file:
            source_file = Path(pos.file)
        if hasattr(pos, "start_line"):
            source_line = pos.start_line

    return source_file, source_line


__all__ = [
    "ConstraintData",
    "extract_all_constraints",
]
