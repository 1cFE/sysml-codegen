#!/usr/bin/env python3
"""Spike Q3: Expression Compilation & Ground Truth Comparison.

For each CalcDef output attribute with an expression AST:
  - Compile the syside AST to a Python expression string
  - Verify syntactic validity with ast.parse()
  - For multi-output CalcDefs, build full function bodies with topological ordering
  - For CalcDefs with handwritten impls, compare compiled vs handwritten numerically

Usage:
    uv run python scripts/spike_compile_expressions.py [model_path ...]
    (defaults to all 4 model suites if no args given)

    # Run with ground truth comparison (Phase 3):
    uv run python scripts/spike_compile_expressions.py --compare

    # Run specific suite:
    uv run python scripts/spike_compile_expressions.py tests/fixtures/solar_battery_model
"""

from __future__ import annotations

import ast
import hashlib
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from agentic_mbse.sysml.expression import extract_feature_refs, extract_operators
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.extractor import SysMLDataExtractor


# ---------------------------------------------------------------------------
# Operator mapping
# ---------------------------------------------------------------------------

PYTHON_OPERATOR_MAP: dict[str, str | None] = {
    "+": " + ",
    "-": " - ",
    "*": " * ",
    "/": " / ",
    "**": " ** ",
    "^": " ** ",     # alias (not observed in Item 1 but documented)
    "[": None,       # unit annotation -- strip, return value operand only
}

# Track which operators were actually encountered
OPERATOR_ENCOUNTERS: dict[str, list[str]] = {}  # operator -> [example expressions]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class OutputCompileResult:
    calc_name: str
    output_name: str
    compiled: str | None = None
    ast_valid: bool = False
    error: str | None = None
    node_types_seen: list[str] = field(default_factory=list)
    literal_value_type: str | None = None  # document LiteralRational.value type
    is_literal_only: bool = False
    is_passthrough: bool = False
    has_unary_negation: bool = False


@dataclass
class CalcDefCompileResult:
    calc_name: str
    suite: str
    output_results: list[OutputCompileResult] = field(default_factory=list)
    execution_order: list[str] | None = None
    full_body: str | None = None
    full_body_valid: bool = False
    full_body_error: str | None = None
    has_circular_deps: bool = False
    undeclared_intermediates: list[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    calc_name: str
    status: str = ""  # MATCH, MISMATCH, STUB, EXCLUDED, ERROR
    max_relative_error: float = 0.0
    per_output: dict[str, dict[str, Any]] = field(default_factory=dict)
    notes: str = ""


# ---------------------------------------------------------------------------
# Helpers (reused from Item 1 scripts)
# ---------------------------------------------------------------------------

def sanitize_name(name: str | None) -> str:
    """Strip quotes, replace spaces (matches extractor._sanitize_name)."""
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    return name


def load_and_extract(model_paths: list[Path]):
    """Load model from one or more directories, return (raw_elements, calc_defs, adapter)."""
    extractor = SysMLDataExtractor(model_paths)
    if not extractor.load_models():
        label = ", ".join(str(p) for p in model_paths)
        print(f"  ERROR: Failed to load models from {label}", file=sys.stderr)
        return [], [], None
    calc_defs = extractor.extract_calculation_definitions()
    raw_elems = list(extractor.adapter.elements_of_type(extractor.model, "CalculationDefinition"))
    return raw_elems, calc_defs, extractor.adapter


def _extract_feature_ref_name(expr_node: Any) -> str:
    """Extract name from a FeatureReferenceExpression node."""
    if hasattr(expr_node, "referent") and expr_node.referent:
        referent = expr_node.referent
        if hasattr(referent, "name") and referent.name:
            return sanitize_name(referent.name)

    if hasattr(expr_node, "memberships"):
        for membership in expr_node.memberships:
            if type(membership).__name__ == "Membership":
                if hasattr(membership, "member_element"):
                    elem = membership.member_element
                    if elem and hasattr(elem, "name") and elem.name:
                        return sanitize_name(elem.name)

    if hasattr(expr_node, "declared_name") and expr_node.declared_name:
        return sanitize_name(expr_node.declared_name)
    if hasattr(expr_node, "name") and expr_node.name:
        return sanitize_name(expr_node.name)

    return f"UNKNOWN_{type(expr_node).__name__}"


# ---------------------------------------------------------------------------
# Phase 1: Core expression compiler
# ---------------------------------------------------------------------------

def compile_expression(
    expr: Any,
    input_names: set[str],
    output_names: set[str],
    all_member_names: set[str] | None = None,
    _context: dict | None = None,
) -> str:
    """Recursively compile a syside AST node to a Python expression string.

    Args:
        expr: syside AST node
        input_names: declared input attribute names for this CalcDef
        output_names: declared output attribute names for this CalcDef
        all_member_names: all owned_member names (for undeclared intermediate resolution)
        _context: internal tracking dict for encountered features
    """
    if _context is None:
        _context = {
            "node_types": [],
            "literal_value_type": None,
            "has_unary_negation": False,
            "undeclared_intermediates": [],
        }

    if expr is None:
        return "None"

    node_type = type(expr).__name__
    _context["node_types"].append(node_type)

    # --- OperatorExpression ---
    if SysideAdapter.is_instance(expr, "OperatorExpression"):
        operator = ""
        if hasattr(expr, "operator") and expr.operator:
            operator = str(expr.operator)

        # Track operator encounter
        if operator not in OPERATOR_ENCOUNTERS:
            OPERATOR_ENCOUNTERS[operator] = []

        operands = []
        if hasattr(expr, "operands"):
            operands = list(expr.operands)

        # Unit annotation: strip, return value operand only
        if operator == "[":
            if operands:
                result = compile_expression(operands[0], input_names, output_names, all_member_names, _context)
                OPERATOR_ENCOUNTERS[operator].append(f"<unit annotation> -> {result}")
                return result
            return "0"

        py_op = PYTHON_OPERATOR_MAP.get(operator)
        if py_op is None and operator != "[":
            return f"UNSUPPORTED_OP_{operator}"

        if len(operands) == 1:
            # Unary operator (e.g., negation)
            _context["has_unary_negation"] = True
            operand = compile_expression(operands[0], input_names, output_names, all_member_names, _context)
            result = f"(-{operand})" if operator == "-" else f"({operator}{operand})"
            OPERATOR_ENCOUNTERS[operator].append(result)
            return result

        if len(operands) == 2:
            left = compile_expression(operands[0], input_names, output_names, all_member_names, _context)
            right = compile_expression(operands[1], input_names, output_names, all_member_names, _context)
            result = f"({left}{py_op}{right})"
            OPERATOR_ENCOUNTERS[operator].append(result)
            return result

        if len(operands) > 2:
            # N-ary: left-fold ((a op b) op c)
            compiled_operands = [
                compile_expression(op, input_names, output_names, all_member_names, _context)
                for op in operands
            ]
            result = compiled_operands[0]
            for i in range(1, len(compiled_operands)):
                result = f"({result}{py_op}{compiled_operands[i]})"
            OPERATOR_ENCOUNTERS[operator].append(result)
            return result

        return operator  # degenerate: operator with no operands

    # --- FeatureReferenceExpression ---
    if SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        name = _extract_feature_ref_name(expr)
        if name in input_names:
            return f"inputs.{name}"
        if name in output_names:
            return name  # intermediate: bare variable name
        # Extended resolution: check all CalcDef members (FR-11)
        if all_member_names and name in all_member_names:
            _context["undeclared_intermediates"].append(name)
            return name  # treat as undeclared intermediate
        return f"UNRESOLVED_{name}"

    # --- LiteralRational / LiteralInteger / LiteralReal ---
    if node_type in ("LiteralRational", "LiteralInteger", "LiteralReal"):
        if hasattr(expr, "value"):
            val = expr.value
            _context["literal_value_type"] = type(val).__name__
            # Value may be string or numeric
            if isinstance(val, str):
                return val
            return str(val)
        return "0"

    # --- FeatureChainExpression ---
    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        # Dotted reference like subsystem.value -- unsupported in CalcDef output
        return f"UNSUPPORTED_CHAIN_{node_type}"

    return f"UNKNOWN_{node_type}"


# ---------------------------------------------------------------------------
# Phase 2: Dependency graph and topological sort
# ---------------------------------------------------------------------------

def get_all_member_names(raw_elem: Any) -> set[str]:
    """Get all owned_member names from a raw CalcDef element."""
    names: set[str] = set()
    if hasattr(raw_elem, "owned_members"):
        for member in raw_elem.owned_members:
            name = sanitize_name(getattr(member, "name", None))
            if name:
                names.add(name)
    return names


def get_output_expression(raw_elem: Any, output_name: str, adapter: Any) -> Any | None:
    """Get the feature_value_expression for a specific output attribute."""
    for member in raw_elem.owned_members:
        if not adapter.is_instance(member, "AttributeUsage"):
            continue
        is_output = False
        if hasattr(member, "direction"):
            direction_str = str(member.direction)
            if "Out" in direction_str or "Return" in direction_str:
                is_output = True
        if not is_output:
            continue
        member_name = sanitize_name(member.name)
        if member_name == output_name:
            if hasattr(member, "feature_value_expression") and member.feature_value_expression is not None:
                return member.feature_value_expression
    return None


def get_member_expression(raw_elem: Any, member_name: str, adapter: Any) -> Any | None:
    """Get the feature_value_expression for any owned member by name (regardless of direction)."""
    for member in raw_elem.owned_members:
        if not adapter.is_instance(member, "AttributeUsage"):
            continue
        name = sanitize_name(getattr(member, "name", None))
        if name == member_name:
            if hasattr(member, "feature_value_expression") and member.feature_value_expression is not None:
                return member.feature_value_expression
    return None


def build_dependency_graph(
    calc_def: Any, raw_elem: Any, adapter: Any,
) -> tuple[dict[str, set[str]], dict[str, Any], set[str]]:
    """Build dependency graph for outputs within a CalcDef.

    Includes undeclared intermediates: members that are referenced by outputs
    but not declared as in/out. These get their own graph nodes so they can
    be emitted as local variable assignments.

    Returns:
        (dep_graph, expr_map, undeclared_intermediates) where:
        - dep_graph: {name: set of names it depends on} (outputs + undeclared intermediates)
        - expr_map: {name: syside AST node}
        - undeclared_intermediates: set of member names that are undeclared intermediates
    """
    output_names = {attr.name for attr in calc_def.output_attributes}
    input_names = {attr.name for attr in calc_def.input_attributes}
    all_member_names = get_all_member_names(raw_elem)

    dep_graph: dict[str, set[str]] = {}
    expr_map: dict[str, Any] = {}
    undeclared_intermediates: set[str] = set()

    def _add_node(name: str, is_output: bool) -> None:
        """Add a node to the graph, extracting its expression and deps."""
        if name in dep_graph:
            return  # already processed

        if is_output:
            expr = get_output_expression(raw_elem, name, adapter)
        else:
            expr = get_member_expression(raw_elem, name, adapter)
        expr_map[name] = expr

        deps: set[str] = set()
        if expr is not None:
            refs = extract_feature_refs(expr, ignore_std_lib=True)
            for ref in refs:
                ref_name = sanitize_name(ref.name)
                if ref_name == name:
                    continue
                if ref_name in output_names:
                    deps.add(ref_name)
                elif ref_name not in input_names and ref_name in all_member_names:
                    # Undeclared intermediate -- also needs a graph node
                    deps.add(ref_name)
                    if ref_name not in output_names:
                        undeclared_intermediates.add(ref_name)

        dep_graph[name] = deps

    # First pass: add all declared outputs
    for output_name in output_names:
        _add_node(output_name, is_output=True)

    # Second pass: add undeclared intermediates discovered in first pass
    # (iterate copy since we may discover more)
    to_process = list(undeclared_intermediates)
    while to_process:
        name = to_process.pop()
        if name not in dep_graph:
            _add_node(name, is_output=False)
            # Check if this undeclared intermediate references more undeclared intermediates
            for new_name in undeclared_intermediates - set(dep_graph.keys()):
                to_process.append(new_name)

    return dep_graph, expr_map, undeclared_intermediates


def topological_sort(dep_graph: dict[str, set[str]]) -> list[str] | None:
    """Kahn's algorithm. Returns sorted list or None if circular."""
    # in_degree[node] = number of deps that ARE in the graph
    in_degree: dict[str, int] = {node: 0 for node in dep_graph}
    for node, deps in dep_graph.items():
        for dep in deps:
            if dep in dep_graph:
                in_degree[node] += 1

    queue = [node for node, deg in in_degree.items() if deg == 0]
    queue.sort()  # deterministic ordering
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        # Find nodes that depend on this one, decrement their in-degree
        for other, deps in dep_graph.items():
            if node in deps and other in in_degree:
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)
                    queue.sort()

    if len(result) != len(dep_graph):
        return None  # circular dependency
    return result


def compile_calc_def_body(
    calc_def: Any, raw_elem: Any, adapter: Any,
) -> tuple[str | None, list[str] | None, list[OutputCompileResult], list[str]]:
    """Compile a full function body for a CalcDef.

    Returns:
        (body_str, execution_order, output_results, undeclared_intermediates)
        body_str is None if compilation fails.
        execution_order includes undeclared intermediates; the return statement
        only includes declared outputs.
    """
    input_names = {attr.name for attr in calc_def.input_attributes}
    output_names = {attr.name for attr in calc_def.output_attributes}
    all_member_names = get_all_member_names(raw_elem)

    dep_graph, expr_map, undeclared_set = build_dependency_graph(calc_def, raw_elem, adapter)
    execution_order = topological_sort(dep_graph)

    output_results: list[OutputCompileResult] = []
    found_undeclared: list[str] = list(undeclared_set)

    if execution_order is None:
        # Circular dependency
        for output_name in sorted(output_names):
            output_results.append(OutputCompileResult(
                calc_name=calc_def.name,
                output_name=output_name,
                error="circular dependency",
            ))
        return None, None, output_results, found_undeclared

    lines: list[str] = []
    any_failed = False

    for name in execution_order:
        expr = expr_map.get(name)
        is_undeclared = name in undeclared_set
        result = OutputCompileResult(calc_name=calc_def.name, output_name=name)

        if expr is None:
            if is_undeclared:
                result.error = "undeclared intermediate: no expression AST"
            else:
                result.error = "no expression AST"
            output_results.append(result)
            any_failed = True
            continue

        context: dict = {
            "node_types": [],
            "literal_value_type": None,
            "has_unary_negation": False,
            "undeclared_intermediates": [],
        }

        compiled = compile_expression(expr, input_names, output_names, all_member_names, context)
        result.node_types_seen = context["node_types"]
        result.literal_value_type = context["literal_value_type"]
        result.has_unary_negation = context["has_unary_negation"]

        # Check for unresolvable refs
        if "UNRESOLVED_" in compiled or "UNSUPPORTED_" in compiled or "UNKNOWN_" in compiled:
            result.compiled = compiled
            result.error = f"unresolvable references in: {compiled}"
            output_results.append(result)
            any_failed = True
            continue

        # Detect literal-only and passthrough
        result.is_literal_only = not any(
            nt == "FeatureReferenceExpression" for nt in context["node_types"]
        ) and not any(
            nt == "OperatorExpression" for nt in context["node_types"]
        )
        result.is_passthrough = (
            len(context["node_types"]) == 1
            and context["node_types"][0] == "FeatureReferenceExpression"
        )

        # Validate with ast.parse
        try:
            ast.parse(compiled, mode="eval")
            result.compiled = compiled
            result.ast_valid = True
        except SyntaxError as e:
            result.compiled = compiled
            result.error = f"SyntaxError: {e}"

        output_results.append(result)
        if result.ast_valid:
            lines.append(f"{name} = {compiled}")
        else:
            any_failed = True

    if any_failed:
        return None, execution_order, output_results, found_undeclared

    # Build return statement -- only declared outputs, in execution order
    return_names = [n for n in execution_order if n in output_names]
    if len(return_names) == 1:
        lines.append(f"return {return_names[0]}")
    else:
        lines.append(f"return ({', '.join(return_names)})")

    body = "\n".join(lines)
    return body, execution_order, output_results, found_undeclared


# ---------------------------------------------------------------------------
# Phase 3: Ground truth comparison
# ---------------------------------------------------------------------------

HANDWRITTEN_IMPL_DIR = Path(
    "/home/reid/1cfe/fusion-tea/generated/solar_battery/handwritten/solarbatterylibrary"
)


def generate_test_inputs(calc_def: Any) -> dict[str, float]:
    """Generate strictly positive non-zero test inputs for a CalcDef."""
    inputs: dict[str, float] = {}
    for attr in calc_def.input_attributes:
        name = attr.name
        # Priority 1: default_value from CalcDef
        if attr.default_value is not None:
            try:
                val = float(attr.default_value)
                if val > 0:
                    inputs[name] = val
                    continue
                # If default is 0 or negative, use synthetic
            except (ValueError, TypeError):
                pass

        # Priority 2: deterministic synthetic
        h = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16) % 100 + 1
        inputs[name] = float(h)

    return inputs


def extract_handwritten_body(impl_path: Path) -> str | None:
    """Extract executable function body from a handwritten _impl.py file.

    Returns None if the file is a stub (NotImplementedError) or can't be exec'd.
    """
    if not impl_path.exists():
        return None

    text = impl_path.read_text()

    # Check for stub
    if "raise NotImplementedError" in text:
        return None

    # Find the function definition
    lines = text.split("\n")
    func_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("def run_"):
            func_start = i
            break

    if func_start is None:
        return None

    # Extract body: everything after the def line
    body_lines = lines[func_start + 1:]

    # Skip docstring
    in_docstring = False
    body_start = 0
    for i, line in enumerate(body_lines):
        stripped = line.strip()
        if not in_docstring and stripped.startswith('"""'):
            if stripped.endswith('"""') and len(stripped) > 3:
                # Single-line docstring
                body_start = i + 1
                continue
            in_docstring = True
            continue
        if in_docstring:
            if '"""' in stripped:
                in_docstring = False
                body_start = i + 1
                continue
            continue
        body_start = i
        break

    body_lines = body_lines[body_start:]

    # Dedent the body
    body = textwrap.dedent("\n".join(body_lines)).strip()

    if not body:
        return None

    return body


def compare_compiled_vs_handwritten(
    calc_def: Any,
    compiled_body: str,
    impl_path: Path,
    input_dict: dict[str, float],
    output_names_ordered: list[str],
) -> ComparisonResult:
    """Execute both compiled and handwritten impls, compare results."""
    result = ComparisonResult(calc_name=calc_def.name)

    handwritten_body = extract_handwritten_body(impl_path)
    if handwritten_body is None:
        result.status = "STUB"
        result.notes = "Handwritten impl is NotImplementedError stub"
        return result

    inputs_ns = SimpleNamespace(**input_dict)

    # --- Execute compiled version ---
    compiled_outputs: dict[str, float] = {}
    try:
        exec_globals: dict[str, Any] = {"inputs": inputs_ns}
        # Execute all assignment lines (skip the return statement)
        assignment_lines = []
        for line in compiled_body.split("\n"):
            stripped = line.strip()
            if stripped == "" or stripped.startswith("return ") or stripped.startswith("return("):
                continue
            assignment_lines.append(line)
        exec("\n".join(assignment_lines), exec_globals)
        for name in output_names_ordered:
            compiled_outputs[name] = exec_globals[name]
    except Exception as e:
        result.status = "ERROR"
        result.notes = f"Compiled exec failed: {e}"
        return result

    # --- Execute handwritten version ---
    hw_outputs: dict[str, float] = {}
    try:
        # Always wrap in function since handwritten bodies contain 'return'
        func_code = f"def _hw(inputs):\n{textwrap.indent(handwritten_body, '    ')}"
        func_globals: dict[str, Any] = {}
        exec(func_code, func_globals)
        hw_result = func_globals["_hw"](inputs_ns)

        if isinstance(hw_result, tuple):
            for i, name in enumerate(output_names_ordered):
                if i < len(hw_result):
                    hw_outputs[name] = hw_result[i]
        elif hw_result is not None:
            if len(output_names_ordered) == 1:
                hw_outputs[output_names_ordered[0]] = hw_result
            else:
                # Single return value -- assign to first output
                hw_outputs[output_names_ordered[0]] = hw_result

    except Exception as e:
        result.status = "ERROR"
        result.notes = f"Handwritten exec failed: {e}"
        return result

    if not hw_outputs:
        result.status = "EXCLUDED"
        result.notes = "Could not extract handwritten outputs"
        return result

    # --- Compare ---
    max_rel_error = 0.0
    all_match = True
    for name in output_names_ordered:
        if name not in compiled_outputs or name not in hw_outputs:
            continue
        compiled_val = compiled_outputs[name]
        hw_val = hw_outputs[name]
        if hw_val == 0 and compiled_val == 0:
            rel_error = 0.0
        elif hw_val == 0:
            rel_error = abs(compiled_val)
        else:
            rel_error = abs(compiled_val - hw_val) / abs(hw_val)
        result.per_output[name] = {
            "compiled": compiled_val,
            "handwritten": hw_val,
            "rel_error": rel_error,
            "match": rel_error < 1e-10,
        }
        max_rel_error = max(max_rel_error, rel_error)
        if rel_error >= 1e-10:
            all_match = False

    result.max_relative_error = max_rel_error
    result.status = "MATCH" if all_match else "MISMATCH"
    return result


# ---------------------------------------------------------------------------
# Suite runner
# ---------------------------------------------------------------------------

DEFAULT_SUITES: list[tuple[str, list[Path]]] = [
    ("chain_spike_model", [Path("tests/fixtures/chain_spike_model")]),
    ("sample_model", [Path("tests/fixtures/sample_model")]),
    ("solar_battery_model", [Path("tests/fixtures/solar_battery_model")]),
    ("catf_mfe", [
        Path("/home/reid/fusion_modeling/models/library"),
        Path("/home/reid/fusion_modeling/models/designs/catf_mfe"),
    ]),
]


def run_suite(
    label: str,
    model_paths: list[Path],
    do_comparison: bool = False,
) -> list[CalcDefCompileResult]:
    """Run expression compilation on a single model suite."""
    print(f"\n{'='*70}")
    print(f"Suite: {label}")
    paths_str = ", ".join(str(p) for p in model_paths)
    print(f"Paths: {paths_str}")
    print(f"{'='*70}")

    raw_elems, calc_defs, adapter = load_and_extract(model_paths)
    if adapter is None:
        return []

    calc_def_by_name = {cd.name: cd for cd in calc_defs}
    all_results: list[CalcDefCompileResult] = []

    for raw_elem in raw_elems:
        name = sanitize_name(raw_elem.name)
        calc_def = calc_def_by_name.get(name)
        if calc_def is None:
            print(f"  WARN: Raw element '{name}' not found in structured extraction")
            continue

        body, exec_order, output_results, undeclared = compile_calc_def_body(
            calc_def, raw_elem, adapter,
        )

        cdr = CalcDefCompileResult(
            calc_name=name,
            suite=label,
            output_results=output_results,
            execution_order=exec_order,
            full_body=body,
            undeclared_intermediates=undeclared,
        )

        if body is not None:
            # Validate full function body
            func_code = f"def run(inputs):\n{textwrap.indent(body, '    ')}"
            try:
                ast.parse(func_code)
                cdr.full_body_valid = True
            except SyntaxError as e:
                cdr.full_body_error = str(e)
        else:
            cdr.has_circular_deps = exec_order is None

        all_results.append(cdr)

    # Print per-output results table
    print(f"\n--- Per-Output Compilation Results ---")
    print(f"{'CalcDef':<30} {'Output':<25} {'Compiled':<50} {'Valid':<6} {'Notes':<30}")
    print("-" * 145)
    for cdr in all_results:
        for i, r in enumerate(cdr.output_results):
            calc_col = cdr.calc_name if i == 0 else ""
            compiled_str = (r.compiled[:47] + "...") if r.compiled and len(r.compiled) > 50 else (r.compiled or "-")
            valid_str = "PASS" if r.ast_valid else "FAIL"
            notes: list[str] = []
            if r.is_literal_only:
                notes.append("literal")
            if r.is_passthrough:
                notes.append("passthrough")
            if r.has_unary_negation:
                notes.append("unary_neg")
            if r.error:
                notes.append(r.error[:25])
            if r.literal_value_type:
                notes.append(f"LitVal={r.literal_value_type}")
            notes_str = ", ".join(notes)
            print(f"{calc_col:<30} {r.output_name:<25} {compiled_str:<50} {valid_str:<6} {notes_str:<30}")

    # Print full-body summary
    print(f"\n--- Full Function Body Summary ---")
    print(f"{'CalcDef':<30} {'Outputs':<8} {'ExecOrder':<45} {'BodyValid':<10} {'Notes':<30}")
    print("-" * 125)
    for cdr in all_results:
        order_str = " -> ".join(cdr.execution_order) if cdr.execution_order else "N/A"
        if len(order_str) > 43:
            order_str = order_str[:40] + "..."
        valid_str = "PASS" if cdr.full_body_valid else "FAIL"
        notes: list[str] = []
        if cdr.has_circular_deps:
            notes.append("CIRCULAR")
        if cdr.undeclared_intermediates:
            notes.append(f"undecl: {cdr.undeclared_intermediates}")
        if cdr.full_body_error:
            notes.append(cdr.full_body_error[:25])
        notes_str = ", ".join(notes)
        print(
            f"{cdr.calc_name:<30} {len(cdr.output_results):<8} {order_str:<45} "
            f"{valid_str:<10} {notes_str:<30}"
        )

    # Phase 3: Ground truth comparison (when handwritten impls exist)
    GROUND_TRUTH_SUITES = {"solar_battery_model"}
    if do_comparison and label in GROUND_TRUTH_SUITES and HANDWRITTEN_IMPL_DIR.exists():
        print(f"\n--- Ground Truth Comparison (Phase 3) ---")
        print(f"Handwritten impls dir: {HANDWRITTEN_IMPL_DIR}")
        print(f"{'CalcDef':<30} {'Status':<12} {'MaxRelErr':<15} {'Notes':<50}")
        print("-" * 110)

        comparison_results: list[ComparisonResult] = []
        for cdr in all_results:
            impl_name = cdr.calc_name.lower() + "_impl.py"
            impl_path = HANDWRITTEN_IMPL_DIR / impl_name

            if cdr.full_body is None or cdr.execution_order is None:
                cr = ComparisonResult(
                    calc_name=cdr.calc_name,
                    status="EXCLUDED",
                    notes="Full body compilation failed",
                )
            else:
                input_dict = generate_test_inputs(calc_def_by_name[cdr.calc_name])
                cr = compare_compiled_vs_handwritten(
                    calc_def_by_name[cdr.calc_name],
                    cdr.full_body,
                    impl_path,
                    input_dict,
                    cdr.execution_order,
                )

            comparison_results.append(cr)
            err_str = f"{cr.max_relative_error:.2e}" if cr.max_relative_error > 0 else "0"
            print(f"{cr.calc_name:<30} {cr.status:<12} {err_str:<15} {cr.notes:<50}")

        # Detailed per-output comparison for MATCH/MISMATCH
        print(f"\n--- Detailed Per-Output Comparison ---")
        for cr in comparison_results:
            if cr.per_output:
                print(f"\n  {cr.calc_name} ({cr.status}):")
                for out_name, vals in cr.per_output.items():
                    match_str = "OK" if vals["match"] else "MISMATCH"
                    print(
                        f"    {out_name:<25} compiled={vals['compiled']:<20.10g} "
                        f"handwritten={vals['handwritten']:<20.10g} "
                        f"rel_err={vals['rel_error']:.2e} {match_str}"
                    )

    # Suite summary
    total = len(all_results)
    fully_compiled = sum(1 for r in all_results if r.full_body_valid)
    total_outputs = sum(len(r.output_results) for r in all_results)
    valid_outputs = sum(sum(1 for o in r.output_results if o.ast_valid) for r in all_results)
    print(f"\n  Suite summary:")
    print(f"    CalcDefs: {fully_compiled}/{total} full body valid")
    print(f"    Outputs:  {valid_outputs}/{total_outputs} ast.parse() pass")

    return all_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    do_comparison = "--compare" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--compare"]

    if args:
        suites = []
        for arg in args:
            paths = [Path(p.strip()) for p in arg.split(",")]
            label = paths[0].name if len(paths) == 1 else "+".join(p.name for p in paths)
            suites.append((label, paths))
    else:
        suites = DEFAULT_SUITES

    grand_results: list[CalcDefCompileResult] = []

    for label, model_paths in suites:
        results = run_suite(label, model_paths, do_comparison=do_comparison)
        grand_results.extend(results)

    # Grand summary
    print(f"\n{'='*70}")
    print("GRAND SUMMARY")
    print(f"{'='*70}")

    total_calcdefs = len(grand_results)
    fully_compiled = sum(1 for r in grand_results if r.full_body_valid)
    total_outputs = sum(len(r.output_results) for r in grand_results)
    valid_outputs = sum(
        sum(1 for o in r.output_results if o.ast_valid) for r in grand_results
    )

    print(f"Total CalcDefs: {total_calcdefs}")
    print(f"Full body valid: {fully_compiled} ({fully_compiled/total_calcdefs*100:.1f}%)")
    print(f"Total outputs: {total_outputs}")
    print(f"Outputs ast.parse() pass: {valid_outputs} ({valid_outputs/total_outputs*100:.1f}%)")

    # Operator mapping table
    print(f"\n--- Operator Mapping Validation ---")
    print(f"{'Operator':<10} {'Python':<10} {'Encountered':<12} {'Example':<60}")
    print("-" * 95)
    for op, py_op in PYTHON_OPERATOR_MAP.items():
        encountered = op in OPERATOR_ENCOUNTERS
        example = OPERATOR_ENCOUNTERS.get(op, ["-"])[0] if encountered else "-"
        if len(example) > 58:
            example = example[:55] + "..."
        py_display = repr(py_op) if py_op is not None else "STRIP"
        print(f"{op!r:<10} {py_display:<10} {str(encountered):<12} {example:<60}")

    # LiteralRational.value type documentation
    literal_types: set[str] = set()
    for r in grand_results:
        for o in r.output_results:
            if o.literal_value_type:
                literal_types.add(o.literal_value_type)
    if literal_types:
        print(f"\nLiteralRational.value types observed: {sorted(literal_types)}")

    # Unary negation summary
    any_unary = any(
        o.has_unary_negation
        for r in grand_results for o in r.output_results
    )
    print(f"Unary negation encountered: {any_unary}")

    # Undeclared intermediates
    all_undeclared: set[str] = set()
    for r in grand_results:
        all_undeclared.update(r.undeclared_intermediates)
    if all_undeclared:
        print(f"\nUndeclared intermediates found: {sorted(all_undeclared)}")
        for r in grand_results:
            if r.undeclared_intermediates:
                print(f"  {r.calc_name}: {r.undeclared_intermediates}")

    # CalcDefs with failures
    failed = [r for r in grand_results if not r.full_body_valid]
    if failed:
        print(f"\n--- Failed CalcDefs ({len(failed)}) ---")
        for r in failed:
            reasons = []
            if r.has_circular_deps:
                reasons.append("circular deps")
            for o in r.output_results:
                if o.error:
                    reasons.append(f"{o.output_name}: {o.error}")
            print(f"  {r.calc_name} ({r.suite}): {'; '.join(reasons)}")


if __name__ == "__main__":
    main()
