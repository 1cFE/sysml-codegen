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
from typing import Any, cast

import agentic_mbse.sysml.aggregation as shared_aggregation
from agentic_mbse.sysml import hierarchy as shared_hierarchy
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
)
from sysml_codegen.extraction.usage_extractor import (
    most_specific,
    owned_feature_typing_targets,
    user_partdef_lookup,
)

logger = logging.getLogger(__name__)

# D3-8: aggregation-expression operator translation. OPERATOR_MAP spells every
# operator correctly *except* `^`, which it maps to Python bitwise-XOR (` ^ `);
# in an aggregation (as in SysML) `^` is exponentiation and must become ` ** `.
# The comparison/logical translations (`> < == != and or implies not ...`) are
# kept as-is — swapping wholesale to PYTHON_OPERATOR_MAP would drop them and
# falsely trip has_unsupported on a valid `sum(x) > threshold` aggregation. An
# operator absent from this map is genuinely untranslatable → has_unsupported.
AGG_PYTHON_OPS = {**OPERATOR_MAP, "^": " ** "}


def _chain_sibling_aliases_aggregation(sibling: RedefinitionData, agg_attribute_name: str) -> bool:
    """True if a CHAIN redefinition aliases the aggregation attribute (REQ-HR-07).

    A sibling aliases the aggregation when its ``source_path`` equals the attribute
    name exactly, or is a dotted path whose leaf equals it (``parent.capital_cost``
    aliases ``capital_cost``). The dotted-leaf match is by leaf ONLY — it does not
    check which part the path references (doc-25 "Edge case"), so a differently-parted
    dotted path with the same leaf still matches. A bare-name suffix like
    ``total_capital_cost`` does NOT match, because the ``"." +`` prefix requires a dot
    boundary. The sibling must redefine a differently-named attribute.
    """
    if sibling.redefinition_type != RedefinitionType.CHAIN or not sibling.source_path:
        return False
    matches_leaf = sibling.source_path == agg_attribute_name or sibling.source_path.endswith(
        "." + agg_attribute_name
    )
    return matches_leaf and sibling.attribute_name != agg_attribute_name


def _extract_single_redefinition(member: Any, owning_qn: str) -> RedefinitionData | None:
    """Compatibility alias for the shared one-member redefinition classifier."""
    return cast(
        RedefinitionData | None,
        shared_hierarchy.classify_redefinition(member, owning_qn),
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
    return cast(list[RedefinitionData], shared_hierarchy.extract_redefinitions(part_element))


def _keep_plain_usage_override(redef_data: RedefinitionData) -> bool:
    """Keep a newly-scanned plain-usage :>> override only when its RHS is LITERAL.

    CHAIN/EXPRESSION overrides on plain usages (e.g. catf_mfe's cross-part refs,
    ife_plant shape 4) are Item 10's job; keeping them out of design_overrides
    means they never reach the literal-rewrite path and never churn a baseline
    (REQ-HR-08 / D3, INV-1).
    """
    return redef_data.redefinition_type is RedefinitionType.LITERAL


def extract_design_overrides(
    part_usages: Iterable[Any],
) -> list[RedefinitionData]:
    """Scan design-level PartUsages for :>> overrides.

    Two shapes carry a :>> override:
    - A 'part redefines' usage (non-empty owned_redefinitions on the usage
      itself). Its owned_members may hold deep-path overrides like
      :>> pv_module.wattage = 400.0. All RHS types are captured (INV-4).
    - A plain typed usage (empty owned_redefinitions). The override lives on a
      member ReferenceUsage — e.g. :>> widget.base_cost = 50.0. These are
      captured too (REQ-HR-08) but filtered to LITERAL RHS (D3); CHAIN/EXPRESSION
      plain overrides are Item 10's job and stay out of design_overrides (INV-1).

    Members are scanned regardless of the usage kind; ``_extract_single_redefinition``
    returns None for non-ReferenceUsage / value-less members, so the scan is cheap.

    Args:
        part_usages: Iterable of PartUsage elements to scan. The caller
            (orchestrator) is responsible for filtering to design-level
            PartUsages via SysideAdapter.elements_of_type().

    Returns:
        List of RedefinitionData for each :>> found on design PartUsages.
    """
    results: list[RedefinitionData] = []

    for usage in part_usages:
        is_part_redefines = bool(getattr(usage, "owned_redefinitions", None))

        usage_qn = build_element_qualified_name(usage)

        for member in getattr(usage, "owned_members", []):
            redef_data = cast(
                RedefinitionData | None,
                shared_hierarchy.classify_redefinition(member, usage_qn),
            )
            if redef_data is None:
                continue
            if not is_part_redefines and not _keep_plain_usage_override(redef_data):
                continue  # plain-usage CHAIN/EXPRESSION override — Item 10's job
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
    return cast(list[MultiplicityData], shared_hierarchy.extract_multiplicities(part_element))


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


def _agg_operator_str(operator: Any, ctx: _AggregationContext) -> str:
    """Translate an aggregation operator to its Python spelling (D3-8).

    `operator` is a SysIDE `Operator` enum on real nodes (a plain str in unit
    stubs); normalize with str() to the SysML symbol first — the same idiom
    reconstruct_operator_expression uses (expression_utils.py:170) — then look up
    the `**`-corrected translation. An operator in neither the arithmetic nor the
    comparison/logical map is untranslatable: it sets ctx.has_unsupported and
    warns (mirroring the unknown-node arm), instead of silently passing the raw
    operator through (the pre-fix path, which stringified `^` to Python XOR).
    """
    op_key = str(operator)
    op_str = AGG_PYTHON_OPS.get(op_key)
    if op_str is None:
        ctx.has_unsupported = True
        logger.warning(
            "Unsupported operator '%s' in aggregation expression; marking aggregation unsupported.",
            op_key,
        )
        return f" {op_key} "
    return op_str


def _apply_sum_term(
    neutral_term: Any,
    mult_lookup: dict[str, MultiplicityData],
    ctx: _AggregationContext,
) -> str:
    part_name = neutral_term.part_usage_name
    attr_name = neutral_term.attribute_name
    chain_name = f"{part_name}.{attr_name}"
    mult_data = mult_lookup.get(part_name)
    if mult_data and mult_data.count_attribute_name:
        ctx.sum_terms.append(
            SumTerm(
                part_usage_name=part_name,
                attribute_name=attr_name,
                multiplicity_attr=mult_data.count_attribute_name,
                multiplicity_count=mult_data.count,
            )
        )
        ctx.input_channels.append(chain_name)
        ctx.entry_points.append(mult_data.count_attribute_name)
        return f"({mult_data.count_attribute_name} * {chain_name})"

    logger.warning(
        "sum(%s) has no multiplicity data for '%s'",
        chain_name,
        part_name,
    )
    ctx.sum_terms.append(
        SumTerm(
            part_usage_name=part_name,
            attribute_name=attr_name,
            multiplicity_attr=None,
            multiplicity_count=None,
        )
    )
    ctx.input_channels.append(chain_name)
    return chain_name


def _render_neutral_aggregation_node(
    node: Any,
    decomposition: Any,
    mult_lookup: dict[str, MultiplicityData],
    ctx: _AggregationContext,
) -> str:
    """Render a shared neutral aggregation node using codegen-local policy."""
    if isinstance(node, shared_aggregation.NullNode):
        return ""

    if isinstance(node, shared_aggregation.FeatureChainNode):
        ctx.singleton_terms.append(SingletonTerm(source_path=node.source_path))
        ctx.input_channels.append(node.source_path)
        return node.source_path

    if isinstance(node, shared_aggregation.FeatureReferenceNode):
        ctx.local_terms.append(LocalTerm(attribute_name=node.attribute_name))
        return node.attribute_name

    if isinstance(node, shared_aggregation.LiteralNode):
        return node.render_text

    if isinstance(node, shared_aggregation.SumNode):
        neutral_term = decomposition.sum_terms[node.term_index]
        return _apply_sum_term(neutral_term, mult_lookup, ctx)

    if isinstance(node, shared_aggregation.OperatorNode):
        operands = [
            _render_neutral_aggregation_node(op, decomposition, mult_lookup, ctx)
            for op in node.operands
        ]
        if len(operands) == 2:
            op_str = _agg_operator_str(node.operator, ctx)
            return f"({operands[0]}{op_str}{operands[1]})"
        if len(operands) == 1:
            inner = operands[0]
            if node.operator == "-":
                return f"-{inner}"
            return f"{node.operator}({inner})"
        if operands:
            op_str = _agg_operator_str(node.operator, ctx)
            return op_str.join(operands)
        return node.operator

    if isinstance(node, shared_aggregation.InvocationNode):
        if node.unsupported:
            ctx.has_unsupported = True
        args = ", ".join(
            _render_neutral_aggregation_node(op, decomposition, mult_lookup, ctx)
            for op in node.operands
        )
        return f"{node.function_name}({args})"

    if isinstance(node, shared_aggregation.UnsupportedNode):
        ctx.has_unsupported = True
        logger.warning(node.diagnostic_message)
        return node.fallback_render

    ctx.has_unsupported = True
    logger.warning(
        "Unrecognized neutral aggregation node type: %s",
        type(node).__name__,
    )
    return str(node)


def _walk_aggregation_ast(
    node: Any,
    mult_lookup: dict[str, MultiplicityData],
    ctx: _AggregationContext,
) -> str:
    """Compatibility shim that renders the shared neutral decomposition locally.

    Args:
        node: AST node to process.
        mult_lookup: Multiplicity data keyed by part_usage_name.
        ctx: Mutable context collecting terms, channels, etc.

    Returns:
        Transformed expression text for this node.
    """
    decomposition = shared_aggregation.decompose_aggregation_expression(node)
    return _render_neutral_aggregation_node(
        decomposition.root,
        decomposition,
        mult_lookup,
        ctx,
    )


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
        redef.expression_ast,
        mult_lookup,
        ctx,
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


def _index_usage_level_retypes(
    part_usages: Iterable[Any],
    base_type_map: dict[tuple[str, str], str],
    qn_to_partdef: dict[str, Any],
) -> dict[tuple[str, str], str]:
    """Index genuine usage-level retypes of inherited part usages, keyed by the
    CONTAINER usage's instance QN (Item 10 two-level specialization, Phase 8).

    The def-level ``usage_type_map`` keys retypes by the declaring PartDef. But a
    two-level specialization retypes an inherited part usage ON A PART USAGE — e.g.
    fusion-tea's ``part hif_plant : 'IFE Power Plant' { part :>> driver : 'HIF Driver' }``,
    where the retype lives on the ``hif_plant`` usage, not on any def. A type-select
    keyed on the consumer's declaring def then sees only the base type (``'IFE Driver'``)
    and misses the retype.

    This indexes ``(container_usage_qn, member_name) -> retyped_def`` for exactly the
    members that are a GENUINE retype: a ``:>>`` redefinition (``owned_redefinitions``)
    whose most-specific owned type DIFFERS from the base def's declared type for that
    member. A value-only ``:>>`` override that keeps the same type (e.g. solar_battery's
    ``:>> solar_array {...}``) is excluded, so no non-two-level fixture gains an entry —
    committed snapshots stay byte-identical.

    ``base_type_map`` is the fully-built def-level ``usage_type_map`` (read-only here).
    """
    new_entries: dict[tuple[str, str], str] = {}
    for usage in part_usages:
        container_targets = [
            qn
            for target in owned_feature_typing_targets(usage)
            if (qn := build_element_qualified_name(target))
        ]
        container_def, _ = most_specific(container_targets, qn_to_partdef)
        if not container_def:
            continue
        for member in getattr(usage, "owned_members", []):
            if not SysideAdapter.is_instance(member, "PartUsage"):
                continue
            if not getattr(member, "owned_redefinitions", None):
                continue  # plain typed usage, not a :>> redefinition
            name = sanitize_name(getattr(member, "name", ""))
            if not name:
                continue
            target_qns = [
                qn
                for target in owned_feature_typing_targets(member)
                if (qn := build_element_qualified_name(target))
            ]
            winner, _ = most_specific(target_qns, qn_to_partdef)
            if not winner:
                continue
            if winner != base_type_map.get((container_def, name)):
                # Genuine retype-of-inherited-usage: the target type differs from the
                # base-declared type. Key by the container usage's instance QN so the
                # resolver's instance-aware type-select reaches the specialized def.
                new_entries[(build_element_qualified_name(usage), name)] = winner
    return new_entries


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
    usage_type_map: dict[tuple[str, str], str] = {}
    # {__-form QN: PartDefElement} for the most-specific-owned-typing pick (FIX 2).
    qn_to_partdef = user_partdef_lookup(model)

    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        redefs = extract_redefinitions(part_def)
        all_redefinitions.extend(redefs)

        mults = extract_multiplicities(part_def)
        all_multiplicities.extend(mults)

        # Collect ALL child PartUsage names (both multiplicity and singleton)
        # and extract usage→type PartDef mapping for LITERAL redefinition lookup.
        owning_qn = build_element_qualified_name(part_def)
        names: set[str] = set()
        for member in getattr(part_def, "owned_members", []):
            if SysideAdapter.is_instance(member, "PartUsage"):
                name = sanitize_name(getattr(member, "name", ""))
                if name:
                    names.add(name)
                    # Resolve the usage's type to its MOST-SPECIFIC owned FeatureTyping
                    # target — not next(iter(member.types)), whose first entry is a
                    # supertype for a retyped usage (REQ-LVP-08). Incomparable multi-
                    # typings resolve to sorted-first with a V10 warning.
                    target_qns = [
                        qn
                        for target in owned_feature_typing_targets(member)
                        if (qn := build_element_qualified_name(target))
                    ]
                    winner, incomparable = most_specific(target_qns, qn_to_partdef)
                    if winner is None:
                        # No owned FeatureTyping to compare — an untyped part (implicit
                        # library `Part`) or a redefinition that inherits its typing.
                        # There is nothing for the most-specific pick to change, so
                        # keep the historical position-0 type. This is the case the
                        # retyping fix does NOT touch, and it holds baselines identical.
                        try:
                            winner = build_element_qualified_name(next(iter(member.types)))
                        except (StopIteration, TypeError, AttributeError):
                            winner = None
                    if winner:
                        usage_type_map[(owning_qn, name)] = winner
                        if incomparable:
                            msg = (
                                f"Usage '{owning_qn}.{name}' has multiple incomparable "
                                f"owned types {sorted(target_qns)}; resolved defaults "
                                f"against '{winner}' (first in stable order)."
                            )
                            logger.warning(msg)
                            warnings.append(msg)
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
                        if _chain_sibling_aliases_aggregation(sibling, agg.attribute_name):
                            agg.aliases.append(sibling.attribute_name)
                    all_aggregations.append(agg)

    # Design-level overrides from PartUsages (materialized: iterated twice below).
    part_usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))
    design_overrides = extract_design_overrides(part_usages)

    # Item 10 two-level specialization (Phase 8): index usage-level retypes of inherited
    # part usages, keyed by the container usage's instance QN. usage_type_map now carries
    # def-level entries only; pass it as the read-only base-type source before extending.
    usage_type_map.update(_index_usage_level_retypes(part_usages, usage_type_map, qn_to_partdef))

    return HierarchyExtractionResult(
        redefinitions=all_redefinitions,
        design_overrides=design_overrides,
        multiplicities=all_multiplicities,
        aggregation_expressions=all_aggregations,
        warnings=warnings,
        part_usage_names=part_usage_names,
        usage_type_map=usage_type_map,
    )
