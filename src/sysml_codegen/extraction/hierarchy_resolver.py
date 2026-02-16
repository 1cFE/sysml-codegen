"""Hierarchy resolver: :>> redefinition extraction, multiplicity, aggregation.

Extracts redefinition data from PartDefs and design PartUsages, producing
standalone data structures that Item 4 consumes for pipeline integration.

This is a pure extraction-layer module — no pipeline, backtracker, or
generation changes.

Key functions:
- extract_redefinitions(): Scan :>> ReferenceUsage members on a PartDef
- extract_design_overrides(): Scan design PartUsages for deep-path :>> overrides
- extract_multiplicities(): (Phase 3) Detect multiplicity on child PartUsages
- build_aggregation_expression(): (Phase 4) Transform sum() to parametric multiply
- extract_hierarchy_data(): (Phase 4) Top-level orchestrator
"""

import logging
from collections.abc import Iterable
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    sanitize_name,
)
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    HierarchyExtractionResult,
    LocalTerm,
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
    SingletonTerm,
    SumTerm,
)
from sysml_codegen.extraction.expression_utils import (
    OPERATOR_MAP,
    extract_feature_chain_name,
    extract_feature_reference_name,
    extract_literal_value,
    is_literal_expression,
    reconstruct_expression,
)

logger = logging.getLogger(__name__)


def _extract_single_redefinition(
    member: Any,
    owning_qn: str,
) -> RedefinitionData | None:
    """Extract a single :>> redefinition from a ReferenceUsage member.

    Shared helper used by both extract_redefinitions() (PartDef members)
    and extract_design_overrides() (design PartUsage members). The two
    callers differ only in their outer loops.

    Args:
        member: A ReferenceUsage element with non-empty owned_redefinitions.
        owning_qn: Qualified name of the owning PartDef or PartUsage.

    Returns:
        RedefinitionData if the member has a value expression, None otherwise.
    """
    if not SysideAdapter.is_instance(member, "ReferenceUsage"):
        return None

    owned_redefs = getattr(member, "owned_redefinitions", None)
    if not owned_redefs:
        return None

    redef = owned_redefs[0]
    redefined_feature = redef.redefined_feature

    # Check for deep-path (chaining_features)
    chaining = list(getattr(redefined_feature, "chaining_features", []))
    if chaining:
        target_path = [sanitize_name(c.name) for c in chaining]
        attr_name = target_path[-1]
        is_deep_path = True
    else:
        attr_name = sanitize_name(getattr(redefined_feature, "name", None)) or sanitize_name(
            getattr(member, "name", None)
        )
        target_path = []
        is_deep_path = False

    # Skip if no value expression (type-only redefinition)
    expr = getattr(member, "feature_value_expression", None)
    if expr is None:
        return None

    # Classify RHS
    if is_literal_expression(expr):
        return RedefinitionData(
            owning_part_qn=owning_qn,
            attribute_name=attr_name,
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=extract_literal_value(expr),
            target_path=target_path,
            is_deep_path=is_deep_path,
        )

    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        source_path = extract_feature_chain_name(expr)
        return RedefinitionData(
            owning_part_qn=owning_qn,
            attribute_name=attr_name,
            redefinition_type=RedefinitionType.CHAIN,
            source_path=source_path,
            target_path=target_path,
            is_deep_path=is_deep_path,
        )

    if SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        source_path = extract_feature_reference_name(expr)
        return RedefinitionData(
            owning_part_qn=owning_qn,
            attribute_name=attr_name,
            redefinition_type=RedefinitionType.CHAIN,
            source_path=source_path,
            target_path=target_path,
            is_deep_path=is_deep_path,
        )

    # EXPRESSION: OperatorExpression, InvocationExpression, or anything else
    return RedefinitionData(
        owning_part_qn=owning_qn,
        attribute_name=attr_name,
        redefinition_type=RedefinitionType.EXPRESSION,
        expression_ast=expr,
        expression_text=reconstruct_expression(expr),
        target_path=target_path,
        is_deep_path=is_deep_path,
    )


def extract_redefinitions(part_element: Any) -> list[RedefinitionData]:
    """Scan :>> redefinitions on a PartDef or PartUsage element.

    Iterates owned_members looking for ReferenceUsage elements with
    non-empty owned_redefinitions. Classifies each by RHS expression type.

    Args:
        part_element: A PartDefinition or PartUsage element.

    Returns:
        List of RedefinitionData for each :>> with a value expression.
    """
    owning_qn = build_element_qualified_name(part_element)
    results: list[RedefinitionData] = []

    for member in getattr(part_element, "owned_members", []):
        redef_data = _extract_single_redefinition(member, owning_qn)
        if redef_data is not None:
            results.append(redef_data)

    return results


def extract_design_overrides(
    part_usages: Iterable[Any],
) -> list[RedefinitionData]:
    """Scan design-level PartUsages for :>> overrides.

    Design PartUsages with non-empty owned_redefinitions are 'part redefines'
    instances. Their owned_members may contain deep-path :>> overrides like
    :>> pv_module.wattage = 400.0.

    Args:
        part_usages: Iterable of PartUsage elements to scan. The caller
            (orchestrator) is responsible for filtering to design-level
            PartUsages via SysideAdapter.elements_of_type().

    Returns:
        List of RedefinitionData for each :>> found on design PartUsages.
    """
    results: list[RedefinitionData] = []

    for usage in part_usages:
        if not getattr(usage, "owned_redefinitions", None):
            continue  # Not a 'part redefines'

        usage_qn = build_element_qualified_name(usage)

        for member in getattr(usage, "owned_members", []):
            redef_data = _extract_single_redefinition(member, usage_qn)
            if redef_data is not None:
                results.append(redef_data)

    return results


def extract_multiplicities(part_element: Any) -> list[MultiplicityData]:
    """Extract multiplicity from child PartUsages of a PartDef.

    Scans owned_members for PartUsage elements with a multiplicity attribute.
    Uses cached_lower_bound for the count (cached_upper_bound is N+1 due to
    syside exclusive convention — spike Q5).

    Args:
        part_element: A PartDefinition element.

    Returns:
        List of MultiplicityData for each PartUsage with multiplicity.
        Singletons (no multiplicity) are excluded.
    """
    owning_qn = build_element_qualified_name(part_element)
    results: list[MultiplicityData] = []

    for member in getattr(part_element, "owned_members", []):
        if not SysideAdapter.is_instance(member, "PartUsage"):
            continue

        mult = getattr(member, "multiplicity", None)
        if mult is None:
            continue  # Singleton

        # Use cached_lower_bound (correct for [N] syntax) — spike Q5
        raw_count = getattr(mult, "cached_lower_bound", None)
        count = int(raw_count) if raw_count is not None else None

        # Extract attribute name from upper_bound expression chain
        count_attr_name = None
        default_value = None
        upper = getattr(mult, "upper_bound", None)
        if upper and hasattr(upper, "referent"):
            referent = upper.referent
            count_attr_name = getattr(referent, "name", None)
            fve = getattr(referent, "feature_value_expression", None)
            if fve and hasattr(fve, "value"):
                raw_default = fve.value
                default_value = int(raw_default) if raw_default is not None else None

        results.append(
            MultiplicityData(
                part_usage_name=sanitize_name(member.name),
                owning_part_def_qn=owning_qn,
                count=count,
                count_attribute_name=count_attr_name,
                default_value=default_value,
            )
        )

    return results


# ---------------------------------------------------------------------------
# Aggregation Expression Transformation (Phase 4)
# ---------------------------------------------------------------------------


class _AggregationContext:
    """Mutable collector for aggregation AST walk results."""

    __slots__ = (
        "sum_terms",
        "singleton_terms",
        "local_terms",
        "input_channels",
        "entry_points",
        "has_unsupported",
    )

    def __init__(self) -> None:
        self.sum_terms: list[SumTerm] = []
        self.singleton_terms: list[SingletonTerm] = []
        self.local_terms: list[LocalTerm] = []
        self.input_channels: list[str] = []
        self.entry_points: list[str] = []
        self.has_unsupported: bool = False


_KNOWN_WRAPPER_FUNCTIONS = frozenset({"Evaluation", "evaluate", "collect", "select"})


def _unwrap_invocation(node: Any, _depth: int = 0) -> Any:
    """Unwrap InvocationExpression wrappers (Evaluation, collect, select, etc.).

    Recursively peels off InvocationExpression layers to find the innermost
    non-InvocationExpression node. Handles nested wrappers like
    collect(Evaluation(FeatureChainExpression)).

    Args:
        node: AST node, potentially an InvocationExpression wrapper.
        _depth: Recursion depth counter (max 3 to prevent infinite loops).

    Returns:
        The unwrapped node, or the original if no wrapper found.
    """
    if _depth >= 3:
        return node
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return node
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return node
    if hasattr(node, "function") and hasattr(node.function, "name"):
        operands = list(getattr(node, "operands", []))
        if operands:
            return _unwrap_invocation(operands[0], _depth + 1)
    return node


def _walk_aggregation_ast(
    node: Any,
    mult_lookup: dict[str, MultiplicityData],
    ctx: _AggregationContext,
) -> str:
    """Recursively walk an aggregation expression AST.

    Transforms sum() calls to parametric multiply, classifies operands
    into SumTerm/SingletonTerm/LocalTerm, and builds the transformed
    expression text. Collects results into ctx.

    Args:
        node: AST node to process.
        mult_lookup: Multiplicity data keyed by part_usage_name.
        ctx: Mutable context collecting terms, channels, etc.

    Returns:
        Transformed expression text for this node.
    """
    if node is None:
        return ""

    # FeatureChainExpression: child.attr → SingletonTerm
    # MUST be before OperatorExpression — FCE is a subtype of OE in SysIDE's
    # type system, so both is_instance() checks return True on the same node.
    # The more specific check must come first.
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        chain_name = extract_feature_chain_name(node)
        ctx.singleton_terms.append(SingletonTerm(source_path=chain_name))
        ctx.input_channels.append(chain_name)
        return chain_name

    # OperatorExpression: recurse into operands
    if SysideAdapter.is_instance(node, "OperatorExpression"):
        operator = getattr(node, "operator", "+")
        operands = list(getattr(node, "operands", []))
        if len(operands) == 2:
            left = _walk_aggregation_ast(operands[0], mult_lookup, ctx)
            right = _walk_aggregation_ast(operands[1], mult_lookup, ctx)
            op_str = OPERATOR_MAP.get(operator, f" {operator} ")
            return f"({left}{op_str}{right})"
        if len(operands) == 1:
            inner = _walk_aggregation_ast(operands[0], mult_lookup, ctx)
            if operator == "-":
                return f"-{inner}"
            return f"{operator}({inner})"
        if operands:
            parts = [
                _walk_aggregation_ast(op, mult_lookup, ctx)
                for op in operands
            ]
            op_str = OPERATOR_MAP.get(operator, f" {operator} ")
            return op_str.join(parts)
        return operator

    # FeatureReferenceExpression: local attribute → LocalTerm
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        ref_name = extract_feature_reference_name(node)
        ctx.local_terms.append(LocalTerm(attribute_name=ref_name))
        return ref_name

    # InvocationExpression: sum() → parametric multiply
    if hasattr(node, "function") and hasattr(node.function, "name"):
        func_name = node.function.name
        operands = list(getattr(node, "operands", []))

        if func_name == "sum" and operands:
            operand = _unwrap_invocation(operands[0])
            if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
                chain_name = extract_feature_chain_name(operand)
            else:
                chain_name = extract_feature_reference_name(operand)

            parts = chain_name.split(".", 1)
            if len(parts) == 2:
                part_name, attr_name = parts
                mult_data = mult_lookup.get(part_name)
                if mult_data and mult_data.count_attribute_name:
                    ctx.sum_terms.append(SumTerm(
                        part_usage_name=part_name,
                        attribute_name=attr_name,
                        multiplicity_attr=mult_data.count_attribute_name,
                        multiplicity_count=mult_data.count,
                    ))
                    ctx.input_channels.append(chain_name)
                    ctx.entry_points.append(mult_data.count_attribute_name)
                    return f"({mult_data.count_attribute_name} * {chain_name})"

                # No multiplicity found — log warning, emit unresolved SumTerm
                logger.warning(
                    "sum(%s) has no multiplicity data for '%s'",
                    chain_name,
                    part_name,
                )
                ctx.sum_terms.append(SumTerm(
                    part_usage_name=part_name,
                    attribute_name=attr_name,
                    multiplicity_attr=None,
                    multiplicity_count=None,
                ))
                ctx.input_channels.append(chain_name)
                return chain_name

            # Single-element sum (unusual)
            ctx.local_terms.append(LocalTerm(attribute_name=chain_name))
            return chain_name

        # Non-sum invocation — unwrap known wrappers before marking unsupported
        if func_name in _KNOWN_WRAPPER_FUNCTIONS and operands:
            unwrapped = _unwrap_invocation(node)
            if unwrapped is not node:
                return _walk_aggregation_ast(unwrapped, mult_lookup, ctx)

        # Truly unsupported invocation — mark and reconstruct
        ctx.has_unsupported = True
        args = ", ".join(
            _walk_aggregation_ast(op, mult_lookup, ctx)
            for op in operands
        )
        return f"{func_name}({args})"

    # Literals: delegate to expression_utils (consistent with is_instance pattern)
    if is_literal_expression(node):
        return reconstruct_expression(node)

    # Unknown node type
    ctx.has_unsupported = True
    logger.warning(
        "Unrecognized AST node type in aggregation expression: %s",
        type(node).__name__,
    )
    return str(node)


def build_aggregation_expression(
    redef: RedefinitionData,
    multiplicities: list[MultiplicityData],
    part_element: Any,
) -> AggregationExpressionData | None:
    """Transform an EXPRESSION-type :>> redefinition into AggregationExpressionData.

    Takes an EXPRESSION-type :>> redefinition from an assembly PartDef and:
    1. Walks the expression AST
    2. Detects InvocationExpression nodes with function.name == 'sum'
    3. Decomposes into SumTerm, SingletonTerm, LocalTerm
    4. Transforms sum() to parametric multiply
    5. Builds the transformed Python expression string

    Args:
        redef: An EXPRESSION-type RedefinitionData with expression_ast.
        multiplicities: MultiplicityData for the owning PartDef's child PartUsages.
        part_element: The owning PartDefinition element.

    Returns:
        AggregationExpressionData, or None if redef is not EXPRESSION type.
    """
    if redef.redefinition_type != RedefinitionType.EXPRESSION:
        return None
    if redef.expression_ast is None:
        return None

    # Build multiplicity lookup by part_usage_name
    mult_lookup = {m.part_usage_name: m for m in multiplicities}

    # Walk the AST
    ctx = _AggregationContext()
    transformed = _walk_aggregation_ast(
        redef.expression_ast, mult_lookup, ctx,
    )

    return AggregationExpressionData(
        owning_part_qn=redef.owning_part_qn,
        owning_part_name=sanitize_name(getattr(part_element, "name", "")),
        attribute_name=redef.attribute_name,
        raw_expression_text=redef.expression_text,
        transformed_expression=transformed,
        sum_terms=ctx.sum_terms,
        singleton_terms=ctx.singleton_terms,
        local_terms=ctx.local_terms,
        input_channels=ctx.input_channels,
        entry_points=ctx.entry_points,
        has_unsupported_nodes=ctx.has_unsupported,
    )


def extract_hierarchy_data(model: Any) -> HierarchyExtractionResult:
    """Top-level orchestrator: extract all hierarchy data from the model.

    Iterates all PartDefinition elements to extract redefinitions,
    multiplicities, and aggregation expressions. Scans design-level
    PartUsages for deep-path overrides.

    Args:
        model: The loaded SysML model.

    Returns:
        HierarchyExtractionResult with all extracted data.
    """
    all_redefinitions: list[RedefinitionData] = []
    all_multiplicities: list[MultiplicityData] = []
    all_aggregations: list[AggregationExpressionData] = []
    warnings: list[str] = []
    part_usage_names: dict[str, set[str]] = {}

    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        redefs = extract_redefinitions(part_def)
        all_redefinitions.extend(redefs)

        mults = extract_multiplicities(part_def)
        all_multiplicities.extend(mults)

        # Collect ALL child PartUsage names (both multiplicity and singleton)
        owning_qn = build_element_qualified_name(part_def)
        names: set[str] = set()
        for member in getattr(part_def, "owned_members", []):
            if SysideAdapter.is_instance(member, "PartUsage"):
                name = sanitize_name(getattr(member, "name", ""))
                if name:
                    names.add(name)
        if names:
            part_usage_names[owning_qn] = names

        # Build aggregation expressions from EXPRESSION-type redefinitions
        for redef in redefs:
            if redef.redefinition_type == RedefinitionType.EXPRESSION:
                agg = build_aggregation_expression(redef, mults, part_def)
                if agg is not None:
                    if agg.has_unsupported_nodes:
                        warnings.append(
                            f"Aggregation expression on "
                            f"{agg.owning_part_qn}.{agg.attribute_name} "
                            f"contains unsupported AST nodes"
                        )
                    # BF-7: Find CHAIN-type aliases for this aggregation attribute
                    # e.g., :>> total_capex = capital_cost creates alias "total_capex"
                    for sibling in redefs:
                        if (
                            sibling.redefinition_type == RedefinitionType.CHAIN
                            and sibling.source_path
                            and sibling.source_path.endswith(agg.attribute_name)
                            and sibling.attribute_name != agg.attribute_name
                        ):
                            agg.aliases.append(sibling.attribute_name)
                    all_aggregations.append(agg)

    # Design-level overrides from PartUsages
    part_usages = SysideAdapter.elements_of_type(model, "PartUsage")
    design_overrides = extract_design_overrides(part_usages)

    return HierarchyExtractionResult(
        redefinitions=all_redefinitions,
        design_overrides=design_overrides,
        multiplicities=all_multiplicities,
        aggregation_expressions=all_aggregations,
        warnings=warnings,
        part_usage_names=part_usage_names,
    )
