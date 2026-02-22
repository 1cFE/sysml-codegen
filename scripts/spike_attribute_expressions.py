#!/usr/bin/env python3
"""Spike: Attribute Expression AST Discovery & Architecture Evaluation.

Inspects SysIDE API responses for PartDef/PartUsage attribute elements,
inventories expression patterns across model suites, attempts compilation
using the Phase 1 expression compiler, and produces a structured report
answering 7 research questions to gate the ATTR-EXPR epic.

Usage:
    uv run python scripts/spike_attribute_expressions.py              # all default suites
    uv run python scripts/spike_attribute_expressions.py path/to/model  # single model
    uv run python scripts/spike_attribute_expressions.py path/a,path/b  # multi-dir model
"""

from __future__ import annotations

import datetime
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.expression import (
    extract_feature_refs,
    extract_operators,
    traverse_expression,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.expression_compiler import (
    CompilationError,
    build_expression_ast,
    compile_expression,
)
from sysml_codegen.extraction.expression_utils import (
    extract_feature_chain_name,
    extract_feature_reference_name,
    reconstruct_expression,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sanitize_name(name: str | None) -> str:
    """Strip quotes, replace spaces (matches extractor._sanitize_name)."""
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    return name


def measure_depth(expr: Any, depth: int = 0) -> int:
    """Measure max depth of expression AST via operands recursion."""
    if expr is None:
        return depth
    max_d = depth
    if hasattr(expr, "operands"):
        try:
            for operand in expr.operands:
                child_d = measure_depth(operand, depth + 1)
                if child_d > max_d:
                    max_d = child_d
        except (TypeError, AttributeError):
            pass
    return max_d


def collect_node_types(expr: Any) -> list[str]:
    """Collect all node type names via traverse_expression."""
    return traverse_expression(expr, lambda node: type(node).__name__)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class AttributeExprInfo:
    part_name: str
    part_type: str  # "PartDefinition" or "PartUsage"
    attr_name: str
    has_expression: bool
    root_node_type: str = ""
    is_literal_only: bool = True
    classification: str = ""  # FORMULA / EXPOSE / LITERAL / NO_EXPRESSION / UNRESOLVABLE / MIXED
    ref_names: list[str] = field(default_factory=list)
    ref_qualified_names: list[str] = field(default_factory=list)
    depth: int = 0
    node_types: list[str] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)
    compiled_python: str | None = None
    compilation_error: str | None = None
    raw_expression: Any = field(default=None, repr=False)
    sysml_text: str = ""


@dataclass
class SuiteResult:
    suite_name: str
    model_paths: list[Path]
    attributes: list[AttributeExprInfo] = field(default_factory=list)
    part_count: int = 0
    part_def_count: int = 0
    part_usage_count: int = 0
    error: str | None = None
    api_fields_sample: dict[str, bool] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Model Loading
# ---------------------------------------------------------------------------

DEFAULT_SUITES: list[tuple[str, list[Path]]] = [
    ("chain_spike_model", [Path("tests/fixtures/chain_spike_model")]),
    ("solar_battery_model", [Path("tests/fixtures/solar_battery_model")]),
    ("catf_mfe", [
        Path("tests/fixtures/catf_mfe_model/library"),
        Path("tests/fixtures/catf_mfe_model/designs/catf_mfe"),
    ]),
    ("attr_expr_probe", [Path("tests/fixtures/attr_expr_probe")]),
]


def load_and_iterate_parts(
    model_paths: list[Path],
) -> tuple[list[tuple[Any, str]], Any | None, Any | None]:
    """Load model, return all part elements with their type labels, adapter, and extractor."""
    extractor = SysMLDataExtractor(model_paths)
    if not extractor.load_models():
        label = ", ".join(str(p) for p in model_paths)
        print(f"  ERROR: Failed to load models from {label}", file=sys.stderr)
        return [], None, None

    parts: list[tuple[Any, str]] = []
    for type_name in ("PartDefinition", "PartUsage"):
        for elem in extractor.adapter.elements_of_type(extractor.model, type_name):
            parts.append((elem, type_name))

    return parts, extractor.adapter, extractor


# ---------------------------------------------------------------------------
# Attribute Inspection
# ---------------------------------------------------------------------------


def inspect_attribute(
    adapter: Any,
    part_elem: Any,
    part_type: str,
    attr_member: Any,
) -> AttributeExprInfo:
    """Inspect a single attribute member on a PartDef/PartUsage."""
    part_name = sanitize_name(part_elem.name)
    attr_name = sanitize_name(attr_member.name)

    expr = getattr(attr_member, "feature_value_expression", None)
    has_expression = expr is not None

    if not has_expression:
        return AttributeExprInfo(
            part_name=part_name,
            part_type=part_type,
            attr_name=attr_name,
            has_expression=False,
            classification="NO_EXPRESSION",
        )

    # Analyze expression
    root_type = type(expr).__name__
    refs = extract_feature_refs(expr, ignore_std_lib=True)
    node_types = collect_node_types(expr)
    operators = extract_operators(expr)
    depth = measure_depth(expr)

    ref_names = [r.name for r in refs]
    ref_qnames = [r.qualified_name for r in refs]
    is_literal_only = len(refs) == 0

    # Get human-readable SysML text
    try:
        sysml_text = reconstruct_expression(expr)
    except Exception:
        sysml_text = ""

    # Classify
    classification = classify_attribute_expression(expr, refs, adapter, part_elem)

    return AttributeExprInfo(
        part_name=part_name,
        part_type=part_type,
        attr_name=attr_name,
        has_expression=True,
        root_node_type=root_type,
        is_literal_only=is_literal_only,
        classification=classification,
        ref_names=ref_names,
        ref_qualified_names=ref_qnames,
        depth=depth,
        node_types=node_types,
        operators=operators,
        raw_expression=expr,
        sysml_text=sysml_text,
    )


# ---------------------------------------------------------------------------
# Classification (Q5)
# ---------------------------------------------------------------------------


def classify_attribute_expression(
    expr: Any,
    refs: list,
    adapter: Any,
    part_elem: Any,
) -> str:
    """Classify an attribute expression pattern.

    LITERAL:       No feature references (pure constants/operators)
    FORMULA:       References only sibling attributes on same part
    EXPOSE:        Single reference to calc usage output (dotted path)
    MIXED:         References both sibling attributes and calc outputs
    UNRESOLVABLE:  References that can't be resolved
    """
    if not refs:
        return "LITERAL"

    # Get sibling attribute names and calc usage names from the part
    sibling_attr_names: set[str] = set()
    calc_usage_names: set[str] = set()
    for member in part_elem.owned_members:
        if adapter.is_instance(member, "AttributeUsage"):
            name = sanitize_name(member.name)
            if name:
                sibling_attr_names.add(name)
        elif adapter.is_instance(member, "CalculationUsage"):
            name = sanitize_name(member.name)
            if name:
                calc_usage_names.add(name)

    has_sibling_ref = False
    has_calc_ref = False
    has_unresolvable = False

    for ref in refs:
        ref_name = ref.name
        # Check if it's a sibling attribute reference
        if ref_name in sibling_attr_names:
            has_sibling_ref = True
        # Check if first segment of dotted path is a calc usage
        elif any(
            ref_name == cn or ref_name.startswith(cn + ".")
            for cn in calc_usage_names
        ):
            has_calc_ref = True
        elif "." in ref_name and ref_name.split(".")[0] in calc_usage_names:
            has_calc_ref = True
        else:
            has_unresolvable = True

    if has_sibling_ref and has_calc_ref:
        return "MIXED"
    if has_calc_ref:
        return "EXPOSE"
    if has_sibling_ref:
        return "FORMULA"
    if has_unresolvable:
        return "UNRESOLVABLE"
    return "LITERAL"


# ---------------------------------------------------------------------------
# FR-8: API Field Inventory
# ---------------------------------------------------------------------------


def inventory_api_fields(attr_member: Any) -> dict[str, bool]:
    """Check which key API fields are available on an attribute element."""
    fields_to_check = [
        "feature_value_expression",
        "name",
        "qualified_name",
        "declared_name",
        "owned_members",
        "heritage",
        "is_abstract",
        "is_derived",
        "is_end",
        "is_ordered",
        "is_unique",
        "is_constant",
        "direction",
        "multiplicity",
        "feature_value",
        "valuation",
    ]
    return {f: hasattr(attr_member, f) for f in fields_to_check}


# ---------------------------------------------------------------------------
# Suite Processing
# ---------------------------------------------------------------------------


def process_suite(
    suite_name: str,
    model_paths: list[Path],
) -> tuple[SuiteResult, list[tuple[Any, str]], Any | None]:
    """Process a single model suite.

    Returns (result, parts_list, adapter) -- parts_list and adapter are kept
    for Q6 compilation attempts.
    """
    result = SuiteResult(suite_name=suite_name, model_paths=model_paths)

    parts, adapter, _extractor = load_and_iterate_parts(model_paths)
    if adapter is None:
        result.error = "Failed to load models"
        return result, [], None

    api_fields_sampled = False
    part_def_count = 0
    part_usage_count = 0

    for part_elem, part_type in parts:
        if part_type == "PartDefinition":
            part_def_count += 1
        else:
            part_usage_count += 1

        for member in part_elem.owned_members:
            if not adapter.is_instance(member, "AttributeUsage"):
                continue

            info = inspect_attribute(adapter, part_elem, part_type, member)
            result.attributes.append(info)

            # FR-8: Sample API fields from first attribute with expression
            if not api_fields_sampled and info.has_expression:
                result.api_fields_sample = inventory_api_fields(member)
                api_fields_sampled = True

    result.part_count = part_def_count + part_usage_count
    result.part_def_count = part_def_count
    result.part_usage_count = part_usage_count

    return result, parts, adapter


# ---------------------------------------------------------------------------
# Q1: AST Availability
# ---------------------------------------------------------------------------


def run_q1(results: list[SuiteResult]) -> str:
    """Q1: Do PartDef attributes have feature_value_expression?"""
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append(
        "Q1: AST Availability -- Do PartDef attributes have feature_value_expression?"
    )
    lines.append("=" * 70)

    total_attrs = 0
    total_with_expr = 0

    for sr in results:
        lines.append(f"\n--- Suite: {sr.suite_name} ---")
        if sr.error:
            lines.append(f"  ERROR: {sr.error}")
            continue

        lines.append(
            f"  Parts found: {sr.part_count} "
            f"(PartDefinition: {sr.part_def_count}, PartUsage: {sr.part_usage_count})"
        )

        current_part = None
        for a in sr.attributes:
            if a.part_name != current_part:
                current_part = a.part_name
                lines.append(f"  Part: {a.part_name} ({a.part_type})")

            expr_str = f"has_expr={a.has_expression}"
            if a.has_expression:
                expr_str += f"  root={a.root_node_type}"
                if a.sysml_text:
                    display = a.sysml_text[:60]
                    expr_str += f"  text={display}"

            lines.append(f"    {a.attr_name:30s} : {expr_str}")
            total_attrs += 1
            if a.has_expression:
                total_with_expr += 1

        # FR-8: API fields
        if sr.api_fields_sample:
            lines.append(
                f"\n  FR-8: API fields on first attribute with expression:"
            )
            for fname, present in sr.api_fields_sample.items():
                lines.append(
                    f"    {fname:30s} : {'YES' if present else 'no'}"
                )

    lines.append(
        f"\n  SUMMARY: {total_with_expr}/{total_attrs} attributes "
        f"have feature_value_expression"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Q2: Reference Resolution
# ---------------------------------------------------------------------------


def run_q2(results: list[SuiteResult]) -> str:
    """Q2: Can references in attribute expressions be resolved?"""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("Q2: Reference Resolution")
    lines.append("=" * 70)

    for sr in results:
        lines.append(f"\n--- Suite: {sr.suite_name} ---")
        if sr.error:
            lines.append(f"  ERROR: {sr.error}")
            continue

        attrs_with_refs = [a for a in sr.attributes if a.ref_names]
        if not attrs_with_refs:
            lines.append("  No attributes with references found")
            continue

        for a in attrs_with_refs:
            lines.append(f"  {a.part_name}.{a.attr_name} ({a.classification}):")
            for rn, rqn in zip(a.ref_names, a.ref_qualified_names):
                lines.append(f"    ref: {rn:30s}  qname: {rqn}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Q3: EXPOSE Pattern Analysis
# ---------------------------------------------------------------------------


def run_q3(results: list[SuiteResult]) -> str:
    """Q3: EXPOSE pattern -- attributes referencing calc usage outputs."""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("Q3: EXPOSE Pattern Analysis")
    lines.append("=" * 70)

    expose_count = 0
    for sr in results:
        lines.append(f"\n--- Suite: {sr.suite_name} ---")
        if sr.error:
            lines.append(f"  ERROR: {sr.error}")
            continue

        expose_attrs = [a for a in sr.attributes if a.classification == "EXPOSE"]
        if not expose_attrs:
            lines.append("  No EXPOSE-pattern attributes found")
            continue

        for a in expose_attrs:
            expose_count += 1
            lines.append(f"  {a.part_name}.{a.attr_name}:")
            lines.append(f"    root_node_type: {a.root_node_type}")
            lines.append(f"    node_types:     {a.node_types}")
            lines.append(f"    sysml_text:     {a.sysml_text}")
            lines.append(f"    refs:           {a.ref_names}")
            lines.append(f"    ref_qnames:     {a.ref_qualified_names}")

    lines.append(f"\n  SUMMARY: {expose_count} EXPOSE-pattern attributes found")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Q4: Cross-Part References
# ---------------------------------------------------------------------------


def run_q4(results: list[SuiteResult]) -> str:
    """Q4: Do any attribute expressions reference attributes on other parts?"""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("Q4: Cross-Part References")
    lines.append("=" * 70)

    cross_part_count = 0
    for sr in results:
        lines.append(f"\n--- Suite: {sr.suite_name} ---")
        if sr.error:
            lines.append(f"  ERROR: {sr.error}")
            continue

        # Look for refs with dotted paths
        cross_part_attrs = [
            a
            for a in sr.attributes
            if a.has_expression and any("." in rn for rn in a.ref_names)
        ]
        if not cross_part_attrs:
            lines.append("  No cross-part references detected")
            continue

        for a in cross_part_attrs:
            cross_part_count += 1
            lines.append(f"  {a.part_name}.{a.attr_name} ({a.classification}):")
            for rn in a.ref_names:
                if "." in rn:
                    lines.append(f"    dotted ref: {rn}")

    lines.append(
        f"\n  SUMMARY: {cross_part_count} attributes with dotted references"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Q5: Pattern Inventory
# ---------------------------------------------------------------------------


def run_q5(results: list[SuiteResult]) -> str:
    """Q5: Pattern inventory table."""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("Q5: Pattern Inventory")
    lines.append("=" * 70)

    # Table header
    header = (
        f"  {'Suite':<25s} | {'FORMULA':>7s} | {'EXPOSE':>7s} | "
        f"{'LITERAL':>7s} | {'UNRESOLVABLE':>12s} | {'MIXED':>5s} | "
        f"{'NO_EXPR':>7s} | {'Total':>5s}"
    )
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))

    grand_total: dict[str, int] = {}
    for sr in results:
        if sr.error:
            lines.append(f"  {sr.suite_name:<25s} | ERROR: {sr.error}")
            continue

        counts: dict[str, int] = {}
        for a in sr.attributes:
            counts[a.classification] = counts.get(a.classification, 0) + 1
            grand_total[a.classification] = (
                grand_total.get(a.classification, 0) + 1
            )

        total = len(sr.attributes)
        lines.append(
            f"  {sr.suite_name:<25s} | {counts.get('FORMULA', 0):>7d} | "
            f"{counts.get('EXPOSE', 0):>7d} | {counts.get('LITERAL', 0):>7d} | "
            f"{counts.get('UNRESOLVABLE', 0):>12d} | {counts.get('MIXED', 0):>5d} | "
            f"{counts.get('NO_EXPRESSION', 0):>7d} | {total:>5d}"
        )

    # Grand totals
    grand = sum(grand_total.values())
    lines.append("  " + "-" * (len(header) - 2))
    lines.append(
        f"  {'TOTAL':<25s} | {grand_total.get('FORMULA', 0):>7d} | "
        f"{grand_total.get('EXPOSE', 0):>7d} | {grand_total.get('LITERAL', 0):>7d} | "
        f"{grand_total.get('UNRESOLVABLE', 0):>12d} | {grand_total.get('MIXED', 0):>5d} | "
        f"{grand_total.get('NO_EXPRESSION', 0):>7d} | {grand:>5d}"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Q6: Compiler Reuse
# ---------------------------------------------------------------------------


def attempt_compilation(
    attr_info: AttributeExprInfo,
    adapter: Any,
    part_elem: Any,
) -> tuple[str | None, str | None]:
    """Attempt to compile an attribute expression using Phase 1 compiler.

    For attribute expressions, "inputs" are sibling attributes on the same part.
    """
    if not attr_info.has_expression or attr_info.raw_expression is None:
        return None, "No expression to compile"

    # Collect sibling attribute names as "inputs" for the expression
    sibling_attr_names: set[str] = set()
    for member in part_elem.owned_members:
        if adapter.is_instance(member, "AttributeUsage"):
            name = sanitize_name(member.name)
            if name and name != attr_info.attr_name:  # exclude self
                sibling_attr_names.add(name)

    try:
        ast_ir = build_expression_ast(
            syside_node=attr_info.raw_expression,
            input_names=sibling_attr_names,
            output_names=set(),
        )
        compiled = compile_expression(ast_ir)
        return compiled, None
    except CompilationError as e:
        return None, f"CompilationError: {e}"
    except Exception as e:
        return None, f"Unexpected: {type(e).__name__}: {e}"


def run_q6(
    results: list[SuiteResult],
    suite_data: dict[str, tuple[list[tuple[Any, str]], Any]],
) -> str:
    """Q6: Can Phase 1 compiler process attribute expressions?"""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append(
        "Q6: Compiler Reuse -- Phase 1 compiler on attribute expressions"
    )
    lines.append("=" * 70)

    compile_successes = 0
    compile_failures = 0

    for sr in results:
        lines.append(f"\n--- Suite: {sr.suite_name} ---")
        if sr.error:
            lines.append(f"  ERROR: {sr.error}")
            continue

        data = suite_data.get(sr.suite_name)
        if data is None:
            lines.append("  No suite data available")
            continue

        parts_list, adapter = data

        # Build part_name -> part_elem lookup
        parts_by_name: dict[str, Any] = {}
        for part_elem, _ptype in parts_list:
            pname = sanitize_name(part_elem.name)
            parts_by_name[pname] = part_elem

        # Try FORMULA and LITERAL attributes first, then EXPOSE
        compilable = [
            a
            for a in sr.attributes
            if a.classification in ("FORMULA", "LITERAL") and a.has_expression
        ]
        expose_attrs = [
            a for a in sr.attributes if a.classification == "EXPOSE" and a.has_expression
        ]

        if not compilable and not expose_attrs:
            lines.append("  No compilable attributes found")
            continue

        for a in compilable:
            part_elem = parts_by_name.get(a.part_name)
            if part_elem is None:
                lines.append(
                    f"  {a.part_name}.{a.attr_name}: SKIP (part not found)"
                )
                continue

            compiled, error = attempt_compilation(a, adapter, part_elem)
            a.compiled_python = compiled
            a.compilation_error = error

            if compiled:
                compile_successes += 1
                lines.append(f"  {a.part_name}.{a.attr_name} ({a.classification}):")
                lines.append(f"    sysml:    {a.sysml_text}")
                lines.append(f"    compiled: {compiled}")
            else:
                compile_failures += 1
                lines.append(f"  {a.part_name}.{a.attr_name} ({a.classification}):")
                lines.append(f"    sysml:    {a.sysml_text}")
                lines.append(f"    error:    {error}")

        # Try at least 2 EXPOSE attributes for gap documentation
        for a in expose_attrs[:2]:
            part_elem = parts_by_name.get(a.part_name)
            if part_elem is None:
                continue

            compiled, error = attempt_compilation(a, adapter, part_elem)
            a.compiled_python = compiled
            a.compilation_error = error

            if compiled:
                compile_successes += 1
                lines.append(f"  {a.part_name}.{a.attr_name} ({a.classification}):")
                lines.append(f"    sysml:    {a.sysml_text}")
                lines.append(f"    compiled: {compiled}")
            else:
                compile_failures += 1
                lines.append(f"  {a.part_name}.{a.attr_name} ({a.classification}):")
                lines.append(f"    sysml:    {a.sysml_text}")
                lines.append(f"    error:    {error}  (expected for EXPOSE)")

    lines.append(
        f"\n  SUMMARY: {compile_successes} compiled successfully, "
        f"{compile_failures} failed"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Q7: Architecture Recommendation
# ---------------------------------------------------------------------------


def run_q7(results: list[SuiteResult]) -> str:
    """Q7: Architecture recommendation based on Q1-Q6 findings."""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("Q7: Architecture Recommendation")
    lines.append("=" * 70)

    # Gather stats
    total_formula = 0
    total_expose = 0
    total_literal = 0
    total_unresolvable = 0
    any_compiled = False

    for sr in results:
        if sr.error:
            continue
        for a in sr.attributes:
            if a.classification == "FORMULA":
                total_formula += 1
            elif a.classification == "EXPOSE":
                total_expose += 1
            elif a.classification == "LITERAL":
                total_literal += 1
            elif a.classification == "UNRESOLVABLE":
                total_unresolvable += 1
            if a.compiled_python:
                any_compiled = True

    lines.append("\n  Findings Summary:")
    lines.append(f"    FORMULA attributes:      {total_formula}")
    lines.append(f"    EXPOSE attributes:       {total_expose}")
    lines.append(f"    LITERAL attributes:      {total_literal}")
    lines.append(f"    UNRESOLVABLE attributes: {total_unresolvable}")
    lines.append(f"    Compilation succeeded:   {'YES' if any_compiled else 'NO'}")

    lines.append("\n  Architecture Options Analysis:")

    lines.append("    Option A (Synthetic CalcDef+CalcUsage):")
    lines.append(
        "      Pro: Reuses all existing infrastructure "
        "(backtracker, graph builder, templates)"
    )
    lines.append(
        "      Con: Heaviest abstraction -- creates phantom SysML elements"
    )
    lines.append(
        "      Fit: Good if FORMULA patterns are dominant "
        "and CalcDef ceremony is the bottleneck"
    )

    lines.append("    Option B (Synthetic CalcUsage only):")
    lines.append(
        "      Pro: Lighter than A, still reuses module generation"
    )
    lines.append(
        "      Con: Still creates phantom elements, CalcDef still needed"
    )
    lines.append(
        "      Fit: Good if a reusable computed-attribute CalcDef "
        "can serve many parts"
    )

    lines.append("    Option C (Direct graph integration):")
    lines.append(
        "      Pro: Cleanest model -- ComputedAttributeData is first-class"
    )
    lines.append(
        "      Con: Requires extending graph builder and templates"
    )
    lines.append(
        "      Fit: Best if FORMULA + EXPOSE both significant "
        "and need different handling"
    )

    lines.append("    Option D (Inline @computed_field):")
    lines.append(
        "      Pro: Simplest for FORMULA patterns -- no new modules"
    )
    lines.append(
        "      Con: Cannot handle EXPOSE (cross-module references)"
    )
    lines.append(
        "      Fit: Good only if FORMULA patterns are rare and simple"
    )

    lines.append("\n  RECOMMENDATION:")
    lines.append(
        "    [To be finalized based on empirical findings above -- "
        "see report.md for full grounded analysis]"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Go/No-Go Decision
# ---------------------------------------------------------------------------


def run_go_nogo(results: list[SuiteResult]) -> str:
    """Generate go/no-go decision based on findings."""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("GO / NO-GO DECISION")
    lines.append("=" * 70)

    has_asts = False
    has_formula = False
    has_compiled = False

    for sr in results:
        if sr.error:
            continue
        for a in sr.attributes:
            if a.has_expression and not a.is_literal_only:
                has_asts = True
            if a.classification == "FORMULA":
                has_formula = True
            if a.compiled_python:
                has_compiled = True

    lines.append("\n  Gate Criteria:")
    lines.append(
        f"    1. ASTs available on PartDef attributes:  "
        f"{'YES' if has_asts else 'NO'}"
    )
    lines.append(
        f"    2. FORMULA pattern found:                 "
        f"{'YES' if has_formula else 'NO'}"
    )
    lines.append(
        f"    3. Phase 1 compiler works for attributes:  "
        f"{'YES' if has_compiled else 'NO'}"
    )

    if has_asts and has_compiled:
        lines.append("\n  DECISION: GO")
        lines.append(
            "    AST availability confirmed and compiler reuse validated."
        )
        lines.append("    Proceed to ATTR-EXPR Item 2.")
    elif has_asts and not has_compiled:
        lines.append("\n  DECISION: CONDITIONAL GO")
        lines.append(
            "    ASTs available but compilation needs adjustments."
        )
        lines.append(
            "    Proceed with caution; Item 2 must address compiler gaps."
        )
    else:
        lines.append("\n  DECISION: NO-GO")
        lines.append("    ASTs not available on PartDef attributes.")
        lines.append("    ATTR-EXPR epic should be deferred or rescoped.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# FR-9: Unsupported Node Types
# ---------------------------------------------------------------------------


def run_fr9(results: list[SuiteResult]) -> str:
    """FR-9: Document any unexpected or unsupported node types encountered."""
    lines: list[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("FR-9: Unsupported / Unexpected Node Types")
    lines.append("=" * 70)

    # Known/expected node types
    expected = {
        "OperatorExpression",
        "FeatureReferenceExpression",
        "FeatureChainExpression",
        "LiteralRational",
        "LiteralInteger",
        "LiteralReal",
        "LiteralBoolean",
        "LiteralString",
    }

    unexpected: dict[str, list[str]] = {}  # node_type -> [attr_name, ...]
    for sr in results:
        if sr.error:
            continue
        for a in sr.attributes:
            for nt in a.node_types:
                if nt not in expected:
                    unexpected.setdefault(nt, []).append(
                        f"{a.part_name}.{a.attr_name}"
                    )

    if not unexpected:
        lines.append("  No unexpected node types encountered.")
    else:
        for nt, attrs in sorted(unexpected.items()):
            lines.append(f"  {nt}: found in {len(attrs)} attributes")
            for attr_ref in attrs[:5]:
                lines.append(f"    - {attr_ref}")
            if len(attrs) > 5:
                lines.append(f"    ... and {len(attrs) - 5} more")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report Writer
# ---------------------------------------------------------------------------


def write_report(
    report_sections: list[str],
    report_path: Path,
) -> None:
    """Write the structured report to file."""
    header = [
        "# Spike Report: Attribute Expression AST Discovery & Architecture Evaluation",
        "",
        f"**Generated:** {datetime.datetime.now().isoformat()}",
        "**Branch:** cost-pattern",
        "**Epic:** ATTR-EXPR Item 1",
        "",
    ]

    body = "\n".join(header)
    for section in report_sections:
        body += "\n```\n" + section + "\n```\n"

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(body)
    print(f"\nReport written to: {report_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Parse CLI args
    if len(sys.argv) > 1:
        suites: list[tuple[str, list[Path]]] = []
        for arg in sys.argv[1:]:
            paths = [Path(p.strip()) for p in arg.split(",")]
            label = (
                paths[0].name
                if len(paths) == 1
                else "+".join(p.name for p in paths)
            )
            suites.append((label, paths))
    else:
        suites = DEFAULT_SUITES

    print("Attribute Expression AST Discovery Spike")
    print("=" * 50)

    # Process all suites, keeping parts+adapter for Q6
    all_results: list[SuiteResult] = []
    suite_data: dict[str, tuple[list[tuple[Any, str]], Any]] = {}

    for suite_name, model_paths in suites:
        print(f"\nLoading suite: {suite_name} ...")
        sr, parts_list, adapter = process_suite(suite_name, model_paths)
        all_results.append(sr)
        if adapter is not None:
            suite_data[suite_name] = (parts_list, adapter)

    # Run all questions
    sections: list[str] = []

    q1 = run_q1(all_results)
    print(q1)
    sections.append(q1)

    q2 = run_q2(all_results)
    print(q2)
    sections.append(q2)

    q3 = run_q3(all_results)
    print(q3)
    sections.append(q3)

    q4 = run_q4(all_results)
    print(q4)
    sections.append(q4)

    q5 = run_q5(all_results)
    print(q5)
    sections.append(q5)

    q6 = run_q6(all_results, suite_data)
    print(q6)
    sections.append(q6)

    q7 = run_q7(all_results)
    print(q7)
    sections.append(q7)

    fr9 = run_fr9(all_results)
    print(fr9)
    sections.append(fr9)

    go_nogo = run_go_nogo(all_results)
    print(go_nogo)
    sections.append(go_nogo)

    # Write persistent report
    report_path = Path(".project/active/attr-expr-spike/report.md")
    write_report(sections, report_path)


if __name__ == "__main__":
    main()
