#!/usr/bin/env python3
"""Aggregation Wiring Diagnostic Spikes (H1–H4).

Read-only investigative script that empirically verifies 4 hypotheses
about the aggregation wiring gap (58 of 70 inputs misclassified as
entry points). Each spike runs against the real solar_battery model
and produces a structured verdict.

  Spike A: H1 — FCE is subtype of OE in SysIDE type system
  Spike B: H2 — Check reorder reclassifies ~37 LocalTerms to SingletonTerms
  Spike C: H3 — Sibling agg outputs resolvable via Key_D
  Spike D: H4 — Plant-level SingletonTerms resolve through actual code path

No files under src/ are modified. All instrumentation lives here.

Usage:
    uv run python scripts/spike_agg_wiring_h1_h4.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.data_models import (
    LocalTerm,
    MultiplicityData,
    RedefinitionType,
    SingletonTerm,
    SumTerm,
)
from sysml_codegen.extraction.expression_utils import (
    OPERATOR_MAP,
    extract_feature_chain_name,
    extract_feature_reference_name,
    is_literal_expression,
    reconstruct_expression,
)
from sysml_codegen.extraction.hierarchy_resolver import (
    _AggregationContext,
    _KNOWN_WRAPPER_FUNCTIONS,
    _unwrap_invocation,
)
from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.generation.initialization import PipelineContext, build_pipeline_context
from sysml_codegen.resolution.graph_builder import _resolve_aggregation_input_channel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = REPO_ROOT / "tests" / "fixtures" / "solar_battery_model"


# ---------------------------------------------------------------------------
# Shared Infrastructure
# ---------------------------------------------------------------------------
def _load_context() -> PipelineContext:
    """Load pipeline context and validate required fields."""
    if not MODEL_PATH.exists():
        print(f"ERROR: Model path not found: {MODEL_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading model from: {MODEL_PATH}")
    ctx = build_pipeline_context([MODEL_PATH])

    if ctx.output_registry is None:
        print("ERROR: output_registry is None — pipeline did not construct it", file=sys.stderr)
        sys.exit(1)

    if not ctx.aggregation_expressions:
        print("ERROR: no aggregation_expressions found", file=sys.stderr)
        sys.exit(1)

    if ctx.hierarchy_data is None:
        print("ERROR: hierarchy_data is None", file=sys.stderr)
        sys.exit(1)

    print(f"Model loaded. {len(ctx.aggregation_expressions)} aggregation expressions found.")
    print(f"OutputRegistry: {ctx.output_registry}")
    print(f"Redefinitions: {len(ctx.hierarchy_data.redefinitions)}")

    return ctx


def _print_verdict(result: dict) -> None:
    """Print formatted verdict for a single spike."""
    print(f"\n{'=' * 70}")
    print(f"  {result['hypothesis']}")
    print(f"  Verdict: {result['verdict']}")
    print(f"{'=' * 70}")

    evidence = result.get("evidence", {})
    for key, value in evidence.items():
        if key == "node_details":
            print(f"\n  Node Details ({len(value)} nodes):")
            for i, node in enumerate(value, 1):
                extras = []
                if node.get("operator"):
                    extras.append(f"op={node['operator']}")
                if node.get("target_feature"):
                    extras.append(f"target={node['target_feature']}")
                if node.get("operand_0_type"):
                    extras.append(f"operand0={node['operand_0_type']}")
                extra_str = f", {', '.join(extras)}" if extras else ""
                print(
                    f"    {i:3d}. [{node['assembly']:20s}] {node['attribute']:25s} "
                    f"{node['node_text']:40s} "
                    f"OE={str(node['is_oe']):5s} FCE={str(node['is_fce']):5s}"
                    f"{extra_str}"
                )
        elif key == "reclassified_terms":
            print(f"\n  Reclassified Terms ({len(value)}):")
            for i, term in enumerate(value, 1):
                print(
                    f"    {i:3d}. [{term['assembly']:20s}] {term['attribute']:25s} "
                    f"{term['was']}  →  {term['now']}"
                )
        elif key == "remaining_local_terms":
            print(f"\n  Remaining Local Terms ({len(value)}):")
            for i, term in enumerate(value, 1):
                print(
                    f"    {i:3d}. [{term['assembly']:20s}] {term['attribute']:25s} "
                    f"{term['local_term']}"
                )
        elif key == "queries":
            print(f"\n  Registry Queries ({len(value)}):")
            for i, q in enumerate(value, 1):
                status = "HIT" if q["resolved"] else "MISS"
                result_str = q["key_d_result"] or "None"
                # Truncate long channel names for readability
                if isinstance(result_str, str) and len(result_str) > 50:
                    result_str = "..." + result_str[-47:]
                print(
                    f"    {i:3d}. [{q['assembly']:20s}] {q['expression']:15s} "
                    f"{q['local_term']:25s} Key_D={q['key_d_query']:35s} "
                    f"→ {status:4s} {result_str}"
                )
        elif key == "resolution_traces":
            print(f"\n  Resolution Traces ({len(value)}):")
            for i, t in enumerate(value, 1):
                s1 = t["step_1_chain_redef"]["result"]
                s2 = t["step_2_scoped_key"]["result"]
                s3 = t["step_3_unscoped_key_d"]["result"]
                channel = t.get("channel") or "None"
                if isinstance(channel, str) and len(channel) > 45:
                    channel = "..." + channel[-42:]
                print(
                    f"    {i:3d}. {t['source_path']:35s} "
                    f"S1={s1:4s} S2={s2:4s} S3={s3:4s} "
                    f"-> {t['final_result']:10s} via {t['resolved_via']}"
                )
                if t["final_result"] == "RESOLVED":
                    print(f"         channel: {channel}")
        elif key == "negative_test_misc_hardware_cost":
            print(f"\n  Negative Tests ({len(value)}):")
            for i, n in enumerate(value, 1):
                status = "PASS (unresolved)" if n["correctly_unresolved"] else "FAIL (resolved!)"
                print(
                    f"    {i:3d}. [{n['assembly']:20s}] {n['expression']:15s} "
                    f"{n['local_term']:25s} Key_D={n['key_d_query']:35s} "
                    f"→ {status}"
                )
        elif isinstance(value, dict):
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")

    if result.get("notes"):
        print(f"\n  Notes: {result['notes']}")
    print()


# ---------------------------------------------------------------------------
# Spike A: H1 — FCE is subtype of OE in SysIDE type system
# ---------------------------------------------------------------------------
def _collect_non_sum_leaves(node: Any) -> list[Any]:
    """Walk expression tree, collecting non-sum leaf nodes.

    Uses FCE-before-OE check ordering (the proposed fix) so that
    FeatureChainExpression nodes are correctly identified as leaves
    rather than being recursed into as OperatorExpression. The spike
    then checks both is_instance types on each leaf to verify H1.

    Skips InvocationExpression(sum) nodes entirely (SumTerms).
    """
    if node is None:
        return []

    # FCE check FIRST — catch dotted refs (e.g., "array_bos.capital_cost")
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return [node]

    # FRE — bare name references (e.g., "misc_hardware_cost")
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return [node]

    # OE — recurse into operands (only genuine arithmetic OE reaches here)
    if SysideAdapter.is_instance(node, "OperatorExpression"):
        operands = list(getattr(node, "operands", []))
        leaves: list[Any] = []
        for op in operands:
            leaves.extend(_collect_non_sum_leaves(op))
        return leaves

    # InvocationExpression — check if sum()
    if hasattr(node, "function") and hasattr(node.function, "name"):
        if node.function.name == "sum":
            return []  # SumTerm — skip entirely
        # Non-sum invocation — unwrap known wrappers
        from sysml_codegen.extraction.hierarchy_resolver import _unwrap_invocation

        unwrapped = _unwrap_invocation(node)
        if unwrapped is not node:
            return _collect_non_sum_leaves(unwrapped)
        return [node]  # Truly unknown invocation

    # Literal or unknown — leaf
    return [node]


def _get_node_text(node: Any) -> str:
    """Extract readable text from an AST node."""
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return extract_feature_chain_name(node)
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(node)
    return type(node).__name__


def spike_a_ast_dual_match(ctx: PipelineContext) -> dict:
    """H1: FCE is subtype of OE in SysIDE type system.

    For each aggregation expression, walks the + tree to find non-sum
    leaf nodes, then checks is_instance for both OperatorExpression
    and FeatureChainExpression on each.
    """
    assert ctx.hierarchy_data is not None

    # Find EXPRESSION-type redefinitions with ASTs, deduplicate by (part_qn, attr)
    seen: set[tuple[str, str]] = set()
    node_details: list[dict] = []

    for redef in ctx.hierarchy_data.redefinitions:
        if redef.redefinition_type != RedefinitionType.EXPRESSION:
            continue
        if redef.expression_ast is None:
            continue

        key = (redef.owning_part_qn, redef.attribute_name)
        if key in seen:
            continue
        seen.add(key)

        assembly = redef.owning_part_qn.split("__")[-1].lower()

        # Walk the expression tree to get non-sum leaf nodes
        leaves = _collect_non_sum_leaves(redef.expression_ast)

        for leaf in leaves:
            is_oe = SysideAdapter.is_instance(leaf, "OperatorExpression")
            is_fce = SysideAdapter.is_instance(leaf, "FeatureChainExpression")

            detail: dict[str, Any] = {
                "assembly": assembly,
                "attribute": redef.attribute_name,
                "node_text": _get_node_text(leaf),
                "is_oe": is_oe,
                "is_fce": is_fce,
            }

            if is_oe:
                detail["operator"] = getattr(leaf, "operator", None)
                operands = list(getattr(leaf, "operands", []))
                if operands:
                    detail["operand_0_type"] = type(operands[0]).__name__

            if is_fce:
                chain_name = extract_feature_chain_name(leaf)
                parts = chain_name.rsplit(".", 1)
                detail["target_feature"] = parts[-1] if len(parts) > 1 else chain_name

            node_details.append(detail)

    # Tally results
    dual_match = sum(1 for d in node_details if d["is_oe"] and d["is_fce"])
    fce_only = sum(1 for d in node_details if not d["is_oe"] and d["is_fce"])
    oe_only = sum(1 for d in node_details if d["is_oe"] and not d["is_fce"])
    neither = sum(1 for d in node_details if not d["is_oe"] and not d["is_fce"])

    # H1 is CONFIRMED if every FCE node also matches OE (fce_only == 0, dual_match > 0)
    if dual_match > 0 and fce_only == 0:
        verdict = "CONFIRMED"
    else:
        verdict = "FALSIFIED"

    return {
        "hypothesis": "H1: FCE is subtype of OE in SysIDE type system",
        "verdict": verdict,
        "evidence": {
            "nodes_tested": len(node_details),
            "dual_match_fce_and_oe": dual_match,
            "fce_only": fce_only,
            "oe_only": oe_only,
            "neither_fce_nor_oe": neither,
            "node_details": node_details,
        },
        "notes": (
            f"{dual_match} of {len(node_details)} non-sum leaf nodes match BOTH "
            f"OperatorExpression and FeatureChainExpression. "
            + (
                "This confirms the subtype relationship causing Bug A."
                if verdict == "CONFIRMED"
                else "Unexpected — FCE does NOT universally match OE."
            )
        ),
    }


# ---------------------------------------------------------------------------
# Spike B: H2 — Check reorder produces ~37 reclassifications
# ---------------------------------------------------------------------------
def _walk_aggregation_ast_patched(
    node: Any,
    mult_lookup: dict[str, MultiplicityData],
    ctx: _AggregationContext,
) -> str:
    """Patched copy of _walk_aggregation_ast with FCE check before OE.

    LOCAL COPY — no module-level monkey-patching. The ONLY change from the
    original is that FeatureChainExpression is checked BEFORE OperatorExpression,
    preventing FCE nodes from being caught by the OE branch.
    """
    if node is None:
        return ""

    # *** THE FIX: Check FCE BEFORE OE ***
    # FeatureChainExpression: child.attr → SingletonTerm
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
            left = _walk_aggregation_ast_patched(operands[0], mult_lookup, ctx)
            right = _walk_aggregation_ast_patched(operands[1], mult_lookup, ctx)
            op_str = OPERATOR_MAP.get(operator, f" {operator} ")
            return f"({left}{op_str}{right})"
        if len(operands) == 1:
            inner = _walk_aggregation_ast_patched(operands[0], mult_lookup, ctx)
            if operator == "-":
                return f"-{inner}"
            return f"{operator}({inner})"
        if operands:
            parts = [
                _walk_aggregation_ast_patched(op, mult_lookup, ctx)
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

                ctx.sum_terms.append(SumTerm(
                    part_usage_name=part_name,
                    attribute_name=attr_name,
                    multiplicity_attr=None,
                    multiplicity_count=None,
                ))
                ctx.input_channels.append(chain_name)
                return chain_name

            ctx.local_terms.append(LocalTerm(attribute_name=chain_name))
            return chain_name

        # Non-sum invocation — unwrap known wrappers
        if func_name in _KNOWN_WRAPPER_FUNCTIONS and operands:
            unwrapped = _unwrap_invocation(node)
            if unwrapped is not node:
                return _walk_aggregation_ast_patched(unwrapped, mult_lookup, ctx)

        ctx.has_unsupported = True
        args = ", ".join(
            _walk_aggregation_ast_patched(op, mult_lookup, ctx)
            for op in operands
        )
        return f"{func_name}({args})"

    # Literals
    if is_literal_expression(node):
        return reconstruct_expression(node)

    # Unknown node type
    ctx.has_unsupported = True
    return str(node)


def spike_b_check_reorder(ctx: PipelineContext) -> dict:
    """H2: Check reorder reclassifies ~37 LocalTerms to SingletonTerms.

    Compares term classification between the CURRENT walker (OE before FCE)
    and a PATCHED walker (FCE before OE). Reports before/after counts,
    verifies zero SumTerm regression, and lists each reclassified term.
    """
    assert ctx.hierarchy_data is not None

    # Build multiplicity lookup grouped by owning PartDef QN
    mult_by_partdef: dict[str, dict[str, MultiplicityData]] = {}
    for m in ctx.hierarchy_data.multiplicities:
        mult_by_partdef.setdefault(m.owning_part_def_qn, {})[m.part_usage_name] = m

    # Build index of EXPRESSION-type redefinitions for AST access
    redef_index: dict[tuple[str, str], Any] = {}
    for redef in ctx.hierarchy_data.redefinitions:
        if redef.redefinition_type == RedefinitionType.EXPRESSION and redef.expression_ast is not None:
            redef_index[(redef.owning_part_qn, redef.attribute_name)] = redef.expression_ast

    # Match aggregation expressions to their ASTs (deduplicate by PartDef)
    seen: set[tuple[str, str]] = set()

    # Totals
    before_sum = 0
    before_singleton = 0
    before_local = 0
    after_sum = 0
    after_singleton = 0
    after_local = 0
    reclassified_terms: list[dict] = []
    remaining_local_terms: list[dict] = []

    for agg in ctx.aggregation_expressions:
        key = (agg.expression.owning_part_qn, agg.expression.attribute_name)
        if key in seen:
            continue
        seen.add(key)

        expr = agg.expression
        assembly = expr.owning_part_qn.split("__")[-1].lower()

        # "Before" — current classification
        before_sum += len(expr.sum_terms)
        before_singleton += len(expr.singleton_terms)
        before_local += len(expr.local_terms)

        # "After" — patched walker
        ast = redef_index.get(key)
        if ast is None:
            # No AST found — carry forward current counts
            after_sum += len(expr.sum_terms)
            after_singleton += len(expr.singleton_terms)
            after_local += len(expr.local_terms)
            continue

        mult_lookup = mult_by_partdef.get(expr.owning_part_qn, {})
        patched_ctx = _AggregationContext()
        _walk_aggregation_ast_patched(ast, mult_lookup, patched_ctx)

        after_sum += len(patched_ctx.sum_terms)
        after_singleton += len(patched_ctx.singleton_terms)
        after_local += len(patched_ctx.local_terms)

        # Identify reclassified terms: new SingletonTerms (before had 0)
        for st in patched_ctx.singleton_terms:
            # The "was" LocalTerm used the first part of the source_path
            was_name = st.source_path.split(".")[0] if "." in st.source_path else st.source_path
            reclassified_terms.append({
                "assembly": assembly,
                "attribute": expr.attribute_name,
                "was": f"LocalTerm(attribute_name='{was_name}')",
                "now": f"SingletonTerm(source_path='{st.source_path}')",
            })

        # Identify remaining LocalTerms (genuinely local)
        for lt in patched_ctx.local_terms:
            remaining_local_terms.append({
                "assembly": assembly,
                "attribute": expr.attribute_name,
                "local_term": lt.attribute_name,
            })

    # Verdict
    sum_term_regression = (before_sum != after_sum)
    reclassified_count = len(reclassified_terms)

    if reclassified_count > 0 and not sum_term_regression:
        verdict = "CONFIRMED"
    else:
        verdict = "FALSIFIED"

    return {
        "hypothesis": "H2: Check reorder reclassifies ~37 LocalTerms to SingletonTerms",
        "verdict": verdict,
        "evidence": {
            "before": {
                "sum_terms": before_sum,
                "singleton_terms": before_singleton,
                "local_terms": before_local,
            },
            "after": {
                "sum_terms": after_sum,
                "singleton_terms": after_singleton,
                "local_terms": after_local,
            },
            "sum_term_regression": sum_term_regression,
            "reclassified_count": reclassified_count,
            "reclassified_terms": reclassified_terms,
            "remaining_local_terms": remaining_local_terms,
        },
        "notes": (
            f"{reclassified_count} LocalTerms reclassified to SingletonTerms. "
            f"SumTerms: {before_sum} → {after_sum} "
            f"({'REGRESSION!' if sum_term_regression else 'no regression'}). "
            f"{len(remaining_local_terms)} genuinely local terms remain."
        ),
    }


# ---------------------------------------------------------------------------
# Spike C: H3 — Sibling agg outputs resolvable via Key_D
# ---------------------------------------------------------------------------
def spike_c_sibling_agg_resolution(ctx: PipelineContext) -> dict:
    """H3: Sibling agg outputs resolvable via Key_D at LocalTerm processing time.

    For each idiot_index aggregation expression, checks whether its LocalTerms
    (capital_cost, raw_material_cost) can be resolved through the OutputRegistry
    using Key_D format (part_usage.attr_name). Also verifies that genuine entry
    points (misc_hardware_cost) do NOT resolve.
    """
    assert ctx.hierarchy_data is not None
    assert ctx.output_registry is not None

    registry = ctx.output_registry
    assemblies_tested: list[str] = []
    queries: list[dict] = []

    # Find all idiot_index aggregation expressions
    for agg in ctx.aggregation_expressions:
        if agg.expression.attribute_name != "idiot_index":
            continue

        part_usage_name = agg.instance_path.split("__")[-1]
        assembly = part_usage_name.lower()

        if assembly not in assemblies_tested:
            assemblies_tested.append(assembly)

        for l_term in agg.expression.local_terms:
            key_d = f"{part_usage_name}.{l_term.attribute_name}"
            result = registry.resolve(key_d)

            # Check if resolved channel has double-attr format (*__attr__attr)
            is_double_attr = False
            if result is not None:
                parts = result.split("__")
                if len(parts) >= 2 and parts[-1] == parts[-2]:
                    is_double_attr = True

            queries.append({
                "assembly": assembly,
                "expression": "idiot_index",
                "local_term": l_term.attribute_name,
                "key_d_query": key_d,
                "key_d_result": result,
                "resolved": result is not None,
                "is_double_attr_channel": is_double_attr,
            })

    # Negative test: misc_hardware_cost should NOT resolve
    # It's a genuine entry point on capital_cost expressions
    negative_tests: list[dict] = []
    seen_neg: set[str] = set()
    for agg in ctx.aggregation_expressions:
        if agg.expression.attribute_name != "capital_cost":
            continue
        part_usage_name = agg.instance_path.split("__")[-1]
        if part_usage_name in seen_neg:
            continue
        seen_neg.add(part_usage_name)
        for l_term in agg.expression.local_terms:
            if l_term.attribute_name == "misc_hardware_cost":
                key_d = f"{part_usage_name}.{l_term.attribute_name}"
                result = registry.resolve(key_d)
                negative_tests.append({
                    "assembly": part_usage_name.lower(),
                    "expression": "capital_cost",
                    "local_term": l_term.attribute_name,
                    "key_d_query": key_d,
                    "key_d_result": result,
                    "correctly_unresolved": result is None,
                })

    # Verdict
    all_idiot_resolved = len(queries) > 0 and all(q["resolved"] for q in queries)
    all_negatives_pass = all(n["correctly_unresolved"] for n in negative_tests)

    if all_idiot_resolved:
        verdict = "CONFIRMED"
    else:
        verdict = "FALSIFIED"

    return {
        "hypothesis": "H3: Sibling agg outputs resolvable via Key_D at LocalTerm processing time",
        "verdict": verdict,
        "evidence": {
            "assemblies_tested": assemblies_tested,
            "queries": queries,
            "all_resolved": all_idiot_resolved,
            "negative_test_misc_hardware_cost": negative_tests,
            "negative_tests_pass": all_negatives_pass,
        },
        "notes": (
            f"{sum(1 for q in queries if q['resolved'])}/{len(queries)} idiot_index "
            f"LocalTerms resolve via Key_D. "
            f"{'misc_hardware_cost correctly unresolved.' if all_negatives_pass else 'UNEXPECTED: misc_hardware_cost resolved!'}"
        ),
    }


# ---------------------------------------------------------------------------
# Spike D: H4 — Plant-level SingletonTerms resolve through actual code path
# ---------------------------------------------------------------------------
def spike_d_plant_level_resolution(ctx: PipelineContext) -> dict:
    """H4: Plant-level SingletonTerms resolve through actual resolution code path.

    Traces the real 3-step resolution in `_resolve_aggregation_input_channel()`
    for plant-level aggregation references. Determines which step succeeds and
    whether Key_E_stripped is needed for robustness.
    """
    assert ctx.hierarchy_data is not None
    assert ctx.output_registry is not None

    registry = ctx.output_registry
    redefinitions = ctx.hierarchy_data.redefinitions

    # Build multiplicity lookup (same as Spike B)
    mult_by_partdef: dict[str, dict[str, MultiplicityData]] = {}
    for m in ctx.hierarchy_data.multiplicities:
        mult_by_partdef.setdefault(m.owning_part_def_qn, {})[m.part_usage_name] = m

    # Build redef index for AST access
    redef_index: dict[tuple[str, str], Any] = {}
    for redef in redefinitions:
        if redef.redefinition_type == RedefinitionType.EXPRESSION and redef.expression_ast is not None:
            redef_index[(redef.owning_part_qn, redef.attribute_name)] = redef.expression_ast

    # Find plant-level aggregation expressions
    plant_expressions_tested = 0
    resolution_traces: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for agg in ctx.aggregation_expressions:
        if not agg.instance_path.endswith("solar_battery_plant"):
            continue
        if agg.expression.attribute_name == "idiot_index":
            continue  # idiot_index has LocalTerms, not SingletonTerms

        key = (agg.expression.owning_part_qn, agg.expression.attribute_name)
        if key in seen:
            continue
        seen.add(key)

        plant_expressions_tested += 1

        # Re-walk with patched walker to get SingletonTerms
        ast = redef_index.get(key)
        if ast is None:
            continue

        mult_lookup = mult_by_partdef.get(agg.expression.owning_part_qn, {})
        patched_ctx = _AggregationContext()
        _walk_aggregation_ast_patched(ast, mult_lookup, patched_ctx)

        for st in patched_ctx.singleton_terms:
            symbolic_ref = st.source_path  # e.g., "solar_array.capital_cost"

            # Call the REAL function
            actual_result = _resolve_aggregation_input_channel(
                symbolic_ref=symbolic_ref,
                instance_path=agg.instance_path,
                redefinitions=redefinitions,
                output_registry=registry,
            )

            # Independent 3-step trace
            part_usage, attr = symbolic_ref.rsplit(".", 1)

            # Step 1: CHAIN redef search
            step_1: dict[str, Any] = {
                "attempted": True, "result": "MISS", "reason": "",
            }
            chain_redef = None
            for redef in redefinitions:
                if (
                    redef.redefinition_type == RedefinitionType.CHAIN
                    and redef.attribute_name == attr
                ):
                    redef_part_name = redef.owning_part_qn.split("__")[-1]
                    if sanitize_name(redef_part_name).lower() == part_usage.lower():
                        chain_redef = redef
                        break
            if chain_redef:
                step_1["result"] = "HIT"
                step_1["reason"] = f"CHAIN redef found: {chain_redef.source_path}"
            else:
                step_1["reason"] = "No CHAIN redef matches (redefs are EXPRESSION type)"

            # Step 2: Scoped key
            step_2: dict[str, Any] = {
                "attempted": True, "result": "MISS", "reason": "",
            }
            instance_parts = agg.instance_path.split("__")
            if len(instance_parts) > 1:
                dotted_scope = ".".join(instance_parts[1:])
                scoped_key = f"{dotted_scope}.{part_usage}.{attr}"
                step_2["scoped_key"] = scoped_key
                scoped_result = registry.resolve(scoped_key)
                if scoped_result is not None:
                    step_2["result"] = "HIT"
                    step_2["channel"] = scoped_result
                    step_2["reason"] = "Scoped key resolved"
                else:
                    step_2["reason"] = "Key_E_stripped not registered"

            # Step 3: Unscoped Key_D
            step_3: dict[str, Any] = {
                "attempted": True, "result": "MISS", "reason": "",
            }
            key_d = f"{part_usage}.{attr}"
            step_3["key_d"] = key_d
            key_d_result = registry.resolve(key_d)
            if key_d_result is not None:
                step_3["result"] = "HIT"
                step_3["channel"] = key_d_result
                step_3["reason"] = "Key_D resolved"
            else:
                step_3["reason"] = "Key_D not in registry"

            # Determine which step resolved
            if step_1["result"] == "HIT":
                resolved_via = "step_1_chain_redef"
            elif step_2["result"] == "HIT":
                resolved_via = "step_2_scoped_key"
            elif step_3["result"] == "HIT":
                resolved_via = "step_3_unscoped_key_d"
            else:
                resolved_via = "NONE"

            # Verify resolved channel is aggregation output (double-attr)
            is_agg_output = False
            if actual_result is not None:
                ch_parts = actual_result.split("__")
                if len(ch_parts) >= 2 and ch_parts[-1] == ch_parts[-2]:
                    is_agg_output = True

            resolution_traces.append({
                "source_path": symbolic_ref,
                "expression": agg.expression.attribute_name,
                "instance_path": agg.instance_path,
                "step_1_chain_redef": step_1,
                "step_2_scoped_key": step_2,
                "step_3_unscoped_key_d": step_3,
                "final_result": "RESOLVED" if actual_result else "UNRESOLVED",
                "resolved_via": resolved_via,
                "channel": actual_result,
                "is_aggregation_output": is_agg_output,
            })

    # Summary
    resolved_via_step_1 = sum(
        1 for t in resolution_traces if t["resolved_via"] == "step_1_chain_redef"
    )
    resolved_via_step_2 = sum(
        1 for t in resolution_traces if t["resolved_via"] == "step_2_scoped_key"
    )
    resolved_via_step_3 = sum(
        1 for t in resolution_traces if t["resolved_via"] == "step_3_unscoped_key_d"
    )
    unresolved = sum(
        1 for t in resolution_traces if t["final_result"] == "UNRESOLVED"
    )
    all_resolved = unresolved == 0 and len(resolution_traces) > 0
    all_agg_outputs = all(
        t["is_aggregation_output"] for t in resolution_traces if t["channel"]
    )

    # Verdict
    if all_resolved:
        if resolved_via_step_3 == len(resolution_traces):
            verdict = "CONFIRMED_WITH_CAVEAT"
        else:
            verdict = "CONFIRMED"
    else:
        verdict = "FALSIFIED"

    # Key_E_stripped recommendation
    if resolved_via_step_3 == len(resolution_traces) and all_resolved:
        recommendation = (
            "Implement Key_E_stripped for robustness — unscoped Key_D fallback "
            "works for solar_battery but could collide if two assemblies "
            "have identically-named sub-parts at different hierarchy levels."
        )
    elif all_resolved:
        recommendation = "All terms resolve — current resolution logic is sufficient."
    else:
        recommendation = f"{unresolved} terms UNRESOLVED — investigation needed."

    return {
        "hypothesis": "H4: Plant-level SingletonTerms resolve through actual resolution code path",
        "verdict": verdict,
        "evidence": {
            "plant_expressions_tested": plant_expressions_tested,
            "resolution_traces": resolution_traces,
            "summary": {
                "resolved_via_step_1": resolved_via_step_1,
                "resolved_via_step_2": resolved_via_step_2,
                "resolved_via_step_3": resolved_via_step_3,
                "unresolved": unresolved,
            },
            "all_channels_are_agg_outputs": all_agg_outputs,
            "key_e_stripped_recommendation": recommendation,
        },
        "notes": (
            f"{len(resolution_traces) - unresolved}/{len(resolution_traces)} plant-level "
            f"terms resolve. Step 1: {resolved_via_step_1}, Step 2: {resolved_via_step_2}, "
            f"Step 3: {resolved_via_step_3}, Unresolved: {unresolved}. "
            + recommendation
        ),
    }


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def _print_summary(results: list[dict]) -> None:
    """Print consolidated summary table of all spike verdicts."""
    print(f"\n{'=' * 78}")
    print("  CONSOLIDATED SUMMARY")
    print(f"{'=' * 78}")
    print(f"  {'Hypothesis':<12s} {'Verdict':<22s} {'Key Evidence'}")
    print(f"  {'-' * 12} {'-' * 22} {'-' * 40}")

    for r in results:
        # Extract short hypothesis label (H1, H2, etc.)
        hyp = r["hypothesis"]
        label = hyp.split(":")[0] if ":" in hyp else hyp[:12]
        verdict = r["verdict"]

        # Key evidence: first sentence of notes
        notes = r.get("notes", "")
        key_evidence = notes.split(". ")[0] if notes else ""

        print(f"  {label:<12s} {verdict:<22s} {key_evidence}")

    print(f"{'=' * 78}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Load model and run spikes."""
    ctx = _load_context()

    # --- Spike A ---
    result_a = spike_a_ast_dual_match(ctx)
    _print_verdict(result_a)

    if result_a["verdict"] == "FALSIFIED":
        print("\nH1 FALSIFIED — stopping. Spikes B-D need redesign.")
        sys.exit(1)

    # --- Spike B ---
    result_b = spike_b_check_reorder(ctx)
    _print_verdict(result_b)

    # --- Spike C (independent of H1/H2 verdicts) ---
    result_c = spike_c_sibling_agg_resolution(ctx)
    _print_verdict(result_c)

    # --- Spike D (only if H2 confirmed) ---
    if result_b["verdict"] == "CONFIRMED":
        result_d = spike_d_plant_level_resolution(ctx)
        _print_verdict(result_d)
    else:
        result_d = {
            "hypothesis": "H4: Plant-level SingletonTerms resolve through actual resolution code path",
            "verdict": "SKIPPED",
            "notes": "H2 was FALSIFIED — plant-level resolution test not meaningful.",
        }
        _print_verdict(result_d)

    # --- Consolidated summary ---
    _print_summary([result_a, result_b, result_c, result_d])

    print("All spikes complete.")


if __name__ == "__main__":
    main()
