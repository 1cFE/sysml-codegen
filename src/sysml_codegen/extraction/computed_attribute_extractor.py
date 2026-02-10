"""Computed attribute extraction for PartDef/PartUsage attributes.

Classifies attribute expressions (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED,
LITERAL, UNRESOLVABLE) using qualified-name resolution and compiles
FORMULA patterns to Python via the Phase 1 expression compiler.

This module is a leaf in the extraction layer — it does NOT import from
analysis/, resolution/, or generation/.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_mbse.sysml.expression import extract_feature_refs
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ExpressionRef

from .data_models import ComputedAttributeClassification, ComputedAttributeData
from .expression_compiler import (
    CompilationError,
    Compilability,
    _sanitize_name,
    build_expression_ast,
    compile_expression,
)
from .expression_utils import reconstruct_expression

logger = logging.getLogger(__name__)


def _classify_attribute_expression(
    refs: list[ExpressionRef],
    owning_part_qualified_name: str,
    calc_usage_names: set[str],
    sibling_attr_names: set[str],
    expression_ast: Any,
) -> ComputedAttributeClassification:
    """Classify an attribute expression by analyzing its feature references.

    Uses qualified-name resolution with positive identification:
    - Step 2a: filter CalcUsage instance refs (traversal artifacts)
    - Step 2b: QN starts with owning part QN → sibling_ref
    - Step 2c: QN non-empty but different namespace → calc_ref
    - Step 2d: empty QN fallback to simple name matching

    Args:
        refs: Feature references from extract_feature_refs().
        owning_part_qualified_name: QN of the owning PartDef/PartUsage.
        calc_usage_names: CalcUsage instance names on this part.
        sibling_attr_names: All AttributeUsage names on this part.
        expression_ast: Raw syside AST root node (for EXPOSE_PURE vs
            EXPOSE_COMPUTED distinction).

    Returns:
        Classification enum value.
    """
    # Step 1: no refs → LITERAL
    if not refs:
        return ComputedAttributeClassification.LITERAL

    sibling_refs: list[str] = []
    calc_refs: list[str] = []
    unresolvable_refs: list[str] = []

    part_qn_prefix = owning_part_qualified_name + "::"

    # Step 2: classify each ref by positive identification
    for ref in refs:
        # 2a: filter CalcUsage instance refs
        if ref.name in calc_usage_names:
            continue

        qn = ref.qualified_name
        if qn:
            # 2b: QN starts with owning part namespace → sibling
            if qn.startswith(part_qn_prefix):
                sibling_refs.append(ref.name)
            else:
                # 2c: QN in different namespace → calc output ref
                calc_refs.append(ref.name)
        else:
            # 2d: empty QN fallback to simple name matching
            if ref.name in sibling_attr_names:
                sibling_refs.append(ref.name)
            elif ref.name in calc_usage_names:
                # Already handled by 2a, but safety net for empty QN case
                continue
            else:
                unresolvable_refs.append(ref.name)

    # Step 3: decide classification
    if unresolvable_refs:
        return ComputedAttributeClassification.UNRESOLVABLE

    if not calc_refs:
        # Only sibling refs (or no refs after filtering)
        return ComputedAttributeClassification.FORMULA

    # calc_refs present → EXPOSE variant
    if not sibling_refs and SysideAdapter.is_instance(
        expression_ast, "FeatureChainExpression"
    ):
        return ComputedAttributeClassification.EXPOSE_PURE

    return ComputedAttributeClassification.EXPOSE_COMPUTED


def extract_computed_attributes(
    adapter: SysideAdapter,
    part_element: Any,
    calc_usage_names: set[str],
) -> list[ComputedAttributeData]:
    """Extract and classify computed attributes from a PartDef/PartUsage.

    Iterates owned_members, classifies each AttributeUsage expression,
    and returns ComputedAttributeData for all non-LITERAL attributes.

    Args:
        adapter: SysIDE adapter for type checking.
        part_element: Raw syside PartDef/PartUsage element.
        calc_usage_names: CalcUsage instance names on this part.

    Returns:
        List of ComputedAttributeData (LITERAL excluded, UNRESOLVABLE included).
    """
    # Build context
    sibling_attr_names: set[str] = set()
    for member in part_element.owned_members:
        if SysideAdapter.is_instance(member, "AttributeUsage"):
            sibling_attr_names.add(member.name)

    part_name = _sanitize_name(part_element.name)
    part_qn = str(getattr(part_element, "qualified_name", "") or part_name)

    results: list[ComputedAttributeData] = []

    for member in part_element.owned_members:
        if not SysideAdapter.is_instance(member, "AttributeUsage"):
            continue

        # Guard: must have an expression
        if (
            not hasattr(member, "feature_value_expression")
            or member.feature_value_expression is None
        ):
            continue

        expr = member.feature_value_expression
        attr_name = member.name

        # Extract refs
        refs = extract_feature_refs(expr, ignore_std_lib=True)

        # Classify
        classification = _classify_attribute_expression(
            refs=refs,
            owning_part_qualified_name=part_qn,
            calc_usage_names=calc_usage_names,
            sibling_attr_names=sibling_attr_names,
            expression_ast=expr,
        )

        # Skip LITERAL
        if classification == ComputedAttributeClassification.LITERAL:
            continue

        # Expression text (display only)
        expression_text = reconstruct_expression(expr)

        # Compilation: FORMULA only
        compiled_expression = None
        compilability = Compilability.MANUAL_REQUIRED

        if classification == ComputedAttributeClassification.FORMULA:
            # Self-exclusion: exclude the attribute being classified from
            # input_names so self-references become UNSUPPORTED (not INPUT_REF).
            # Sanitize names so they match _sanitize_name() in build_expression_ast.
            input_names = {
                _sanitize_name(n) for n in sibling_attr_names
            } - {_sanitize_name(attr_name)}
            try:
                ast_ir = build_expression_ast(
                    syside_node=expr,
                    input_names=input_names,
                    output_names=set(),
                    all_member_names=None,
                )
                compiled_expression = compile_expression(ast_ir)
                compilability = Compilability.FULLY_COMPILABLE
            except CompilationError as e:
                compiled_expression = None
                compilability = Compilability.MANUAL_REQUIRED
                logger.warning(
                    "FORMULA compilation failed for '%s' on '%s': %s",
                    attr_name,
                    part_name,
                    e,
                )

        if classification == ComputedAttributeClassification.UNRESOLVABLE:
            unresolvable_names = [r.name for r in refs]
            logger.warning(
                "Unresolvable attribute '%s' on '%s': refs=%s",
                attr_name,
                part_name,
                unresolvable_names,
            )

        logger.debug(
            "Classified '%s' on '%s': %s (compiled=%s)",
            attr_name,
            part_name,
            classification.value,
            compiled_expression,
        )

        results.append(
            ComputedAttributeData(
                name=attr_name,
                python_name=_sanitize_name(attr_name),
                owning_part_name=part_name,
                owning_part_qualified_name=part_qn,
                expression_ast=expr,
                expression_text=expression_text,
                references=refs,
                classification=classification,
                compilability=compilability,
                compiled_expression=compiled_expression,
            )
        )

    return results
